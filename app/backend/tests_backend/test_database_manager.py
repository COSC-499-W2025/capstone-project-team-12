import pytest
import json
import uuid
from unittest.mock import Mock, patch, call, MagicMock
from database_manager import DatabaseManager

@pytest.fixture
def mock_db_connector():
    """Fixture to create a mock DB_connector."""
    with patch('database_manager.DB_connector') as mock_connector:
        mock_instance = MagicMock()
        mock_connector.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def db_manager(mock_db_connector):
    """Fixture to create a DatabaseManager instance with mocked DB_connector"""
    db_manager = DatabaseManager()
    db_manager.db = mock_db_connector
    return DatabaseManager()


@pytest.fixture
def sample_analysis_id():
    """Fixture providing a sample UUID as string"""
    return str(uuid.uuid4())

@pytest.fixture
def sample_metadata_insights():
    """Fixture providing sample metadata insights as a dictionary."""
    return {
        "basic_stats": {"total_files": 10},
        "extension_stats": {".py": {"count": 5}},
        "skill_stats": {"Python": {"is_primary": True}},
        "primary_skills": ["Python"],
        "date_stats": {"recent_activity_count": 10}
    }

class TestDatabaseManagerInit:
    def test_init_creates_db_connector(self, mock_db_connector):
        db_manager = DatabaseManager()
        assert db_manager.db is not None

class TestCreateAnalyses:
    def test_create_analyses_success(self, db_manager, mock_db_connector):
        """Test successful creation of analysis and child records."""
        expected_uuid = uuid.uuid4()
        
        # FIX: Wrap the first return value in a LIST []
        mock_db_connector.execute_update.side_effect = [
            [{'analysis_id': expected_uuid}], # <--- Changed from dict to list of dict
            None, # Results insert
            None, # Tracked_Data insert
            None, # Resumes insert
            None  # Portfolios insert
        ]
        
        analysis_id = db_manager.create_analysis()
        assert analysis_id == str(expected_uuid)

    def test_create_analyses_failure(self, db_manager, mock_db_connector):
        """Test handling failure when generating ID."""
        mock_db_connector.execute_update.return_value = None
        
        with pytest.raises(Exception, match="Failed to generate analysis_id"):
            db_manager.create_analysis()

def execute_update_sideeffect_func(query,params,returning=False):
    """Helper function for conditional mocking execute update calls in database db_manager"""
    if returning:
        if 'INSERT INTO Filesets' in query:
            return [{'fileset_id': 1}] #When Inserting into Fileset return fileset_id for later use
        if 'UPDATE Filesets SET file_data =' in query:
            return #return none as no value is used in case of existing fileset as fileset_id is retrieved prior to update in query
        if 'INSERT INTO Filetrees' in query:
            return[{'filetree_id' : 125}] # When Inserting into Filetrees return filetree_id so file_set can be updated with appropriate filetree_id
        
        #Last case included for completeness not checked therefore returns None!
        if 'UPDATE Filesets SET file_data_tree_id' in query:
            return 
    else:
        return 1 #if returning param is not set to zero just return one as only one row should be affected in all cases!

class TestSaveFileset:
    """Tests for new save_fileset method."""
    def test_save_fileset_insert_new(self, db_manager, mock_db_connector, sample_analysis_id):
        """Test inserting a new fileset."""
        # Mock check_query returning empty (no existing fileset)
        # Then insert returns ID
        mock_db_connector.execute_query.return_value = [] 
        mock_db_connector.execute_update = MagicMock(side_effect=execute_update_sideeffect_func)
        tree = {"name": "root"}
        binary = b"fake_zip_content"
        
        # FIX: Pass dummy file_path
        result = db_manager.save_fileset(sample_analysis_id, binary, tree, "/tmp/dummy")
        mock_db_connector.execute_query.return_value = []
        assert result is True
        
        assert 'INSERT INTO Filesets' in mock_db_connector.execute_update.call_args_list[0][0][0]
        assert 'INSERT INTO Filetrees' in mock_db_connector.execute_update.call_args_list[1][0][0]
        assert 'UPDATE Filesets' in mock_db_connector.execute_update.call_args_list[2][0][0] #Test for filetree, fileset association

    def test_save_fileset_update_existing(self, db_manager, mock_db_connector, sample_analysis_id):
        """Test updating an existing fileset."""
        # Mock check_query returning existing fileset_id
        mock_db_connector.execute_query.return_value = [{'fileset_id': 55}]
        mock_db_connector.execute_update = MagicMock(side_effect=execute_update_sideeffect_func)
        tree = {"name": "root"}
        binary = b"new_zip_content"
        
        # FIX: Pass dummy file_path
        result = db_manager.save_fileset(sample_analysis_id, binary, tree, "/tmp/dummy")
        
        assert result is True
        
        calls = mock_db_connector.execute_update.call_args_list
        # Should be UPDATE Filesets, then INSERT Filetrees
        assert 'UPDATE Filesets' in calls[0][0][0]
        assert 'INSERT INTO Filetrees' in calls[1][0][0]
        assert 'UPDATE Filesets' in calls[2][0][0] #Test for filetree, fileset association

class TestSaveMetadataAnalysis:
    def test_save_metadata_analysis_success(self, db_manager, mock_db_connector, sample_analysis_id, sample_metadata_insights):
        mock_db_connector.execute_update.return_value = None
        result = db_manager.save_metadata_analysis(sample_analysis_id, sample_metadata_insights)
        
        assert result is True
        call_args = mock_db_connector.execute_update.call_args
        assert 'UPDATE Results' in call_args[0][0]
        assert 'SET metadata_insights' in call_args[0][0]

class TestSaveTrackedData:
    """Tests for save_tracked_data method (now using UPDATE)."""
    
    def test_save_tracked_data_update(self, db_manager, mock_db_connector, sample_analysis_id):
        metadata = {"file1.py": {"size": 1024}}
        
        result = db_manager.save_tracked_data(
            sample_analysis_id, metadata, bow_cache=None
        )
        
        assert result is True
        call_args = mock_db_connector.execute_update.call_args
        # Updated logic checks for UPDATE, not INSERT
        assert 'UPDATE Tracked_Data' in call_args[0][0]
        assert 'COALESCE' in call_args[0][0]

class TestSaveResumeData:
    """Tests for new save_resume_data method."""
    
    def test_save_resume_data_success(self, db_manager, mock_db_connector, sample_analysis_id):
        
        resume_data = {
            "summary": "Experienced Dev",
            "skills": ["Python", "SQL"]
        }
        
        result = db_manager.save_resume(sample_analysis_id, resume_data)
        
        call_args = mock_db_connector.execute_update.call_args
        assert 'INSERT INTO Resumes' in call_args[0][0]
        assert 'VALUES' in call_args[0][0]

def test_resume_handling_successes(db_manager, mock_db_connector):
    mock_db_connector.execute_update.return_value = [{"resume_id": 42}]
    mock_db_connector.execute_query.return_value = [{"resume_id": 42}]

    assert db_manager.save_resume("analysis-1", {"name": "Alice"}, "My Resume") == 42
    assert db_manager.update_resume("resume-1", {"name": "Bob"}) is True
    assert db_manager.get_all_resumes() == [{"resume_id": 42}]
    assert db_manager.get_resumes_by_analysis_id("analysis-1") == [{"resume_id": 42}]
    assert db_manager.get_resume_by_resume_id(42) == [{"resume_id": 42}]


def test_portfolio_handling_successes(db_manager, mock_db_connector):
    mock_db_connector.execute_update.return_value = [{"portfolio_id": 10}]
    mock_db_connector.execute_query.return_value = [{"portfolio_id": 10}]

    assert db_manager.save_portfolio("analysis-1", {"project": "X"}) == 10
    assert db_manager.update_portfolio("port-1", {"project": "Y"}) is True
    assert db_manager.get_all_portfolios() == [{"portfolio_id": 10}]
    assert db_manager.get_portfolios_by_analysis_id("analysis-1") == [{"portfolio_id": 10}]
    assert db_manager.get_portfolio_by_portfolio_id(10) == [{"portfolio_id": 10}]


def test_resume_handling_failures(db_manager, mock_db_connector):
    mock_db_connector.execute_update.side_effect = Exception("Some DB Error")
    mock_db_connector.execute_query.side_effect = Exception("Some DB Error")

    with pytest.raises(RuntimeError):
        db_manager.save_resume("analysis-1", {"name": "Alice"})
    with pytest.raises(RuntimeError):
        db_manager.update_resume("resume-1", {"name": "Bob"})
    with pytest.raises(LookupError):
        db_manager.get_all_resumes()
    with pytest.raises(LookupError):
        db_manager.get_resumes_by_analysis_id("analysis-1")
    with pytest.raises(LookupError):
        db_manager.get_resume_by_resume_id(1)


def test_portfolio_handling_failures(db_manager, mock_db_connector):
    mock_db_connector.execute_update.side_effect = Exception("Some DB Error")
    mock_db_connector.execute_query.side_effect = Exception("Some DB Error")

    with pytest.raises(RuntimeError):
        db_manager.save_portfolio("analysis-1", {"project": "X"})
    # NOTE: bug in source — update_portfolio swallows the exception and returns None
    with pytest.raises(RuntimeError):
        db_manager.update_portfolio("port-1", {"project": "Y"})
    with pytest.raises(LookupError):
        db_manager.get_all_portfolios()
    with pytest.raises(LookupError):
        db_manager.get_portfolios_by_analysis_id("analysis-1")
    with pytest.raises(LookupError):
        db_manager.get_portfolio_by_portfolio_id(1)

class TestGetAnalysisData:
    """Tests for get_analysis_data (formerly get_result_by_id)."""
    
    def test_get_analysis_data_success(self, db_manager, mock_db_connector, sample_analysis_id):
        mock_row = {
            'analysis_id': uuid.UUID(sample_analysis_id),
            'analysis_title': None,
            'topic_vector': {},
            'resume_points': [],
            'project_insights': {},
            'package_insights': {},
            'metadata_insights': {},
            'bow_cache': [],
            'project_data': {},
            'package_data': {},
            'metadata_stats': {},
            'resume_data':{},
            'portfolio_data':{}
        }
        
        mock_db_connector.execute_query.return_value = [mock_row]
        
        result = db_manager.get_analysis_data(sample_analysis_id)
        
        assert result is not None
        assert result['analysis_id'] == sample_analysis_id
        assert 'tracked_data' in result
        
        # Verify JOIN query usage
        call_query = mock_db_connector.execute_query.call_args[0][0]
        assert 'JOIN Results' in call_query
        assert 'JOIN Resumes' in call_query

class TestDeleteAnalysis:
    """Tests for delete_analysis (formerly delete_result)."""
    
    def test_delete_analysis_success(self, db_manager, mock_db_connector, sample_analysis_id):
        mock_db_connector.execute_update.return_value = None
        
        result = db_manager.delete_analysis(sample_analysis_id)
        
        assert result is True
        # Logic deletes Filetrees -> Child Tables (5) -> Parent Table (1)
        # Exact count may vary depending on how you group deletes, but based on code it is 7 calls
        assert mock_db_connector.execute_update.call_count == 1
        
        calls = mock_db_connector.execute_update.call_args_list
        assert 'DELETE FROM Analyses' in calls[-1][0][0] # Last call should be parent

class TestWipeAllData:
    def test_wipe_all_data_success(self, db_manager, mock_db_connector):
        result = db_manager.wipe_all_data()
        
        assert result is True
        call_args = mock_db_connector.execute_update.call_args
        # Verify all new tables are included
        sql = call_args[0][0]
        assert 'Analyses' in sql
        assert 'Filesets' in sql
        assert 'Resumes' in sql
        assert 'Portfolios' in sql

class TestSaveResultThumbnail:
    def test_save_thumbnail_success(self, db_manager, mock_db_connector, sample_analysis_id):
        mock_data = b"image_binary"
        result = db_manager.save_analysis_thumbnail(sample_analysis_id, mock_data)
        
        assert result is True
        call_args = mock_db_connector.execute_update.call_args
        assert 'UPDATE Analyses SET thumbnail_image' in call_args[0][0]

class TestDeleteResume:
    def test_delete_resume_success_calls_correct_sql(self, db_manager, mock_db_connector):
        mock_db_connector.execute_update.return_value = None
        result = db_manager.delete_resume(1)
        assert result is True
        sql = mock_db_connector.execute_update.call_args[0][0]
        assert "DELETE FROM Resumes" in sql
        assert mock_db_connector.execute_update.call_args[0][1] == (1,)

    def test_delete_resume_raises_runtime_error_on_db_failure(self, db_manager, mock_db_connector):
        mock_db_connector.execute_update.side_effect = Exception("constraint violation")
        with pytest.raises(RuntimeError, match="Error deleting resume"):
            db_manager.delete_resume(1)

    def test_delete_resume_does_not_silently_swallow_error(self, db_manager, mock_db_connector):
        """Ensure the error message surfaces the resume_id for traceability."""
        mock_db_connector.execute_update.side_effect = Exception("db error")
        with pytest.raises(RuntimeError) as exc_info:
            db_manager.delete_resume(99)
        assert "99" in str(exc_info.value)


class TestDeletePortfolio:
    def test_delete_portfolio_success_calls_correct_sql(self, db_manager, mock_db_connector):
        mock_db_connector.execute_update.return_value = None
        result = db_manager.delete_portfolio(5)
        assert result is True
        sql = mock_db_connector.execute_update.call_args[0][0]
        assert "DELETE FROM Portfolios" in sql
        assert mock_db_connector.execute_update.call_args[0][1] == (5,)

    def test_delete_portfolio_raises_runtime_error_on_db_failure(self, db_manager, mock_db_connector):
        mock_db_connector.execute_update.side_effect = Exception("foreign key violation")
        with pytest.raises(RuntimeError, match="Error deleting portfolio"):
            db_manager.delete_portfolio(5)

    def test_delete_portfolio_does_not_silently_swallow_error(self, db_manager, mock_db_connector):
        """Ensure the error message surfaces the portfolio_id for traceability."""
        mock_db_connector.execute_update.side_effect = Exception("db error")
        with pytest.raises(RuntimeError) as exc_info:
            db_manager.delete_portfolio(42)
        assert "42" in str(exc_info.value)