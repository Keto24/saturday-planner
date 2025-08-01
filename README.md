# SaturdayPlanner AI Agent

An autonomous AI agent built with NVIDIA's NeMo Agent Toolkit that plans your perfect Saturday activities.

## What This Agent Does

Every Saturday, the agent will:
1. 🌤️ Check the weather in your area
2. 🔍 Search for activities (restaurants, entertainment, outdoor activities)
3. 🧠 Filter activities based on weather (indoor if rainy, outdoor if sunny)
4. ⭐ Rank options based on ratings and your past preferences
5. 📅 Schedule the best option in your calendar
6. 📱 Send you a notification with the plan

## Project Structure

```
saturday_planner/
├── agent_tools.py       # The agent's "hands" - functions to check weather, find restaurants, etc.
├── saturday_agent.py    # The agent's "brain" - main thinking and decision logic
├── agent_prompts.py     # The agent's "instructions" - what to say to the AI model
├── planning_logic.py    # The agent's "wisdom" - how to choose the best activities
├── main.py             # The agent's "interface" - web API for users to interact
├── config.py           # The agent's "settings" - API keys and preferences
└── requirements.txt    # The agent's "dependencies" - what software it needs
```

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys:**
   - Copy `.env.example` to `.env`
   - Fill in your API keys and preferences

3. **Run the Agent:**
   ```bash
   python main.py
   ```

## Built With
- 🧠 NVIDIA Nemotron AI Model (llama-3.3-nemotron-super-49b-v1)
- 🔧 NeMo Agent Toolkit & LangGraph
- ☁️ Deployed on NVIDIA Brev GPU Platform