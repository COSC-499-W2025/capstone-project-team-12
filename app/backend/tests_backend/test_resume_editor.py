import pytest
from unittest.mock import patch
from resume_editor import ResumeEditor


class TestResumeEditor:
    
    @pytest.fixture
    def mock_cli(self, mocker):
        """Create a mock CLI interface"""
        return mocker.Mock()
    
    @pytest.fixture
    def sample_resume(self):
        """Create sample resume data for testing"""
        return {
            'summary': 'Experienced developer with expertise in Python',
            'skills': ['Python', 'JavaScript', 'Docker'],
            'languages': [
                {'name': 'Python', 'file_count': 15},
                {'name': 'JavaScript', 'file_count': 8}
            ],
            'projects': [
                {
                    'name': 'Web App',
                    'date_range': 'Jan 2024 - Jun 2024',
                    'frameworks': ['Flask', 'SQLAlchemy'],
                    'collaboration': 'Led backend development'
                }
            ]
        }
    
    # ========== Helper Method Tests ==========
    
    def test_edit_text_field_single_line(self, mock_cli):
        """Test single-line text field editing"""
        editor = ResumeEditor(mock_cli)
        
        with patch('resume_editor.prompt', return_value='New value'):
            result = editor._edit_text_field("Name", "Old value", allow_multiline=False)
            assert result == 'New value'
        
        # Test cancellation with KeyboardInterrupt
        with patch('resume_editor.prompt', side_effect=KeyboardInterrupt):
            result = editor._edit_text_field("Name", "Old value", allow_multiline=False)
            assert result == 'Old value'
    
    def test_edit_text_field_multiline_edit(self, mock_cli):
        """Test multiline text field editing with edit option"""
        editor = ResumeEditor(mock_cli)
        mock_cli.get_input.return_value = 'e'
        
        with patch('resume_editor.prompt', return_value='Updated text'):
            result = editor._edit_text_field("Summary", "Old summary", allow_multiline=True)
            assert result == 'Updated text'
        
        # Test edit cancellation
        mock_cli.get_input.return_value = 'e'
        with patch('resume_editor.prompt', side_effect=KeyboardInterrupt):
            result = editor._edit_text_field("Summary", "Old summary", allow_multiline=True)
            assert result == 'Old summary'
    
    def test_edit_text_field_multiline_replace(self, mock_cli):
        """Test multiline text field replacement"""
        editor = ResumeEditor(mock_cli)
        mock_cli.get_input.return_value = 'r'
        
        with patch('resume_editor.prompt', return_value='Completely new text'):
            result = editor._edit_text_field("Summary", "Old summary", allow_multiline=True)
            assert result == 'Completely new text'
        
        # Test replace cancellation
        mock_cli.get_input.return_value = 'r'
        with patch('resume_editor.prompt', side_effect=KeyboardInterrupt):
            result = editor._edit_text_field("Summary", "Old summary", allow_multiline=True)
            assert result == 'Old summary'
    
    def test_edit_text_field_multiline_keep(self, mock_cli):
        """Test keeping current multiline text"""
        editor = ResumeEditor(mock_cli)
        
        # Empty input keeps current
        mock_cli.get_input.return_value = ''
        result = editor._edit_text_field("Summary", "Old summary", allow_multiline=True)
        assert result == 'Old summary'
        
        # Invalid option keeps current
        mock_cli.get_input.return_value = 'x'
        result = editor._edit_text_field("Summary", "Old summary", allow_multiline=True)
        assert result == 'Old summary'
    
    def test_edit_list_field_add_items(self, mock_cli):
        """Test adding items to a list"""
        editor = ResumeEditor(mock_cli)
        
        mock_cli.get_input.side_effect = ['React', 'TypeScript', 'done']
        result = editor._edit_list_field("Skills", ['Python'])
        assert 'React' in result and 'TypeScript' in result
        assert len(result) == 3
    
    def test_edit_list_field_remove_items_case_insensitive(self, mock_cli):
        """Test case-insensitive item removal"""
        editor = ResumeEditor(mock_cli)
        
        # Remove with different case
        mock_cli.get_input.side_effect = ['python', 'y', 'done']
        result = editor._edit_list_field("Skills", ['Python', 'JavaScript'])
        assert 'Python' not in result
        assert 'JavaScript' in result
        
        # Cancel removal
        mock_cli.get_input.side_effect = ['python', 'n', 'done']
        result = editor._edit_list_field("Skills", ['Python', 'JavaScript'])
        assert 'Python' in result
    
    def test_edit_list_field_empty_input(self, mock_cli):
        """Test that empty strings are not added to list"""
        editor = ResumeEditor(mock_cli)
        
        mock_cli.get_input.side_effect = ['', '  ', 'done']
        result = editor._edit_list_field("Skills", ['Python'])
        assert '' not in result
        assert '  ' not in result
        assert len(result) == 1
    
    def test_validate_date_range_valid_formats(self):
        """Test valid date range formats"""
        editor = ResumeEditor(None)
        
        assert editor._validate_date_range('Jan 2020 - Dec 2021')
        assert editor._validate_date_range('Feb 2019 - Present')
        assert editor._validate_date_range('Mar 2020 - present')  # case insensitive
        assert editor._validate_date_range('Apr 2020  -  May 2021')  # extra spaces
    
    def test_validate_date_range_invalid_formats(self):
        """Test invalid date range formats"""
        editor = ResumeEditor(None)
        
        assert not editor._validate_date_range('Invalid')  # no dash
        assert not editor._validate_date_range('2020-2021')  # wrong format
        assert not editor._validate_date_range('January 2020 - December 2021')  # full month name
        assert not editor._validate_date_range('13 2020 - Dec 2021')  # invalid month number
        assert not editor._validate_date_range('Abc 2020 - Dec 2021')  # invalid month abbreviation
        assert not editor._validate_date_range('Jan 1800 - Dec 2021')  # year too old
        assert not editor._validate_date_range('Jan 2020 - Dec 2200')  # year too far future
        assert not editor._validate_date_range('')  # empty string
    
    # ========== Updated Original Tests ==========
    
    def test_edit_summary(self, mock_cli):
        """Test summary editing"""
        editor = ResumeEditor(mock_cli)
        mock_cli.get_input.return_value = 'e'
        
        with patch('resume_editor.prompt', return_value='New summary'):
            result = editor._edit_summary('Old summary')
            assert result == 'New summary'
    
    def test_edit_skills(self, mock_cli):
        """Test skills add and remove"""
        editor = ResumeEditor(mock_cli)
        
        # Add skill
        mock_cli.get_input.side_effect = ['React', 'done']
        result = editor._edit_skills(['Python', 'JavaScript'])
        assert 'React' in result
        
        # Remove skill (case-insensitive)
        mock_cli.get_input.side_effect = ['python', 'y', 'done']
        result = editor._edit_skills(['Python', 'JavaScript'])
        assert 'Python' not in result
    
    def test_edit_languages(self, mock_cli):
        """Test languages add and remove with file_count preservation"""
        editor = ResumeEditor(mock_cli)
        languages = [{'name': 'Python', 'file_count': 15}, {'name': 'JavaScript', 'file_count': 8}]
        
        # Add new language
        mock_cli.get_input.side_effect = ['TypeScript', 'done']
        result = editor._edit_languages(languages.copy())
        assert len(result) == 3
        assert any(lang['name'] == 'TypeScript' and lang['file_count'] == 0 for lang in result)
        
        # Remove language preserves file_count for kept languages
        mock_cli.get_input.side_effect = ['javascript', 'y', 'done']
        result = editor._edit_languages(languages.copy())
        assert len(result) == 1
        assert result[0]['name'] == 'Python' and result[0]['file_count'] == 15
    
    def test_edit_single_project_name_and_collaboration(self, mock_cli):
        """Test editing project name and collaboration"""
        editor = ResumeEditor(mock_cli)
        project = {'name': 'Old Name', 'collaboration': 'Old collab', 'frameworks': []}
        
        with patch('resume_editor.prompt', return_value='New Name'):
            mock_cli.get_input.side_effect = ['n', 'q']
            result = editor._edit_single_project(project.copy())
            assert result['name'] == 'New Name'
        
        with patch('resume_editor.prompt', return_value='New collab'):
            mock_cli.get_input.side_effect = ['c', 'q']
            result = editor._edit_single_project(project.copy())
            assert result['collaboration'] == 'New collab'
    
    def test_edit_single_project_date_validation(self, mock_cli):
        """Test date range validation in project editing"""
        editor = ResumeEditor(mock_cli)
        project = {'name': 'Project', 'date_range': 'Jan 2024 - Jun 2024', 'frameworks': []}
        
        # Valid date change
        with patch('resume_editor.prompt', return_value='Feb 2024 - Aug 2024'):
            mock_cli.get_input.side_effect = ['d', 'q']
            result = editor._edit_single_project(project.copy())
            assert result['date_range'] == 'Feb 2024 - Aug 2024'
        
        # Invalid date rejected, keeps retrying until valid or cancelled
        with patch('resume_editor.prompt', side_effect=['Invalid', 'Jan 2024 - Jun 2024']):
            mock_cli.get_input.side_effect = ['d', 'q']
            result = editor._edit_single_project(project.copy())
            assert result['date_range'] == 'Jan 2024 - Jun 2024'
    
    def test_edit_single_project_frameworks(self, mock_cli):
        """Test framework editing with case-insensitive handling"""
        editor = ResumeEditor(mock_cli)
        project = {'name': 'Project', 'frameworks': ['Flask', 'SQLAlchemy']}
        
        # Add framework
        mock_cli.get_input.side_effect = ['f', 'Pytest', 'done', 'q']
        result = editor._edit_single_project(project.copy())
        assert 'Pytest' in result['frameworks']
        
        # Remove framework (case-insensitive)
        mock_cli.get_input.side_effect = ['f', 'flask', 'y', 'done', 'q']
        result = editor._edit_single_project(project.copy())
        assert 'Flask' not in result['frameworks']
    
    def test_edit_projects(self, mock_cli, sample_resume):
        """Test project selection and editing"""
        editor = ResumeEditor(mock_cli)
        
        # Valid selection and edit
        with patch('resume_editor.prompt', return_value='Updated Name'):
            mock_cli.get_input.side_effect = ['1', 'n', 'q', 'done']
            result = editor._edit_projects(sample_resume['projects'].copy())
            assert result[0]['name'] == 'Updated Name'
        
        # Invalid selections
        mock_cli.get_input.side_effect = ['99', 'done']
        result = editor._edit_projects(sample_resume['projects'].copy())
        assert len(result) == 1
        
        # Empty project list
        result = editor._edit_projects([])
        assert result == []
    
    def test_preview_resume(self, mock_cli, sample_resume, capsys):
        """Test resume preview output"""
        editor = ResumeEditor(mock_cli)
        
        editor._preview_resume(sample_resume)
        captured = capsys.readouterr()
        assert 'Summary:' in captured.out
        assert 'Python' in captured.out
        assert 'Web App' in captured.out
    
    def test_edit_resume_main_flow(self, mock_cli, sample_resume):
        """Test main edit menu navigation"""
        editor = ResumeEditor(mock_cli)
        
        # Navigate through menu options
        mock_cli.get_input.side_effect = ['s', 'r', 'd']
        with patch('resume_editor.prompt', return_value='New summary'):
            result = editor.edit_resume(sample_resume.copy())
            assert result['summary'] == 'New summary'
        
        # Invalid option handling
        mock_cli.get_input.side_effect = ['z', 'd']
        editor.edit_resume(sample_resume.copy())
        mock_cli.print_status.assert_any_call(
            "Invalid choice. Please select a valid option.", "warning"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])