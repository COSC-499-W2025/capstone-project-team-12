import pytest
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
    
    def test_edit_summary(self, mock_cli, sample_resume):
        """Test summary editing with new text and keeping current"""
        editor = ResumeEditor(mock_cli)
        
        # Test new text
        mock_cli.get_input.return_value = 'New summary'
        assert editor._edit_summary(sample_resume['summary']) == 'New summary'
        
        # Test keeping current with empty input
        mock_cli.get_input.return_value = ''
        assert editor._edit_summary(sample_resume['summary']) == sample_resume['summary']
    
    def test_edit_skills(self, mock_cli, sample_resume):
        """Test skills add, remove, and case-insensitive operations"""
        editor = ResumeEditor(mock_cli)
        
        # Add new skill
        mock_cli.get_input.side_effect = ['React', 'done']
        result = editor._edit_skills(sample_resume['skills'].copy())
        assert 'React' in result and len(result) == 4
        
        # Remove skill (case-insensitive)
        mock_cli.get_input.side_effect = ['python', 'y', 'done']
        result = editor._edit_skills(sample_resume['skills'].copy())
        assert 'Python' not in result
        
        # Cancel removal
        mock_cli.get_input.side_effect = ['Python', 'n', 'done']
        result = editor._edit_skills(sample_resume['skills'].copy())
        assert 'Python' in result
        
        # Empty input ignored
        mock_cli.get_input.side_effect = ['', 'done']
        result = editor._edit_skills(sample_resume['skills'].copy())
        assert '' not in result and len(result) == 3
    
    def test_edit_languages(self, mock_cli, sample_resume):
        """Test languages add, remove, and case-insensitive operations"""
        editor = ResumeEditor(mock_cli)
        
        # Add new language
        mock_cli.get_input.side_effect = ['TypeScript', 'done']
        result = editor._edit_languages(sample_resume['languages'].copy())
        assert len(result) == 3
        assert any(lang['name'] == 'TypeScript' and lang['file_count'] == 0 for lang in result)
        
        # Remove language (case-insensitive)
        mock_cli.get_input.side_effect = ['javascript', 'y', 'done']
        result = editor._edit_languages(sample_resume['languages'].copy())
        assert not any(lang['name'] == 'JavaScript' for lang in result)
        
        # Empty input ignored
        mock_cli.get_input.side_effect = ['', 'done']
        result = editor._edit_languages(sample_resume['languages'].copy())
        assert len(result) == 2
    
    def test_edit_single_project_basic_fields(self, mock_cli, sample_resume):
        """Test editing project name, date, and collaboration"""
        editor = ResumeEditor(mock_cli)
        project = sample_resume['projects'][0].copy()
        
        # Edit name
        mock_cli.get_input.side_effect = ['n', 'New Name', 'q']
        result = editor._edit_single_project(project.copy())
        assert result['name'] == 'New Name'
        
        # Keep current name with empty input
        mock_cli.get_input.side_effect = ['n', '', 'q']
        result = editor._edit_single_project(project.copy())
        assert result['name'] == 'Web App'
        
        # Edit date range
        mock_cli.get_input.side_effect = ['d', 'Feb 2024 - Aug 2024', 'q']
        result = editor._edit_single_project(project.copy())
        assert result['date_range'] == 'Feb 2024 - Aug 2024'
        
        # Invalid date range (no dash)
        mock_cli.get_input.side_effect = ['d', 'Invalid', 'q']
        result = editor._edit_single_project(project.copy())
        assert result['date_range'] == 'Jan 2024 - Jun 2024'
        
        # Edit collaboration
        mock_cli.get_input.side_effect = ['c', 'New collab', 'q']
        result = editor._edit_single_project(project.copy())
        assert result['collaboration'] == 'New collab'
    
    def test_edit_project_frameworks_add_remove(self, mock_cli, sample_resume):
        """Test framework add and remove operations"""
        editor = ResumeEditor(mock_cli)
        project = sample_resume['projects'][0].copy()
        
        # Add framework
        mock_cli.get_input.side_effect = ['f', 'Pytest', 'done', 'q']
        result = editor._edit_single_project(project.copy())
        assert 'Pytest' in result['frameworks']
        
        # Remove framework (exact match)
        mock_cli.get_input.side_effect = ['f', 'Flask', 'y', 'done', 'q']
        result = editor._edit_single_project(project.copy())
        assert 'Flask' not in result['frameworks']
        
        # Cancel removal
        mock_cli.get_input.side_effect = ['f', 'Flask', 'n', 'done', 'q']
        result = editor._edit_single_project(project.copy())
        assert 'Flask' in result['frameworks']
    
    def test_edit_project_frameworks_case_insensitive(self, mock_cli, sample_resume):
        """Test case-insensitive framework removal - EXPOSES BUG"""
        editor = ResumeEditor(mock_cli)
        project = sample_resume['projects'][0].copy()
        
        # This should remove 'Flask' but will fail due to case-sensitivity bug
        mock_cli.get_input.side_effect = ['f', 'flask', 'y', 'done', 'q']
        result = editor._edit_single_project(project.copy())
        assert 'Flask' not in result['frameworks']
    
    def test_edit_projects_selection(self, mock_cli, sample_resume):
        """Test project selection and editing"""
        editor = ResumeEditor(mock_cli)
        
        # Edit project successfully
        mock_cli.get_input.side_effect = ['1', 'n', 'Updated', 'q', 'done']
        result = editor._edit_projects(sample_resume['projects'].copy())
        assert result[0]['name'] == 'Updated'
        
        # Invalid numeric selection
        mock_cli.get_input.side_effect = ['99', 'done']
        result = editor._edit_projects(sample_resume['projects'].copy())
        assert len(result) == 1
        
        # Non-numeric input
        mock_cli.get_input.side_effect = ['abc', 'done']
        result = editor._edit_projects(sample_resume['projects'].copy())
        assert len(result) == 1
        
        # Empty project list
        result = editor._edit_projects([])
        assert result == []
        mock_cli.print_status.assert_called_with("No projects available to edit.", "warning")
    
    def test_preview_resume(self, mock_cli, sample_resume, capsys):
        """Test resume preview with full and minimal data"""
        editor = ResumeEditor(mock_cli)
        
        # Full preview
        editor._preview_resume(sample_resume)
        captured = capsys.readouterr()
        assert all(section in captured.out for section in 
                   ['Summary:', 'Skills:', 'Projects:', 'Languages:', 'Web App', 'Python'])
        
        # Minimal preview
        editor._preview_resume({})
        captured = capsys.readouterr()
        assert 'No Summary' in captured.out
    
    def test_edit_resume_main_menu(self, mock_cli, sample_resume):
        """Test main edit menu operations"""
        editor = ResumeEditor(mock_cli)
        
        # Complete flow with multiple edits
        mock_cli.get_input.side_effect = [
            's', 'Updated summary',
            'k', 'React', 'done',
            'd'
        ]
        result = editor.edit_resume(sample_resume.copy())
        assert result['summary'] == 'Updated summary'
        assert 'React' in result['skills']
        
        # Invalid choice handling
        mock_cli.get_input.side_effect = ['x', 'd']
        editor.edit_resume(sample_resume.copy())
        mock_cli.print_status.assert_any_call(
            "Invalid choice. Please select a valid option.", "warning"
        )
        
        # Exception handling
        mock_cli.get_input.side_effect = ['s', Exception("Error"), 'd']
        result = editor.edit_resume(sample_resume.copy())
        assert result is not None
    
    def test_edit_resume_preview_option(self, mock_cli, sample_resume, capsys):
        """Test preview option from main menu"""
        editor = ResumeEditor(mock_cli)
        mock_cli.get_input.side_effect = ['v', 'd']
        
        editor.edit_resume(sample_resume.copy())
        
        captured = capsys.readouterr()
        assert 'Summary:' in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])