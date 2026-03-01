import pytest
from fastapi.testclient import TestClient
from database_manager import DatabaseManager
from db_utils import DB_connector
import sys
import os
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from main_api import app, get_db

#global client initatied later with database override
client = None

@pytest.fixture
def placeholder_UUID():
    return "00000000-0000-0000-0000-000000000000"

@pytest.fixture
def sample_analysis(placeholder_UUID):
    return {
        'analysis_id': placeholder_UUID,
        'analysis_title': 'Title',
        'topic_vector': {},
        'resume_points': {},
        'project_insights': {},
        'package_insights': {},
        'metadata_insights': {},
        'tracked_data': {
            'bow_cache': {},
            'project_data': {},
            'package_data': {},
            'metadata_stats': {}
        },
        'resume_data': {},
        'portfolio_data': {}
    }

@pytest.fixture
def sample_resume(placeholder_UUID):
    return {
        "resume_id": 1,
        "result_id": placeholder_UUID,
        "summary": "Test summary",
        "projects": [],
        "skills": [],
        "languages": []
    }

@pytest.fixture
def sample_portfolio(placeholder_UUID):
    return {
        "portfolio_id": 1,
        "result_id": placeholder_UUID,
        "projects_detail": [],
        "skill_timeline": {},
        "growth_metrics": {}
    }

@pytest.fixture
def test_db_manager():
    db_manager = DatabaseManager()
    db_manager.db = DB_connector(database_name="test_db")
    return db_manager

@pytest.fixture
def set_api_manager(test_db_manager):
    """Overrides the API's get_db dependency to use test_db and sets the global client."""
    def override_get_db():
        try:
            yield test_db_manager
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    global client
    client = TestClient(app)
    yield                               # hands control to the tests
    app.dependency_overrides.clear()    # teardown after test finishes

@pytest.fixture(autouse=True) #Autouse makes the check run on every test in module
def require_test_db(request):
    """Skip tests marked with requires_test_db if not connected to test_db."""
    if request.node.get_closest_marker("requires_test_db"): #Check for custom node marker (defined in pytest.ini)
        test_db = request.getfixturevalue("test_db_manager")
        db_name = test_db.db.execute_query("SELECT current_database();")[0]['current_database']
        if db_name != "test_db":
            pytest.skip("Not using 'test_db' — check integration test config")

# --- End of helpers ---

@pytest.mark.usefixtures("set_api_manager")
@pytest.mark.requires_test_db
class TestAPIIntegration:

    def test_init(self):
        """Verify the test client was initialised correctly."""
        assert client is not None

    def test_post_upload_extract_and_commit(self):
        """Loads a sample analysis via the upload endpoint."""
        with open('/app/tests_backend/test_main_dir/test_zip_dir.zip', 'rb') as f:
            file = {'file': ('test_main_dir.zip', f)}
            extract_response = client.post("/projects/upload/extract", files=file)
 
        analysis_id:str = extract_response.json()['analysis_id']
        
        payload = {
            "topic_keywords": [
                {"topic_id": 0, "keywords": ["result", "data", "code"]}
            ],
            "user_highlights": ["CSS"],
            "selected_projects": [],
            "online_llm_consent": True,
        }
        
        commit_response = client.post(f'/projects/{analysis_id}/upload/commit',json = payload)
        
        assert extract_response.status_code == 200
        assert commit_response.status_code == 200
        try:
            uuid.UUID(analysis_id)
        except ValueError: #Value error if returned uuid is invalid
            pytest.fail(f"Returned analysis_id '{analysis_id}' is not a valid UUID")
        assert commit_response.json()['status'] == 'success'
        