import json
import uuid
import pytest
from unittest.mock import MagicMock, patch
from database_manager import DatabaseManager
from display_helpers import display_project_insights, display_project_summary, display_project_timeline


@pytest.fixture
def mock_db_manager():
    """Fixture to provide a DatabaseManager instance with mocked DB."""
    with patch("database_manager.DB_connector") as MockDB:
        mock_db = MockDB.return_value
        mock_db.execute_update.return_value = {"result_id": uuid.uuid4()}
        mock_db.execute_query.return_value = []
        yield DatabaseManager()

@pytest.fixture
def sample_analysis_data():
    """Sample project analysis data for display functions (nested format)."""
    return {
        "analyzed_insights": [
            {
                "repository_name": "repo1",
                "importance_score": 0.95,
                "user_commits": ["commit1", "commit2", "commit3", "commit4", "commit5", 
                 "commit6", "commit7", "commit8", "commit9", "commit10"],
                "statistics": {              
                    "commits": 10,
                    "user_lines_added": 200,
                    "duration_days": 5
                },
                "dates": {                  
                    "start_date": "2025-12-01",
                    "end_date": "2025-12-07"
                },
                "contribution_analysis": {},
                "collaboration_insights": {},
                "testing_insights": {},
                "imports_summary": {}
            },
            {
                "repository_name": "repo2",
                "importance_score": 0.85,
                "user_commits": ["commit3", "commit4", "commit5", "commit6", "commit7"],
                "statistics": {
                    "commits": 5,
                    "user_lines_added": 150,
                    "duration_days": 3
                },
                "dates": {
                    "start_date": "2025-12-02",
                    "end_date": "2025-12-06"
                },
                "contribution_analysis": {},
                "collaboration_insights": {},
                "testing_insights": {},
                "imports_summary": {}
            }
        ],
        "timeline": [
            {
                "name": "repo1",
                "start_date": "2025-12-01",
                "end_date": "2025-12-07"
            },
            {
                "name": "repo2",
                "start_date": "2025-12-02",
                "end_date": "2025-12-06"
            }
        ]
    }



@pytest.fixture
def sample_tracked_data():
    """Sample raw tracked data for save_tracked_data."""
    return {
        "metadata_results": {"repo1": {"files": 10}},
        "bow_cache": [["import", "os"]],
        "project_data": {"repo1": {"commits": 10}},
        "package_data": {"repo1": {"imports": ["numpy"]}}
    }

# Database Tests

def test_save_repository_analysis_success(mock_db_manager, sample_analysis_data):
    """Test that save_repository_analysis stores data correctly."""
    result_id = str(uuid.uuid4())
    success = mock_db_manager.save_repository_analysis(result_id, sample_analysis_data)
    assert success is True
    # check that execute_update was called once
    mock_db_manager.db.execute_update.assert_called_once()
    # check that the data passed was serialized JSON
    args, _ = mock_db_manager.db.execute_update.call_args
    stored_data = json.loads(args[1][0])
    assert stored_data == sample_analysis_data

def test_save_tracked_data_success(mock_db_manager, sample_tracked_data):
    """Test that save_tracked_data stores raw tracked project data correctly."""
    result_id = str(uuid.uuid4())
    success = mock_db_manager.save_tracked_data(
        result_id,
        sample_tracked_data["metadata_results"],
        sample_tracked_data["bow_cache"],
        sample_tracked_data["project_data"],
        sample_tracked_data["package_data"]
    )
    assert success is True
    mock_db_manager.db.execute_update.assert_called_once()
    args, _ = mock_db_manager.db.execute_update.call_args
    # check JSON serialization for each field
    assert json.loads(args[1][0]) == sample_tracked_data["metadata_results"]
    assert json.loads(args[1][1]) == sample_tracked_data["bow_cache"]
    assert json.loads(args[1][2]) == sample_tracked_data["project_data"]
    assert json.loads(args[1][3]) == sample_tracked_data["package_data"]

def test_get_result_by_id_formats_data(mock_db_manager, sample_analysis_data, sample_tracked_data):
    """Test get_result_by_id returns properly formatted data with tracked_data."""
    result_id = str(uuid.uuid4())
    mock_db_manager.db.execute_query.return_value = [{
        "analysis_id": uuid.UUID(result_id), 
        "topic_vector": None,
        "resume_points": None,
        "project_insights": json.dumps(sample_analysis_data),
        "package_insights": None,
        "metadata_insights": None,
        "bow_cache": json.dumps(sample_tracked_data["bow_cache"]),
        "project_data": json.dumps(sample_tracked_data["project_data"]),
        "package_data": json.dumps(sample_tracked_data["package_data"]),
        "metadata_stats": json.dumps(sample_tracked_data["metadata_results"])
    }]

    # FIX: get_result_by_id -> get_analysis_data
    result = mock_db_manager.get_analysis_data(result_id)
    
    assert result["analysis_id"] == result_id
    assert json.loads(result["project_insights"]) == sample_analysis_data
    assert json.loads(result["tracked_data"]["bow_cache"]) == sample_tracked_data["bow_cache"]
    assert json.loads(result["tracked_data"]["project_data"]) == sample_tracked_data["project_data"]
    assert json.loads(result["tracked_data"]["package_data"]) == sample_tracked_data["package_data"]
    assert json.loads(result["tracked_data"]["metadata_stats"]) == sample_tracked_data["metadata_results"]

# Display Helper Tests

def test_display_project_summary_and_insights(capsys, sample_analysis_data):
    display_project_summary(sample_analysis_data["analyzed_insights"], top_n=1)
    captured = capsys.readouterr()
    assert "repo1" in captured.out
    assert "Score: 0.95" in captured.out
    assert "Commits: 10" in captured.out
    assert "Lines Added: 200" in captured.out

def test_display_project_timeline(capsys, sample_analysis_data):
    display_project_timeline(sample_analysis_data["timeline"])
    captured = capsys.readouterr()
    assert "repo1" in captured.out
    assert "2025-12-01 -> 2025-12-07" in captured.out
    assert "repo2" in captured.out
    assert "2025-12-02 -> 2025-12-06" in captured.out

def test_display_project_timeline_no_unknown(capsys, sample_analysis_data):
    # This test case is to catch any "Unknown" repo names in timeline display 
    # which should not happen with valid data
    display_project_timeline(sample_analysis_data["timeline"])
    captured = capsys.readouterr()

    # Verify both repos are displayed correctly
    assert "repo1" in captured.out
    assert "repo2" in captured.out

    assert "Unknown" not in captured.out