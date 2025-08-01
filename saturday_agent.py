"""
Saturday Agent - The SaturdayPlanner's "Brain" 

This is the core reasoning system that orchestrates the entire Saturday planning process.
It uses NVIDIA's Nemotron model to think step-by-step and decide what tools to use when.

Think of this as the agent's "thought process" - it goes through a logical sequence
of steps to plan the perfect Saturday, just like a human would.
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from langgraph.graph import StateGraph, START, END
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from config import config
from agent_tools import get_weather, search_places, memory_fetch, memory_store, schedule_event, send_notification
from agent_prompts import (
    SATURDAY_PLANNER_SYSTEM_PROMPT,
    WEATHER_CHECK_PROMPT,
    CATEGORY_DECISION_PROMPT,
    ACTIVITY_SEARCH_PROMPT,
    WEATHER_FILTER_PROMPT,
    RANKING_PROMPT,
    FINAL_SELECTION_PROMPT,
    SUCCESS_PROMPT
)

class SaturdayPlannerState(BaseModel):
    """
    The agent's memory during the planning process.
    
    This keeps track of everything the agent learns and decides
    as it goes through each step of planning your Saturday.
    """
    # Input parameters
    zip_code: str = config.DEFAULT_ZIP_CODE
    user_message: str = ""
    
    # Step-by-step results
    weather: Optional[Dict[str, Any]] = None
    chosen_categories: List[str] = []
    candidates: List[Dict[str, Any]] = []
    filtered: List[Dict[str, Any]] = []
    ranking: List[Dict[str, Any]] = []
    choice: Optional[Dict[str, Any]] = None
    calendar: Optional[Dict[str, Any]] = None
    notification: Optional[Dict[str, str]] = None
    
    # Process tracking
    current_step: str = "start"
    reasoning: List[str] = []
    errors: List[str] = []
    
    class Config:
        arbitrary_types_allowed = True

class SaturdayPlannerAgent:
    """
    The main agent class that coordinates all the thinking and tool usage.
    
    This is like the agent's brain that decides what to do next based on
    what it has learned so far.
    """
    
    def __init__(self):
        # Initialize the NVIDIA Nemotron AI model
        self.llm = ChatNVIDIA(
            model="nvidia/llama-3.3-nemotron-super-49b-v1",
            api_key=config.NEMO_API_KEY,
            base_url=config.NEMO_ENDPOINT
        )
        
        # Build the step-by-step workflow graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the agent's step-by-step thinking process.
        
        This creates a flowchart of decisions the agent follows:
        START -> Check Weather -> Choose Categories -> Search -> Filter -> Rank -> Select -> Schedule -> Notify -> END
        """
        workflow = StateGraph(SaturdayPlannerState)
        
        # Add each step of the planning process
        workflow.add_node("weather_check", self._weather_check_step)
        workflow.add_node("category_decision", self._category_decision_step)  
        workflow.add_node("activity_search", self._activity_search_step)
        workflow.add_node("weather_filter", self._weather_filter_step)
        workflow.add_node("ranking", self._ranking_step)
        workflow.add_node("final_selection", self._final_selection_step)
        workflow.add_node("scheduling", self._scheduling_step)
        workflow.add_node("notification", self._notification_step)
        
        # Define the flow: each step leads to the next
        workflow.add_edge(START, "weather_check")
        workflow.add_edge("weather_check", "category_decision")
        workflow.add_edge("category_decision", "activity_search")
        workflow.add_edge("activity_search", "weather_filter")
        workflow.add_edge("weather_filter", "ranking")
        workflow.add_edge("ranking", "final_selection")
        workflow.add_edge("final_selection", "scheduling")
        workflow.add_edge("scheduling", "notification") 
        workflow.add_edge("notification", END)
        
        return workflow.compile()
    
    def _get_ai_response(self, prompt: str, context: str = "") -> str:
        """
        Ask the NVIDIA Nemotron AI model to think about something.
        
        This is like asking a very smart assistant for their opinion
        on what to do next in the planning process.
        """
        try:
            messages = [
                SystemMessage(content=SATURDAY_PLANNER_SYSTEM_PROMPT),
                HumanMessage(content=f"{context}\n\n{prompt}")
            ]
            
            response = self.llm.invoke(messages)
            return response.content
            
        except Exception as e:
            print(f"AI model error: {e}")
            return f"AI reasoning unavailable: {e}"
    
    def _weather_check_step(self, state: SaturdayPlannerState) -> SaturdayPlannerState:
        """
        Step 1: Check the weather for the user's location.
        
        This is like looking outside or checking a weather app before deciding
        what kind of activities to recommend.
        """
        print(f"Step 1: Checking weather for {state.zip_code}")
        
        try:
            # Get weather data using our weather tool
            weather_data = get_weather(state.zip_code)
            state.weather = weather_data
            state.current_step = "weather_checked"
            
            # Ask AI to reason about the weather
            weather_summary = f"{weather_data['forecast']}, {weather_data['high']}F, {weather_data['rain_chance']}% rain"
            prompt = WEATHER_CHECK_PROMPT.format(zip_code=state.zip_code)
            reasoning = self._get_ai_response(prompt, f"Weather result: {weather_summary}")
            state.reasoning.append(f"Weather Check: {reasoning}")
            
            print(f"Weather: {weather_summary}")
            
        except Exception as e:
            error_msg = f"Weather check failed: {e}"
            state.errors.append(error_msg)
            print(f"Error: {error_msg}")
            
            # Fallback weather for planning
            state.weather = {"forecast": "unknown", "high": 70, "low": 60, "rain_chance": 30}
        
        return state
    
    def _category_decision_step(self, state: SaturdayPlannerState) -> SaturdayPlannerState:
        """
        Step 2: Decide what types of activities to look for based on weather.
        
        This is the agent's decision-making: "It's raining, so let's look for 
        restaurants and museums instead of parks."
        """
        print("Step 2: Deciding activity categories based on weather")
        
        try:
            weather = state.weather
            rain_chance = weather.get("rain_chance", 0)
            temp_high = weather.get("high", 70)
            forecast = weather.get("forecast", "unknown")
            
            # Agent's decision logic
            categories = []
            if rain_chance > 70 or forecast == "rainy":
                categories = ["restaurant", "entertainment"]  # Indoor only
                reasoning = "High rain chance - focusing on indoor activities"
            elif rain_chance > 30:
                categories = ["restaurant", "entertainment", "shopping"]  # Mixed indoor
                reasoning = "Moderate rain chance - indoor activities with some options"
            else:
                categories = ["restaurant", "outdoor", "entertainment"]  # Include outdoor
                reasoning = "Low rain chance - including outdoor activities"
            
            # Temperature adjustments
            if temp_high < 50:
                categories = ["restaurant", "entertainment", "shopping"]  # Warm places
                reasoning += " + cold weather favors indoor venues"
            elif temp_high > 85:
                categories = ["restaurant", "entertainment", "outdoor"]  # Include parks with shade
                reasoning += " + hot weather, including shaded outdoor options"
            
            state.chosen_categories = categories
            state.current_step = "categories_chosen"
            
            # Get AI reasoning about the decision
            weather_summary = f"{forecast}, {temp_high}F, {rain_chance}% rain"
            prompt = CATEGORY_DECISION_PROMPT.format(
                weather_summary=weather_summary,
                chosen_categories=", ".join(categories)
            )
            ai_reasoning = self._get_ai_response(prompt)
            state.reasoning.append(f"Category Decision: {ai_reasoning}")
            
            print(f"Chosen categories: {categories}")
            print(f"Reasoning: {reasoning}")
            
        except Exception as e:
            error_msg = f"Category decision failed: {e}"
            state.errors.append(error_msg)
            print(f"Error: {error_msg}")
            
            # Fallback to restaurants
            state.chosen_categories = ["restaurant"]
        
        return state
    
    def _activity_search_step(self, state: SaturdayPlannerState) -> SaturdayPlannerState:
        """
        Step 3: Search for actual activities using Google Places API.
        
        This is where the agent uses its "hands" (the search tool) to find
        real restaurants, parks, museums, etc. in the user's area.
        """
        print("Step 3: Searching for activities")
        
        all_candidates = []
        
        for category in state.chosen_categories:
            try:
                print(f"   Searching {category}...")
                
                # Use our Google Places search tool
                places = search_places(
                    category=category,
                    zip_code=state.zip_code,
                    radius_miles=config.DEFAULT_RADIUS_MILES,
                    max_price=config.DEFAULT_MAX_PRICE
                )
                
                all_candidates.extend(places)
                print(f"   Found {len(places)} {category} options")
                
            except Exception as e:
                error_msg = f"Search failed for {category}: {e}"
                state.errors.append(error_msg)
                print(f"Error: {error_msg}")
        
        state.candidates = all_candidates
        state.current_step = "search_complete"
        
        # Get AI reasoning about the search
        prompt = ACTIVITY_SEARCH_PROMPT.format(
            category=", ".join(state.chosen_categories),
            zip_code=state.zip_code,
            radius=config.DEFAULT_RADIUS_MILES,
            max_price=config.DEFAULT_MAX_PRICE
        )
        reasoning = self._get_ai_response(prompt, f"Found {len(all_candidates)} total activities")
        state.reasoning.append(f"Activity Search: {reasoning}")
        
        print(f"Total candidates found: {len(all_candidates)}")
        return state
    
    def _weather_filter_step(self, state: SaturdayPlannerState) -> SaturdayPlannerState:
        """
        Step 4: Filter activities based on weather appropriateness.
        
        This removes activities that don't make sense for the weather.
        Like removing "outdoor park" if it's stormy.
        """
        print("Step 4: Filtering activities by weather appropriateness")
        
        try:
            weather = state.weather
            rain_chance = weather.get("rain_chance", 0)
            forecast = weather.get("forecast", "unknown")
            
            filtered_activities = []
            
            for activity in state.candidates:
                keep = True
                reason = ""
                
                # Weather-based filtering logic
                if forecast in ["rainy", "stormy"] or rain_chance > 70:
                    # High rain - only keep indoor activities
                    if activity["category"] == "outdoor":
                        keep = False
                        reason = "outdoor activity in rainy weather"
                
                elif rain_chance > 40:
                    # Moderate rain - prefer covered/indoor
                    if activity["category"] == "outdoor" and activity["rating"] < 4.0:
                        keep = False  # Only keep high-rated outdoor if moderate rain
                        reason = "lower-rated outdoor activity with moderate rain risk"
                
                if keep:
                    filtered_activities.append(activity)
                else:
                    print(f"   Filtered out {activity['name']}: {reason}")
            
            state.filtered = filtered_activities
            state.current_step = "weather_filtered"
            
            # Get AI reasoning about filtering
            prompt = WEATHER_FILTER_PROMPT.format(
                candidate_count=len(state.candidates),
                weather_conditions=f"{forecast}, {rain_chance}% rain",
                filtered_count=len(filtered_activities)
            )
            reasoning = self._get_ai_response(prompt)
            state.reasoning.append(f"Weather Filtering: {reasoning}")
            
            print(f"After weather filtering: {len(filtered_activities)} activities remain")
            
        except Exception as e:
            error_msg = f"Weather filtering failed: {e}"
            state.errors.append(error_msg)
            print(f"Error: {error_msg}")
            
            # If filtering fails, use all candidates
            state.filtered = state.candidates
        
        return state
    
    def _ranking_step(self, state: SaturdayPlannerState) -> SaturdayPlannerState:
        """
        Step 5: Rank activities based on rating, user history, and weather fit.
        
        This is where the agent gets smart about recommendations - it considers
        what you've liked before and how well each activity fits the weather.
        """
        print("Step 5: Ranking activities")
        
        try:
            # Get user's past preferences
            user_history = memory_fetch("liked_places")
            
            ranked_activities = []
            
            for activity in state.filtered:
                # Calculate composite score
                rating_score = activity.get("rating", 0) / 5.0  # Normalize to 0-1
                
                # History bonus - check if user liked similar places
                history_score = 0
                for liked_place in user_history:
                    if liked_place.lower() in activity["name"].lower():
                        history_score = 1.0  # Exact match bonus
                        break
                    elif activity["category"] in liked_place.lower():
                        history_score = 0.5  # Category match bonus
                
                # Weather appropriateness score
                weather_score = 1.0  # Default
                if state.weather.get("rain_chance", 0) < 30 and activity["category"] == "outdoor":
                    weather_score = 1.2  # Bonus for outdoor in good weather
                elif state.weather.get("rain_chance", 0) > 70 and activity["category"] != "outdoor":
                    weather_score = 1.1  # Bonus for indoor in bad weather
                
                # Weighted composite score
                composite_score = (
                    rating_score * 0.4 +
                    history_score * 0.4 +
                    (weather_score - 1.0) * 0.2
                )
                
                ranked_activities.append({
                    **activity,
                    "composite_score": composite_score,
                    "rating_score": rating_score,
                    "history_score": history_score,
                    "weather_score": weather_score
                })
            
            # Sort by composite score (highest first)
            ranked_activities.sort(key=lambda x: x["composite_score"], reverse=True)
            
            # Take top 3 for final consideration
            state.ranking = ranked_activities[:3]
            state.current_step = "activities_ranked"
            
            # Get AI reasoning about ranking
            top_activities_text = "\n".join([
                f"{i+1}. {act['name']} - Score: {act['composite_score']:.2f} (Rating: {act['rating']}, Category: {act['category']})"
                for i, act in enumerate(state.ranking)
            ])
            
            prompt = RANKING_PROMPT.format(
                activity_count=len(state.filtered),
                user_history=", ".join(user_history) if user_history else "No previous history",
                weather_factor=f"Rain chance: {state.weather.get('rain_chance', 0)}%",
                top_activities=top_activities_text
            )
            reasoning = self._get_ai_response(prompt)
            state.reasoning.append(f"Activity Ranking: {reasoning}")
            
            print(f"Top 3 activities selected based on rating + preferences + weather")
            for i, activity in enumerate(state.ranking):
                print(f"   {i+1}. {activity['name']} - Score: {activity['composite_score']:.2f}")
            
        except Exception as e:
            error_msg = f"Ranking failed: {e}"
            state.errors.append(error_msg)
            print(f"Error: {error_msg}")
            
            # Fallback: just take top 3 by rating
            state.ranking = sorted(state.filtered, key=lambda x: x.get("rating", 0), reverse=True)[:3]
        
        return state
    
    def _final_selection_step(self, state: SaturdayPlannerState) -> SaturdayPlannerState:
        """
        Step 6: Make the final choice from the top-ranked activities.
        
        This is the agent's final decision - picking the best option for Saturday.
        """
        print("Step 6: Making final selection")
        
        try:
            if state.ranking:
                # Choose the top-ranked activity
                selected = state.ranking[0]
                state.choice = selected
                state.current_step = "selection_made"
                
                # Get AI reasoning for the final choice
                selection_reasoning = f"""
                Selected {selected['name']} because:
                - Highest composite score: {selected['composite_score']:.2f}
                - Rating: {selected['rating']}/5.0
                - Category: {selected['category']} (appropriate for {state.weather.get('forecast', 'current')} weather)
                - Location: {selected['address']}
                """
                
                prompt = FINAL_SELECTION_PROMPT.format(
                    selected_activity=selected['name'],
                    selection_reasoning=selection_reasoning
                )
                reasoning = self._get_ai_response(prompt)
                state.reasoning.append(f"Final Selection: {reasoning}")
                
                print(f"Selected: {selected['name']} ({selected['rating']} stars)")
                print(f"   Address: {selected['address']}")
                print(f"   Score breakdown: Rating={selected['rating_score']:.2f}, History={selected['history_score']:.2f}, Weather={selected['weather_score']:.2f}")
                
            else:
                error_msg = "No activities available for selection"
                state.errors.append(error_msg)
                print(f"Error: {error_msg}")
                
        except Exception as e:
            error_msg = f"Final selection failed: {e}"
            state.errors.append(error_msg)
            print(f"Error: {error_msg}")
        
        return state
    
    def _scheduling_step(self, state: SaturdayPlannerState) -> SaturdayPlannerState:
        """
        Step 7: Schedule the selected activity in the user's calendar.
        
        This creates a calendar event for Saturday at 11 AM with the chosen activity.
        """
        print("Step 7: Scheduling calendar event")
        
        try:
            if state.choice:
                # Calculate next Saturday at 11 AM
                next_saturday = datetime.now()
                days_ahead = 5 - next_saturday.weekday()  # Saturday is 5
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                next_saturday += timedelta(days=days_ahead)
                next_saturday = next_saturday.replace(hour=11, minute=0, second=0, microsecond=0)
                
                # Create calendar event
                event_title = f"Saturday Plan: {state.choice['name']}"
                datetime_str = next_saturday.strftime("%Y-%m-%d %H:%M")
                
                calendar_result = schedule_event(
                    calendar_id="primary",
                    title=event_title,
                    datetime_str=datetime_str
                )
                
                state.calendar = calendar_result
                state.current_step = "event_scheduled"
                
                print(f"Calendar event created: {event_title} at {datetime_str}")
                
            else:
                error_msg = "No activity selected for scheduling"
                state.errors.append(error_msg)
                print(f"Error: {error_msg}")
                
        except Exception as e:
            error_msg = f"Scheduling failed: {e}"
            state.errors.append(error_msg)
            print(f"Error: {error_msg}")
            # Continue without calendar event
            state.calendar = {"status": "failed", "error": str(e)}
        
        return state
    
    def _notification_step(self, state: SaturdayPlannerState) -> SaturdayPlannerState:
        """
        Step 8: Send a notification to the user about their Saturday plan.
        
        This is the final step - letting the user know their plan is ready!
        """
        print("Step 8: Sending notification")
        
        try:
            if state.choice:
                # Create notification message
                weather_summary = f"{state.weather['forecast']}, {state.weather['high']}F"
                message = f"""Your Saturday Plan is Ready!

Activity: {state.choice['name']}
Address: {state.choice['address']}  
Rating: {state.choice['rating']} stars
Time: Saturday 11:00 AM
Weather: {weather_summary}

Calendar event created! Have a great Saturday!"""
                
                notification_result = send_notification("sms", message)
                state.notification = notification_result
                state.current_step = "notification_sent"
                
                # Store this choice in memory for future recommendations
                memory_store("liked_places", state.choice['name'])
                
                print(f"Notification sent successfully")
                
                # Get final AI success message
                success_message = SUCCESS_PROMPT.format(
                    activity_name=state.choice['name'],
                    activity_address=state.choice['address'],
                    weather_summary=weather_summary
                )
                state.reasoning.append(f"Success: {success_message}")
                
            else:
                error_msg = "No activity selected for notification"
                state.errors.append(error_msg)
                print(f"Error: {error_msg}")
                
        except Exception as e:
            error_msg = f"Notification failed: {e}"
            state.errors.append(error_msg)
            print(f"Error: {error_msg}")
            # Continue - notification failure shouldn't stop the process
            state.notification = {"status": "failed", "error": str(e)}
        
        return state
    
    def plan_saturday(self, zip_code: str = None, user_message: str = "") -> Dict[str, Any]:
        """
        Main function to plan a Saturday - this runs the entire agent workflow.
        
        Args:
            zip_code: Where to plan activities (defaults to SF)
            user_message: Any specific requests from user
            
        Returns:
            Complete planning result in JSON format
        """
        print("Starting Saturday Planning Agent")
        print("=" * 50)
        
        # Initialize the planning state
        initial_state = SaturdayPlannerState(
            zip_code=zip_code or config.DEFAULT_ZIP_CODE,
            user_message=user_message
        )
        
        try:
            # Run the complete workflow
            final_state = self.graph.invoke(initial_state)
            
            # Format the final JSON response - LangGraph returns a dictionary
            result = {
                "weather": final_state.get('weather', None),
                "candidates": final_state.get('candidates', []),
                "filtered": final_state.get('filtered', []),
                "ranking": final_state.get('ranking', []),
                "choice": final_state.get('choice', None),
                "calendar": final_state.get('calendar', {"status": "unknown"}),
                "notification": final_state.get('notification', {"status": "unknown"})
            }
            
            print("\nSaturday Planning Complete!")
            print("=" * 50)
            
            return result
            
        except Exception as e:
            error_result = {
                "error": f"Planning failed: {e}",
                "weather": initial_state.weather,
                "candidates": [],
                "filtered": [],
                "ranking": [],
                "choice": None,
                "calendar": {"status": "failed"},
                "notification": {"status": "failed"}
            }
            
            print(f"Planning failed: {e}")
            return error_result


# Create a global agent instance
saturday_agent = SaturdayPlannerAgent()

def plan_saturday(zip_code: str = None, user_message: str = "") -> Dict[str, Any]:
    """
    Simple function to plan a Saturday - this is what other parts of our app will call.
    """
    return saturday_agent.plan_saturday(zip_code, user_message)