#!/usr/bin/env python3
"""
Simplified Tool Web Interface

A simplified web interface for the Tool multi-agent system.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import json
from typing import Dict, Any, List

# Import our data loader
from multi_agent_system.data.data_loader import get_data_loader

app = FastAPI(title="Tool Multi-Agent System", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="src/tool_web/static"), name="static")

# Templates
templates = Jinja2Templates(directory="src/tool_web/templates")

# Data loader
data_loader = get_data_loader()

# User types
USER_TYPES = [
    "Private Equity Investor",
    "Loan Officer", 
    "Chief Risk Officer",
    "Chief Sustainability Officer",
    "Data Science Officer",
    "Crop Insurance Officer",
    "Credit Officer",
    "Government Funder"
]

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main dashboard page."""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user_types": USER_TYPES
    })

@app.get("/api/user-types")
async def get_user_types():
    """Get available user types."""
    return {"user_types": USER_TYPES}

@app.get("/api/data-summary")
async def get_data_summary():
    """Get summary of available data."""
    return data_loader.get_all_data_summary()

@app.get("/api/nature-based-solutions")
async def get_nature_based_solutions():
    """Get nature-based solutions data."""
    return data_loader.load_nature_based_solutions()

@app.get("/api/historical-events")
async def get_historical_events():
    """Get historical weather events."""
    return data_loader.load_historical_weather_events()

@app.get("/api/regional-profiles")
async def get_regional_profiles():
    """Get regional risk profiles."""
    return data_loader.load_regional_risk_profiles()

@app.get("/api/economic-impacts")
async def get_economic_impacts():
    """Get economic impact data."""
    return data_loader.load_economic_impact_data()

@app.get("/api/solutions/{risk_type}")
async def get_solutions_by_risk_type(risk_type: str):
    """Get nature-based solutions for a specific risk type."""
    solutions = data_loader.get_solutions_by_risk_type(risk_type)
    return {"risk_type": risk_type, "solutions": solutions}

@app.get("/api/region/{region_name}")
async def get_region_profile(region_name: str):
    """Get risk profile for a specific region."""
    profile = data_loader.get_regional_profile(region_name)
    if profile:
        return {"region": region_name, "profile": profile}
    return {"error": f"Region '{region_name}' not found"}

@app.post("/api/analyze")
async def analyze_risk(user_type: str = Form(...), location: str = Form(...), query: str = Form(...)):
    """Analyze risk based on user input."""
    
    # Simulate multi-agent analysis
    analysis_result = {
        "user_type": user_type,
        "location": location,
        "query": query,
        "risk_assessment": {
            "risk_level": "High",
            "confidence": 85,
            "primary_risks": ["hurricanes", "flooding"],
            "risk_score": 82
        },
        "recommendations": [
            {
                "type": "nature_based",
                "name": "Wetland Restoration",
                "description": "Restore wetlands for natural flood protection",
                "cost": "$50,000 - $200,000",
                "roi": "15-25% over 5 years",
                "timeline": "6-12 months"
            },
            {
                "type": "infrastructure",
                "name": "Elevated Foundations",
                "description": "Raise building foundations above flood level",
                "cost": "$150,000 - $300,000",
                "roi": "20-30% over 10 years",
                "timeline": "12-18 months"
            }
        ],
        "economic_impact": {
            "asset_protection": "$2.5M - $5M",
            "insurance_reduction": "15-25%",
            "operational_continuity": "95%+"
        },
        "data_sources": [
            "NOAA historical weather data",
            "FEMA flood maps",
            "Local adaptation case studies"
        ]
    }
    
    return analysis_result

@app.get("/api/export/{analysis_id}")
async def export_analysis(analysis_id: str):
    """Export analysis results."""
    # This would normally load from a database
    # For now, return a sample export
    export_data = {
        "analysis_id": analysis_id,
        "timestamp": "2024-01-15T10:30:00Z",
        "user_type": "Private Equity Investor",
        "location": "Mobile Bay, Alabama",
        "risk_assessment": {
            "risk_level": "High",
            "confidence": 85
        },
        "recommendations": [
            {
                "name": "Wetland Restoration",
                "cost": "$50,000 - $200,000",
                "roi": "15-25%"
            }
        ]
    }
    
    return export_data

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Tool Multi-Agent System"}

@app.get("/api/demo")
async def demo_data():
    """Get demo data for testing."""
    return {
        "message": "Tool Multi-Agent System is running!",
        "available_endpoints": [
            "/api/user-types",
            "/api/data-summary", 
            "/api/nature-based-solutions",
            "/api/historical-events",
            "/api/regional-profiles",
            "/api/economic-impacts",
            "/api/analyze",
            "/health"
        ],
        "data_summary": data_loader.get_all_data_summary()
    }

if __name__ == "__main__":
    print("🌍 Starting Tool Multi-Agent System...")
    print("📊 Available data:")
    summary = data_loader.get_all_data_summary()
    print(f"  • {summary['nature_based_solutions']['count']} nature-based solutions")
    print(f"  • {summary['historical_events']['count']} historical weather events")
    print(f"  • {summary['regions']['count']} regional risk profiles")
    print("\n🚀 Starting web server...")
    print("🌐 Open your browser to: http://localhost:8000")
    print("📋 API documentation: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print("📊 Demo data: http://localhost:8000/api/demo")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 