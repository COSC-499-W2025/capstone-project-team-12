import os
import shutil
import tempfile
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
import uuid

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from analysis_pipeline import AnalysisPipeline
from cli_interface import CLI
from config_manager import ConfigManager
from database_manager import DatabaseManager
from llm.llm_clients import LocalLLMClient, OnlineLLMClient
from portfolio_builder import PortfolioBuilder

app = FastAPI(title="Artifact Mining API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = DatabaseManager()
    try:
        yield db
    finally:
        db.close()

class ResumeEditRequest(BaseModel):
    resume_points: str # Accepts raw text or JSON string

class PortfolioEditRequest(BaseModel):
    insights: Dict[str, Any]

class ConsentRequest(BaseModel):
    consent_type: str
    value: bool


# --- Endpoints ---
@app.get("/")
def health_check():
    return {"status": "active"}

@app.post("/projects/upload")
async def upload_project(
    file: UploadFile = File(...),
    github_username: Optional[str] = Form(None),
    github_email: Optional[str] = Form(None),
    # Removed frontend-generated result_id to enforce backend state management
    db: DatabaseManager = Depends(get_db)
):

    """
    Pipeline from uploading filepath to returning back 
    status along with the backend-generated result_id.
    """

    # 1. Save File
    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # 2. Initialize Classes
        cli = CLI()
        config = ConfigManager()

        # 3. Run Pipeline
        # pipeline will call database_manager.create_new_result()
        # internally, which generates and returns a new UUID.
        pipeline = AnalysisPipeline(cli, config, db)
        
        # return_id=True ensures we get the new UUID back to send to the frontend
        result_id = pipeline.run_analysis(tmp_path, return_id=True)

        # 4. Return the ID 
        return {"status": "success", "result_id": result_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.get("/projects")
async def get_projects(db: DatabaseManager = Depends(get_db)):
    """
    Fetch all projects.
    Returns: List of {result_id, project_data} from tracked_data table.
    """
    query = "SELECT analysis_id, project_data FROM Tracked_Data;"
    try:
        results = db.db.execute_query(query)
        # Convert UUID objects to strings for JSON serialization
        for row in results:
            row['result_id'] = str(row.pop('analysis_id'))
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.get("/projects/{result_id}")
async def get_project_detail(result_id: str, db: DatabaseManager = Depends(get_db)):
    """
    Fetch specific project details.
    Returns: {project_data} from tracked_Data table for the given ID.
    """
    query = "SELECT project_data FROM Tracked_Data WHERE analysis_id = %s;"
    try:
        # Validate UUID format
        u_id = uuid.UUID(result_id)
        results = db.db.execute_query(query, (u_id,))
            
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    if not results:
        raise HTTPException(status_code=404, detail="Project not found")
        
    return results[0] # Returns dict like {"project_data": {...}}

    

@app.get("/skills")
async def get_skills(db: DatabaseManager = Depends(get_db)):
    """Aggregate skills across all analysed projects."""
    results = db.get_all_results_summary()
    skill_counts: Dict[str, int] = {}
    for row in results:
        #extract languages from language_stats (metadata stuff)
        meta = row.get("metadata_insights")
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except (json.JSONDecodeError, TypeError):
                meta = {}
        if not isinstance(meta, dict):
            meta = {}

        #langauge stat is dict
        for lang_name, lang_info in meta.get("language_stats", {}).items():
            if lang_name and lang_name != "Text only":
                count = lang_info.get("file_count", 1) if isinstance(lang_info, dict) else 1
                skill_counts[lang_name] = skill_counts.get(lang_name, 0) + count

        #skill_stats has categories like "Backend Development", "Web Development"
        for skill_name, skill_info in meta.get("skill_stats", {}).items():
            if skill_name and skill_name != "Documentation":
                count = skill_info.get("file_count", 1) if isinstance(skill_info, dict) else 1
                skill_counts[skill_name] = skill_counts.get(skill_name, 0) + count

        # project_insights: extract frameworks/libraries from imports_summary ---
        proj = row.get("project_insights")
        if isinstance(proj, str):
            try:
                proj = json.loads(proj)
            except (json.JSONDecodeError, TypeError):
                proj = {}
        if not isinstance(proj, dict):
            proj = {}

        for project in proj.get("analyzed_insights", []):
            if not isinstance(project, dict):
                continue
            # imports_summary is a dict like {"pytest": {"frequency": 2, ...}, "anytree": {...}}
            for import_name, import_info in project.get("imports_summary", {}).items():
                if not import_name:
                    continue
                freq = import_info.get("frequency", 1) if isinstance(import_info, dict) else 1
                skill_counts[import_name] = skill_counts.get(import_name, 0) + freq

    sorted_skills = dict(sorted(skill_counts.items(), key=lambda x: x[1], reverse=True))
    return {"skills": sorted_skills}

@app.get("/resume/{result_id}")
async def get_resume(result_id: str, db: DatabaseManager = Depends(get_db)):
    res = db.get_analysis_data(result_id)
    if not res:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"resume_points": res.get("resume_points")}

@app.post("/resume/generate")
async def generate_resume_manual(result_id: str = Form(...), db: DatabaseManager = Depends(get_db)):
    """Triggers LLM generation manually using stored topic vectors."""
    result = db.get_analysis_data(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    # 1. Check Config for Consent
    config = ConfigManager()
    use_online = config.preferences.get("online_llm_consent", False) 
    
    summary = ""
    model_used = "local"
    
    try:
        if use_online:
            try:
                # 2. Try Online Generation
                client = OnlineLLMClient()
                summary = client.generate_summary(result.get("topic_vector", {}))
                model_used = "online"
            except Exception as e:
                # 3. Fallback to Local if API Key missing or Request fails
                print(f"Online LLM failed: {e}. Falling back to local.")
                client = LocalLLMClient()
                summary = client.generate_summary(result.get("topic_vector", {}))
                model_used = "local_fallback"
        else:
            # 4. Use Local Default
            client = LocalLLMClient()
            summary = client.generate_summary(result.get("topic_vector", {}))
            model_used = "local"

        db.save_resume_points(result_id, summary)
        return {"status": "success", "resume_points": summary, "model_used": model_used}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/resume/{result_id}/edit")
async def edit_resume(result_id: str, new: ResumeEditRequest, db: DatabaseManager = Depends(get_db)):
    success = db.save_resume_points(result_id, new.resume_points)
    if not success:
        raise HTTPException(status_code=500, detail="Save failed")
    return {"status": "success"}

@app.get("/portfolio/{result_id}")
async def get_portfolio(result_id: str, db: DatabaseManager = Depends(get_db)):
    """Generate and return a portfolio for the given result."""
    #check if result id exists
    result_data = db.get_analysis_data(result_id)
    if not result_data:
        raise HTTPException(status_code=404, detail="Result ID not found in database")
    
    builder = PortfolioBuilder()
    cli = CLI()
    portfolio = builder.create_portfolio_from_result_id(db, cli, result_id)
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio

@app.post("/portfolio/generate")
async def generate_portfolio(result_id: str = Form(...)):
    """Placeholder for potential future standalone generation"""
    return {"status": "ignored", "message": "Portfolio generation happens in upload"}

@app.post("/portfolio/{result_id}/edit")
async def edit_portfolio(result_id: str, req: PortfolioEditRequest, db: DatabaseManager = Depends(get_db)):
    """Placeholder for potential future standalone generation"""
    return {"status": "ignored", "message": "Portfolio generation happens in upload"}

@app.post("/privacy-consent")
async def update_consent(req: ConsentRequest):
    """Updates user preferences file."""
    cfg = ConfigManager()
    cfg.save_prefs({req.consent_type: req.value})
    return {"status": "success"}