"""
Web Interface for SaturdayPlanner AI Agent
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

from saturday_agent import plan_saturday

# Create the web application
app = FastAPI(title="SaturdayPlanner", description="AI Agent for Perfect Saturday Planning")

class PlanRequest(BaseModel):
    message: str = "Plan my Saturday"
    zip_code: Optional[str] = None

class PlanResponse(BaseModel):
    success: bool
    plan: Optional[dict] = None
    error: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SaturdayPlanner - AI Agent</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                margin: 0;
                padding: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                padding: 40px;
                max-width: 600px;
                width: 100%;
            }
            
            .header {
                text-align: center;
                margin-bottom: 30px;
            }
            
            h1 {
                color: #333;
                font-size: 2.5em;
                margin-bottom: 10px;
            }
            
            .subtitle {
                color: #666;
                font-size: 1.2em;
                margin-bottom: 30px;
            }
            
            .input-group {
                margin-bottom: 20px;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 600;
            }
            
            input, textarea {
                width: 100%;
                padding: 15px;
                border: 2px solid #e1e5e9;
                border-radius: 10px;
                font-size: 1em;
                box-sizing: border-box;
            }
            
            input:focus, textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            
            .plan-button {
                width: 100%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 18px 30px;
                border-radius: 10px;
                font-size: 1.2em;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s;
                margin-bottom: 20px;
            }
            
            .plan-button:hover {
                transform: translateY(-2px);
            }
            
            .plan-button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            
            .result {
                margin-top: 30px;
                padding: 25px;
                border-radius: 15px;
                display: none;
            }
            
            .result.success {
                background: #e8f5e8;
                border: 2px solid #4caf50;
            }
            
            .result.error {
                background: #ffebee;
                border: 2px solid #f44336;
            }
            
            .loading {
                text-align: center;
                padding: 20px;
                display: none;
            }
            
            .spinner {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin: 0 auto 15px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .plan-details {
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin: 15px 0;
            }
            
            .plan-item {
                margin: 10px 0;
                padding: 8px 0;
                border-bottom: 1px solid #eee;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🗓️ SaturdayPlanner</h1>
                <p class="subtitle">Your AI agent for perfect Saturday activities</p>
            </div>
            
            <form id="planForm">
                <div class="input-group">
                    <label for="zipCode">📍 Your Location (Zip Code)</label>
                    <input type="text" id="zipCode" name="zipCode" placeholder="94102" value="94102">
                </div>
                
                <div class="input-group">
                    <label for="message">💬 Your Request</label>
                    <textarea id="message" name="message" rows="3" placeholder="Plan something fun for my Saturday!">Plan something fun for my Saturday!</textarea>
                </div>
                
                <button type="submit" class="plan-button" id="planButton">
                    🚀 Plan My Perfect Saturday
                </button>
            </form>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>🤖 AI Agent is planning your Saturday...</p>
            </div>
            
            <div class="result" id="result">
                <div id="resultContent"></div>
            </div>
        </div>
        
        <script>
            document.getElementById('planForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const button = document.getElementById('planButton');
                const loading = document.getElementById('loading');
                const result = document.getElementById('result');
                const resultContent = document.getElementById('resultContent');
                
                button.disabled = true;
                button.textContent = '🤖 Planning...';
                loading.style.display = 'block';
                result.style.display = 'none';
                
                try {
                    const formData = new FormData(e.target);
                    const response = await fetch('/plan', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: formData.get('message'),
                            zip_code: formData.get('zipCode')
                        })
                    });
                    
                    const data = await response.json();
                    
                    loading.style.display = 'none';
                    result.style.display = 'block';
                    
                    if (data.success && data.plan) {
                        result.className = 'result success';
                        const choice = data.plan.choice;
                        const weather = data.plan.weather;
                        
                        resultContent.innerHTML = `
                            <h3>🎉 Your Perfect Saturday Plan</h3>
                            <div class="plan-details">
                                <h2 style="color: #667eea; text-align: center;">${choice ? choice.name : 'No activity selected'}</h2>
                                ${choice ? `
                                <div class="plan-item"><strong>📍 Location:</strong> ${choice.address}</div>
                                <div class="plan-item"><strong>⭐ Rating:</strong> ${choice.rating}/5.0</div>
                                <div class="plan-item"><strong>🏷️ Category:</strong> ${choice.category}</div>
                                ` : ''}
                                <div class="plan-item"><strong>🕐 When:</strong> Saturday, 11:00 AM</div>
                                <div class="plan-item"><strong>🌤️ Weather:</strong> ${weather ? weather.description : 'Unknown'}</div>
                                <div class="plan-item"><strong>📅 Calendar:</strong> Event scheduled</div>
                                <div class="plan-item"><strong>📱 Notification:</strong> Confirmation sent</div>
                            </div>
                            <div style="text-align: center; margin-top: 20px; color: #667eea;">
                                <p>🤖 Planned by AI • Have a great Saturday!</p>
                            </div>
                        `;
                    } else {
                        result.className = 'result error';
                        resultContent.innerHTML = `
                            <h3>❌ Planning Failed</h3>
                            <p>${data.error || 'Unknown error occurred'}</p>
                        `;
                    }
                } catch (error) {
                    loading.style.display = 'none';
                    result.style.display = 'block';
                    result.className = 'result error';
                    resultContent.innerHTML = `
                        <h3>❌ Error</h3>
                        <p>Failed to connect: ${error.message}</p>
                    `;
                }
                
                button.disabled = false;
                button.textContent = '🚀 Plan My Perfect Saturday';
            });
        </script>
    </body>
    </html>
    """

@app.post("/plan", response_model=PlanResponse)
async def create_plan(request: PlanRequest):
    try:
        print(f"🚀 Planning request: {request.message} for {request.zip_code}")
        
        result = plan_saturday(
            zip_code=request.zip_code,
            user_message=request.message
        )
        
        if result:
            print(f"✅ Plan created!")
            return PlanResponse(success=True, plan=result)
        else:
            return PlanResponse(success=False, error="Failed to create plan")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return PlanResponse(success=False, error=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "SaturdayPlanner"}

if __name__ == "__main__":
    print("🌐 Starting SaturdayPlanner Web Interface...")
    print("🔗 Open: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)