from fastapi import FastAPI, Request, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
import json
from typing import Dict, Any, List, Optional
from multi_agent_system.agent_team import AgentTeamManager
from multi_agent_system.a2a import A2AMessage, A2AMultiPartMessage, A2APart
from multi_agent_system.a2a.enums import MessageType, Priority, StatusCode
from multi_agent_system.a2a.parts import create_text_part, create_data_part, create_file_part
import logging
import os
from multi_agent_system.a2a.message import create_request_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Climate Risk Analysis System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent team manager
agent_manager = None

@app.on_event("startup")
async def startup_event():
    """Initialize the agent team manager on startup."""
    global agent_manager
    agent_manager = AgentTeamManager()
    await agent_manager.start()
    logger.info("Agent team manager started")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown."""
    global agent_manager
    if agent_manager:
        await agent_manager.stop()
    logger.info("Agent team manager stopped")

@app.post("/analyze")
async def analyze(location: str = Form(...)):
    """Analyze climate risks for a location."""
    logger.info(f"Received request for location: {location}")
    try:
        request = {
            "location": location,
            "task": "analyze_climate_risks"
        }
        result = await agent_manager.handle_request(request, session_id="web_session", user_id="web_user")
        logger.info(f"Analysis result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during analysis.")

@app.post("/a2a/message")
async def send_a2a_message(request: Dict[str, Any]):
    """Send an A2A message between agents."""
    try:
        # Extract message parameters
        sender = request.get("sender")
        recipient = request.get("recipient")
        content = request.get("content")
        message_type = request.get("message_type", "request")
        priority = request.get("priority", "normal")
        
        if not all([sender, recipient, content]):
            raise HTTPException(status_code=400, detail="Missing required fields: sender, recipient, content")
        
        # Convert string enums to actual enum values
        message_type_enum = MessageType(message_type)
        priority_enum = Priority(priority)
        
        # Send A2A message
        message = create_request_message(
            sender=sender,
            recipients=[recipient],
            content=content,
            message_type=message_type_enum,
            priority=priority_enum
        )
        
        # Route message through agent manager
        result = await agent_manager.route_a2a_message(sender, recipient, content, message_type_enum)
        
        return {
            "status": "success",
            "message_id": message.id,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error sending A2A message: {e}")
        raise HTTPException(status_code=500, detail=f"Error sending A2A message: {str(e)}")

@app.post("/a2a/multipart")
async def send_multipart_message(
    sender: str = Form(...),
    recipient: str = Form(...),
    message_type: str = Form(default="request"),
    priority: str = Form(default="normal"),
    text_content: Optional[str] = Form(default=None),
    data_content: Optional[str] = Form(default=None),
    files: List[UploadFile] = File(default=[])
):
    """Send a multi-part A2A message."""
    try:
        # Convert string enums to actual enum values
        message_type_enum = MessageType(message_type)
        priority_enum = Priority(priority)
        
        # Create parts
        parts = []
        
        # Add text part if provided
        if text_content:
            text_part = create_text_part(text_content)
            parts.append(text_part)
        
        # Add data part if provided
        if data_content:
            try:
                data_dict = json.loads(data_content)
                data_part = create_data_part(data_dict)
                parts.append(data_part)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON in data_content")
        
        # Add file parts if provided
        for file in files:
            if file.filename:
                # Save uploaded file temporarily
                temp_path = f"/tmp/{file.filename}"
                with open(temp_path, "wb") as f:
                    content = await file.read()
                    f.write(content)
                
                # Create file part
                file_part = create_file_part(temp_path)
                parts.append(file_part)
                
                # Clean up temp file
                os.remove(temp_path)
        
        if not parts:
            raise HTTPException(status_code=400, detail="At least one part must be provided")
        
        # Send multi-part message
        result = await agent_manager.send_multipart_message(sender, recipient, parts, message_type_enum)
        
        return {
            "status": "success",
            "message_id": result.id,
            "part_count": len(parts)
        }
        
    except Exception as e:
        logger.error(f"Error sending multi-part message: {e}")
        raise HTTPException(status_code=500, detail=f"Error sending multi-part message: {str(e)}")

@app.get("/a2a/agents")
async def get_agents():
    """Get list of registered agents."""
    try:
        agents = agent_manager.get_registered_agents()
        return {
            "status": "success",
            "agents": agents
        }
    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting agents: {str(e)}")

@app.get("/a2a/status")
async def get_a2a_status():
    """Get A2A protocol status and statistics."""
    try:
        status = agent_manager.get_a2a_status()
        return {
            "status": "success",
            "a2a_status": status
        }
    except Exception as e:
        logger.error(f"Error getting A2A status: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting A2A status: {str(e)}")

@app.get("/a2a/agent-cards")
async def get_agent_cards():
    """Get all agent cards in ADK format for discovery."""
    try:
        cards = agent_manager.get_agent_cards()
        return {"status": "success", "agent_cards": cards}
    except Exception as e:
        logger.error(f"Error getting agent cards: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting agent cards: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Climate Risk Analysis System API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "POST - Analyze climate risks for a location",
            "/a2a/message": "POST - Send A2A message between agents",
            "/a2a/multipart": "POST - Send multi-part A2A message",
            "/a2a/agents": "GET - Get list of registered agents",
            "/a2a/agent-cards": "GET - Get all agent cards in ADK format",
            "/a2a/status": "GET - Get A2A protocol status"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 