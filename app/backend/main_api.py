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
from llm_local import LocalLLMClient
from llm_online import OnlineLLMClient

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
    # Optional: Frontend can provide ID, or we generate one
    result_id: Optional[str] = Form(None), 
    db: DatabaseManager = Depends(get_db)
):

    """
    pipeline from uploading filepath, to returning back 
    status along with result_id from db 
    """

    #1. Determine the ID upfront
    if not result_id:
        result_id = str(uuid.uuid4())

    # 2. Save File
    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # 3. Create the Database Row manually
        # We bypass db.create_new_result() because we want to specify the ID.
        # We use the raw connection from DatabaseManager.
        insert_query = "INSERT INTO Results (result_id) VALUES (%s);"
        db.db.execute_update(insert_query, (result_id,))

        # 4. Initialize Classes
        cli = CLI()
        config = ConfigManager()


        def use_preexisting_id():
            return result_id
            
        # Overwrite the method on this specific instance
        db.create_new_result = use_preexisting_id

        # 5. Run Pipeline
        pipeline = AnalysisPipeline(cli, config, db)
        pipeline.run_analysis(tmp_path)

        # 6. Return the ID 
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
    query = "SELECT result_id, project_data FROM Tracked_Data;"
    try:
        results = db.db.execute_query(query)
        # Convert UUID objects to strings for JSON serialization
        for row in results:
            row['result_id'] = str(row['result_id'])
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.get("/projects/{result_id}")
async def get_project_detail(result_id: str, db: DatabaseManager = Depends(get_db)):
    """
    Fetch specific project details.
    Returns: {project_data} from tracked_Data table for the given ID.
    """
    query = "SELECT project_data FROM Tracked_Data WHERE result_id = %s;"
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
    """Aggregate skills (Placeholder cause we don't have a separate skills thing yet)."""
    results = db.get_all_results_summary()
    return {"count": len(results), "message": "Skill aggregation logic pending."}

@app.get("/resume/{result_id}")
async def get_resume(result_id: str, db: DatabaseManager = Depends(get_db)):
    res = db.get_result_by_id(result_id)
    if not res:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"resume_points": res.get("resume_points")}

@app.post("/resume/generate")
async def generate_resume_manual(result_id: str = Form(...), db: DatabaseManager = Depends(get_db)):
    """Triggers LLM generation manually using stored topic vectors."""
    result = db.get_result_by_id(result_id)
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
    """Placeholder for potential future standalone generation"""
    return {"status": "ignored", "message": "Portfolio generation happens in upload"}

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