#!/usr/bin/env python3
"""
Standalone Tool Web Interface

A standalone web interface for the Tool multi-agent system.
"""

import json
import os
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from typing import Dict, Any, List

app = FastAPI(title="Tool Multi-Agent System", version="1.0.0")

# Mount static files (if they exist)
static_dir = Path("src/tool_web/static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Templates (if they exist)
templates_dir = Path("src/tool_web/templates")
if templates_dir.exists():
    templates = Jinja2Templates(directory=str(templates_dir))
else:
    templates = None

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

def load_json_data(filename: str) -> Dict[str, Any]:
    """Load JSON data from the data directory."""
    data_file = Path("src/multi_agent_system/data") / filename
    if data_file.exists():
        with open(data_file, 'r') as f:
            return json.load(f)
    return {}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Main dashboard page."""
    if templates:
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user_types": USER_TYPES
        })
    else:
        # Fallback HTML if templates don't exist
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Tool Multi-Agent System</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                .user-type {{ margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 3px; }}
                .api-link {{ color: #3498db; text-decoration: none; }}
                .api-link:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌍 Tool Multi-Agent Extreme Weather Risk Analysis System</h1>
                    <p>Data-driven decision support for extreme weather risks</p>
                </div>
                
                <div class="section">
                    <h2>📋 Available User Types</h2>
                    {''.join([f'<div class="user-type">{user_type}</div>' for user_type in USER_TYPES])}
                </div>
                
                <div class="section">
                    <h2>🔗 API Endpoints</h2>
                    <p><a href="/api/user-types" class="api-link">/api/user-types</a> - Get available user types</p>
                    <p><a href="/api/data-summary" class="api-link">/api/data-summary</a> - Get data summary</p>
                    <p><a href="/api/nature-based-solutions" class="api-link">/api/nature-based-solutions</a> - Get nature-based solutions</p>
                    <p><a href="/api/historical-events" class="api-link">/api/historical-events</a> - Get historical weather events</p>
                    <p><a href="/api/regional-profiles" class="api-link">/api/regional-profiles</a> - Get regional risk profiles</p>
                    <p><a href="/api/economic-impacts" class="api-link">/api/economic-impacts</a> - Get economic impact data</p>
                    <p><a href="/api/demo" class="api-link">/api/demo</a> - Get demo data</p>
                    <p><a href="/health" class="api-link">/health</a> - Health check</p>
                </div>
                
                <div class="section">
                    <h2>📚 Documentation</h2>
                    <p><a href="/docs" class="api-link">/docs</a> - Interactive API documentation</p>
                </div>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

@app.get("/api/user-types")
async def get_user_types():
    """Get available user types."""
    return {"user_types": USER_TYPES}

@app.get("/api/data-summary")
async def get_data_summary():
    """Get summary of available data."""
    # Load data files and create summary
    nbs_data = load_json_data("nature_based_solutions.json")
    hist_data = load_json_data("historical_weather_events.json")
    regional_data = load_json_data("regional_risk_profiles.json")
    economic_data = load_json_data("economic_impact_data.json")
    
    summary = {
        "nature_based_solutions": {
            "count": len(nbs_data.get("solutions", [])),
            "risk_types": list(set([risk for solution in nbs_data.get("solutions", []) 
                                  for risk in solution.get("risk_types", [])])),
            "location_types": list(set([loc for solution in nbs_data.get("solutions", []) 
                                      for loc in solution.get("suitable_locations", [])]))
        },
        "historical_events": {
            "count": len(hist_data.get("events", [])),
            "event_types": list(set([event.get("type") for event in hist_data.get("events", [])])),
            "regions": list(set([event.get("location", {}).get("region") for event in hist_data.get("events", [])]))
        },
        "regions": {
            "count": len(regional_data.get("regions", {})),
            "region_names": list(regional_data.get("regions", {}).keys())
        },
        "economic_impacts": {
            "impact_types": list(economic_data.get("economic_impacts", {}).keys())
        }
    }
    
    return summary

@app.get("/api/nature-based-solutions")
async def get_nature_based_solutions():
    """Get nature-based solutions data."""
    return load_json_data("nature_based_solutions.json")

@app.get("/api/historical-events")
async def get_historical_events():
    """Get historical weather events."""
    return load_json_data("historical_weather_events.json")

@app.get("/api/regional-profiles")
async def get_regional_profiles():
    """Get regional risk profiles."""
    return load_json_data("regional_risk_profiles.json")

@app.get("/api/economic-impacts")
async def get_economic_impacts():
    """Get economic impact data."""
    return load_json_data("economic_impact_data.json")

@app.get("/api/solutions/{risk_type}")
async def get_solutions_by_risk_type(risk_type: str):
    """Get nature-based solutions for a specific risk type."""
    data = load_json_data("nature_based_solutions.json")
    solutions = []
    
    for solution in data.get("solutions", []):
        if risk_type in solution.get("risk_types", []):
            solutions.append(solution)
    
    return {"risk_type": risk_type, "solutions": solutions}

@app.get("/api/region/{region_name}")
async def get_region_profile(region_name: str):
    """Get risk profile for a specific region."""
    data = load_json_data("regional_risk_profiles.json")
    profile = data.get("regions", {}).get(region_name)
    
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

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "service": "Tool Multi-Agent System",
        "version": "1.0.0",
        "data_files": {
            "nature_based_solutions": Path("src/multi_agent_system/data/nature_based_solutions.json").exists(),
            "historical_events": Path("src/multi_agent_system/data/historical_weather_events.json").exists(),
            "regional_profiles": Path("src/multi_agent_system/data/regional_risk_profiles.json").exists(),
            "economic_impacts": Path("src/multi_agent_system/data/economic_impact_data.json").exists()
        }
    }

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
        "data_summary": await get_data_summary(),
        "example_queries": {
            "Private Equity Investor": "What are hurricane risks for manufacturing facilities in Mobile Bay?",
            "Loan Officer": "What are water scarcity risks for cattle operations in western Kansas?",
            "Chief Risk Officer": "What are portfolio-level extreme weather risks for agricultural lending?",
            "Data Science Officer": "Validate our agricultural risk models with extreme weather data"
        }
    }

if __name__ == "__main__":
    print("🌍 Starting Tool Multi-Agent System...")
    print("📊 Checking data files...")
    
    data_files = [
        "src/multi_agent_system/data/nature_based_solutions.json",
        "src/multi_agent_system/data/historical_weather_events.json", 
        "src/multi_agent_system/data/regional_risk_profiles.json",
        "src/multi_agent_system/data/economic_impact_data.json"
    ]
    
    for file in data_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file}")
    
    print("\n🚀 Starting web server...")
    print("🌐 Open your browser to: http://localhost:8000")
    print("📋 API documentation: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print("📊 Demo data: http://localhost:8000/api/demo")
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 