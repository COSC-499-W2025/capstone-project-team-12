import pytest
from portfolio_builder import PortfolioBuilder


class TestPortfolioBuilder:
    
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
            'metadata_insights': {
                'primary_skills': ['Backend Development', 'API Design', 'DevOps'],
                'language_stats': {
                    'Python': {'language': 'Python', 'file_count': 30, 'percentage': 60.0},
                    'JavaScript': {'language': 'JavaScript', 'file_count': 15, 'percentage': 30.0},
                    'Go': {'language': 'Go', 'file_count': 5, 'percentage': 10.0}
                }
            },
            'project_insights': {
                'analyzed_insights': [
                    {
                        'repository_name': 'API Gateway',
                        'dates': {
                            'start_date': '2023-03-01T10:00:00',
                            'end_date': '2023-08-15T14:30:00',
                            'duration_days': 167
                        },
                        'statistics': {
                            'user_lines_added': 4000,
                            'user_lines_deleted': 800,
                            'user_files_modified': 60
                        },
                        'repository_context': {
                            'total_commits_all_authors': 150,
                            'repo_total_files_modified': 100,
                            'repo_total_lines_added': 8000,
                            'repo_total_lines_deleted': 2000,
                            'is_collaborative': True,
                            'total_contributors': 4
                        },
                        'user_commits': [{'hash': 'abc'}, {'hash': 'def'}],
                        'collaboration_insights': {
                            'is_collaborative': True,
                            'team_size': 4,
                            'user_contribution_share_percentage': 30.0
                        },
                        'user_role': {
                            'role': 'Feature Developer',
                            'blurb': 'Developed core API endpoints'
                        },
                        'contribution_analysis': {
                            'contribution_level': 'Major Contributor',
                            'rank_by_commits': 2,
                            'percentile': 75.0
                        },
                        'testing_insights': {
                            'has_tests': True,
                            'test_files_modified': 12,
                            'code_files_modified': 48,
                            'testing_percentage_files': 20.0,
                            'testing_percentage_lines': 22.5
                        },
                        'imports_summary': {
                            'flask': {'frequency': 35},
                            'sqlalchemy': {'frequency': 28},
                            'pytest': {'frequency': 15}
                        }
                    },
                    {
                        'repository_name': 'Data Pipeline',
                        'dates': {
                            'start_date': '2023-10-01T09:00:00',
                            'end_date': '2024-02-15T17:00:00',
                            'duration_days': 137
                        },
                        'statistics': {
                            'user_lines_added': 6500,
                            'user_lines_deleted': 1500,
                            'user_files_modified': 95
                        },
                        'repository_context': {
                            'total_commits_all_authors': 200,
                            'repo_total_files_modified': 180,
                            'repo_total_lines_added': 13000,
                            'repo_total_lines_deleted': 3500,
                            'is_collaborative': True,
                            'total_contributors': 6
                        },
                        'user_commits': [{'hash': 'ghi'}, {'hash': 'jkl'}, {'hash': 'mno'}],
                        'collaboration_insights': {
                            'is_collaborative': True,
                            'team_size': 6,
                            'user_contribution_share_percentage': 25.5
                        },
                        'user_role': {
                            'role': 'Maintainer',
                            'blurb': 'Optimized data processing workflows'
                        },
                        'contribution_analysis': {
                            'contribution_level': 'Significant Contributor',
                            'rank_by_commits': 3,
                            'percentile': 60.0
                        },
                        'testing_insights': {
                            'has_tests': True,
                            'test_files_modified': 20,
                            'code_files_modified': 75,
                            'testing_percentage_files': 21.1,
                            'testing_percentage_lines': 24.0
                        },
                        'imports_summary': {
                            'pandas': {'frequency': 42},
                            'apache-airflow': {'frequency': 35},
                            'pytest': {'frequency': 18}
                        }
                    }
                ]
            }
        }
    
    def test_create_portfolio_from_result_id_success(self, mock_db_manager, mock_cli, sample_result_data):
        """Test successful portfolio creation from result ID"""
        builder = PortfolioBuilder()
        mock_db_manager.get_analysis_data.return_value = sample_result_data
        
        portfolio = builder.create_portfolio_from_result_id(mock_db_manager, mock_cli, 'test-result-id')
        
        assert portfolio is not None
        assert 'portfolio_id' in portfolio
        assert 'result_id' in portfolio
        assert portfolio['result_id'] == 'test-result-id'
        assert 'projects_detail' in portfolio
        assert 'skill_timeline' in portfolio
        assert 'growth_metrics' in portfolio
        mock_cli.print_status.assert_any_call("Portfolio generated successfully!", "success")
    
    def test_create_portfolio_result_not_found(self, mock_db_manager, mock_cli):
        """Test handling when result is not found in database"""
        builder = PortfolioBuilder()
        mock_db_manager.get_analysis_data.return_value = None
        
        portfolio = builder.create_portfolio_from_result_id(mock_db_manager, mock_cli, 'invalid-id')
        
        assert portfolio is None
        mock_cli.print_status.assert_called_with("Result not found in database.", "error")
    
    def test_create_portfolio_empty_content(self, mock_db_manager, mock_cli):
        """Test handling when generated portfolio has no content"""
        builder = PortfolioBuilder()
        empty_data = {
            'metadata_insights': {},
            'project_insights': {}
        }
        mock_db_manager.get_analysis_data.return_value = empty_data
        
        portfolio = builder.create_portfolio_from_result_id(mock_db_manager, mock_cli, 'test-id')
        
        # Portfolio is still created but with empty sections
        assert portfolio is not None
        assert len(portfolio['projects_detail']) == 0
        assert portfolio['growth_metrics']['has_comparison'] == False
    
    def test_create_portfolio_handles_exception(self, mock_db_manager, mock_cli):
        """Test error handling during portfolio creation"""
        builder = PortfolioBuilder()
        mock_db_manager.get_analysis_data.side_effect = Exception("Database error")
        
        portfolio = builder.create_portfolio_from_result_id(mock_db_manager, mock_cli, 'test-id')
        
        assert portfolio is None
        assert mock_cli.print_status.call_count > 0
    
    def test_build_portfolio_structure(self, sample_result_data):
        """Test internal portfolio building creates correct structure"""
        builder = PortfolioBuilder()
        
        portfolio = builder._build_portfolio(sample_result_data, 'test-result-id')
        
        assert portfolio['result_id'] == 'test-result-id'
        assert isinstance(portfolio['portfolio_id'], str)
        assert len(portfolio['portfolio_id']) > 0
        
        # Verify projects_detail
        assert len(portfolio['projects_detail']) == 2
        assert portfolio['projects_detail'][0]['name'] == 'API Gateway'  # Chronological order
        
        # Verify skill_timeline
        skill_timeline = portfolio['skill_timeline']
        assert 'high_level_skills' in skill_timeline
        assert 'framework_timeline' in skill_timeline
        assert 'language_progression' in skill_timeline
        assert len(skill_timeline['high_level_skills']) == 3
        
        # Verify growth_metrics
        growth = portfolio['growth_metrics']
        assert growth['has_comparison'] == True
        assert 'code_metrics' in growth
        assert 'technology_metrics' in growth
    
    def test_build_portfolio_handles_invalid_data(self):
        """Test _build_portfolio handles invalid data gracefully"""
        builder = PortfolioBuilder()
        invalid_data = {'invalid': 'structure'}
        
        portfolio = builder._build_portfolio(invalid_data, 'test-id')
        
        assert portfolio['result_id'] == 'test-id'
        assert isinstance(portfolio['portfolio_id'], str)
        assert portfolio['projects_detail'] == []
        # skill_timeline returns a dict with empty values, not empty dict
        assert portfolio['skill_timeline']['high_level_skills'] == []
        assert portfolio['skill_timeline']['framework_timeline'] == {}
        assert portfolio['growth_metrics']['has_comparison'] == False
    
    def test_display_portfolio_full(self, sample_result_data, mocker, capsys):
        """Test complete portfolio display"""
        builder = PortfolioBuilder()
        portfolio = builder._build_portfolio(sample_result_data, 'test-id')
        mock_cli = mocker.Mock()
        
        builder.display_portfolio(portfolio, cli=mock_cli)
        
        # Verify cli.print_header was called
        mock_cli.print_header.assert_called_once_with("DEVELOPER PORTFOLIO")
        
        captured = capsys.readouterr()
        assert 'Portfolio ID:' in captured.out
        assert 'LEARNING PROGRESSION & EVOLUTION' in captured.out
        assert 'PROJECT DEEP DIVES' in captured.out
        assert 'SKILL EVOLUTION & TECHNICAL GROWTH' in captured.out
    
    def test_display_portfolio_with_error(self, mocker):
        """Test display_portfolio handles errors"""
        builder = PortfolioBuilder()
        invalid_portfolio = None
        mock_cli = mocker.Mock()
        
        builder.display_portfolio(invalid_portfolio, cli=mock_cli)
        
        mock_cli.print_status.assert_called()
        assert 'error' in str(mock_cli.print_status.call_args).lower()
    
    def test_display_growth_metrics(self, sample_result_data, capsys):
        """Test growth metrics display formatting"""
        builder = PortfolioBuilder()
        portfolio = builder._build_portfolio(sample_result_data, 'test-id')
        
        builder._display_growth_metrics(portfolio['growth_metrics'])
        
        captured = capsys.readouterr()
        assert 'LEARNING PROGRESSION & EVOLUTION' in captured.out
        assert 'Code Volume Growth:' in captured.out
        assert 'Technology Stack Evolution:' in captured.out
        assert 'Testing Practice Evolution:' in captured.out
        assert 'Collaboration & Teamwork Evolution:' in captured.out
        assert 'Role & Contribution Style Evolution:' in captured.out
    
    def test_format_growth_positive(self):
        """Test growth percentage formatting for positive values"""
        builder = PortfolioBuilder()
        
        assert builder._format_growth(50.5) == "+50.5%"
        assert builder._format_growth(100.0) == "+100.0%"
    
    def test_format_growth_negative(self):
        """Test growth percentage formatting for negative values"""
        builder = PortfolioBuilder()
        
        assert builder._format_growth(-25.3) == "-25.3%"
        assert builder._format_growth(-50.0) == "-50.0%"
    
    def test_format_growth_zero(self):
        """Test growth percentage formatting for zero"""
        builder = PortfolioBuilder()
        
        assert builder._format_growth(0.0) == "No change"
        assert builder._format_growth(0) == "No change"
    
    def test_display_detailed_projects(self, sample_result_data, capsys):
        """Test detailed project display"""
        builder = PortfolioBuilder()
        portfolio = builder._build_portfolio(sample_result_data, 'test-id')
        
        builder._display_detailed_projects(portfolio['projects_detail'])
        
        captured = capsys.readouterr()
        assert 'PROJECT DEEP DIVES' in captured.out
        assert 'API Gateway' in captured.out
        assert 'Data Pipeline' in captured.out
        assert 'Role:' in captured.out
        assert 'Contribution Analysis:' in captured.out
        assert 'Project Statistics:' in captured.out
        assert 'Testing & Quality:' in captured.out
        assert 'Technologies & Frameworks:' in captured.out
    
    def test_display_detailed_projects_shows_statistics(self, sample_result_data, capsys):
        """Test that project statistics are displayed correctly"""
        builder = PortfolioBuilder()
        portfolio = builder._build_portfolio(sample_result_data, 'test-id')
        
        builder._display_detailed_projects(portfolio['projects_detail'])
        
        captured = capsys.readouterr()
        assert 'Total Project:' in captured.out
        assert 'Your Contribution:' in captured.out
        assert 'Commits:' in captured.out
        assert 'Files:' in captured.out
        assert 'Lines Added:' in captured.out
    
    def test_display_skill_timeline(self, sample_result_data, capsys):
        """Test skill timeline display"""
        builder = PortfolioBuilder()
        portfolio = builder._build_portfolio(sample_result_data, 'test-id')
        
        builder._display_skill_timeline(portfolio['skill_timeline'])
        
        captured = capsys.readouterr()
        assert 'SKILL EVOLUTION & TECHNICAL GROWTH' in captured.out
        assert 'Core Competencies' in captured.out
        assert 'Technical Framework Evolution' in captured.out
        assert 'Programming Language Proficiency' in captured.out
        assert 'Backend Development' in captured.out
        assert 'Python' in captured.out
    
    def test_display_skill_timeline_framework_chronology(self, sample_result_data, capsys):
        """Test that frameworks are displayed chronologically"""
        builder = PortfolioBuilder()
        portfolio = builder._build_portfolio(sample_result_data, 'test-id')
        
        builder._display_skill_timeline(portfolio['skill_timeline'])
        
        captured = capsys.readouterr()
        # API Gateway should appear before Data Pipeline (chronological order)
        api_pos = captured.out.find('API Gateway')
        pipeline_pos = captured.out.find('Data Pipeline')
        assert api_pos < pipeline_pos
    
    def test_display_portfolio_sections_order(self, sample_result_data, mocker, capsys):
        """Test that portfolio sections are displayed in correct order"""
        builder = PortfolioBuilder()
        portfolio = builder._build_portfolio(sample_result_data, 'test-id')
        mock_cli = mocker.Mock()
        
        builder.display_portfolio(portfolio, cli=mock_cli)
        
        captured = capsys.readouterr()
        
        # Find positions of each section
        evolution_pos = captured.out.find('LEARNING PROGRESSION & EVOLUTION')
        projects_pos = captured.out.find('PROJECT DEEP DIVES')
        skills_pos = captured.out.find('SKILL EVOLUTION & TECHNICAL GROWTH')
        
        # Verify order: Evolution -> Projects -> Skills
        assert evolution_pos < projects_pos < skills_pos
    
    def test_portfolio_with_single_project_no_growth(self):
        """Test portfolio generation with only one project (no growth comparison)"""
        builder = PortfolioBuilder()
        single_project_data = {
            'metadata_insights': {
                'primary_skills': ['Python'],
                'language_stats': {}
            },
            'project_insights': {
                'analyzed_insights': [
                    {
                        'repository_name': 'Solo Project',
                        'dates': {'start_date': '2024-01-01T00:00:00', 'duration_days': 30},
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
        }
        
        portfolio = builder._build_portfolio(single_project_data, 'test-id')
        
        assert portfolio['growth_metrics']['has_comparison'] == False
        assert len(portfolio['projects_detail']) == 1
    
    def test_display_empty_portfolio_sections(self, mocker, capsys):
        """Test display handles missing portfolio sections gracefully"""
        builder = PortfolioBuilder()
        mock_cli = mocker.Mock()
        
        minimal_portfolio = {
            'portfolio_id': 'test-id',
            'result_id': 'result-id',
            'projects_detail': [],
            'skill_timeline': {},
            'growth_metrics': {'has_comparison': False}
        }
        
        # Shouldn't crash
        builder.display_portfolio(minimal_portfolio, cli=mock_cli)
        
        captured = capsys.readouterr()
        assert 'Portfolio ID:' in captured.out