import pytest
from datetime import datetime
from project_success import ProjectSuccess


class TestProjectSuccess:
    
    @pytest.fixture
    def minimal_project_data(self):
        """Minimal valid project data structure"""
        return {
            'all_files': set(),
            'repository_context': {
                'total_commits_all_authors': 0,
                'repo_total_lines_added': 0,
                'repo_total_lines_deleted': 0,
                'all_commits_dates': [],
                'repository_date_range': {
                    'start_date': None,
                    'end_date': None,
                    'duration_days': 0
                }
            }
        }
    
    @pytest.fixture
    def project_with_deployment(self):
        """Project with deployment configs"""
        return {
            'all_files': {
                '.github/workflows/ci.yml',
                'dockerfile',
                'vercel.json'
            },
            'repository_context': {
                'total_commits_all_authors': 10,
                'repo_total_lines_added': 500,
                'repo_total_lines_deleted': 100,
                'all_commits_dates': [],
                'repository_date_range': {
                    'start_date': '2024-01-01T00:00:00',
                    'end_date': '2024-01-10T00:00:00',
                    'duration_days': 10
                }
            }
        }
    
    @pytest.fixture
    def project_with_commits(self):
        """Project with commit history"""
        start = datetime(2024, 1, 1)
        dates = [
            datetime(2024, 1, 1),   # Day 1
            datetime(2024, 1, 2),   # Day 2
            datetime(2024, 1, 3),   # Day 3
            datetime(2024, 1, 10),  # Day 10 (last quarter)
        ]
        return {
            'all_files': set(),
            'repository_context': {
                'total_commits_all_authors': 4,
                'repo_total_lines_added': 400,
                'repo_total_lines_deleted': 100,
                'all_commits_dates': dates,
                'repository_date_range': {
                    'start_date': '2024-01-01T00:00:00',
                    'end_date': '2024-01-10T00:00:00',
                    'duration_days': 10
                }
            }
        }
    
    @pytest.fixture
    def project_crammed_at_end(self):
        """Project with commits crammed at end"""
        dates = [
            datetime(2024, 1, 1),   # 1 commit early
            datetime(2024, 1, 9),   # Rest in last quarter
            datetime(2024, 1, 9),
            datetime(2024, 1, 10),
            datetime(2024, 1, 10),
        ]
        return {
            'all_files': set(),
            'repository_context': {
                'total_commits_all_authors': 5,
                'repo_total_lines_added': 500,
                'repo_total_lines_deleted': 100,
                'all_commits_dates': dates,
                'repository_date_range': {
                    'start_date': '2024-01-01T00:00:00',
                    'end_date': '2024-01-10T00:00:00',
                    'duration_days': 10
                }
            }
        }

    
    def test_detect_deployment_no_files(self, minimal_project_data):
        """Test with no deployment files"""
        ps = ProjectSuccess(minimal_project_data)
        result = ps.detect_deployment()
        
        assert result['has_cicd'] is False
        assert result['has_containerization'] is False
        assert result['has_hosting_platform'] is False
        assert len(result['cicd_tools']) == 0
        assert len(result['containerization_tools']) == 0
        assert len(result['hosting_platforms']) == 0
    
    def test_detect_deployment_github_actions(self):
        """Test GitHub Actions detection"""
        data = {
            'all_files': {'.github/workflows/deploy.yml'}
        }
        ps = ProjectSuccess(data)
        result = ps.detect_deployment()
        
        assert result['has_cicd'] is True
        assert 'GitHub Actions' in result['cicd_tools']
    
    def test_detect_deployment_docker(self):
        """Test Docker detection"""
        data = {
            'all_files': {'dockerfile', 'docker-compose.yml'}
        }
        ps = ProjectSuccess(data)
        result = ps.detect_deployment()
        
        assert result['has_containerization'] is True
        assert 'Docker' in result['containerization_tools']
        assert 'Docker Compose' in result['containerization_tools']
    
    def test_detect_deployment_hosting_platforms(self):
        """Test hosting platform detection"""
        data = {
            'all_files': {'vercel.json', 'netlify.toml', 'heroku.yml'}
        }
        ps = ProjectSuccess(data)
        result = ps.detect_deployment()
        
        assert result['has_hosting_platform'] is True
        assert 'Vercel' in result['hosting_platforms']
        assert 'Netlify' in result['hosting_platforms']
        assert 'Heroku' in result['hosting_platforms']
    
    def test_detect_deployment_all_types(self, project_with_deployment):
        """Test detection of all deployment types"""
        ps = ProjectSuccess(project_with_deployment)
        result = ps.detect_deployment()
        
        assert result['has_cicd'] is True
        assert result['has_containerization'] is True
        assert result['has_hosting_platform'] is True
    
    def test_detect_deployment_case_insensitive(self):
        """Test that file detection is case insensitive"""
        data = {
            'all_files': {'Dockerfile', 'DOCKERFILE'}  # stored as lowercase
        }
        ps = ProjectSuccess(data)
        result = ps.detect_deployment()
        
        # Should not detect because files should already be lowercased
        # This tests the assumption that all_files are already lowercase
        assert result['has_containerization'] is False

    def test_detect_deployment_files_already_lowercase(self):
        """Test with properly lowercased files"""
        data = {
            'all_files': {'dockerfile'}  # properly lowercased
        }
        ps = ProjectSuccess(data)
        result = ps.detect_deployment()
        
        assert result['has_containerization'] is True
        assert 'Docker' in result['containerization_tools']

    
    def test_version_control_no_commits(self, minimal_project_data):
        """Test with no commits"""
        ps = ProjectSuccess(minimal_project_data)
        result = ps.version_control_success_indicators()
        
        assert result['avg_lines_per_commit'] == 0
        assert 'No date information available' in result['commit_consistency']
    
    def test_version_control_lines_per_commit(self, project_with_commits):
        """Test average lines per commit calculation"""
        ps = ProjectSuccess(project_with_commits)
        result = ps.version_control_success_indicators()
        
        # (400 + 100) / 4 = 125
        assert result['avg_lines_per_commit'] == 125.0
    
    def test_version_control_well_distributed(self, project_with_commits):
        """Test well-distributed commits"""
        ps = ProjectSuccess(project_with_commits)
        result = ps.version_control_success_indicators()
        
        # 1 out of 4 commits in last quarter = 25%
        assert 'well-distributed' in result['commit_consistency'].lower()
    
    def test_version_control_crammed_at_end(self, project_crammed_at_end):
        """Test commits crammed at end"""
        ps = ProjectSuccess(project_crammed_at_end)
        result = ps.version_control_success_indicators()
        
        # 4 out of 5 commits in last quarter = 80%
        assert 'crammed at the end' in result['commit_consistency'].lower()
    
    def test_version_control_end_heavy(self):
        """Test end-heavy commits (50-75%)"""
        dates = [
            datetime(2024, 1, 1),
            datetime(2024, 1, 2),
            datetime(2024, 1, 8),  # Last quarter
            datetime(2024, 1, 9),  # Last quarter
            datetime(2024, 1, 10), # Last quarter
        ]
        data = {
            'all_files': set(),
            'repository_context': {
                'total_commits_all_authors': 5,
                'repo_total_lines_added': 500,
                'repo_total_lines_deleted': 100,
                'all_commits_dates': dates,
                'repository_date_range': {
                    'start_date': '2024-01-01T00:00:00',
                    'end_date': '2024-01-10T00:00:00',
                    'duration_days': 10
                }
            }
        }
        ps = ProjectSuccess(data)
        result = ps.version_control_success_indicators()
        
        # 3 out of 5 = 60%, should be "end-heavy"
        assert 'end-heavy' in result['commit_consistency'].lower()
    
    def test_version_control_missing_dates(self):
        """Test with missing date information"""
        data = {
            'all_files': set(),
            'repository_context': {
                'total_commits_all_authors': 5,
                'repo_total_lines_added': 500,
                'repo_total_lines_deleted': 100,
                'all_commits_dates': [],
                'repository_date_range': {
                    'start_date': None,
                    'end_date': None,
                    'duration_days': 0
                }
            }
        }
        ps = ProjectSuccess(data)
        result = ps.version_control_success_indicators()
        
        assert 'No date information available' in result['commit_consistency']

    
    def test_all_success_indicators(self, project_with_deployment):
        """Test combined success indicators"""
        ps = ProjectSuccess(project_with_deployment)
        result = ps.all_success_indicators()
        
        assert 'deployment' in result
        assert 'version_control' in result
        assert isinstance(result['deployment'], dict)
        assert isinstance(result['version_control'], dict)
    
    def test_all_success_indicators_structure(self, minimal_project_data):
        """Test that all_success_indicators returns correct structure"""
        ps = ProjectSuccess(minimal_project_data)
        result = ps.all_success_indicators()
        
        # Check deployment keys
        assert 'has_cicd' in result['deployment']
        assert 'has_containerization' in result['deployment']
        assert 'has_hosting_platform' in result['deployment']
        
        # Check version control keys
        assert 'avg_lines_per_commit' in result['version_control']
        assert 'commit_consistency' in result['version_control']
