import pytest
from fastapi.testclient import TestClient
import sys
import os

# path to import backend code
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from main_api import app

client = TestClient(app)

@pytest.fixture
def mock_backend(mocker):
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
        if "WHERE result_id" in query:
            if params and str(params[0]) == "00000000-0000-0000-0000-000000000000":
                return [] 
            return [{"project_data": {"name": "Test Project", "info": "Details"}}]
        return [{"result_id": "fake-uuid-123", "project_data": {"name": "Test Project"}}]
        
    db_instance.db.execute_query.side_effect = simple_query_side_effect
    db_instance.get_result_by_id.side_effect = lambda rid: None if rid == "missing-id" else {"topic_vector": {}, "resume_points": "Old Summary"}
    db_instance.save_resume_points.return_value = True
    db_instance.get_all_results_summary.return_value = []

    # 4. Configure LLM Defaults
    local_llm_instance.generate_summary.return_value = "Local AI Summary"
    online_llm_instance.generate_summary.return_value = "Online AI Summary"

    # 5. Configure Config Defaults (Default to Local)
    config_instance.preferences = {"online_llm_consent": False}

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
    res = client.post("/projects/upload", files=files)
    
    assert res.status_code == 200
    assert res.json()["status"] == "success"
    # Check if the pipeline instance was called
    mock_backend["pipeline"].run_analysis.assert_called_once()

def test_get_projects_success(mock_backend):
    """Test fetching project list."""
    res = client.get("/projects")
    assert res.status_code == 200
    assert len(res.json()) > 0

def test_get_project_detail_success(mock_backend):
    """Test fetching valid project detail."""
    # Use a valid UUID string
    res = client.get("/projects/123e4567-e89b-12d3-a456-426614174000")
    assert res.status_code == 200
    assert res.json()["project_data"]["name"] == "Test Project"

def test_edit_resume_success(mock_backend):
    """Test saving edits."""
    res = client.post("/resume/valid-id/edit", json={"resume_points": "Edited"})
    assert res.status_code == 200

def test_privacy_consent(mock_backend):
    """Test consent update."""
    res = client.post("/privacy-consent", json={"consent_type": "online_llm_consent", "value": True})
    assert res.status_code == 200
    assert res.json()["status"] == "success"


def test_generate_resume_online_consent(mock_backend):
    """Scenario: User CONSENTS to Online LLM, and it works."""
    mock_backend["config"].preferences = {"online_llm_consent": True}
    
    res = client.post("/resume/generate", data={"result_id": "valid-id"})
    
    assert res.status_code == 200
    data = res.json()
    assert data["resume_points"] == "Online AI Summary" 
    assert data["model_used"] == "online"
    
    mock_backend["online_llm"].generate_summary.assert_called()
    mock_backend["local_llm"].generate_summary.assert_not_called()

def test_generate_resume_local_consent(mock_backend):
    """Scenario: User DENIES consent (or default), uses Local LLM."""
    mock_backend["config"].preferences = {"online_llm_consent": False}
    
    res = client.post("/resume/generate", data={"result_id": "valid-id"})
    
    assert res.status_code == 200
    data = res.json()
    assert data["resume_points"] == "Local AI Summary"
    assert data["model_used"] == "local"
    
    mock_backend["local_llm"].generate_summary.assert_called()
    mock_backend["online_llm"].generate_summary.assert_not_called()

def test_generate_resume_online_fallback(mock_backend):
    """Scenario: User CONSENTS, but Online LLM fails. Should fallback."""
    mock_backend["config"].preferences = {"online_llm_consent": True}
    
    # Simulate Online LLM crashing
    mock_backend["online_llm"].generate_summary.side_effect = Exception("API Key Missing")
    
    res = client.post("/resume/generate", data={"result_id": "valid-id"})
    
    assert res.status_code == 200
    data = res.json()
    assert data["resume_points"] == "Local AI Summary" 
    assert data["model_used"] == "local_fallback" 
    
    mock_backend["online_llm"].generate_summary.assert_called()
    mock_backend["local_llm"].generate_summary.assert_called()
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