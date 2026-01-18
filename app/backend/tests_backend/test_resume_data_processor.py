import pytest
from datetime import datetime
from resume_data_processor import ResumeDataProcessor


class TestResumeDataProcessor:
    
    @pytest.fixture
    def sample_result_data(self):
        """Create comprehensive sample result data"""
        return {
            'resume_points': 'Skilled developer with 5+ years of experience in full-stack development',
            'metadata_insights': {
                'primary_skills': ['Python', 'React', 'Docker', 'PostgreSQL'],
                'language_stats': {
                    'Python': {'language': 'Python', 'file_count': 25},
                    'JavaScript': {'language': 'JavaScript', 'file_count': 18},
                    'TypeScript': {'language': 'TypeScript', 'file_count': 12},
                    'N/A': {'language': 'N/A', 'file_count': 5}
                }
            },
            'project_insights': {
                'analyzed_insights': [
                    {
                        'repository_name': 'E-commerce Platform',
                        'dates': {
                            'start_date': '2024-01-15T10:00:00',
                            'end_date': '2024-12-20T14:30:00'
                        },
                        'statistics': {},
                        'collaboration_insights': {},
                        'user_role': {'blurb': 'Led backend development and API design'},
                        'imports_summary': {
                            'django': {'frequency': 30},
                            'celery': {'frequency': 15},
                            'redis': {'frequency': 12},
                            'pytest': {'frequency': 10},
                            'stripe': {'frequency': 8}
                        }
                    },
                    {
                        'repository_name': 'Mobile App Backend',
                        'dates': {
                            'start_date': '2023-06-01T09:00:00',
                            'end_date': '2023-11-15T17:00:00'
                        },
                        'statistics': {},
                        'collaboration_insights': {},
                        'user_role': {'blurb': 'Built REST API and database architecture'},
                        'imports_summary': {
                            'flask': {'frequency': 25},
                            'sqlalchemy': {'frequency': 20}
                        }
                    }
                ]
            }
        }
    
    def test_initialization(self, sample_result_data):
        processor = ResumeDataProcessor(sample_result_data)
        assert processor.result_data == sample_result_data
    
    def test_extract_summary(self, sample_result_data):
        """Test summary extraction for various scenarios"""
        # Success case
        processor = ResumeDataProcessor(sample_result_data)
        assert processor.extract_summary() == sample_result_data['resume_points']
        
        # Edge cases
        assert ResumeDataProcessor({}).extract_summary() is None
        assert ResumeDataProcessor({'resume_points': None}).extract_summary() is None
    
    def test_extract_metadata_skills(self, sample_result_data):
        """Test skills extraction"""
        processor = ResumeDataProcessor(sample_result_data)
        skills = processor.extract_metadata_skills()
        assert len(skills) == 4
        assert 'Python' in skills and 'Docker' in skills
        
        # Empty case
        assert ResumeDataProcessor({}).extract_metadata_skills() == []
    
    def test_extract_languages(self, sample_result_data):
        """Test language extraction, sorting, and N/A filtering"""
        processor = ResumeDataProcessor(sample_result_data)
        languages = processor.extract_languages()
        
        assert len(languages) == 3
        assert languages[0] == {'name': 'Python', 'file_count': 25}
        # Verify sorted descending and N/A filtered
        assert [lang['file_count'] for lang in languages] == [25, 18, 12]
        assert not any(lang['name'] == 'N/A' for lang in languages)
        
        # Empty case
        assert ResumeDataProcessor({'metadata_insights': {}}).extract_languages() == []
    
    def test_extract_top_projects(self, sample_result_data):
        """Test project extraction with various top_n values"""
        processor = ResumeDataProcessor(sample_result_data)
        
        # Default (top 3)
        projects = processor.extract_top_projects()
        assert len(projects) == 2  # Only 2 in sample
        assert projects[0]['name'] == 'E-commerce Platform'
        
        # Custom count
        assert len(processor.extract_top_projects(top_n=1)) == 1
        
        # Empty case
        assert ResumeDataProcessor({}).extract_top_projects() == []
    
    def test_format_project_for_resume(self, sample_result_data):
        """Test project formatting"""
        processor = ResumeDataProcessor(sample_result_data)
        project_data = sample_result_data['project_insights']['analyzed_insights'][0]
        formatted = processor._format_project_for_resume(project_data)
        
        assert formatted['name'] == 'E-commerce Platform'
        assert 'Jan 2024' in formatted['date_range'] and 'Dec 2024' in formatted['date_range']
        assert 'Led backend development' in formatted['collaboration']
        assert len(formatted['frameworks']) <= 5
        assert 'django' in formatted['frameworks']
    
    def test_get_top_frameworks(self, sample_result_data):
        """Test framework extraction from imports"""
        processor = ResumeDataProcessor(sample_result_data)
        imports = sample_result_data['project_insights']['analyzed_insights'][0]['imports_summary']
        frameworks = processor._get_top_frameworks(imports, top_n=3)
        
        assert frameworks == ['django', 'celery', 'redis']
        assert ResumeDataProcessor({})._get_top_frameworks({}, top_n=5) == []
    
    @pytest.mark.parametrize("start,end,expected", [
        ('2024-01-15T10:00:00', '2024-06-20T14:30:00', 'Jan 2024 - Jun 2024'),
        ('2024-01-15T10:00:00', None, 'Jan 2024 - Present'),
        (None, '2024-06-20T14:30:00', 'Dates unavailable'),
        ('2024-01-15T10:00:00+00:00', '2024-06-20T14:30:00+00:00', 'Jan 2024 - Jun 2024'),
        ('invalid', 'also-invalid', 'Dates unavailable'),
    ])
    def test_format_date_range(self, start, end, expected):
        """Test date range formatting for various scenarios"""
        processor = ResumeDataProcessor({})
        assert processor._format_date_range(start, end) == expected