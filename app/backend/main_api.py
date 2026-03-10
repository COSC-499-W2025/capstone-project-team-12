import os
import shutil
import tempfile
import json
import pickle
from typing import Optional, Dict, Any, List
from pathlib import Path
import uuid
from input_validation import validate_uuid

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from resume_builder import ResumeBuilder

from analysis_pipeline import AnalysisPipeline
from cli_interface import CLI
from config_manager import ConfigManager
from database_manager import DatabaseManager
from llm.llm_clients import LocalLLMClient, OnlineLLMClient
from portfolio_builder import PortfolioBuilder
from main_utils import perform_update_merge
from anytree.importer import DictImporter
from anytree.exporter import DictExporter
from tree_manager import TreeManager
from file_manager import FileManager

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

#helper
def location_header(location:str):
    """Returns dict with location header with given location string"""
    return {"location": location}
    

class ResumeEditRequest(BaseModel):
    resume_title: str = None
    resume_data:Dict[str,Any]

class PortfolioEditRequest(BaseModel):
    portfolio_title: str = None
    portfolio_data:Dict[str,Any]


class ConsentRequest(BaseModel):
    consent_type: str
    value: bool

class TopicEditRequest(BaseModel):
    topic_keywords: List[Dict[str, Any]] 

class TopicKeyword(BaseModel):
    topic_id: int
    keywords: List[str]


class CommitUpdateRequest(BaseModel):
    topic_keywords: List[TopicKeyword]
    user_highlights: List[str]
    selected_projects: List[str]  # Ordered list of repo names
    online_llm_consent: bool


# --- Endpoints ---
@app.get("/")
def health_check():
    return {"status": "active"}

@app.post("/projects/upload/extract")
async def extract_upload(
    file: UploadFile = File(...),
    github_username: Optional[str] = Form(None),
    github_email: Optional[str] = Form(None),
    db: DatabaseManager = Depends(get_db),
):
    """
    Phase 1 – Upload & Extract for a NEW project.
    Saves the uploaded file, runs the extraction pipeline (which creates
    a new analysis ID internally), caches heavy state for the commit step,
    and returns lightweight results to the frontend.
    """
    # Save uploaded file to a temporary path
    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # Initialize pipeline
        cli = CLI()
        config = ConfigManager()
        pipeline = AnalysisPipeline(cli, config, db)

        # Run extraction – no existing_analysis_id or preloaded data,
        # so the pipeline creates a brand-new analysis ID and saves
        # the initial fileset to the database automatically.
        extract_result = pipeline.run_analysis_extract(
            filepath=tmp_path,
            github_username=github_username,
            github_email=github_email,
        )

        if extract_result is None:
            raise HTTPException(status_code=500, detail="Extraction phase failed")

        analysis_id, topic_vector_bundle, detected_skills, text_analysis_data = extract_result

        # Gather analyzed repos from pipeline result bundle
        analyzed_repos = (
            pipeline.result_bundle.project_analysis_data.get("analyzed_insights", [])
            if pipeline.result_bundle.project_analysis_data
            else []
        )

        # Cache heavy state for Phase 2 (commit)
        cache_data = {
            "topic_vector_bundle": topic_vector_bundle,
            "text_analysis_data": text_analysis_data,
            "analyzed_repos": analyzed_repos,
        }

        os.makedirs("cache", exist_ok=True)
        cache_path = os.path.join("cache", f"pending_new_{analysis_id}.pkl")
        with open(cache_path, "wb") as f:
            pickle.dump(cache_data, f)

        # Build JSON-friendly response
        analyzed_projects = [
            {
                "repository_name": repo.get("repository_name", repo.get("name", "Unknown")),
                "importance_score": repo.get("importance_score", 0),
            }
            for repo in analyzed_repos
        ]

        return JSONResponse(
            status_code=200,
            content={
                "analysis_id": str(analysis_id),
                "topic_keywords": topic_vector_bundle.get("topic_keywords", []),
                "detected_skills": detected_skills,
                "analyzed_projects": analyzed_projects,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/projects/{analysis_id}/upload/commit")
async def commit_upload(
    analysis_id: str,
    request: CommitUpdateRequest,
    db: DatabaseManager = Depends(get_db),
):
    """
    Phase 2 – Commit & Generate for a NEW upload.
    Applies user edits (topic keywords, highlights, project selection)
    to the cached extraction data from Phase 1, generates the AI summary,
    and persists everything to the database.
    """
    cache_path = os.path.join("cache", f"pending_new_{analysis_id}.pkl")
    if not os.path.exists(cache_path):
        raise HTTPException(
            status_code=404,
            detail="No pending upload found – cache expired or invalid analysis ID",
        )

    # Load and immediately delete the cache file
    with open(cache_path, "rb") as f:
        cached_data = pickle.load(f)
    os.remove(cache_path)

    try:
        config = ConfigManager()
        config.save_prefs({"online_llm_consent": request.online_llm_consent})

        #rReconstruct topic_vector_bundle with user edits
        topic_vector_bundle = cached_data["topic_vector_bundle"]
        topic_vector_bundle["topic_keywords"] = [
            {"topic_id": tk.topic_id, "keywords": tk.keywords}
            for tk in request.topic_keywords
        ]
        topic_vector_bundle["user_highlights"] = request.user_highlights

        # Filter / order analyzed repos to match user selection
        cached_repos = cached_data.get("analyzed_repos", [])
        repo_lookup = {
            repo.get("repository_name", repo.get("name", "")): repo
            for repo in cached_repos
        }
        filtered_repos = [
            repo_lookup[name]
            for name in request.selected_projects
            if name in repo_lookup
        ]
        cached_data["analyzed_repos"] = filtered_repos

        # Phase 2: generate AI summary and save results
        #db.save_fileset not called here because run_analysis_extract already saved the fileset during Phase 1.
        pipeline = AnalysisPipeline(CLI(), ConfigManager(), db)
        summary = pipeline.run_analysis_generate(
            analysis_id=analysis_id,
            topic_vector_bundle=topic_vector_bundle,
            text_analysis_data=cached_data["text_analysis_data"],
            selected_projects=request.selected_projects,
            return_id=False,
        )

        return JSONResponse(
            status_code=200,
            content={"status": "success", "summary": summary},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/projects")
async def get_projects(db: DatabaseManager = Depends(get_db)):
    """
    Fetch all projects.
    Returns: List of {analysis_id, project_data} from tracked_data table.
    """
    
    try:
        results = db.get_all_analyses_summary()
        # Convert UUID objects to strings for JSON serialization
        for row in results:
            row['analysis_id'] = str(row.pop('analysis_id'))
        return JSONResponse(status_code=200,content=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.get("/projects/{analysis_id}")
async def get_project_detail(analysis_id: str, db: DatabaseManager = Depends(get_db)):
    """
    Fetch specific project details.
    Returns: complete analysis data from all child tables for the given ID.
    """
    try:
        validate_uuid(analysis_id)
        # Validate UUID format
        
        result:Dict[str,Any] = db.get_analysis_data(analysis_id)
        return JSONResponse(status_code=200,content=result)   
    
    except LookupError:
        raise HTTPException(status_code=404, detail=f"No analysis with{analysis_id} found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.get("/skills")
async def get_skills(db: DatabaseManager = Depends(get_db)):
    """Aggregate skills across all analysed projects."""
    results = db.get_all_analyses_summary()
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
    return JSONResponse(status_code=200,content={'skills':sorted_skills})

#reworked to return a full resume instead of resume points. resume_points can be extracted from returned result by front_end
@app.get("/resumes")
async def get_all_resumes(db:DatabaseManager = Depends(get_db)):
    """
        Returns all resumes stored in database
    """
    try:
        result = db.get_all_resumes()
        
        # Convert UUID objects to strings for JSON serialization
        for row in result:
            row['analysis_id'] = str(row.pop('analysis_id'))
        
        return JSONResponse(status_code=200,content=result)

    except LookupError as e: #redundant catch case it is here for consistency with other getters for resumes
        raise HTTPException(status_code=404, detail =f"Internal Server Error:{e}")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail =f"Internal Server Error:{e}")
    

@app.get("/resumes/{analysis_id}")
async def get_resumes(analysis_id: str, db: DatabaseManager = Depends(get_db)):
    """
        Returns all resumes associated with an analysis.
    """
    try:
        validate_uuid(analysis_id)
        # Validate UUID format
        
        result = db.get_resumes_by_analysis_id(analysis_id)    
        
        # Convert UUID objects to strings for JSON serialization
        for row in result:
            row['analysis_id'] = str(row.pop('analysis_id'))
        
        return JSONResponse(status_code=200,content=result)
    
    except HTTPException as e:
        raise e
    except LookupError:
        raise HTTPException(status_code=404, detail="Analysis for resume request not Found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
            raise HTTPException(status_code=500, detail =f"Internal Server Error:{e}")

@app.get("/resume/{resume_id}")
async def get_resume(resume_id: int, db: DatabaseManager = Depends(get_db)):
    """
        Returns a particular resume with given id.
    """
    try:
        
        result = db.get_resume_by_resume_id(resume_id)
        result = result[0]
        # Convert UUID objects to strings for JSON serialization
        
        result['analysis_id'] = str(result.pop('analysis_id'))
        return JSONResponse(status_code=200,content=result)
    
    except HTTPException as e:
        raise e
    except LookupError:
        raise HTTPException(status_code=404, detail = f"Resume with id {resume_id} not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid resume_id parameter. Expected integer")
    except Exception as e:
            raise HTTPException(status_code=500, detail =f"Internal Server Error:{e}")

@app.post("/resume/generate/{analysis_id}")
async def generate_resume(analysis_id: str, db: DatabaseManager = Depends(get_db),resume_title:str = None):
    """Uses resume_builder to build and save new resume for a given analysis
        Important Param note, resume title if any must be sent as query request by the frontend
        Eg. client.post(resume/generate/<some UUID>?resume_title= 'Capybara Resume' """    
    try:
        
        #Check to make sure provided uuid is valid 
        try:
            validate_uuid(analysis_id)
            # Validate UUID format
        except ValueError as e:
            raise e
        
        #Check to ensure that user llm consent has been set, expected to be done by frontend using a seperate endpoint
        try:
            config = ConfigManager()
            llm_consent = config.preferences['online_llm_consent'] #raises key error when not set 
            if llm_consent is None or llm_consent is {}:
                #On fail raise precondition error
                raise HTTPException(status_code=422, detail="LLM consent must be set before generating a resume")
        except KeyError:
            raise HTTPException(status_code=422, detail="LLM consent must be set before generating a portfolio")
        except HTTPException as e:
            raise e
        except Exception as e:
            raise Exception(f"Internal error during online consent check:{e}")
        
        #Main execution block
        #Use resume_builder to generate new resume
        try:
            #get data
            analysis_data = db.get_analysis_data(analysis_id) #raises Lookup error on analysis_id not found
                        
            #build actual resume object
            resume_builder = ResumeBuilder()
            resume = resume_builder._build_resume(analysis_data,analysis_id)
            if not resume:
                raise RuntimeError("Resume builder returned empty resume")
        
        except LookupError as e:
            raise HTTPException(status_code=404,detail =f"No Analysis with {analysis_id} found:")
        except Exception as e:
            raise RuntimeError(f"Failed to build resume:{e}") 
        
        #Save new resume to database
        try:
            resume_id = db.save_resume(analysis_id,resume,resume_title)
            resume['resume_id'] = resume_id #add to match actual return since return by build resume doesnt have field
        except Exception as e:
            raise RuntimeError("Failed to save new resume")
        return JSONResponse(status_code=201,headers=location_header(f"/resume/{resume_id}"),content = resume)
    except HTTPException as e:
        raise e
    except ValueError as e:
         raise HTTPException(status_code=400, detail=f"Generation failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500,detail = f"Fatal Internal error during resume generation:{e}")

#for updating a resume make a PUT request to a resume's url 
@app.put("/resume/{resume_id}")
async def edit_resume(resume_id: int, new: ResumeEditRequest, db: DatabaseManager = Depends(get_db)):
    try: 
        
        db.update_resume(resume_id,new.resume_data,new.resume_title)
        return JSONResponse(status_code=204,headers = location_header(f"/resume/{resume_id}"),content = None)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

@app.get("/portfolios")
async def get_all_portfolios(db:DatabaseManager = Depends(get_db)):
    """
        Returns all portfolios stored in database
    """
    try:
        result = db.get_all_portfolios()
        
        # Convert UUID objects to strings for JSON serialization
        for row in result:
            row['analysis_id'] = str(row.pop('analysis_id'))
        
        return JSONResponse(status_code=200,content=result)
    
    except LookupError as e: #redundant catch case it is here for consistency with other getters for portfolios
        raise HTTPException(status_code=404, detail =f"Internal Server Error:{e}")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail =f"Internal Server Error:{e}")
    

@app.get("/portfolios/{analysis_id}")
async def get_portfolios(analysis_id: str, db: DatabaseManager = Depends(get_db)):
    """
        Returns all portfolios associated with an analysis.
    """
    try:
        validate_uuid(analysis_id)
        # Validate UUID format
        
        result = db.get_portfolios_by_analysis_id(analysis_id)    
        
        # Convert UUID objects to strings for JSON serialization
        for row in result:
            row['analysis_id'] = str(row.pop('analysis_id'))
        
        return JSONResponse(status_code=200,content=result)
    
    except HTTPException as e:
        raise e
    except LookupError:
        raise HTTPException(status_code=404, detail="Analysis for portfolio request not Found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
            raise HTTPException(status_code=500, detail =f"Internal Server Error:{e}")

@app.get("/portfolio/{portfolio_id}")
async def get_portfolio(portfolio_id: int, db: DatabaseManager = Depends(get_db)):
    """
        Returns a particular portfolio with given id.
    """
    try:
        result = db.get_portfolio_by_portfolio_id(portfolio_id)
        result = result[0]
        result['analysis_id'] = str(result.pop('analysis_id'))
        return JSONResponse(status_code=200,content=result)
    
    except HTTPException as e:
        raise e
    except LookupError:
        raise HTTPException(status_code=404, detail = f"portfolio with id {portfolio_id} not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid portfolio_id parameter. Expected integer")
    except Exception as e:
            raise HTTPException(status_code=500, detail =f"Internal Server Error:{e}")

@app.post("/portfolio/generate/{analysis_id}")
async def generate_portfolio(analysis_id: str, db: DatabaseManager = Depends(get_db),portfolio_title:str = None):
    """Uses portfolio_builder to build and save new portfolio for a given analysis
        Important Param note, portfolio title if any must be sent as query request by the frontend
        Eg. client.post(portfolio/generate/<some UUID>?portfolio_title= 'Capybara portfolio' """    
    try:
        
        #Check to make sure provided uuid is valid 
        try:
            validate_uuid(analysis_id)
            # Validate UUID format
        except ValueError as e:
            raise e
        
        #Check to ensure that user llm consent has been set, expected to be done by frontend using a seperate endpoint
        try:
            config = ConfigManager()
            llm_consent = config.preferences['online_llm_consent'] #raises key_error if it is not set!
            if llm_consent is None or llm_consent is {}:
                #On fail raise precondition error
                raise HTTPException(status_code=422, detail="LLM consent must be set before generating a portfolio")
        except KeyError:
            raise HTTPException(status_code=422, detail="LLM consent must be set before generating a portfolio")
        except HTTPException as e:
            raise e
        except Exception as e:
            raise Exception(f"Internal error during online consent check:{e}")
        
        #Main execution block
        #Use portfolio_builder to generate new portfolio
        try:
            #get data
            analysis_data = db.get_analysis_data(analysis_id) #raises Lookup error on analysis_id not found
                        
            #build actual portfolio object
            portfolio_builder = PortfolioBuilder()
            portfolio = portfolio_builder._build_portfolio(analysis_data,analysis_id)
            if not portfolio:
                raise RuntimeError("portfolio builder returned empty portfolio")
            
        except LookupError as e:
            raise HTTPException(status_code=404,detail =f"No Analysis with {analysis_id} found:")
        except Exception as e:
            raise RuntimeError(f"Failed to build portfolio:{e}") 
        
        #Save new portfolio to database
        try:
            portfolio_id = db.save_portfolio(analysis_id,portfolio,portfolio_title)
        except Exception as e:
            raise RuntimeError("Failed to save new portfolio")
        portfolio['portfolio_id'] = portfolio_id # Save new portfolio id to object
        return JSONResponse(status_code=201,headers=location_header(f"/portfolio/{portfolio_id}"),content = portfolio)
    except HTTPException as e:
        raise e
    except ValueError as e:
         raise HTTPException(status_code=400, detail=f"Generation failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500,detail = f"Fatal Internal error during portfolio generation:{e}")

#for updating a portfolio make a PUT request to a portfolio's url 
@app.put("/portfolio/{portfolio_id}")
async def edit_portfolio(portfolio_id: int, new: PortfolioEditRequest, db: DatabaseManager = Depends(get_db)):
    try: 
        
        db.update_portfolio(portfolio_id,new.portfolio_data,new.portfolio_title)
        return JSONResponse(status_code=204,headers = location_header(f"/portfolio/{portfolio_id}"),content = None)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")

@app.post("/privacy-consent")
async def update_consent(req: ConsentRequest):
    """Updates user preferences file."""
    cfg = ConfigManager()
    cfg.save_prefs({req.consent_type: req.value})
    return {"status": "success"}

@app.put("/projects/{analysis_id}/update/extract")
async def extract_update(
    analysis_id: str,
    file: UploadFile = File(...),
    github_username: Optional[str] = Form(None),
    github_email: Optional[str] = Form(None),
    db: DatabaseManager = Depends(get_db),
):
    """
    Phase 1 – Upload & Extract.
    Merges the uploaded file with the existing analysis, runs extraction,
    and caches the heavy state for the subsequent commit step.
    """
    try:
        validate_uuid(analysis_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    # Save uploaded file to a temporary path
    suffix = Path(file.filename).suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # Initialise helpers
        file_manager = FileManager()
        tree_manager = TreeManager()
        importer = DictImporter()
        exporter = DictExporter()

        # Load the new file
        fm_result = file_manager.load_from_filepath(tmp_path)
        if fm_result.get("status") == "error":
            raise HTTPException(
                status_code=400,
                detail=f"Load Error: {fm_result.get('message', 'Unknown error')}",
            )

        new_tree = fm_result["tree"]
        new_binary_list = fm_result.get("binary_data", [])

        # Merge with existing analysis data
        try:
            merged_tree, merged_binary_list = perform_update_merge(
                analysis_id, tmp_path, file_manager, db, importer
            )
        except LookupError:
            raise HTTPException(
                status_code=404,
                detail=f"No existing analysis found for ID {analysis_id}",
            )
        except RuntimeError as e:
            # Catch the load error specifically thrown by perform_update_merge
            raise HTTPException(
                status_code=400,
                detail=str(e),
            )

        if merged_tree is None:
            raise HTTPException(
                status_code=404,
                detail=f"Merge failed – no existing analysis for ID {analysis_id}",
            )

        # Phase 1: run extraction
        pipeline = AnalysisPipeline(CLI(), ConfigManager(), db)
        extract_result = pipeline.run_analysis_extract(
            filepath=tmp_path,
            existing_analysis_id=analysis_id,
            preloaded_tree=merged_tree,
            preloaded_binary=merged_binary_list,
            github_username=github_username,
            github_email=github_email,
        )

        if extract_result is None:
            raise HTTPException(status_code=500, detail="Extraction phase failed")

        analysis_id_out, topic_vector_bundle, detected_skills, text_analysis_data = extract_result

        # Gather analyzed repos from pipeline result bundle
        analyzed_repos = (
            pipeline.result_bundle.project_analysis_data.get("analyzed_insights", [])
            if pipeline.result_bundle.project_analysis_data
            else []
        )

        # Cache the heavy state for Phase 2
        cache_data = {
            "merged_tree_dict": exporter.export(merged_tree),
            "merged_binary_list": merged_binary_list,
            "topic_vector_bundle": topic_vector_bundle,
            "text_analysis_data": text_analysis_data,
            "analyzed_repos": analyzed_repos,
        }

        os.makedirs("cache", exist_ok=True)
        cache_path = os.path.join("cache", f"pending_update_{analysis_id}.pkl")
        with open(cache_path, "wb") as f:
            pickle.dump(cache_data, f)

        # Build JSON-friendly response
        analyzed_projects = [
            {
                "repository_name": repo.get("repository_name", repo.get("name", "Unknown")),
                "importance_score": repo.get("importance_score", 0),
            }
            for repo in analyzed_repos
        ]

        return JSONResponse(
            status_code=200,
            content={
                "topic_keywords": topic_vector_bundle.get("topic_keywords", []),
                "detected_skills": detected_skills,
                "analyzed_projects": analyzed_projects,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/projects/{analysis_id}/update/commit")
async def commit_update(
    analysis_id: str,
    request: CommitUpdateRequest,
    db: DatabaseManager = Depends(get_db),
):
    """
    Phase 2 – Commit & Generate.
    Applies user edits (topic keywords, highlights, project selection)
    to the cached extraction data, generates the AI summary, and persists
    everything to the database.
    """
    cache_path = os.path.join("cache", f"pending_update_{analysis_id}.pkl")
    if not os.path.exists(cache_path):
        raise HTTPException(
            status_code=404,
            detail="No pending update found – cache expired or invalid analysis ID",
        )

    # Load and immediately delete the cache file
    with open(cache_path, "rb") as f:
        cached_data = pickle.load(f)
    os.remove(cache_path)

    try:
        # Set LLM consent
        config = ConfigManager()
        config.save_prefs({"online_llm_consent": request.online_llm_consent})

        # Reconstruct topic_vector_bundle with user edits
        topic_vector_bundle = cached_data["topic_vector_bundle"]
        topic_vector_bundle["topic_keywords"] = [
            {"topic_id": tk.topic_id, "keywords": tk.keywords}
            for tk in request.topic_keywords
        ]
        topic_vector_bundle["user_highlights"] = request.user_highlights

        # Filter / order analyzed repos to match user selection
        cached_repos = cached_data.get("analyzed_repos", [])
        repo_lookup = {
            repo.get("repository_name", repo.get("name", "")): repo
            for repo in cached_repos
        }
        filtered_repos = [
            repo_lookup[name]
            for name in request.selected_projects
            if name in repo_lookup
        ]
        cached_data["analyzed_repos"] = filtered_repos

        # Save merged files to DB
        db.save_fileset(
            analysis_id,
            pickle.dumps(cached_data["merged_binary_list"]),
            cached_data["merged_tree_dict"],
            "Updated via API",
        )

        # Phase 2: generate AI summary and save results
        pipeline = AnalysisPipeline(CLI(), ConfigManager(), db)
        summary = pipeline.run_analysis_generate(
            analysis_id=analysis_id,
            topic_vector_bundle=topic_vector_bundle,
            text_analysis_data=cached_data["text_analysis_data"],
            selected_projects=request.selected_projects,
            return_id=False,
        )

        return JSONResponse(
            status_code=200,
            content={"status": "success", "summary": summary},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.delete("/projects/{analysis_id}")
async def delete_project(analysis_id: str, db: DatabaseManager = Depends(get_db)):
    """
    Delete a specific analysis and all its associated data (resumes, portfolios, filesets, etc.).
    """
    try:
        validate_uuid(analysis_id)
        
        db.get_analysis_data(analysis_id)
        
        db.delete_analysis(analysis_id)
        
        #return 204 No Content on success
        return JSONResponse(status_code=204, content=None)
        
    except HTTPException as e:
        raise e
    except LookupError:
        raise HTTPException(status_code=404, detail=f"No analysis with {analysis_id} found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.delete("/projects")
async def delete_all_projects(db: DatabaseManager = Depends(get_db)):
    """
    Wipe all analyses and associated data from the database.
    """
    try:
        db.wipe_all_data()
        
        return JSONResponse(status_code=204, content=None)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.delete("/resume/{resume_id}")
async def delete_resume(resume_id: int, db: DatabaseManager = Depends(get_db)):
    """
    Delete a specific resume by its ID.
    """
    try:
        db.get_resume_by_resume_id(resume_id)
        
        db.delete_resume(resume_id)
        return JSONResponse(status_code=204, content=None)
        
    except HTTPException as e:
        raise e
    except LookupError:
        raise HTTPException(status_code=404, detail=f"Resume with id {resume_id} not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid resume_id parameter. Expected integer")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@app.delete("/portfolio/{portfolio_id}")
async def delete_portfolio(portfolio_id: int, db: DatabaseManager = Depends(get_db)):
    """
    Delete a specific portfolio by its ID.
    """
    try:
        db.get_portfolio_by_portfolio_id(portfolio_id)
        
        db.delete_portfolio(portfolio_id)
        return JSONResponse(status_code=204, content=None)
        
    except HTTPException as e:
        raise e
    except LookupError:
        raise HTTPException(status_code=404, detail=f"Portfolio with id {portfolio_id} not found")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid portfolio_id parameter. Expected integer")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
