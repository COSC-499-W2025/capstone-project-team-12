import pytest
import json
import uuid
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

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
def sample_result_id():
    """Fixture providing a sample UUID as string"""
    return str(uuid.uuid4())


@pytest.fixture
def sample_metadata_insights():
    """Fixture providing sample metadata insights as a dictionary."""
    return {
        "basic_stats": {
            "total_files": 10,
            "total_size": 50000,
            "total_lines": 1200,
            "total_words": 8000,
            "total_characters": 50000
        },
        "extension_stats": {
            ".py": {
                "extension": ".py",
                "count": 5,
                "total_size": 25000,
                "avg_size": 5000,
                "category": "Code"
            },
            ".js": {
                "extension": ".js",
                "count": 3,
                "total_size": 15000,
                "avg_size": 5000,
                "category": "Code"
            }
        },
        "skill_stats": {
            "Python": {
                "file_count": 5,
                "total_size": 25000,
                "is_primary": True,
                "category": "Programming Language"
            },
            "JavaScript": {
                "file_count": 3,
                "total_size": 15000,
                "is_primary": False,
                "category": "Programming Language"
            }
        },
        "primary_skills": ["Python", "JavaScript"],
        "date_stats": {
            "by_creation_date": {"2024": 5, "2025": 5},
            "by_modified_date": {"2025": 10},
            "recent_activity_count": 10,
            "activity_level": "high"
        }
    }


class TestDatabaseManagerInit:
    """Tests for DatabaseManager initialization"""
    
    def test_init_creates_db_connector(self, mock_db_connector):
        """Test that __init__ creates a DB_connector instance"""
        db_manager = DatabaseManager()
        assert db_manager.db is not None


class TestCreateNewResult:
    """Tests for create_new_result method."""
    
    def test_create_new_result_success(self, db_manager, mock_db_connector):
        """Test successful creation of a new result"""
        expected_uuid = uuid.uuid4()
        mock_db_connector.execute_update.return_value = {'result_id': expected_uuid}
        
        result_id = db_manager.create_new_result()
        
        assert result_id == str(expected_uuid)
        mock_db_connector.execute_update.assert_called_once()
        call_args = mock_db_connector.execute_update.call_args
        assert 'INSERT INTO Results DEFAULT VALUES' in call_args[0][0]
        assert call_args[1]['returning'] is True
    
    def test_create_new_result_failure(self, db_manager, mock_db_connector):
        """Test handling of failed result creation."""
        mock_db_connector.execute_update.return_value = None
        
        with pytest.raises(Exception, match="Failed to generate result_id"):
            db_manager.create_new_result()
    
    def test_create_new_result_database_error(self, db_manager, mock_db_connector):
        """Test handling of database errors during result creation."""
        mock_db_connector.execute_update.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception, match="Database connection failed"):
            db_manager.create_new_result()


class TestSaveMetadataAnalysis:
    """Tests for save_metadata_analysis method."""
    
    def test_save_metadata_analysis_success(self, db_manager, mock_db_connector, sample_result_id, sample_metadata_insights):
        """Test successful saving of metadata analysis."""
        mock_db_connector.execute_update.return_value = None
        
        result = db_manager.save_metadata_analysis(sample_result_id, sample_metadata_insights)
        
        assert result is True
        mock_db_connector.execute_update.assert_called_once()
        call_args = mock_db_connector.execute_update.call_args
        assert 'UPDATE Results' in call_args[0][0]
        assert 'SET metadata_insights' in call_args[0][0]
        
        #Verify JSON structure
        json_data = json.loads(call_args[0][1][0])
        assert 'basic_stats' in json_data
        assert 'extension_stats' in json_data
        assert 'skill_stats' in json_data
        assert 'primary_skills' in json_data
        assert 'date_stats' in json_data
    
    def test_save_metadata_analysis_with_empty_data(self, db_manager, mock_db_connector, sample_result_id):
        """Test saving metadata analysis with empty collections."""
        empty_insights = {
            "basic_stats": {},
            "extension_stats": {},
            "skill_stats": {},
            "primary_skills": [],
            "date_stats": {}
        }
        mock_db_connector.execute_update.return_value = None
        
        result = db_manager.save_metadata_analysis(sample_result_id, empty_insights)
        
        assert result is True
        call_args = mock_db_connector.execute_update.call_args
        json_data = json.loads(call_args[0][1][0])
        assert json_data['extension_stats'] == {}
        assert json_data['primary_skills'] == []
    
    def test_save_metadata_analysis_database_error(self, db_manager, mock_db_connector, sample_result_id, sample_metadata_insights):
        """Test handling of database errors during metadata save."""
        mock_db_connector.execute_update.side_effect = Exception("Database error")
        
        result = db_manager.save_metadata_analysis(sample_result_id, sample_metadata_insights)
        
        assert result is False


class TestSaveTextAnalysis:
    """Tests for save_text_analysis method"""
    
    def test_save_text_analysis_success(self, db_manager, mock_db_connector, sample_result_id):
        """Test successful saving of text analysis"""
        doc_vectors = [[0.8, 0.2], [0.1, 0.9]]
        topic_vectors = [[("tech", 0.9), ("web", 0.1)], [("data", 0.85), ("science", 0.15)]]
        mock_db_connector.execute_update.return_value = None
        
        result = db_manager.save_text_analysis(sample_result_id, doc_vectors, topic_vectors)
        
        assert result is True
        mock_db_connector.execute_update.assert_called_once()
        call_args = mock_db_connector.execute_update.call_args
        assert 'UPDATE Results' in call_args[0][0]
        assert 'SET topic_vector' in call_args[0][0]
        
        json_data = json.loads(call_args[0][1][0])
        assert json_data['doc_topic_vectors'] == doc_vectors
        expected_topic_vectors = [
            [list(term) for term in topic] 
            for topic in topic_vectors
        ]
        assert json_data['topic_term_vectors'] == expected_topic_vectors
    
    def test_save_text_analysis_empty_vectors(self, db_manager, mock_db_connector, sample_result_id):
        """Test saving text analysis with empty vectors"""
        mock_db_connector.execute_update.return_value = None
        
        result = db_manager.save_text_analysis(sample_result_id, [], [])
        
        assert result is True
        call_args = mock_db_connector.execute_update.call_args
        json_data = json.loads(call_args[0][1][0])
        assert json_data['doc_topic_vectors'] == []
        assert json_data['topic_term_vectors'] == []


class TestSaveResumePoints:
    """Tests for save_resume_points method"""
    
    def test_save_resume_points_success(self, db_manager, mock_db_connector, sample_result_id):
        """Test successful saving of resume points"""
        points = ["Developed full-stack applications", "Managed PostgreSQL databases"]
        mock_db_connector.execute_update.return_value = None
        
        result = db_manager.save_resume_points(sample_result_id, points)
        
        assert result is True
        call_args = mock_db_connector.execute_update.call_args
        assert 'UPDATE Results' in call_args[0][0]
        assert 'SET resume_points' in call_args[0][0]
        assert json.loads(call_args[0][1][0]) == points
    
    def test_save_resume_points_empty_list(self, db_manager, mock_db_connector, sample_result_id):
        """Test saving empty resume points list"""
        mock_db_connector.execute_update.return_value = None
        
        result = db_manager.save_resume_points(sample_result_id, [])
        
        assert result is True
        call_args = mock_db_connector.execute_update.call_args
        assert json.loads(call_args[0][1][0]) == []


class TestSavePackageAnalysis:
    """Tests for save_package_analysis method"""
    
    def test_save_package_analysis_success(self, db_manager, mock_db_connector, sample_result_id):
        """Test successful saving of package analysis"""
        insights = {"npm": {"react": "18.2.0"}, "pip": {"fastapi": "0.104.1"}}
        mock_db_connector.execute_update.return_value = None
        
        result = db_manager.save_package_analysis(sample_result_id, insights)
        
        assert result is True
        call_args = mock_db_connector.execute_update.call_args
        assert 'UPDATE Results' in call_args[0][0]
        assert 'SET package_insights' in call_args[0][0]
        assert json.loads(call_args[0][1][0]) == insights
    
    def test_save_package_analysis_empty_dict(self, db_manager, mock_db_connector, sample_result_id):
        """Test saving empty package analysis"""
        mock_db_connector.execute_update.return_value = None
        
        result = db_manager.save_package_analysis(sample_result_id, {})
        
        assert result is True
        call_args = mock_db_connector.execute_update.call_args
        assert json.loads(call_args[0][1][0]) == {}


class TestSaveRepositoryAnalysis:
    """Tests for save_repository_analysis method"""
    
    def test_save_repository_analysis_success(self, db_manager, mock_db_connector, sample_result_id):
        """Test successful saving of repository analysis"""
        repos = {"repo1": {"commits": 50, "contributors": 3}}
        timeline = [{"project": "test_project", "date": "2024-01-01"}]
        mock_db_connector.execute_update.return_value = None
        
        result = db_manager.save_repository_analysis(sample_result_id, repos, timeline)
        
        assert result is True
        call_args = mock_db_connector.execute_update.call_args
        assert 'UPDATE Results' in call_args[0][0]
        assert 'SET project_insights' in call_args[0][0]
        
        json_data = json.loads(call_args[0][1][0])
        assert json_data['repositories'] == repos
        assert json_data['timeline'] == timeline
        assert json_data['total_projects'] == 1
    
    def test_save_repository_analysis_empty_timeline(self, db_manager, mock_db_connector, sample_result_id):
        """Test saving repository analysis with empty timeline"""
        mock_db_connector.execute_update.return_value = None
        
        result = db_manager.save_repository_analysis(sample_result_id, {}, [])
        
        assert result is True
        call_args = mock_db_connector.execute_update.call_args
        json_data = json.loads(call_args[0][1][0])
        assert json_data['total_projects'] == 0


class TestSaveTrackedData:
    """Tests for save_tracked_data method"""
    
    def test_save_tracked_data_all_fields(self, db_manager, mock_db_connector, sample_result_id):
        """Test saving tracked data with all fields"""
        metadata = {"file1.py": {"size": 1024, "lines": 50}}
        bow_cache = [["word1", "word2"], ["word3"]]
        project_data = {"commits": [{"hash": "abc", "msg": "Initial"}]}
        package_data = {"package.json": "content"}
        mock_db_connector.execute_update.return_value = None
        
        result = db_manager.save_tracked_data(
            sample_result_id, metadata, bow_cache, project_data, package_data
        )
        
        assert result is True
        call_args = mock_db_connector.execute_update.call_args
        assert 'INSERT INTO Tracked_Data' in call_args[0][0]
        
        #Verify all parameters are passed correctly
        params = call_args[0][1]
        assert isinstance(params[0], uuid.UUID)
        assert json.loads(params[1]) == metadata
        assert json.loads(params[2]) == bow_cache
        assert json.loads(params[3]) == project_data
        assert json.loads(params[4]) == package_data
    
    def test_save_tracked_data_empty_collections(self, db_manager, mock_db_connector, sample_result_id):
        """Test that empty collections are stored as JSON, not NULL"""
        metadata = {"file1.py": {"size": 1024}}
        mock_db_connector.execute_update.return_value = None
        
        result = db_manager.save_tracked_data(
            sample_result_id, metadata, bow_cache=[], project_data={}, package_data={}
        )
        
        assert result is True
        call_args = mock_db_connector.execute_update.call_args
        params = call_args[0][1]
        
        #empty collections should be JSON strings, not None
        assert params[2] == '[]'  #bow_cache
        assert params[3] == '{}'  #project_data
        assert params[4] == '{}'  #package_data
    
    def test_save_tracked_data_none_optionals(self, db_manager, mock_db_connector, sample_result_id):
        """Test that None values are stored as NULL"""
        metadata = {"file1.py": {"size": 1024}}
        mock_db_connector.execute_update.return_value = None
        
        result = db_manager.save_tracked_data(
            sample_result_id, metadata, bow_cache=None, project_data=None, package_data=None
        )
        
        assert result is True
        call_args = mock_db_connector.execute_update.call_args
        params = call_args[0][1]
        
        #None values should remain None (NULL in DB)
        assert params[2] is None  #bow_cache
        assert params[3] is None  #project_data
        assert params[4] is None  #package_data


class TestGetResultById:
    """Tests for get_result_by_id method"""
    
    def test_get_result_by_id_success(self, db_manager, mock_db_connector, sample_result_id):
        """Test successful retrieval of result by ID"""
        mock_row = {
            'result_id': uuid.UUID(sample_result_id),
            'topic_vector': {'doc_topic_vectors': [[0.5, 0.5]]},
            'resume_points': ['Point 1', 'Point 2'],
            'project_insights': {'total_projects': 1},
            'package_insights': {'npm': {'react': '18.0.0'}},
            'metadata_insights': {'basic_stats': {}},
            'bow_cache': [['word1']],
            'project_data': {'commits': []},
            'package_data': {'package.json': 'data'},
            'metadata_stats': {'file1.py': {}}
        }
        mock_db_connector.execute_query.return_value = [mock_row]
        
        result = db_manager.get_result_by_id(sample_result_id)
        
        assert result is not None
        assert result['result_id'] == sample_result_id
        assert 'tracked_data' in result
        assert result['tracked_data']['bow_cache'] == [['word1']]
        mock_db_connector.execute_query.assert_called_once()
    
    def test_get_result_by_id_not_found(self, db_manager, mock_db_connector, sample_result_id):
        """Test retrieval of non-existent result"""
        mock_db_connector.execute_query.return_value = []
        
        result = db_manager.get_result_by_id(sample_result_id)
        
        assert result is None
    
    def test_get_result_by_id_database_error(self, db_manager, mock_db_connector, sample_result_id):
        """Test handling of database errors during retrieval"""
        mock_db_connector.execute_query.side_effect = Exception("Database error")
        
        result = db_manager.get_result_by_id(sample_result_id)
        
        assert result is None


class TestGetAllResultsSummary:
    """Tests for get_all_results_summary method"""
    
    def test_get_all_results_summary_success(self, db_manager, mock_db_connector):
        """Test successful retrieval of all results summary"""
        mock_results = [
            {'result_id': uuid.uuid4(), 'metadata_insights': {'stats': 'data1'}},
            {'result_id': uuid.uuid4(), 'metadata_insights': {'stats': 'data2'}}
        ]
        mock_db_connector.execute_query.return_value = mock_results
        
        results = db_manager.get_all_results_summary()
        
        assert len(results) == 2
        assert all(isinstance(r['result_id'], str) for r in results)
        mock_db_connector.execute_query.assert_called_once()
    
    def test_get_all_results_summary_empty(self, db_manager, mock_db_connector):
        """Test retrieval when no results exist"""
        mock_db_connector.execute_query.return_value = []
        
        results = db_manager.get_all_results_summary()
        
        assert results == []
    
    def test_get_all_results_summary_database_error(self, db_manager, mock_db_connector):
        """Test handling of database errors during summary retrieval"""
        mock_db_connector.execute_query.side_effect = Exception("Database error")
        
        results = db_manager.get_all_results_summary()
        
        assert results == []


class TestDeleteResult:
    """Tests for delete_result method"""
    
    def test_delete_result_success(self, db_manager, mock_db_connector, sample_result_id):
        """Test successful deletion of a result"""
        mock_db_connector.execute_update.return_value = None
        
        result = db_manager.delete_result(sample_result_id)
        
        assert result is True
        assert mock_db_connector.execute_update.call_count == 2
        
        #Verify correct order - >  Tracked_Data first, then Results
        calls = mock_db_connector.execute_update.call_args_list
        assert 'DELETE FROM Tracked_Data' in calls[0][0][0]
        assert 'DELETE FROM Results' in calls[1][0][0]
    
    def test_delete_result_database_error(self, db_manager, mock_db_connector, sample_result_id):
        """Test handling of database errors during deletion"""
        mock_db_connector.execute_update.side_effect = Exception("Database error")
        
        result = db_manager.delete_result(sample_result_id)
        
        assert result is False


class TestWipeAllData:
    """Tests for wipe_all_data method"""
    
    def test_wipe_all_data_success(self, db_manager, mock_db_connector):
        """Test successful wiping of all data"""
        mock_db_connector.execute_update.return_value = None
        
        result = db_manager.wipe_all_data()
        
        assert result is True
        mock_db_connector.execute_update.assert_called_once()
        call_args = mock_db_connector.execute_update.call_args
        assert 'TRUNCATE TABLE Results, Tracked_Data' in call_args[0][0]
        assert 'RESTART IDENTITY CASCADE' in call_args[0][0]
    
    def test_wipe_all_data_database_error(self, db_manager, mock_db_connector):
        """Test handling of database errors during wipe"""
        mock_db_connector.execute_update.side_effect = Exception("Database error")
        
        result = db_manager.wipe_all_data()
        
        assert result is False


class TestClose:
    """Tests for close method"""
    
    def test_close_no_error(self, db_manager):
        """Test that close method executes without error"""
        db_manager.close()
        assert True

#holymoly, sorry for whoevers reviewing this haha