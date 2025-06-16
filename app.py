from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio
from src.multi_agent_system.agent_team import AgentTeamManager
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/analyze")
async def analyze(location: str = Form(...)):
    logger.info(f"Received request for location: {location}")
    try:
        manager = AgentTeamManager()
        request = {
            "location": location,
            "task": "analyze_climate_risks"
        }
        result = await manager.handle_request(request, session_id="web_session", user_id="web_user")
        logger.info(f"Analysis result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during analysis.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 