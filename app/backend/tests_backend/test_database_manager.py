import pytest
import json
import uuid
from unittest.mock import Mock, patch, call
from database_manager import DatabaseManager

@pytest.fixture
def mock_db_connector():
    """Fixture to create a mock DB_connector."""
    with patch('database_manager.DB_connector') as mock_connector:
        mock_instance = Mock()
        mock_connector.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def db_manager(mock_db_connector):
    """Fixture to create a DatabaseManager instance with mocked DB_connector"""
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
    """Tests for create_analyses method (formerly create_new_result)."""
    
    def test_create_analyses_success(self, db_manager, mock_db_connector):
        """Test successful creation of analysis and child records."""
        expected_uuid = uuid.uuid4()
        # Mock the first return (Analyses insert)
        mock_db_connector.execute_update.side_effect = [
            {'analysis_id': expected_uuid}, # Return from Analyses insert
            None, # Results insert
            None, # Tracked_Data insert
            None, # Resumes insert
            None  # Portfolios insert
        ]
        
        analysis_id = db_manager.create_analyses()
        
        assert analysis_id == str(expected_uuid)
        
        # Should call execute_update 5 times (1 parent + 4 children)
        assert mock_db_connector.execute_update.call_count == 5
        
        # Verify specific calls
        calls = mock_db_connector.execute_update.call_args_list
        assert 'INSERT INTO Analyses' in calls[0][0][0]
        assert 'INSERT INTO Results' in calls[1][0][0]
        assert 'INSERT INTO Tracked_Data' in calls[2][0][0]
        assert 'INSERT INTO Resumes' in calls[3][0][0]
        assert 'INSERT INTO Portfolios' in calls[4][0][0]

    def test_create_analyses_failure(self, db_manager, mock_db_connector):
        """Test handling failure when generating ID."""
        mock_db_connector.execute_update.return_value = None
        
        with pytest.raises(Exception, match="Failed to generate analysis_id"):
            db_manager.create_analyses()

class TestSaveFileset:
    """Tests for new save_fileset method."""
    
    def test_save_fileset_insert_new(self, db_manager, mock_db_connector, sample_analysis_id):
        """Test inserting a new fileset."""
        # Mock check_query returning empty (no existing fileset)
        # Then insert returns ID
        mock_db_connector.execute_query.return_value = [] 
        mock_db_connector.execute_update.side_effect = [
            {'fileset_id': 1}, # Insert Fileset
            None               # Insert Filetree
        ]
        
        tree = {"name": "root"}
        binary = b"fake_zip_content"
        
        result = db_manager.save_fileset(sample_analysis_id, binary, tree)
        
        assert result is True
        assert 'INSERT INTO Filesets' in mock_db_connector.execute_update.call_args_list[0][0][0]
        assert 'INSERT INTO Filetrees' in mock_db_connector.execute_update.call_args_list[1][0][0]

    def test_save_fileset_update_existing(self, db_manager, mock_db_connector, sample_analysis_id):
        """Test updating an existing fileset."""
        # Mock check_query returning existing fileset_id
        mock_db_connector.execute_query.return_value = [{'fileset_id': 55}]
        
        tree = {"name": "root"}
        binary = b"new_zip_content"
        
        result = db_manager.save_fileset(sample_analysis_id, binary, tree)
        
        assert result is True
        
        calls = mock_db_connector.execute_update.call_args_list
        # Should be UPDATE Filesets, then INSERT Filetrees
        assert 'UPDATE Filesets' in calls[0][0][0]
        assert 'INSERT INTO Filetrees' in calls[1][0][0]

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
        
        result = db_manager.save_resume_data(sample_analysis_id, resume_data)
        
        assert result is True
        call_args = mock_db_connector.execute_update.call_args
        assert 'UPDATE Resumes' in call_args[0][0]
        assert 'SET summary' in call_args[0][0]

class TestGetAnalysisData:
    """Tests for get_analysis_data (formerly get_result_by_id)."""
    
    def test_get_analysis_data_success(self, db_manager, mock_db_connector, sample_analysis_id):
        mock_row = {
            'analysis_id': uuid.UUID(sample_analysis_id),
            'topic_vector': {},
            'resume_points': [],
            'project_insights': {},
            'package_insights': {},
            'metadata_insights': {},
            'bow_cache': [],
            'project_data': {},
            'package_data': {},
            'metadata_stats': {},
            'resume_summary': "Summary",
            'full_resume': "Full",
            'resume_projects': [],
            'resume_skills': []
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
        assert mock_db_connector.execute_update.call_count == 7
        
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
        assert 'UPDATE Results SET thumbnail_image' in call_args[0][0]