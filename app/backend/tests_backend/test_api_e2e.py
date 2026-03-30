import pytest
from fastapi.testclient import TestClient
from database_manager import DatabaseManager
from db_utils import DB_connector
import sys
import os
import uuid
import pprint

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from main_api import app, get_db

#global client initatied later with database override
client = None

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

def make_new_analysis() -> str:
    """Makes new analysis using minimal test_main_dir.zip"""
     # Load our small test zip
    with open('/app/tests_backend/test_main_dir/test_zip_dir.zip', 'rb') as f:
        file = {'file': ('test_main_dir.zip', f)}
        #post the file to new analysis 
        extract_response = client.post("/projects/upload/extract", files=file)
    
    extract_body = extract_response.json()
    analysis_id = extract_body["analysis_id"]

    #Make the commit for new analysis
    topic_keywords = extract_body.get("topic_keywords", [])
    analyzed_projects = extract_body.get("analyzed_projects", [])
    selected_projects = [p["repository_name"] for p in analyzed_projects]

    commit_package =  {
        "topic_keywords": topic_keywords,
        "user_highlights":[],
        "selected_projects": selected_projects,
        "online_llm_consent": True,
    }
    
    #Commit the new analysis
    client.post(f'/projects/{analysis_id}/upload/commit',json = commit_package)
    return analysis_id

# --- End of helpers ---

def test_reset_test_db(test_db_manager): #Delete all items in test_db without using api before testing begins
    db_manager = test_db_manager
    assert db_manager.wipe_all_data()
    
@pytest.mark.usefixtures("set_api_manager")
@pytest.mark.requires_test_db
class TestAPIEndToEnd:
    def test_init(self):
        """Verify the test client was initialised correctly."""
        assert client is not None
    
    def test_newanalysis_workflow(self):
        """Test workflow new analysis, retrieving it, making an edit and deleting it""""""
        1. Extract phase  - POST /projects/upload/extract
        2. Commit phase   - POST /projects/{id}/upload/commit
        3. Retrieve all   - GET  /projects
        4. Retrieve one   - GET  /projects/{id}
        5. Delete one     - DELETE /projects/{id}
        6. Confirm gone   - GET  /projects/{id} → 404
        
        DOES NOT USE make_new_analysis() helper to allow for each step can be validated with asserts
        """
 
        # Load our small test zip
        with open('/app/tests_backend/test_main_dir/test_zip_dir.zip', 'rb') as f:
            file = {'file': ('test_main_dir.zip', f)}
            #post the file to new analysis 
            extract_response = client.post("/projects/upload/extract", files=file)
       
        #Check for success
        assert extract_response.status_code == 200, f"Extract phase returned fail code {extract_response.status_code}"
        
        extract_body = extract_response.json()
        assert "analysis_id" in extract_body, "Response missing analysis_id"
 
        analysis_id = extract_body["analysis_id"]
        
        # Validate UUID format
        uuid.UUID(analysis_id)  # raises ValueError if malformed
 
        # Response should carry results
        assert "topic_keywords" in extract_body
        assert "detected_skills" in extract_body
        assert "analyzed_projects" in extract_body
 
        #Make the commit for new analysis
        topic_keywords = extract_body.get("topic_keywords", [])
        analyzed_projects = extract_body.get("analyzed_projects", [])
        selected_projects = [p["repository_name"] for p in analyzed_projects]
 
        commit_package =  {
            "topic_keywords": topic_keywords,
            "user_highlights":[],
            "selected_projects": selected_projects,
            "online_llm_consent": True,
        }
        
        commit_response = client.post(f'/projects/{analysis_id}/upload/commit',json = commit_package)
        
        assert commit_response.status_code == 200, f"Commit phase returned fail code {extract_response.status_code}"
        commit_body = commit_response.json()
        assert commit_body.get("status") == "success"
 
        #Get ALL projects and check if new one is present
        get_all_projects_resp = client.get("/projects")
        assert get_all_projects_resp.status_code == 200
        projects =get_all_projects_resp.json()
        
        assert isinstance(projects, list)
        ids = [p["analysis_id"] for p in projects]
        assert analysis_id in ids, "Newly created analysis not returned by GET /projects"
 
        # Try getting directly by analysis_id instead
        detailed_response = client.get(f"/projects/{analysis_id}")
        assert detailed_response.status_code == 200
        detailed_body = detailed_response.json()
        assert detailed_body  
        
        # NEW ASSERTS TO VERIFY ARCHITECTURAL FIXES:
        # Ensure they are dictionaries (thanks to parse_json_fields) and have data (thanks to deep memory caching)
        assert isinstance(detailed_body.get("metadata_insights"), dict)
        assert isinstance(detailed_body.get("project_insights"), dict)
 
        # Delete the new analysis
        delete_response = client.delete(f"/projects/{analysis_id}")
        assert delete_response.status_code == 204
 
        # Check for proper deletion
        check_response = client.get(f"/projects/{analysis_id}")
        assert check_response.status_code == 404
 
 
    def test_resume_workflow(self):
        """
        Create new analysis, then generate, edit and delete a resume for the new analysis
        
        1. Create a new analysis (extract + commit)
        2. GET /resumes (empty for this analysis)
        3. POST /resume/generate/{analysis_id}  - creates resume
        4. GET  /resume/{resume_id}             - retrieve it
        5. GET  /resumes/{analysis_id}          - list for analysis
        6. PUT  /resume/{resume_id}             - edit it
        7. DELETE /resume/{resume_id}           - delete it
        8. Confirm gone via GET                 - 404
        9. Teardown: delete the analysis
        """

        #Make a new analysis with test_main_dir.zip
        analysis_id = make_new_analysis()
 
        #GET resume by analysis_id before generation
        resp_empty = client.get(f"/resumes/{analysis_id}")
        assert resp_empty.status_code == 404
 
        #POST to Generate the resume
        generate_response = client.post(f"/resume/generate/{analysis_id}",params={"resume_title": "Test Resume"})
        assert generate_response.status_code == 201, (f"Resume generation failed: {generate_response.status_code}")
        
        resume_body = generate_response.json()
        assert "resume_id" in resume_body
        resume_id = resume_body["resume_id"]

        #GET by analysis_id should not be 404 this time
        get_resumes_response = client.get(f"/resumes/{analysis_id}")
        assert get_resumes_response.status_code == 200
        resume_ids = [r["resume_id"] for r in get_resumes_response.json()]
        assert resume_id in resume_ids
 
        #GET all resumes
        get_all_resumes_response = client.get("/resumes")
        assert get_all_resumes_response.status_code == 200
        all_ids = [r["resume_id"] for r in get_all_resumes_response.json()]
        assert resume_id in all_ids
        
        #GET by resume_id
        get_resume_response = client.get(f"/resume/{resume_id}")
        assert get_resume_response.status_code == 200
        assert get_resume_response.json()["resume_id"] == resume_id
        
        #Setup for next test
        get_resume_body = get_resume_response.json()
 
        # PUT resumes for editing check
        resume_data = get_resume_body['resume_data']
        resume_data['summary'] = "Edited Resume Summary"
        edited_data = resume_data
        edit_response = client.put(f"/resume/{resume_id}",json={"resume_title": "Edited Resume Title", "resume_data": edited_data})
        assert edit_response.status_code == 204
 
        # Verify the edit persisted
        check_edit_response = client.get(f"/resume/{resume_id}")
        assert check_edit_response.status_code == 200
        assert check_edit_response.json()['resume_title'] == "Edited Resume Title"
 
        #DELETE the new resume
        delete_response = client.delete(f"/resume/{resume_id}")
        assert delete_response.status_code == 204
 
        #Check DELETE
        check_response = client.get(f"/resume/{resume_id}")
        assert check_response.status_code == 404

    def test_portfolio_workflow(self):
        """
        Create new analysis, then generate, edit and delete a portfolio for the new analysis
        
        1. Create a new analysis (extract + commit)
        2. GET /portfolios (empty for this analysis)
        3. POST /portfolio/generate/{analysis_id}     - creates portfolio
        4. GET  /portfolio/{portfolio_id}             - retrieve it
        5. GET  /portfolios/{analysis_id}             - list for analysis
        6. PUT  /portfolio/{portfolio_id}             - edit it
        7. DELETE /portfolio/{portfolio_id}           - delete it
        8. Confirm gone via GET                       - 404
        9. Teardown: delete the analysis
        """

        #Make a new analysis with test_main_dir.zip
        analysis_id = make_new_analysis()
 
        #GET portfolio by analysis_id before generation
        resp_empty = client.get(f"/portfolios/{analysis_id}")
        assert resp_empty.status_code == 404
 
        #POST to Generate the portfolio
        generate_response = client.post(f"/portfolio/generate/{analysis_id}",params={"portfolio_title": "Test Portfolio"})
        assert generate_response.status_code == 201, (f"Portfolio generation failed: {generate_response.status_code}")
        
        portfolio_body = generate_response.json()
        assert "portfolio_id" in portfolio_body
        portfolio_id = portfolio_body["portfolio_id"]

        #GET by analysis_id should not be 404 this time
        get_portfolios_response = client.get(f"/portfolios/{analysis_id}")
        assert get_portfolios_response.status_code == 200
        portfolio_ids = [r["portfolio_id"] for r in get_portfolios_response.json()]
        assert portfolio_id in portfolio_ids
 
        #GET all portfolios
        get_all_portfolios_response = client.get("/portfolios")
        assert get_all_portfolios_response.status_code == 200
        all_ids = [r["portfolio_id"] for r in get_all_portfolios_response.json()]
        assert portfolio_id in all_ids
        
        #GET by portfolio_id
        get_portfolio_response = client.get(f"/portfolio/{portfolio_id}")
        assert get_portfolio_response.status_code == 200
        assert get_portfolio_response.json()["portfolio_id"] == portfolio_id
        
        #Setup for next test
        get_portfolio_body = get_portfolio_response.json()
 
        # PUT portfolios for editing check
        portfolio_data = get_portfolio_body['portfolio_data']
        pprint.pprint(portfolio_data)
        portfolio_data['projects_detail'] = ['Some Detail']
        edited_data = portfolio_data
        edit_response = client.put(f"/portfolio/{portfolio_id}",json={"portfolio_title": "Edited Portfolio Title", "portfolio_data": edited_data})
        assert edit_response.status_code == 204
 
        # Verify the edit persisted
        check_edit_response = client.get(f"/portfolio/{portfolio_id}")
        assert check_edit_response.status_code == 200
        assert check_edit_response.json()['portfolio_title'] == "Edited Portfolio Title"
 
        #DELETE the new portfolio
        delete_response = client.delete(f"/portfolio/{portfolio_id}")
        assert delete_response.status_code == 204
 
        #Check DELETE
        check_response = client.get(f"/portfolio/{portfolio_id}")
        assert check_response.status_code == 404