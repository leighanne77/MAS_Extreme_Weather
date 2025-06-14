from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio
from multi_tool_agent.agent_team import AgentTeamManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze")
async def analyze(location: str = Form(...)):
    logger.info(f"Received request for location: {location}")
    manager = AgentTeamManager()
    request = {
        "location": location,
        "task": "analyze_climate_risks"
    }
    result = await manager.handle_request(request, session_id="web_session", user_id="web_user")
    logger.info(f"Analysis result: {result}")
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 