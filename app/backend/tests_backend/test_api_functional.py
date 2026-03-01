import pytest
from fastapi.testclient import TestClient
import sys
import os
from unittest.mock import ANY,patch


"""
API Testing methodology:

- This module mostly covers functional testing.
- Most Tests are written to test both interface/endpoint availability and implemention together.
- The tests use realistic mocks of our various backend data artifacts 
- which are then used exhaustively trace each endpoint's returns and execution paths
- Each major endpoint has 2 test cases, one for success scenario and another for failure
    - Success tests have only one case the primary intended pathway
    - Failure tests attempt elicit all failure responses from the api
    - EXCEPT for Internal Errors, code 500 indicates issues not in endpoint but in application logic



"""

# path to import backend code
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from main_api import app,get_db

client = TestClient(app)

@pytest.fixture
def placeholder_UUID():
    return "00000000-0000-0000-0000-000000000000"

@pytest.fixture
def sample_analysis(placeholder_UUID):
    return {
            'analysis_id':placeholder_UUID,
            'analysis_title': 'Title',
            'topic_vector':{},
            'resume_points':{},
            'project_insights':{},
            'package_insights':{},
            'metadata_insights':{},
            'tracked_data':{
                'bow_cache':{}, 
                'project_data':{}, 
                'package_data':{},
                'metadata_stats':{}
                },
            'resume_data':{},
            'portfolio_data':{}
        }
    
@pytest.fixture
def sample_resume(placeholder_UUID):
    return {
            "resume_id": 1,
            "analysis_id": placeholder_UUID,
            "summary": "Test summary",
            "projects": [],
            "skills": [],
            "languages": []
        }
@pytest.fixture
def sample_portfolio(placeholder_UUID):
    return {
        "portfolio_id": 1,
        "analysis_id": placeholder_UUID,
        "projects_detail": [],
        "skill_timeline": {},
        "growth_metrics": {}
    }



@pytest.fixture
def mock_backend(mocker,sample_analysis,sample_resume, sample_portfolio,placeholder_UUID):
    """
    Mocks all external dependencies using the pytest 'mocker' fixture.
    """
    # We patch the class names where they are IMPORTED in main_api
    MockDBClass = mocker.patch("main_api.DatabaseManager")
    MockCLIClass = mocker.patch("main_api.CLI")
    MockConfigClass = mocker.patch("main_api.ConfigManager")
    MockPipelineClass = mocker.patch("main_api.AnalysisPipeline")
    MockLocalLLMClass = mocker.patch("main_api.LocalLLMClient")
    MockOnlineLLMClass = mocker.patch("main_api.OnlineLLMClient")

    #Get the Instances
    db_instance = MockDBClass.return_value
    pipeline_instance = MockPipelineClass.return_value
    local_llm_instance = MockLocalLLMClass.return_value
    online_llm_instance = MockOnlineLLMClass.return_value
    config_instance = MockConfigClass.return_value

    # Mock the internal db connector's update method
    db_instance.db.execute_update.return_value = True
    
    def simple_query_side_effect(query, params=None):
        if "WHERE analysis_id" in query:
            if params and str(params[0]) == placeholder_UUID:
                return [] 
            return [{"project_data": {"name": "Test Project", "info": "Details"}}]
        return [{"analysis_id": "fake-uuid-123", "project_data": {"name": "Test Project"}}]
        
    
    #db_instance.db.execute_query.side_effect = simple_query_side_effect
    db_instance.get_analysis_data.side_effect = lambda rid: None if rid == "missing-id" else sample_analysis
    
    db_instance.save_resume_points.return_value = True
    
    #mock db_manager return for return all analyses
    db_instance.get_all_analyses_summary.return_value =[
        {'analysis_id':placeholder_UUID,'analysis_title': 'Title','metadata_insights':'Some JSON Object as string','project_insights':'Some JSON Object as string','file_path':'some_path'},
        {'analysis_id':placeholder_UUID,'analysis_title': 'Title2','metadata_insights':'Some JSON Object as string','project_insights':'Some JSON Object as string','file_path':'some_path2'}
    ]
    
    # mock db_manager returns for resume functions
    db_instance.get_all_resumes.return_value = [sample_resume, sample_resume]
    db_instance.get_resumes_by_analysis_id.return_value = [sample_resume]
    db_instance.get_resume_by_resume_id.return_value = [sample_resume]
    db_instance.save_resume.return_value = 1  # integer resume_id
    
    
    # mock porfolio_manager returns for portfolio functions
    db_instance.get_all_portfolios.return_value = [sample_portfolio, sample_portfolio]
    db_instance.get_portfolios_by_analysis_id.return_value = [sample_portfolio]
    db_instance.get_portfolio_by_portfolio_id.return_value = [sample_portfolio]
    db_instance.save_portfolio.return_value = 1  # integer portfolio_id
    
    # Funny note because this needs to go somewhere:
    # Tesume and Portfolio testing and endpoints are so similar
    # that i basically went copy paste , ctrl+f 'resume' and replaced it with 'portfolio'
    # and it worked?!?! Unbelievable
    
    
    # 4. Configure LLM Defaults
    local_llm_instance.generate_summary.return_value = "Local AI Summary"
    online_llm_instance.generate_summary.return_value = "Online AI Summary"

    # 5. Configure Config Defaults (Default to Local)
    config_instance.preferences = {"online_llm_consent": False}

    # 6. Configure Pipeline Return Value
    # The API now expects run_analysis to return a UUID string.
    pipeline_instance.run_analysis.return_value = placeholder_UUID

    def override_get_db():
        yield db_instance

    app.dependency_overrides[get_db] = override_get_db

    yield {                          # <-- change return to yield
        "db": db_instance,
        "pipeline": pipeline_instance,
        "local_llm": local_llm_instance,
        "online_llm": online_llm_instance,
        "config": config_instance
    }

    app.dependency_overrides.clear()  # teardown runs after each test
    
# ---- Generalized tests ----

def test_health_check():
    """Does the API turn on?"""
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "active"

# ---- Project/ Analysis end point tests ----
def test_get_projects_success(mock_backend):
    """Test fetching project list."""
    response = client.get("/projects")
    print(response.content)
    assert response.status_code == 200
    assert len(response.content) > 0

def test_get_project_success(mock_backend,sample_analysis,placeholder_UUID):
    """Test fetching valid project detail."""
    # Use a valid UUID string
    response = client.get(f"/projects/{placeholder_UUID}")
    assert response.status_code == 200
    assert response.json() == sample_analysis

# ---- Delete Endpoints Tests ----

def test_delete_project_success(mock_backend, placeholder_UUID, sample_analysis):
    """Test successful deletion of a specific project."""
    
    mock_backend["db"].get_analysis_data.return_value = sample_analysis
    
    mock_backend["db"].delete_analysis.return_value = True

    response = client.delete(f"/projects/{placeholder_UUID}")
    
    #success returns 204 No Content
    assert response.status_code == 204
    mock_backend["db"].delete_analysis.assert_called_once_with(placeholder_UUID)

def test_delete_project_failures(mock_backend, placeholder_UUID, sample_analysis):
    """Test all failure modes for deleting a specific project."""
    
    #case 1: invalid UUID format
    response = client.delete("/projects/invalid-uuid")
    assert response.status_code == 400

    #case 2: analysis not found in DB
    #the endpoint calls get_analysis_data first to verify existence
    mock_backend["db"].get_analysis_data.side_effect = LookupError("Analysis not found")
    response = client.delete(f"/projects/{placeholder_UUID}")
    assert response.status_code == 404
    
    #reset side effect for next case
    mock_backend["db"].get_analysis_data.side_effect = None

    #case 3: general DB error during the actual deletion
    mock_backend["db"].get_analysis_data.return_value = sample_analysis
    mock_backend["db"].delete_analysis.side_effect = Exception("DB deletion failed")
    response = client.delete(f"/projects/{placeholder_UUID}")
    assert response.status_code == 500


def test_delete_all_projects_success(mock_backend):
    """Test successful wipe of all projects from the database."""
    
    mock_backend["db"].wipe_all_data.return_value = True

    response = client.delete("/projects")
    
    assert response.status_code == 204
    mock_backend["db"].wipe_all_data.assert_called_once()

def test_delete_all_projects_failures(mock_backend):
    """Test failure modes for wiping all projects."""
    
    mock_backend["db"].wipe_all_data.side_effect = Exception("DB truncate failed")
    
    response = client.delete("/projects")
    
    assert response.status_code == 500

# ---- Resume Tests ----#
def test_generate_resume_success(mock_backend, sample_analysis,sample_resume,placeholder_UUID):
    """Test successful resume generation and save."""
    
    #test analysis UUID
    analysis_id = placeholder_UUID
    
    with patch("main_api.ConfigManager") as mock_config, \
         patch("main_api.ResumeBuilder") as mock_builder:
        
        mock_config.return_value.preferences = {"online_llm_consent": True}
        
        mock_backend['db'].get_analysis_data.return_value = sample_analysis

        #Sample valid resume
        mock_builder.return_value._build_resume.return_value = sample_resume
        
        #Expected value for returns based on fixture's mock
        resume_id = sample_resume['resume_id']
        #Exec and retrieve result
        mock_backend['db'].save_resume.return_value = resume_id
        
        response = client.post(f"/resume/generate/{analysis_id}")
        
        if not response.status_code == 201:
            print(response.json()['detail'])
        
        assert response.status_code == 201
        assert response.headers["location"] == f"/resume/{resume_id}"

def test_edit_resume_success(mock_backend):
    """Test saving edits."""
    response = client.put(
                    "/resume/0", #Changed to dummy int because isinstance(int) is verfied by dbmanager, 
                     json={
                        'resume_title':'new_title',
                        'resume_data':{} #Has some data exists here just for type matching
                        }
                     )
    assert response.status_code == 204
    assert response.headers['location'] == "/resume/0"
    
def test_get_all_resumes_success(mock_backend, sample_resume):
    """Test fetching all resumes."""
    response = client.get("/resumes")
    assert response.status_code == 200
    assert response.json() == [sample_resume, sample_resume]

def test_get_resumes_by_analysis_success(mock_backend, sample_resume,placeholder_UUID):
    """Test fetching all resumes for a given analysis."""
    response = client.get(f"/resumes/{placeholder_UUID}")
    assert response.status_code == 200
    assert response.json() == [sample_resume]

def test_get_resume_success(mock_backend, sample_resume):
    """Test fetching a single resume by id."""
    
    mock_backend["db"].get_resume_by_resume_id.return_value = [sample_resume]
    
    response = client.get("/resume/1")
    assert response.status_code == 200
    assert response.json() == sample_resume

def test_generate_resume_failures(mock_backend,placeholder_UUID):
    """Trigger all non Internal Error responses + some internal"""
    
    """Trigger all non Internal Error responses + some internal"""
    
    #Case one: Endpoint with missing analysis parameter
    response = client.post('/portfolio/generate')
    assert response.status_code == 405 #similar to resume this is handled by fastAPI but is good to check
    
    # Case two: Malformed analysis parameter
    response = client.post('portfolio/generate/invalid-uuid')
    assert response.status_code == 400
    
    #Case three: valid analysis id by not found in db
    with patch("main_api.ConfigManager") as mock_config:    
        mock_config.return_value.preferences = {"online_llm_consent": False}
        mock_backend["db"].get_analysis_data.side_effect = LookupError("Analysis not found")
        response = client.post(f"/portfolio/generate/{placeholder_UUID}")
        assert response.status_code == 404
    
    #reset mocks for next case
    mock_backend["db"].get_analysis_data.side_effect = None
    mock_backend["db"].get_analysis_data.return_value = sample_analysis
    
    #Case Four: Everything is valid but llm-consent is not set
    with patch("main_api.ConfigManager") as mock_config:
        mock_config.return_value.preferences = {} 
        response = client.post(f"/portfolio/generate/{placeholder_UUID}")
        assert response.status_code == 422
    
def test_get_all_resumes_failures(mock_backend):

    # Case one - no resumes in db
    mock_backend["db"].get_all_resumes.side_effect = LookupError("No entries in db for resumes")
    response = client.get("/resumes")
    assert response.status_code == 404

    # Case two - db errorr
    mock_backend["db"].get_all_resumes.side_effect = Exception("DB error")
    response = client.get("/resumes")
    assert response.status_code == 500

def test_get_resumes_by_analysis_failures(mock_backend, placeholder_UUID):

    # Case one- invalid UUID
    response = client.get("/resumes/invalid-uuid")
    assert response.status_code == 400

    # Case twp - no resumes for analysis
    mock_backend["db"].get_resumes_by_analysis_id.side_effect = LookupError("no resumes for analysis")
    response = client.get(f"/resumes/{placeholder_UUID}")
    assert response.status_code == 404

    # Case three - generalize db error.
    mock_backend["db"].get_resumes_by_analysis_id.side_effect = Exception("DB error")
    response = client.get(f"/resumes/{placeholder_UUID}")
    assert response.status_code == 500

def test_get_resume_failures(mock_backend):

    #Case one: non-integer id
    response = client.get("/resume/not-an-int")
    assert response.status_code == 422

    # Case two: resume not found
    mock_backend["db"].get_resume_by_resume_id.side_effect = LookupError("Database returned None")
    response = client.get("/resume/999")
    assert response.status_code == 404

    # Case three: DB error
    mock_backend["db"].get_resume_by_resume_id.side_effect = Exception("DB error")
    response = client.get("/resume/1")
    assert response.status_code == 500

def test_edit_resume_failures(mock_backend, sample_resume):
    
    #Case one: non-integer id
    response = client.put("/resume/not-an-int", json={"resume_title": "title", "resume_data": sample_resume})
    assert response.status_code == 422

    #Case two : missing field
    response = client.put("/resume/1", json={"resume_title": "title only"})
    assert response.status_code == 422

    # Case 3 : DB error
    mock_backend["db"].update_resume.side_effect = Exception("DB error")
    response = client.put("/resume/1", json={"resume_title": "title", "resume_data": sample_resume})
    assert response.status_code == 500

# ---- Resume Delete Tests ----

def test_delete_resume_success(mock_backend, sample_resume):
    """Test successful deletion of a specific resume."""
    
    mock_backend["db"].get_resume_by_resume_id.return_value = sample_resume
    mock_backend["db"].delete_resume.return_value = True

    response = client.delete("/resume/1")
    
    assert response.status_code == 204
    mock_backend["db"].delete_resume.assert_called_once_with(1)

def test_delete_resume_failures(mock_backend):
    """Test all failure modes for deleting a resume."""
    
    # Case 1: type validation failure 
    response = client.delete("/resume/not-an-int")
    assert response.status_code == 422

    #case 2: resume not found in DB
    mock_backend["db"].get_resume_by_resume_id.side_effect = LookupError("Not found")
    response = client.delete("/resume/999")
    assert response.status_code == 404
    
    mock_backend["db"].get_resume_by_resume_id.side_effect = None

    #case 3: general DB Error during deletion
    mock_backend["db"].get_resume_by_resume_id.return_value = {"resume_id": 1}
    mock_backend["db"].delete_resume.side_effect = Exception("DB error")
    response = client.delete("/resume/1")
    assert response.status_code == 500
    
# ---- Portfolio Tests ----
# Portfolio endpoint and testing was reworked to match fastAPI best practices 
# most responses are formatted objects (either JSON or HTTPException) instead of binary_streams

# ---- portfolio Tests ----#
def test_generate_portfolio_success(mock_backend, sample_analysis,sample_portfolio,placeholder_UUID):
    """Test successful portfolio generation and save."""
    
    #test analysis UUID
    analysis_id = placeholder_UUID
    
    with patch("main_api.ConfigManager") as mock_config, \
         patch("main_api.PortfolioBuilder") as mock_builder:
        
        mock_config.return_value.preferences = {"online_llm_consent": True}
        
        mock_backend['db'].get_analysis_data.return_value = sample_analysis

        #Sample valid portfolio
        mock_builder.return_value._build_portfolio.return_value = sample_portfolio
        
        #Expected value for returns based on fixture's mock
        portfolio_id = sample_portfolio['portfolio_id']
        #Exec and retrieve result
        mock_backend['db'].save_portfolio.return_value = portfolio_id
        
        response = client.post(f"/portfolio/generate/{analysis_id}")
        
        if not response.status_code == 201:
            print(response.json()['detail'])
        
        assert response.status_code == 201
        assert response.headers["location"] == f"/portfolio/{portfolio_id}"

def test_edit_portfolio_success(mock_backend):
    """Test saving edits."""
    response = client.put(
                    "/portfolio/0", #Changed to dummy int because isinstance(int) is verfied by dbmanager, 
                     json={
                        'portfolio_title':'new_title',
                        'portfolio_data':{} #Has some data exists here just for type matching
                        }
                     )
    assert response.status_code == 204
    assert response.headers['location'] == "/portfolio/0"
    
def test_get_all_portfolios_success(mock_backend, sample_portfolio):
    """Test fetching all portfolios."""
    response = client.get("/portfolios")
    assert response.status_code == 200
    assert response.json() == [sample_portfolio, sample_portfolio]

def test_get_portfolios_by_analysis_success(mock_backend, sample_portfolio,placeholder_UUID):
    """Test fetching all portfolios for a given analysis."""
    response = client.get(f"/portfolios/{placeholder_UUID}")
    assert response.status_code == 200
    assert response.json() == [sample_portfolio]

def test_get_portfolio_success(mock_backend, sample_portfolio):
    """Test fetching a single portfolio by id."""
    mock_backend["db"].get_portfolio_by_portfolio_id.return_value = [sample_portfolio]
    response = client.get("/portfolio/1")
    assert response.status_code == 200
    assert response.json() == sample_portfolio

def test_generate_portfolio_failures(mock_backend,placeholder_UUID,sample_analysis):
    """Trigger all non Internal Error responses + some internal"""
    
    #Case one: Endpoint with missing analysis parameter
    response = client.post('/portfolio/generate')
    assert response.status_code == 405 #similar to resume this is handled by fastAPI but is good to check
    
    # Case two: Malformed analysis parameter
    response = client.post('portfolio/generate/invalid-uuid')
    assert response.status_code == 400
    
    #Case three: valid analysis id by not found in db
    with patch("main_api.ConfigManager") as mock_config:    
        mock_config.return_value.preferences = {"online_llm_consent": False}
        mock_backend["db"].get_analysis_data.side_effect = LookupError("Analysis not found")
        response = client.post(f"/portfolio/generate/{placeholder_UUID}")
        assert response.status_code == 404
    
    #reset mocks for next case
    mock_backend["db"].get_analysis_data.side_effect = None
    mock_backend["db"].get_analysis_data.return_value = sample_analysis
    
    #Case Four: Everything is valid but llm-consent is not set
    with patch("main_api.ConfigManager") as mock_config:
        mock_config.return_value.preferences = {} 
        response = client.post(f"/portfolio/generate/{placeholder_UUID}")
        assert response.status_code == 422
    
    
    # Although not necessary, checking cases of known possible internal failures
    
    #Case Five: Builder Failure
    with patch("main_api.PortfolioBuilder") as mock_builder:
        mock_builder.return_value._build_portfolio.return_value = {}
        response = client.post(f"/portfolio/generate/{placeholder_UUID}")
        assert response.status_code == 500
    
    #Case Six: Save to database failure
    mock_backend["db"].save_portfolio.side_effect = Exception("DB write failed")
    response = client.post(f"/portfolio/generate/{placeholder_UUID}")
    assert response.status_code == 500
    
def test_get_all_portfolios_failures(mock_backend):

    # Case one - no portfolios in db
    mock_backend["db"].get_all_portfolios.side_effect = LookupError("No portfolios in db")
    response = client.get("/portfolios")
    assert response.status_code == 404

    # Case two - db errorr
    mock_backend["db"].get_all_portfolios.side_effect = Exception("DB error")
    response = client.get("/portfolios")
    assert response.status_code == 500

def test_get_portfolios_by_analysis_failures(mock_backend, placeholder_UUID):

    # Case one- invalid UUID
    response = client.get("/portfolios/invalid-uuid")
    assert response.status_code == 400

    # Case twp - no portfolios for analysis
    mock_backend["db"].get_portfolios_by_analysis_id.side_effect = LookupError("No portfolios for analysis")
    response = client.get(f"/portfolios/{placeholder_UUID}")
    assert response.status_code == 404

    # Case three - generalize db error.
    mock_backend["db"].get_portfolios_by_analysis_id.side_effect = Exception("DB error")
    response = client.get(f"/portfolios/{placeholder_UUID}")
    assert response.status_code == 500

def test_get_portfolio_failures(mock_backend):

    #Case one: non-integer id
    response = client.get("/portfolio/not-an-int")
    assert response.status_code == 422

    # Case two: portfolio not found
    mock_backend["db"].get_portfolio_by_portfolio_id.side_effect = LookupError("Database returned None")
    response = client.get("/portfolio/999")
    assert response.status_code == 404

    # Case three: DB error
    mock_backend["db"].get_portfolio_by_portfolio_id.side_effect = Exception("DB error")
    response = client.get("/portfolio/1")
    assert response.status_code == 500

def test_edit_portfolio_failures(mock_backend, sample_portfolio):
    
    #Case one: non-integer id
    response = client.put("/portfolio/not-an-int", json={"portfolio_title": "title", "portfolio_data": sample_portfolio})
    assert response.status_code == 422

    #Case two : missing field
    response = client.put("/portfolio/1", json={"portfolio_title": "title only"})
    assert response.status_code == 422

    # Case 3 : DB error
    mock_backend["db"].update_portfolio.side_effect = Exception("DB error")
    response = client.put("/portfolio/1", json={"portfolio_title": "title", "portfolio_data": sample_portfolio})
    assert response.status_code == 500

# ---- Portfolio Delete Tests ----

def test_delete_portfolio_success(mock_backend, sample_portfolio):
    """Test successful deletion of a specific portfolio."""
    
    mock_backend["db"].get_portfolio_by_portfolio_id.return_value = sample_portfolio
    mock_backend["db"].delete_portfolio.return_value = True

    response = client.delete("/portfolio/1")
    
    assert response.status_code == 204
    mock_backend["db"].delete_portfolio.assert_called_once_with(1)

def test_delete_portfolio_failures(mock_backend):
    """Test all failure modes for deleting a portfolio."""
    
    #case 1: type validation failure
    response = client.delete("/portfolio/not-an-int")
    assert response.status_code == 422

    #case 2: portfolio not found in DB
    mock_backend["db"].get_portfolio_by_portfolio_id.side_effect = LookupError("Not found")
    response = client.delete("/portfolio/999")
    assert response.status_code == 404
    
    mock_backend["db"].get_portfolio_by_portfolio_id.side_effect = None

    #case 3: general DB Error during deletion
    mock_backend["db"].get_portfolio_by_portfolio_id.return_value = {"portfolio_id": 1}
    mock_backend["db"].delete_portfolio.side_effect = Exception("DB error")
    response = client.delete("/portfolio/1")
    assert response.status_code == 500
    
# --- Negative Tests ---

def test_get_project_detail_invalid_uuid(mock_backend):
    """Test asking for a malformed UUID."""
    res = client.get("/projects/not-a-real-uuid")
    assert res.status_code == 400
    assert "Invalid UUID" in res.json()["detail"]

def test_get_project_detail_not_found(mock_backend,placeholder_UUID):
    """Test asking for a UUID that doesn't exist in DB."""
    # mock returns empty list for this specific zero-UUID
    mock_backend["db"].get_analysis_data.side_effect = LookupError(f"No analysis with id: {placeholder_UUID}")
    res = client.get(f"/projects/{placeholder_UUID}")
    assert res.status_code == 404

def test_privacy_consent(mock_backend):
    """Test consent update."""
    res = client.post("/privacy-consent", json={"consent_type": "online_llm_consent", "value": True})
    assert res.status_code == 200
    assert res.json()["status"] == "success"

def test_get_skills_interface_success(mock_backend):
    """Interface test: GET /skills aggregates languages/frameworks correctly."""
    mock_backend["db"].get_all_analyses_summary.return_value = [
        {
            "metadata_insights": {
                "language_stats": {
                    "Python": {"file_count": 3},
                    "JavaScript": {"file_count": 1}
                },
                "skill_stats": {
                    "Backend Development": {"file_count": 2}
                }
            },
            "project_insights": {
                "analyzed_insights": [{
                    "imports_summary": {
                        "FastAPI": {"frequency": 1}
                    }
                }]
            }
        },
        {
            "metadata_insights": {
                "language_stats": {
                    "Python": {"file_count": 2}
                },
                "skill_stats": {}
            },
            "project_insights": {
                "analyzed_insights": [{
                    "imports_summary": {
                        "React": {"frequency": 1}
                    }
                }]
            }
        },
    ]

    res = client.get("/skills")

    assert res.status_code == 200
    skills = res.json()['skills']
    assert skills["Python"] == 5
    assert skills["JavaScript"] == 1
    assert skills["FastAPI"] == 1
    assert skills["React"] == 1
    assert skills["Backend Development"] == 2

def test_get_skills_implementation_empty_db(mock_backend):
    """Implementation test: GET /skills returns empty skills on empty database."""
    mock_backend["db"].get_all_analyses_summary.return_value = []

    res = client.get("/skills")

    assert res.status_code == 200
    assert res.json() == {"skills": {}}
TEST_UUID = "123e4567-e89b-12d3-a456-426614174000"
@patch("main_api.DictExporter")
@patch("main_api.DictImporter")
@patch("main_api.TreeManager")
@patch("main_api.perform_update_merge")
@patch("main_api.FileManager")
@patch("main_api.AnalysisPipeline")
@patch("main_api.CLI")
@patch("main_api.ConfigManager")
@patch("main_api.DatabaseManager")
def test_extract_update_endpoint(
    mock_db_cls, mock_config_cls, mock_cli_cls,
    mock_pipeline_cls, mock_fm_cls, mock_merge,
    mock_tm_cls, mock_importer_cls, mock_exporter_cls,
):
    """Test Phase 1: PUT /projects/{analysis_id}/update/extract"""
    # Mock FileManager to return a valid tree structure
    mock_tree = {"name": "root"}
    mock_fm_cls.return_value.load_from_filepath.return_value = {
        "status": "success",
        "tree": mock_tree,
        "binary_data": [],
    }

    mock_merge.return_value = (mock_tree, [])
    mock_pipeline = mock_pipeline_cls.return_value
    mock_pipeline.run_analysis_extract.return_value = (
        TEST_UUID,
        {"topic_keywords": [{"topic_id": 0, "keywords": ["test", "code"]}]},
        ["Python", "React"],
        {},
    )
    mock_pipeline.result_bundle.project_analysis_data = {"analyzed_insights": []}
    mock_exporter_cls.return_value.export.return_value = {}

    # Simulate dummy zip file and form-data credentials
    files = {"file": ("test_repo.zip", b"dummy zip content", "application/zip")}
    data = {
        "github_username": "testuser",
        "github_email": "test@example.com",
    }
    response = client.put(f"/projects/{TEST_UUID}/update/extract", files=files, data=data)

    assert response.status_code == 200
    json_response = response.json()
    assert "topic_keywords" in json_response
    assert "detected_skills" in json_response
    assert json_response["detected_skills"] == ["Python", "React"]

    mock_pipeline.run_analysis_extract.assert_called_once()
    assert mock_pipeline.run_analysis_extract.call_args.kwargs["github_username"] == "testuser"

    # Clean up the cache file created by the endpoint
    cache_path = os.path.join("cache", f"pending_update_{TEST_UUID}.pkl")
    if os.path.exists(cache_path):
        os.remove(cache_path)
@patch("main_api.AnalysisPipeline")
@patch("main_api.CLI")
@patch("main_api.ConfigManager")
@patch("main_api.DatabaseManager")
def test_commit_update_endpoint(mock_db_cls, mock_config_cls, mock_cli_cls, mock_pipeline_cls):
    """Test Phase 2: POST /projects/{analysis_id}/update/commit"""
    import pickle
    cache_data = {
        "merged_tree_dict": {},
        "merged_binary_list": [],
        "topic_vector_bundle": {"topic_keywords": []},
        "text_analysis_data": {},
        "analyzed_repos": [
            {"repository_name": "capstone_repo", "importance_score": 5},
            {"repository_name": "other_repo", "importance_score": 3},
        ],
    }
    os.makedirs("cache", exist_ok=True)
    cache_path = os.path.join("cache", f"pending_update_{TEST_UUID}.pkl")
    with open(cache_path, "wb") as f:
        pickle.dump(cache_data, f)
    mock_pipeline = mock_pipeline_cls.return_value
    mock_pipeline.run_analysis_generate.return_value = (
        "This is a fake AI generated summary for testing."
    )
    payload = {
        "topic_keywords": [
            {"topic_id": 0, "keywords": ["result", "data", "code"]}
        ],
        "user_highlights": ["Python"],
        "selected_projects": ["capstone_repo", "other_repo"],
        "online_llm_consent": True,
    }
    try:
        response = client.post(f"/projects/{TEST_UUID}/update/commit", json=payload)

        assert response.status_code == 200
        json_response = response.json()
        assert json_response["status"] == "success"
        assert json_response["summary"] == "This is a fake AI generated summary for testing."
        mock_pipeline.run_analysis_generate.assert_called_once()
        assert mock_pipeline.run_analysis_generate.call_args.kwargs["selected_projects"] == [
            "capstone_repo", "other_repo"
        ]
    finally:
        if os.path.exists(cache_path):
            os.remove(cache_path)
            
UPLOAD_MOCK_UUID = "mock-uuid-1234"

UPLOAD_DUMMY_CACHE = {
    "topic_vector_bundle": {"topic_keywords": []},
    "text_analysis_data": {},
    "analyzed_repos": [{"repository_name": "Repo1", "importance_score": 10}],
}


@patch("main_api.os.makedirs")
@patch("main_api.pickle.dump")
@patch("main_api.AnalysisPipeline")
@patch("main_api.CLI")
@patch("main_api.ConfigManager")
@patch("main_api.DatabaseManager")
def test_extract_upload_success(
    mock_db_cls, mock_config_cls, mock_cli_cls,
    mock_pipeline_cls, mock_pickle_dump, mock_makedirs,
):
    """Test Case 1 (Success): POST /projects/upload/extract returns 200 with expected fields."""
    mock_pipeline = mock_pipeline_cls.return_value
    mock_pipeline.run_analysis_extract.return_value = (
        UPLOAD_MOCK_UUID,
        {"topic_keywords": []},
        ["Python"],
        {},
    )
    mock_pipeline.result_bundle.project_analysis_data = {"analyzed_insights": []}

    files = {"file": ("test.zip", b"dummy zip content", "application/zip")}
    response = client.post("/projects/upload/extract", files=files)

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["analysis_id"] == UPLOAD_MOCK_UUID
    assert "topic_keywords" in json_response
    assert "detected_skills" in json_response
    assert "analyzed_projects" in json_response
    assert json_response["detected_skills"] == ["Python"]


@patch("main_api.AnalysisPipeline")
@patch("main_api.CLI")
@patch("main_api.ConfigManager")
@patch("main_api.DatabaseManager")
def test_extract_upload_pipeline_failure(
    mock_db_cls, mock_config_cls, mock_cli_cls, mock_pipeline_cls,
):
    """Test Case 2 (Failure): POST /projects/upload/extract returns 500 when pipeline returns None."""
    mock_pipeline = mock_pipeline_cls.return_value
    mock_pipeline.run_analysis_extract.return_value = None

    files = {"file": ("test.zip", b"dummy zip content", "application/zip")}
    response = client.post("/projects/upload/extract", files=files)

    assert response.status_code == 500


@patch("main_api.AnalysisPipeline")
@patch("main_api.CLI")
@patch("main_api.ConfigManager")
@patch("main_api.os.remove")
@patch("main_api.pickle.load")
@patch("builtins.open")
@patch("main_api.os.path.exists")
@patch("main_api.DatabaseManager")
def test_commit_upload_success(
    mock_db_cls, mock_exists, mock_open_call, mock_pickle_load,
    mock_os_remove, mock_config_cls, mock_cli_cls, mock_pipeline_cls,
):
    """Test Case 3 (Success): POST /projects/{analysis_id}/upload/commit returns 200."""
    mock_exists.return_value = True
    mock_pickle_load.return_value = UPLOAD_DUMMY_CACHE

    mock_pipeline = mock_pipeline_cls.return_value
    mock_pipeline.run_analysis_generate.return_value = "Mocked AI Summary"

    payload = {
        "topic_keywords": [{"topic_id": 1, "keywords": ["ai", "python"]}],
        "user_highlights": ["highlight1"],
        "selected_projects": ["Repo1"],
        "online_llm_consent": True,
    }
    response = client.post(f"/projects/{UPLOAD_MOCK_UUID}/upload/commit", json=payload)

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "success"
    assert json_response["summary"] == "Mocked AI Summary"


@patch("main_api.os.path.exists")
@patch("main_api.DatabaseManager")
def test_commit_upload_cache_expired(mock_db_cls, mock_exists):
    """Test Case 4 (Failure): POST /projects/{analysis_id}/upload/commit returns 404 when cache is missing."""
    mock_exists.return_value = False

    payload = {
        "topic_keywords": [{"topic_id": 1, "keywords": ["ai", "python"]}],
        "user_highlights": ["highlight1"],
        "selected_projects": ["Repo1"],
        "online_llm_consent": True,
    }
    response = client.post(f"/projects/{UPLOAD_MOCK_UUID}/upload/commit", json=payload)

    assert response.status_code == 404
    assert "pending upload found" in response.json()["detail"]
