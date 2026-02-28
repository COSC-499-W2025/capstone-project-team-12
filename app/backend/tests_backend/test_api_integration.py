import pytest
from fastapi import testclient
from database_manager import DatabaseManager
from db_utils import DB_connector
"""
This Module primarily contains integration tests 
I.e test the real execution of the app when serving the API
The db conn of the api is patched to use our 'test_db' instead.
The 'test_db' is an exact schema copy 
"""

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
def placeholder_UUID():
    return "00000000-0000-0000-0000-000000000000"

@pytest.fixture
def test_db_manager():
    db_manager = DatabaseManager()
    db_manager.db = DB_connector(database_name="test_db")
    return db_manager

#Below is series of helper methods for proper init of 'test_db'

def test_is_using_test_db(test_db_manager):
    """Ensure that the test module is configured to use 'test_db' and not the 'user' db """
    db_manager = test_db_manager
    db_name = db_manager.db.execute_query("SELECT current_database();")[0]['current_database']
    return db_name == 'test_db'

def load_analysis_data(test_db_manager):
    """ Loads a sample analysis result artifact with real test data to the analyses table."""
    # Note this function exists to enable the use of all tests that dont affect the /projects/upload and project/generate endpoints to run when these endpoints fail
    # Is necessary, since if generate or upload fails and ensuing tests fail because of it, it isnt an isolated integration failure but endpoint incompatibility
    # In effect, without this step, this test_module will become a partial E2E test which is NOT the goal for this module.
    # See, test_api_e2e.py for End-to-End testing.

db_manager = test_db_manager


# ---End of helpers---

# This pytest mark means that if the patch to make the system use the test_db is non-functional
# All tests within the class gets skipped (reported as failed in output)
@pytest.mark.skipif(test_is_using_test_db(),reason="Not using 'test_db' check integration test config" )
class APIIntegrationTests:
    
    def test_