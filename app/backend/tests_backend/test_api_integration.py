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

#global id holders to not have to poll the api for each test
gl_analysis_id = None 
gl_resume_id = None
gl_portfolio_id = None
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

def makelog(response): #debug helper for development
    """Write the contents of a valid JSON response returned by API to log.txt in /app """
    with open('tests_backend/log.txt','w') as file:
        file.write(str(response.json()))


# --- End of helpers ---

def test_reset_test_db(test_db_manager): #Delete all items in test_db without using api before testing begins
    db_manager = test_db_manager
    assert db_manager.wipe_all_data()
    
@pytest.mark.usefixtures("set_api_manager")
@pytest.mark.requires_test_db
class TestAPIIntegration:

    def test_init(self):
        """Verify the test client was initialised correctly."""
        assert client is not None
    

    
    def test_post_upload_extract_and_commit(self):
        """Loads a sample analysis via the extract and commit endpoints. Also tests both endpoints with test_main_dir.zip"""
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
        
        #New analysis test successful, update global analysis id used by other tests
        global gl_analysis_id 
        gl_analysis_id = analysis_id

    def test_put_upload_extract_and_commit(self):
        """Test incremental extract and commit endpoints"""
        with open('/app/tests_backend/test_main_dir/test_zip_dir.zip', 'rb') as f:
            file = {'file': ('test_main_dir.zip', f)}
            
            global gl_analysis_id
            extract_response = client.put(f"/projects/{gl_analysis_id}/update/extract", files=file)
        
        payload = {
            "topic_keywords": [
                {"topic_id": 0, "keywords": ["result", "data", "code"]}
            ],
            "user_highlights": ["CSS"],
            "selected_projects": [],
            "online_llm_consent": True,
        }
        
        commit_response = client.post(f'/projects/{gl_analysis_id}/update/commit',json = payload)
        
        assert extract_response.status_code == 200
        assert commit_response.status_code == 200
        assert commit_response.json()['status'] == 'success'
        
    def test_get_projects(self):
        """Test get all analyses summary endpoint"""
        response = client.get("/projects")
        assert response.status_code == 200
        for result_entry in response.json():
            assert isinstance(result_entry,dict)
            assert 'analysis_id' in result_entry
    
    def test_get_project(self):
        """Test get specific analysis data endpoint"""
        global gl_analysis_id
        response = client.get(f"/projects/{gl_analysis_id}")
        assert response.status_code == 200
        result = response.json()
        assert 'analysis_id' in result
        assert len(result) > 5 #Arbritary check for number of fields so it doesnt break because of reworks
    
    def test_get_skills(self):
        """Test get aggregated skills endpoint"""
        response = client.get('/skills')
        assert response.status_code == 200
        
        result = response.json()
        assert 'skills' in result
        assert len(result) > 0
    
    def test_post_generate_resume(self):
        global gl_analysis_id
        response = client.post(f'resume/generate/{gl_analysis_id}')
        
        assert response.status_code == 201
        assert 'location' in response.headers
        assert 'resume_id' in response.json()
        
        global gl_resume_id
        gl_resume_id = int(response.json()['resume_id'])
       
    def test_get_resumes(self):
        """Test get all resumes endpoint"""
        response = client.get("/resumes")
        assert response.status_code == 200
        for result_entry in response.json():
            assert isinstance(result_entry,dict)
            assert 'resume_id' in result_entry
    
    def test_get_resumes_by_analysis_id(self):
        """Test get all resumes of an analysis endpoint"""
        global gl_analysis_id
        response = client.get(f"/resumes/{gl_analysis_id}")
        assert response.status_code == 200
        result = response.json()
        for result_entry in response.json():
            assert isinstance(result_entry,dict)
            assert 'resume_id' in result_entry
    
    def test_get_resume_by_resume_id(self):
        global gl_resume_id
        print(f"/resume/{gl_resume_id}")
        response = client.get(f"/resume/{gl_resume_id}")
        assert response.status_code == 200
        assert isinstance(response.json(),dict)
        assert 'resume_id' in response.json()

    def test_post_generate_portfolio(self):
            global gl_analysis_id
            response = client.post(f'portfolio/generate/{gl_analysis_id}')
            
            assert response.status_code == 201
            assert 'location' in response.headers
            assert 'portfolio_id' in response.json()
            
            global gl_portfolio_id
            gl_portfolio_id = int(response.json()['portfolio_id'])
       
    def test_get_portfolios(self):
        """Test get all portfolios endpoint"""
        response = client.get("/portfolios")
        print(response.json())
        assert response.status_code == 200
        for result_entry in response.json():
            assert isinstance(result_entry,dict)
            assert 'portfolio_id' in result_entry
    
    def test_get_portfolios_by_analysis_id(self):
        """Test get all portfolios of an analysis endpoint"""
        global gl_analysis_id
        response = client.get(f"/portfolios/{gl_analysis_id}")
        assert response.status_code == 200
        result = response.json()
        for result_entry in response.json():
            assert isinstance(result_entry,dict)
            assert 'portfolio_id' in result_entry
    
    def test_get_portfolio_by_portfolio_id(self):
        global gl_portfolio_id
        print(f"/portfolio/{gl_portfolio_id}")
        response = client.get(f"/portfolio/{gl_portfolio_id}")
        assert response.status_code == 200
        assert isinstance(response.json(),dict)
        assert 'portfolio_id' in response.json()

    def test_delete_portfolio_by_portfolio_id(self):
        """Test deleting a specific portfolio via endpoint"""
        global gl_portfolio_id
        
        response = client.delete(f"/portfolio/{gl_portfolio_id}")
        assert response.status_code == 204
        
        # verify it was actually removed (should return 404 Not Found)
        verify_response = client.get(f"/portfolio/{gl_portfolio_id}")
        assert verify_response.status_code == 404

    def test_delete_resume_by_resume_id(self):
        """Test deleting a specific resume via endpoint"""
        global gl_resume_id
        
        response = client.delete(f"/resume/{gl_resume_id}")
        assert response.status_code == 204
        
        verify_response = client.get(f"/resume/{gl_resume_id}")
        assert verify_response.status_code == 404

    