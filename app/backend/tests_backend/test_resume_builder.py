import pytest
from resume_builder import ResumeBuilder


class TestResumeBuilder:
    
    @pytest.fixture
    def mock_cli(self, mocker):
        """Create a mock CLI interface"""
        cli = mocker.Mock()
        return cli
    
    @pytest.fixture
    def mock_db_manager(self, mocker):
        """Create a mock DatabaseManager"""
        return mocker.Mock()
    
    @pytest.fixture
    def sample_result_data(self):
        """Create sample result data for testing"""
        return {
            'resume_points': 'Experienced developer with expertise in Python and web technologies',
            'metadata_insights': {
                'primary_skills': ['Python', 'JavaScript', 'Docker'],
                'language_stats': {
                    'Python': {'language': 'Python', 'file_count': 15},
                    'JavaScript': {'language': 'JavaScript', 'file_count': 8},
                    'Java': {'language': 'Java', 'file_count': 3}
                }
            },
            'project_insights': {
                'analyzed_insights': [
                    {
                        'repository_name': 'Web App',
                        'dates': {'start_date': '2024-01-15T10:00:00', 'end_date': '2024-06-20T14:30:00'},
                        'statistics': {},
                        'collaboration_insights': {},
                        'user_role': {'blurb': 'Led development of backend services'},
                        'imports_summary': {
                            'flask': {'frequency': 25},
                            'sqlalchemy': {'frequency': 18},
                            'pytest': {'frequency': 12}
                        }
                    }
                ]
            }
        }
    
    def test_create_resume_from_result_id_success(self, mock_db_manager, mock_cli, sample_result_data):
        """Test successful resume creation from result ID"""
        builder = ResumeBuilder()
        mock_db_manager.get_analysis_data.return_value = sample_result_data
        
        resume = builder.create_resume_from_result_id(mock_db_manager, mock_cli, 'test-result-id')
        
        assert resume is not None
        assert 'resume_id' in resume
        assert 'result_id' in resume
        assert resume['result_id'] == 'test-result-id'
        assert 'summary' in resume
        assert 'projects' in resume
        assert 'skills' in resume
        assert 'languages' in resume
        mock_cli.print_status.assert_any_call("Resume generated successfully!", "success")
    
    def test_create_resume_result_not_found(self, mock_db_manager, mock_cli):
        """Test handling when result is not found in database"""
        builder = ResumeBuilder()
        mock_db_manager.get_analysis_data.return_value = None
        
        resume = builder.create_resume_from_result_id(mock_db_manager, mock_cli, 'invalid-id')
        
        assert resume is None
        mock_cli.print_status.assert_called_with("Result not found in database.", "error")
    
    def test_create_resume_empty_content(self, mock_db_manager, mock_cli):
        """Test handling when generated resume has no content"""
        builder = ResumeBuilder()
        empty_data = {
            'resume_points': None,
            'metadata_insights': {},
            'project_insights': {}
        }
        mock_db_manager.get_analysis_data.return_value = empty_data
        
        resume = builder.create_resume_from_result_id(mock_db_manager, mock_cli, 'test-id')
        
        assert resume is None
        mock_cli.print_status.assert_called_with(
            "Generated resume is empty. Cannot save or display.", "error"
        )
    
    def test_create_resume_handles_exception(self, mock_db_manager, mock_cli):
        """Test error handling during resume creation"""
        builder = ResumeBuilder()
        mock_db_manager.get_analysis_data.side_effect = Exception("Database error")
        
        resume = builder.create_resume_from_result_id(mock_db_manager, mock_cli, 'test-id')
        
        assert resume is None
        assert mock_cli.print_status.call_count > 0
    
    def test_build_resume_structure(self, sample_result_data):
        """Test internal resume building creates correct structure"""
        builder = ResumeBuilder()
        
        resume = builder._build_resume(sample_result_data, 'test-result-id')
        
        assert resume['result_id'] == 'test-result-id'
        assert isinstance(resume['resume_id'], str)
        assert len(resume['resume_id']) > 0
        assert resume['summary'] == sample_result_data['resume_points']
        assert len(resume['skills']) == 3
        assert len(resume['projects']) > 0
    
    def test_build_resume_handles_invalid_data(self):
        """Test _build_resume handles invalid data gracefully"""
        builder = ResumeBuilder()
        invalid_data = {'invalid': 'structure'}
        
        resume = builder._build_resume(invalid_data, 'test-id')
        
        assert resume['result_id'] == 'test-id'
        assert isinstance(resume['resume_id'], str)
        assert resume['summary'] is None
        assert resume['projects'] == []
        assert resume['skills'] == []
        assert resume['languages'] == []
    
    def test_display_resume_with_cli(self, sample_result_data, mocker, capsys):
        """Test resume display with CLI interface"""
        builder = ResumeBuilder()
        resume = builder._build_resume(sample_result_data, 'test-id')
        mock_cli = mocker.Mock()
        
        builder.display_resume(resume, cli=mock_cli)
        
        captured = capsys.readouterr()
        assert 'Resume ID:' in captured.out
        assert 'SUMMARY' in captured.out
        assert 'PROJECTS' in captured.out
        assert 'SKILLS' in captured.out
    
    def test_display_resume_with_error(self, mocker, capsys):
        """Test display_resume handles errors"""
        builder = ResumeBuilder()
        invalid_resume = None
        mock_cli = mocker.Mock()
        
        builder.display_resume(invalid_resume, cli=mock_cli)
        
        mock_cli.print_status.assert_called()
        assert 'error' in str(mock_cli.print_status.call_args).lower()