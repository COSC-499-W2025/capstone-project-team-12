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
        """Test processor initialization"""
        processor = ResumeDataProcessor(sample_result_data)
        assert processor.result_data == sample_result_data
    
    def test_extract_summary_success(self, sample_result_data):
        """Test successful summary extraction"""
        processor = ResumeDataProcessor(sample_result_data)
        summary = processor.extract_summary()
        
        assert summary == sample_result_data['resume_points']
        assert isinstance(summary, str)
    
    def test_extract_summary_missing(self):
        """Test summary extraction when resume_points is missing"""
        processor = ResumeDataProcessor({})
        summary = processor.extract_summary()
        assert summary is None
    
    def test_extract_summary_handles_exception(self):
        """Test summary extraction error handling"""
        processor = ResumeDataProcessor({'resume_points': None})
        summary = processor.extract_summary()
        assert summary is None
    
    def test_extract_metadata_skills_success(self, sample_result_data):
        """Test successful skills extraction"""
        processor = ResumeDataProcessor(sample_result_data)
        skills = processor.extract_metadata_skills()
        
        assert len(skills) == 4
        assert 'Python' in skills
        assert 'Docker' in skills
    
    def test_extract_metadata_skills_empty(self):
        """Test skills extraction with empty metadata"""
        processor = ResumeDataProcessor({})
        skills = processor.extract_metadata_skills()
        assert skills == []
    
    def test_extract_metadata_skills_no_primary_skills(self):
        """Test skills extraction when primary_skills is missing"""
        data = {'metadata_insights': {}}
        processor = ResumeDataProcessor(data)
        skills = processor.extract_metadata_skills()
        assert skills == []
    
    def test_extract_languages_success(self, sample_result_data):
        """Test successful language extraction"""
        processor = ResumeDataProcessor(sample_result_data)
        languages = processor.extract_languages()
        
        assert len(languages) == 3  # N/A should be filtered out
        assert languages[0]['name'] == 'Python'
        assert languages[0]['file_count'] == 25
        assert all('name' in lang and 'file_count' in lang for lang in languages)
    
    def test_extract_languages_sorted_by_count(self, sample_result_data):
        """Test languages are sorted by file count descending"""
        processor = ResumeDataProcessor(sample_result_data)
        languages = processor.extract_languages()
        
        counts = [lang['file_count'] for lang in languages]
        assert counts == sorted(counts, reverse=True)
    
    def test_extract_languages_filters_na(self, sample_result_data):
        """Test that N/A languages are filtered out"""
        processor = ResumeDataProcessor(sample_result_data)
        languages = processor.extract_languages()
        
        assert not any(lang['name'] == 'N/A' for lang in languages)
    
    def test_extract_languages_empty(self):
        """Test language extraction with no language stats"""
        processor = ResumeDataProcessor({'metadata_insights': {}})
        languages = processor.extract_languages()
        assert languages == []
    
    def test_extract_top_projects_default(self, sample_result_data):
        """Test extracting top 3 projects by default"""
        processor = ResumeDataProcessor(sample_result_data)
        projects = processor.extract_top_projects()
        
        assert len(projects) == 2  # Only 2 projects in sample data
        assert projects[0]['name'] == 'E-commerce Platform'
    
    def test_extract_top_projects_custom_count(self, sample_result_data):
        """Test extracting custom number of projects"""
        processor = ResumeDataProcessor(sample_result_data)
        projects = processor.extract_top_projects(top_n=1)
        
        assert len(projects) == 1
        assert projects[0]['name'] == 'E-commerce Platform'
    
    def test_extract_top_projects_empty(self):
        """Test project extraction with no projects"""
        processor = ResumeDataProcessor({})
        projects = processor.extract_top_projects()
        assert projects == []
    
    def test_format_project_for_resume(self, sample_result_data):
        """Test project formatting for resume"""
        processor = ResumeDataProcessor(sample_result_data)
        project_data = sample_result_data['project_insights']['analyzed_insights'][0]
        
        formatted = processor._format_project_for_resume(project_data)
        
        assert formatted['name'] == 'E-commerce Platform'
        assert 'Jan 2024' in formatted['date_range']
        assert 'Dec 2024' in formatted['date_range']
        assert 'Led backend development' in formatted['collaboration']
        assert len(formatted['frameworks']) <= 5
        assert 'django' in formatted['frameworks']
    
    def test_get_top_frameworks(self, sample_result_data):
        """Test framework extraction from imports"""
        processor = ResumeDataProcessor(sample_result_data)
        imports = sample_result_data['project_insights']['analyzed_insights'][0]['imports_summary']
        
        frameworks = processor._get_top_frameworks(imports, top_n=3)
        
        assert len(frameworks) == 3
        assert frameworks[0] == 'django'  # Highest frequency
        assert frameworks[1] == 'celery'
    
    def test_get_top_frameworks_empty(self):
        """Test framework extraction with no imports"""
        processor = ResumeDataProcessor({})
        frameworks = processor._get_top_frameworks({}, top_n=5)
        assert frameworks == []
    
    def test_format_date_range_complete(self):
        """Test date range formatting with start and end dates"""
        processor = ResumeDataProcessor({})
        date_range = processor._format_date_range(
            '2024-01-15T10:00:00',
            '2024-06-20T14:30:00'
        )
        assert date_range == 'Jan 2024 - Jun 2024'
    
    def test_format_date_range_no_end_date(self):
        """Test date range formatting without end date"""
        processor = ResumeDataProcessor({})
        date_range = processor._format_date_range('2024-01-15T10:00:00', None)
        assert date_range == 'Jan 2024 - Present'
    
    def test_format_date_range_no_start_date(self):
        """Test date range formatting without start date"""
        processor = ResumeDataProcessor({})
        date_range = processor._format_date_range(None, '2024-06-20T14:30:00')
        assert date_range == 'Dates unavailable'
    
    def test_format_date_range_recent_end_date(self):
        """Test that recent end dates (within 30 days) show as Present"""
        processor = ResumeDataProcessor({})
        recent_date = datetime.now().isoformat()
        date_range = processor._format_date_range('2024-01-15T10:00:00', recent_date)
        assert 'Present' in date_range
    
    def test_format_date_range_with_timezone(self):
        """Test date range formatting handles timezone info"""
        processor = ResumeDataProcessor({})
        date_range = processor._format_date_range(
            '2024-01-15T10:00:00+00:00',
            '2024-06-20T14:30:00+00:00'
        )
        assert date_range == 'Jan 2024 - Jun 2024'
    
    def test_format_date_range_invalid_dates(self):
        """Test date range formatting with invalid dates"""
        processor = ResumeDataProcessor({})
        date_range = processor._format_date_range('invalid', 'also-invalid')
        assert date_range == 'Dates unavailable'