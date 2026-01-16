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
    Mocks all external dependencies
    Returns the specific instances that will be used by the API, 
    """
    # We patch the class names where they are IMPORTED in main_api
    MockDBClass = mocker.patch("main_api.DatabaseManager")
    MockCLIClass = mocker.patch("main_api.CLI")
    MockConfigClass = mocker.patch("main_api.ConfigManager")
    MockPipelineClass = mocker.patch("main_api.AnalysisPipeline")
    MockLLMClass = mocker.patch("main_api.LocalLLMClient")

    db_instance = MockDBClass.return_value
    pipeline_instance = MockPipelineClass.return_value
    llm_instance = MockLLMClass.return_value
    cli_instance = MockCLIClass.return_value
    config_instance = MockConfigClass.return_value

    # Mock the internal db connector's update method
    db_instance.db.execute_update.return_value = True
    
    def simple_query_side_effect(query, params=None):
        # If asking for a specific ID, check if it matches a "valid" one
        if "WHERE result_id" in query:
            # Simulate "Not Found" for a specific zero-UUID
            if params and str(params[0]) == "00000000-0000-0000-0000-000000000000":
                return [] 
            return [{"project_data": {"name": "Test Project", "info": "Details"}}]
        
        # If asking for list
        return [{"result_id": "fake-uuid-123", "project_data": {"name": "Test Project"}}]
        
    db_instance.db.execute_query.side_effect = simple_query_side_effect
    
    # Mock standard DB methods
    db_instance.get_result_by_id.side_effect = lambda rid: None if rid == "missing-id" else {"topic_vector": {}, "resume_points": "Old Summary"}
    db_instance.save_resume_points.return_value = True
    db_instance.get_all_results_summary.return_value = []

    llm_instance.generate_summary.return_value = "New AI Summary"

    #return the instances to use in tests
    return {
        "db": db_instance,
        "pipeline": pipeline_instance,
        "llm": llm_instance,
        "cli": cli_instance,
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

def test_generate_resume_success(mock_backend):
    """Test LLM generation."""
    res = client.post("/resume/generate", data={"result_id": "valid-id"})
    assert res.status_code == 200
    assert res.json()["resume_points"] == "New AI Summary"
    # Verify we used the LLM instance
    mock_backend["llm"].generate_summary.assert_called()

def test_edit_resume_success(mock_backend):
    """Test saving edits."""
    res = client.post("/resume/valid-id/edit", json={"resume_points": "Edited"})
    assert res.status_code == 200

def test_privacy_consent(mock_backend):
    """Test consent update."""
    res = client.post("/privacy-consent", json={"consent_type": "x", "value": True})
    assert res.status_code == 200

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