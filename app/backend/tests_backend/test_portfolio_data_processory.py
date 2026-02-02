import pytest
from datetime import datetime
from portfolio_data_processor import PortfolioDataProcessor


class TestPortfolioDataProcessor:
    
    @pytest.fixture
    def sample_result_data(self):
        """Create sample result data with multiple projects"""
        return {
            'metadata_insights': {
                'primary_skills': ['Backend Development', 'DevOps', 'API Design', 'Database Management'],
                'language_stats': {
                    'Python': {'language': 'Python', 'file_count': 45, 'percentage': 55.5},
                    'JavaScript': {'language': 'JavaScript', 'file_count': 30, 'percentage': 37.0},
                    'Go': {'language': 'Go', 'file_count': 6, 'percentage': 7.5},
                    'N/A': {'language': 'N/A', 'file_count': 0, 'percentage': 0}
                }
            },
            'project_insights': {
                'analyzed_insights': [
                    {
                        'repository_name': 'E-commerce API',
                        'dates': {
                            'start_date': '2023-01-15T10:00:00',
                            'end_date': '2023-06-20T14:30:00',
                            'duration_days': 156
                        },
                        'statistics': {
                            'user_lines_added': 5000,
                            'user_lines_deleted': 1200,
                            'user_files_modified': 85
                        },
                        'repository_context': {
                            'total_commits_all_authors': 250,
                            'repo_total_files_modified': 150,
                            'repo_total_lines_added': 12000,
                            'repo_total_lines_deleted': 3000,
                            'is_collaborative': True,
                            'total_contributors': 3
                        },
                        'user_commits': [{'hash': 'abc123'}, {'hash': 'def456'}],  # 2 commits
                        'collaboration_insights': {
                            'is_collaborative': True,
                            'team_size': 3,
                            'user_contribution_share_percentage': 35.5
                        },
                        'user_role': {
                            'role': 'Feature Developer',
                            'blurb': 'Led API development and database design'
                        },
                        'contribution_analysis': {
                            'contribution_level': 'Top Contributor',
                            'rank_by_commits': 1,
                            'percentile': 95.5
                        },
                        'testing_insights': {
                            'has_tests': True,
                            'test_files_modified': 15,
                            'code_files_modified': 70,
                            'testing_percentage_files': 17.6,
                            'testing_percentage_lines': 20.3
                        },
                        'imports_summary': {
                            'django': {'frequency': 45},
                            'celery': {'frequency': 30},
                            'redis': {'frequency': 25},
                            'pytest': {'frequency': 20},
                            'requests': {'frequency': 18}
                        }
                    },
                    {
                        'repository_name': 'Analytics Dashboard',
                        'dates': {
                            'start_date': '2023-08-01T09:00:00',
                            'end_date': '2024-01-15T17:00:00',
                            'duration_days': 167
                        },
                        'statistics': {
                            'user_lines_added': 8500,
                            'user_lines_deleted': 2100,
                            'user_files_modified': 120
                        },
                        'repository_context': {
                            'total_commits_all_authors': 180,
                            'repo_total_files_modified': 200,
                            'repo_total_lines_added': 15000,
                            'repo_total_lines_deleted': 4000,
                            'is_collaborative': True,
                            'total_contributors': 5
                        },
                        'user_commits': [{'hash': 'ghi789'}, {'hash': 'jkl012'}, {'hash': 'mno345'}],  # 3 commits
                        'collaboration_insights': {
                            'is_collaborative': True,
                            'team_size': 5,
                            'user_contribution_share_percentage': 28.2
                        },
                        'user_role': {
                            'role': 'Maintainer',
                            'blurb': 'Focused on code quality and optimization'
                        },
                        'contribution_analysis': {
                            'contribution_level': 'Major Contributor',
                            'rank_by_commits': 2,
                            'percentile': 80.0
                        },
                        'testing_insights': {
                            'has_tests': True,
                            'test_files_modified': 25,
                            'code_files_modified': 95,
                            'testing_percentage_files': 20.8,
                            'testing_percentage_lines': 25.0
                        },
                        'imports_summary': {
                            'react': {'frequency': 50},
                            'axios': {'frequency': 35},
                            'chart.js': {'frequency': 28},
                            'jest': {'frequency': 22}
                        }
                    },
                    {
                        'repository_name': 'Microservices Platform',
                        'dates': {
                            'start_date': '2024-02-01T08:00:00',
                            'end_date': None,
                            'duration_days': 90
                        },
                        'statistics': {
                            'user_lines_added': 12000,
                            'user_lines_deleted': 3500,
                            'user_files_modified': 180
                        },
                        'repository_context': {
                            'total_commits_all_authors': 320,
                            'repo_total_files_modified': 280,
                            'repo_total_lines_added': 25000,
                            'repo_total_lines_deleted': 7000,
                            'is_collaborative': True,
                            'total_contributors': 8
                        },
                        'user_commits': [{'hash': 'pqr678'}, {'hash': 'stu901'}, {'hash': 'vwx234'}, {'hash': 'yza567'}],  # 4 commits
                        'collaboration_insights': {
                            'is_collaborative': True,
                            'team_size': 8,
                            'user_contribution_share_percentage': 22.5
                        },
                        'user_role': {
                            'role': 'Feature Developer',
                            'blurb': 'Built microservices architecture and deployment pipeline'
                        },
                        'contribution_analysis': {
                            'contribution_level': 'Significant Contributor',
                            'rank_by_commits': 3,
                            'percentile': 70.0
                        },
                        'testing_insights': {
                            'has_tests': True,
                            'test_files_modified': 40,
                            'code_files_modified': 140,
                            'testing_percentage_files': 22.2,
                            'testing_percentage_lines': 28.5
                        },
                        'imports_summary': {
                            'docker': {'frequency': 55},
                            'kubernetes': {'frequency': 48},
                            'prometheus': {'frequency': 35},
                            'grafana': {'frequency': 30},
                            'rabbitmq': {'frequency': 25}
                        }
                    }
                ]
            }
        }
    
    def test_initialization(self, sample_result_data):
        """Test processor initializes with result data"""
        processor = PortfolioDataProcessor(sample_result_data)
        assert processor.result_data == sample_result_data
    
    def test_extract_detailed_projects_default(self, sample_result_data):
        """Test extracting top 3 projects with full details"""
        processor = PortfolioDataProcessor(sample_result_data)
        projects = processor.extract_detailed_projects()
        
        assert len(projects) == 3
        # Verify chronological sorting (oldest first)
        assert projects[0]['name'] == 'E-commerce API'
        assert projects[1]['name'] == 'Analytics Dashboard'
        assert projects[2]['name'] == 'Microservices Platform'
    
    def test_extract_detailed_projects_custom_count(self, sample_result_data):
        """Test extracting custom number of projects"""
        processor = PortfolioDataProcessor(sample_result_data)
        
        projects = processor.extract_detailed_projects(top_n=2)
        assert len(projects) == 2
        
        projects = processor.extract_detailed_projects(top_n=1)
        assert len(projects) == 1
    
    def test_extract_detailed_projects_empty_data(self):
        """Test handling empty or missing project data"""
        processor = PortfolioDataProcessor({})
        assert processor.extract_detailed_projects() == []
        
        processor = PortfolioDataProcessor({'project_insights': {}})
        assert processor.extract_detailed_projects() == []
    
    def test_format_detailed_project_structure(self, sample_result_data):
        """Test detailed project formatting creates correct structure"""
        processor = PortfolioDataProcessor(sample_result_data)
        project_data = sample_result_data['project_insights']['analyzed_insights'][0]
        
        formatted = processor._format_detailed_project(project_data)
        
        assert formatted is not None
        assert formatted['name'] == 'E-commerce API'
        assert 'Jan 2023' in formatted['date_range']
        assert formatted['duration_days'] == 156
        
        # Verify statistics structure
        stats = formatted['statistics']
        assert stats['commits'] == 250  # Total project commits
        assert stats['user_commits'] == 2  # User's commit count
        assert stats['files'] == 150
        assert stats['additions'] == 12000
        assert stats['deletions'] == 3000
        assert stats['net_lines'] == 9000
        assert stats['user_lines_added'] == 5000
        assert stats['user_lines_deleted'] == 1200
        assert stats['user_net_lines'] == 3800
        assert stats['user_files_modified'] == 85
        
        # Verify user role structure
        assert formatted['user_role']['role'] == 'Feature Developer'
        assert 'Led API development' in formatted['user_role']['blurb']
        
        # Verify contribution structure
        contribution = formatted['contribution']
        assert contribution['level'] == 'Top Contributor'
        assert contribution['rank'] == 1
        assert contribution['percentile'] == 95.5
        assert contribution['is_collaborative'] == True
        assert contribution['team_size'] == 3
        assert contribution['contribution_share'] == 35.5
        
        # Verify testing structure
        testing = formatted['testing']
        assert testing['has_tests'] == True
        assert testing['test_files'] == 15
        assert testing['code_files'] == 70
        assert testing['coverage_by_files'] == 17.6
        assert testing['coverage_by_lines'] == 20.3
    
    def test_get_all_frameworks(self, sample_result_data):
        """Test framework extraction and sorting"""
        processor = PortfolioDataProcessor(sample_result_data)
        imports = sample_result_data['project_insights']['analyzed_insights'][0]['imports_summary']
        
        frameworks = processor._get_all_frameworks(imports)
        
        assert len(frameworks) == 5
        # Verify sorted by frequency (descending)
        assert frameworks[0]['name'] == 'django'
        assert frameworks[0]['frequency'] == 45
        assert frameworks[1]['name'] == 'celery'
        assert frameworks[-1]['name'] == 'requests'
        
        # Test empty case
        assert processor._get_all_frameworks({}) == []
    
    def test_extract_skill_timeline(self, sample_result_data):
        """Test skill timeline extraction with high-level skills and frameworks"""
        processor = PortfolioDataProcessor(sample_result_data)
        projects = processor.extract_detailed_projects()
        
        skill_timeline = processor.extract_skill_timeline(projects)
        
        assert 'high_level_skills' in skill_timeline
        assert 'framework_timeline' in skill_timeline
        assert 'language_progression' in skill_timeline
        
        # Verify high-level skills
        skills = skill_timeline['high_level_skills']
        assert len(skills) == 4
        assert 'Backend Development' in skills
        assert 'DevOps' in skills
        
        # Verify framework timeline
        fw_timeline = skill_timeline['framework_timeline']
        assert len(fw_timeline) == 3
        assert 'E-commerce API' in fw_timeline
        
        # Verify language progression
        langs = skill_timeline['language_progression']
        assert len(langs) == 3  # Excludes N/A
        assert langs[0]['name'] == 'Python'
        assert langs[0]['file_count'] == 45
    
    def test_create_framework_timeline(self, sample_result_data):
        """Test framework timeline creation"""
        processor = PortfolioDataProcessor(sample_result_data)
        projects = processor.extract_detailed_projects()
        
        timeline = processor._create_framework_timeline(projects)
        
        assert 'E-commerce API' in timeline
        assert 'Analytics Dashboard' in timeline
        
        # Verify structure
        ecommerce = timeline['E-commerce API']
        assert len(ecommerce['frameworks']) <= 8  # Top 8
        assert 'django' in ecommerce['frameworks']
        assert ecommerce['total_frameworks'] == 5
        assert 'Jan 2023' in ecommerce['date_range']
    
    def test_create_language_progression(self, sample_result_data):
        """Test language progression creation and sorting"""
        processor = PortfolioDataProcessor(sample_result_data)
        lang_stats = sample_result_data['metadata_insights']['language_stats']
        
        progression = processor._create_language_progression(lang_stats)
        
        assert len(progression) == 3  # N/A filtered out
        # Verify sorted by file count
        assert progression[0]['name'] == 'Python'
        assert progression[0]['file_count'] == 45
        assert progression[0]['percentage'] == 55.5
        assert progression[-1]['name'] == 'Go'
    
    def test_calculate_growth_metrics_with_comparison(self, sample_result_data):
        """Test growth metrics calculation comparing earliest and latest projects"""
        processor = PortfolioDataProcessor(sample_result_data)
        projects = processor.extract_detailed_projects()
        
        metrics = processor.calculate_growth_metrics(projects)
        
        assert metrics['has_comparison'] == True
        assert metrics['earliest_project'] == 'E-commerce API'
        assert metrics['latest_project'] == 'Microservices Platform'
        
        # Verify code metrics
        code_metrics = metrics['code_metrics']
        assert 'commit_growth' in code_metrics
        assert 'file_growth' in code_metrics
        assert 'lines_growth' in code_metrics
        assert 'user_lines_growth' in code_metrics
        
        # Verify technology metrics
        tech_metrics = metrics['technology_metrics']
        assert 'framework_growth' in tech_metrics
        assert tech_metrics['earliest_frameworks'] == 5  # E-commerce API has 5 frameworks
        assert tech_metrics['latest_frameworks'] == 5  # Microservices has 5 frameworks
        
        # Verify testing evolution
        testing = metrics['testing_evolution']
        assert testing['earliest_has_tests'] == True
        assert testing['latest_has_tests'] == True
        assert testing['coverage_improvement'] > 0  # 17.6% -> 22.2%
        
        # Verify collaboration evolution
        collab = metrics['collaboration_evolution']
        assert collab['earliest_solo'] == False
        assert collab['latest_solo'] == False
        assert collab['earliest_team_size'] == 3
        assert collab['latest_team_size'] == 8
        
        # Verify role evolution
        role = metrics['role_evolution']
        assert role['earliest_role'] == 'Feature Developer'
        assert role['latest_role'] == 'Feature Developer'
        assert role['role_changed'] == False
    
    def test_calculate_growth_metrics_insufficient_projects(self):
        """Test growth metrics with less than 2 projects"""
        processor = PortfolioDataProcessor({
            'project_insights': {
                'analyzed_insights': [
                    {
                        'repository_name': 'Single Project',
                        'dates': {'start_date': '2024-01-01T00:00:00'},
                        'statistics': {},
                        'repository_context': {},
                        'user_commits': [],
                        'collaboration_insights': {},
                        'user_role': {},
                        'contribution_analysis': {},
                        'testing_insights': {},
                        'imports_summary': {}
                    }
                ]
            }
        })
        
        projects = processor.extract_detailed_projects(top_n=1)
        metrics = processor.calculate_growth_metrics(projects)
        
        assert metrics['has_comparison'] == False
        assert 'message' in metrics
    
    def test_calculate_percentage_change(self, sample_result_data):
        """Test percentage change calculation"""
        processor = PortfolioDataProcessor(sample_result_data)
  
        assert processor._calculate_percentage_change(100, 150) == 50.0
        assert processor._calculate_percentage_change(100, 75) == -25.0
        assert processor._calculate_percentage_change(0, 50) == 100.0
        assert processor._calculate_percentage_change(100, 100) == 0.0
        assert processor._calculate_percentage_change(0, 0) == 0.0
    
    @pytest.mark.parametrize("start,end,expected", [
        ('2023-01-15T10:00:00', '2023-06-20T14:30:00', 'Jan 2023 - Jun 2023'),
        ('2024-01-15T10:00:00', None, 'Jan 2024 - Present'),
        (None, '2024-06-20T14:30:00', 'Dates unavailable'),
        ('2024-01-15T10:00:00+00:00', '2024-06-20T14:30:00+00:00', 'Jan 2024 - Jun 2024'),
        ('invalid', 'also-invalid', 'Dates unavailable'),
    ])
    def test_format_date_range(self, start, end, expected):
        """Test date range formatting for various scenarios"""
        processor = PortfolioDataProcessor({})
        assert processor._format_date_range(start, end) == expected
    
    def test_format_date_range_recent_end_date(self, sample_result_data):
        """Test that recent end dates are shown as 'Present'"""
        processor = PortfolioDataProcessor(sample_result_data)
        
        # Create a date within last 30 days
        recent_date = datetime.now()
        recent_iso = recent_date.isoformat()
        
        result = processor._format_date_range('2024-01-01T00:00:00', recent_iso)
        assert 'Present' in result