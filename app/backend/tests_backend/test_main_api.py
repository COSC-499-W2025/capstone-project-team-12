import pytest
from fastapi.testclient import TestClient
import sys
import os
from unittest.mock import ANY,patch

# path to import backend code
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from main_api import app

client = TestClient(app)

@pytest.fixture
def sample_analysis():
    return {
            'analysis_id':'00000000-0000-0000-0000-000000000000',
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
def sample_resume():
    return {
            "resume_id": 1,
            "result_id": 00000000-0000-0000-0000-000000000000,
            "summary": "Test summary",
            "projects": [],
            "skills": [],
            "languages": []
        }

@pytest.fixture
def mock_backend(mocker,sample_analysis):
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
            if params and str(params[0]) == "00000000-0000-0000-0000-000000000000":
                return [] 
            return [{"project_data": {"name": "Test Project", "info": "Details"}}]
        return [{"analysis_id": "fake-uuid-123", "project_data": {"name": "Test Project"}}]
        
    
    #db_instance.db.execute_query.side_effect = simple_query_side_effect
    db_instance.get_analysis_data.side_effect = lambda rid: None if rid == "missing-id" else sample_analysis
    
    db_instance.save_resume_points.return_value = True
    
    #mock db_manager return for return all analyses
    db_instance.get_all_analyses_summary.return_value =[
        {'analysis_id':'00000000-0000-0000-0000-000000000000','analysis_title': 'Title','metadata_insights':'Some JSON Object as string','project_insights':'Some JSON Object as string','file_path':'some_path'},
        {'analysis_id':'00000000-0000-0000-0000-000000000001','analysis_title': 'Title2','metadata_insights':'Some JSON Object as string','project_insights':'Some JSON Object as string','file_path':'some_path2'}
    ]
    
    # 4. Configure LLM Defaults
    local_llm_instance.generate_summary.return_value = "Local AI Summary"
    online_llm_instance.generate_summary.return_value = "Online AI Summary"

    # 5. Configure Config Defaults (Default to Local)
    config_instance.preferences = {"online_llm_consent": False}

    # 6. Configure Pipeline Return Value
    # The API now expects run_analysis to return a UUID string.
    pipeline_instance.run_analysis.return_value = "00000000-0000-0000-0000-000000000000"

    return {
        "db": db_instance,
        "pipeline": pipeline_instance,
        "local_llm": local_llm_instance,
        "online_llm": online_llm_instance,
        "config": config_instance
    }


def test_health_check():
    """Does the API turn on?"""
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "active"

def test_upload_project_success(mock_backend):
    """Test successful upload."""
    files = {'file': ('test.zip', b'content', 'application/zip')}
    
    # We no longer pass 'result_id' in the form data
    response = client.post("/projects/upload", files=files)
        
    #check success
    assert response.status_code == 201
    
    # Verify Analysis ID of new entry is returned
    assert response.headers["location"] == "/projects/00000000-0000-0000-0000-000000000000"

    # Check if the pipeline instance was called correctly
    # We use ANY for the path since it's a random temp file
    mock_backend["pipeline"].run_analysis.assert_called_once_with(ANY, return_id=True)


def test_get_projects_success(mock_backend):
    """Test fetching project list."""
    response = client.get("/projects")
    print(response.content)
    assert response.status_code == 200
    assert len(response.content) > 0

def test_get_project_success(mock_backend,sample_analysis):
    """Test fetching valid project detail."""
    # Use a valid UUID string
    response = client.get("/projects/123e4567-e89b-12d3-a456-426614174000")
    assert response.status_code == 200
    assert response.json() == sample_analysis

def test_get_resume_success(mock_backend,sample_resume):
    #TODO Implement test
    assert True

def test_generate_resume_success(mock_backend, sample_analysis,sample_resume):
    """Test successful resume generation and save."""
    
    #test analysis UUID
    analysis_id = "00000000-0000-0000-0000-000000000000"
    
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

def test_privacy_consent(mock_backend):
    """Test consent update."""
    res = client.post("/privacy-consent", json={"consent_type": "online_llm_consent", "value": True})
    assert res.status_code == 200
    assert res.json()["status"] == "success"



# --- Negative Tests ---

def test_upload_project_pipeline_failure(mock_backend):
    """Test handling of pipeline crashes."""
    # Force the pipeline instance to raise an error
    mock_backend["pipeline"].run_analysis.side_effect = Exception("Analysis Failed")
    
    files = {'file': ('test.zip', b'content', 'application/zip')}
    res = client.post("/projects/upload", files=files)
    
    assert res.status_code == 500
    assert "Analysis Failed" in res.json()["detail"]

def test_get_project_detail_invalid_uuid(mock_backend):
    """Test asking for a malformed UUID."""
    res = client.get("/projects/not-a-real-uuid")
    assert res.status_code == 400
    assert "Invalid UUID" in res.json()["detail"]

def test_get_project_detail_not_found(mock_backend):
    """Test asking for a UUID that doesn't exist in DB."""
    # mock returns empty list for this specific zero-UUID
    res = client.get("/projects/00000000-0000-0000-0000-000000000000")
    assert res.status_code == 404
    assert "Project not found" in res.json()["detail"]

def test_generate_resume_not_found(mock_backend):
    """Test generating resume for missing ID."""
    #mock side_effect returns None for "missing-id"
    res = client.post("/resume/generate", data={"result_id": "missing-id"})
    assert res.status_code == 404
    assert "Result not found" in res.json()["detail"]

def test_edit_resume_db_failure(mock_backend):
    """Test handling database save errors."""
    # Simulate DB returning False (fail)
    mock_backend["db"].save_resume_points.return_value = False
    
    res = client.post("/resume/valid-id/edit", json={"resume_points": "Text"})
    assert res.status_code == 500
    assert "Save failed" in res.json()["detail"]

# --- Portfolio & Skills Tests ---

def test_get_portfolio_interface_success(mock_backend, mocker):
    """Interface test: GET /portfolio/{result_id} returns mocked portfolio data."""
    mock_builder_class = mocker.patch("main_api.PortfolioBuilder")
    mock_builder_instance = mock_builder_class.return_value
    dummy_portfolio = {"portfolio_id": "123", "projects_detail": [{"name": "Mocked Project"}]}
    mock_builder_instance.create_portfolio_from_result_id.return_value = dummy_portfolio

    res = client.get("/portfolio/valid-uuid")

    assert res.status_code == 200
    assert res.json() == dummy_portfolio

def test_get_portfolio_implementation_not_found(mock_backend, mocker):
    """Implementation test: returns 404 when builder cannot find the result."""
    mock_builder_class = mocker.patch("main_api.PortfolioBuilder")
    mock_builder_instance = mock_builder_class.return_value
    mock_builder_instance.create_portfolio_from_result_id.return_value = None

    res = client.get("/portfolio/invalid-uuid")

    assert res.status_code == 404
    assert res.json()["detail"] == "Portfolio not found"

def test_get_skills_interface_success(mock_backend):
    """Interface test: GET /skills aggregates languages/frameworks correctly."""
    mock_backend["db"].get_all_results_summary.return_value = [
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
    skills = res.json()["skills"]
    assert skills["Python"] == 5
    assert skills["JavaScript"] == 1
    assert skills["FastAPI"] == 1
    assert skills["React"] == 1
    assert skills["Backend Development"] == 2

def test_get_skills_implementation_empty_db(mock_backend):
    """Implementation test: GET /skills returns empty skills on empty database."""
    mock_backend["db"].get_all_results_summary.return_value = []

    res = client.get("/skills")

    assert res.status_code == 200
    assert res.json() == {"skills": {}}