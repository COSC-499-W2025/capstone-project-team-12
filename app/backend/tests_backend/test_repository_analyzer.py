from typing import Any, Dict, List
import pytest
from pathlib import Path
from datetime import datetime
from repository_analyzer import RepositoryAnalyzer

TEST_FILE_DIR = Path(__file__).parent
TEST_REPO_PATH = TEST_FILE_DIR / "test_main_dir" / "capstone_team12_testrepo"


def create_mock_project_data(
    repo_name: str = "TestRepo", user_commits_count: int = 5, lines_added: int = 100,
    duration_days: int = 30, start_date: str = "2024-01-01T00:00:00", total_contributors: int = 1
) -> Dict[str, Any]:
    """Helper to create mock project data"""
    return {
        'status': 'success', 'repository_name': repo_name,
        'user_commits': [{'hash': f'h{i}', 'date': start_date, 'modified_files': [
            {'filename': f'f{i}.py', 'change_type': 'MODIFY', 'added_lines': lines_added // user_commits_count,
             'deleted_lines': 10, 'source_code': 'import os\nimport sys'}
        ]} for i in range(user_commits_count)],
        'statistics': {'user_files_modified': user_commits_count, 'user_lines_added': lines_added,
                       'user_lines_deleted': 50, 'change_types': {'MODIFY', 'ADD'}},
        'repository_context': {
            'total_contributors': total_contributors, 'total_commits_all_authors': user_commits_count * 2,
            'repo_total_lines_added': lines_added * 2, 'repo_total_lines_deleted': 100,
            'repo_total_files_modified': user_commits_count * 2, 'is_collaborative': total_contributors > 1,
            'all_authors_stats': {'target_user': {'commits': user_commits_count, 'lines_added': lines_added,
                                                            'lines_deleted': 50, 'files_modified': user_commits_count,
                                                            'is_target_user': True}}
        },
        'dates': {'start_date': start_date, 'end_date': start_date, 'duration_days': duration_days,
                  'duration_seconds': duration_days * 86400}
    }


class TestRepositoryAnalyzer:
    
    def test_initialization_and_chronological_list(self) -> None:
        analyzer = RepositoryAnalyzer("test_user")
        assert analyzer.username == "test_user"
        
        # Test chronological sorting
        data = [create_mock_project_data('A', start_date='2024-01-01T00:00:00'),
                create_mock_project_data('B', start_date='2024-03-01T00:00:00')]
        projects = analyzer.create_chronological_project_list(data)
        assert len(projects) == 2 and projects[0]['name'] == 'B'
        
        # Test filtering and edge cases (covers line 394)
        data_with_errors = [create_mock_project_data('Good'),
                            {'status': 'error', 'repository_name': 'Bad'},
                            {'status': 'success', 'repository_name': 'NoDate', 'dates': {'start_date': None}}]
        projects = analyzer.create_chronological_project_list(data_with_errors)
        assert len(projects) == 1
        assert analyzer.create_chronological_project_list([]) == []
    
    def test_ranking_and_importance(self):
        analyzer = RepositoryAnalyzer("testuser")
        assert RepositoryAnalyzer.normalize_for_rankings(5, 10, 0) == 0.5
        assert RepositoryAnalyzer.normalize_for_rankings(5, 5, 5) == 0
        
        projects = [create_mock_project_data("Low", 5, 100, 5),
                    create_mock_project_data("High", 10, 500, 10)]
        ranked = analyzer.rank_importance_of_projects(projects)
        assert ranked[0]['repository_name'] == 'High'
        
        top3 = analyzer.get_most_important_projects([*projects, create_mock_project_data("Mid", 8, 300, 8)])
        assert len(top3) == 3 and top3[0]['repository_name'] == 'High'
        assert analyzer.get_most_important_projects([]) == []
    
    
    def test_contribution_insights(self):
        analyzer = RepositoryAnalyzer("testuser")
        
        # Sole contributor
        project = create_mock_project_data(total_contributors=1)
        result = analyzer._calculate_contribution_insights(project)
        assert result['contribution_level'] == 'Sole Contributor'
        
        # Top contributor (line 274)
        project = create_mock_project_data(total_contributors=3)
        project['repository_context']['all_authors_stats'] = {
            'target_user': {'commits': 10, 'is_target_user': True}, 
            'contributor_1': {'commits': 5, 'is_target_user': False}, 
            'contributor_2': {'commits': 3, 'is_target_user': False}}
        assert analyzer._calculate_contribution_insights(project)['contribution_level'] == 'Top Contributor'
        
        # Major contributor (line 276) - need 76th percentile or higher
        project['repository_context']['all_authors_stats'] = {
            'target_user': {'commits': 9, 'is_target_user': True}, 
            'contributor_1': {'commits': 10, 'is_target_user': False}, 
            'contributor_2': {'commits': 5, 'is_target_user': False},
            'contributor_3': {'commits': 4, 'is_target_user': False}, 
            'contributor_4': {'commits': 2, 'is_target_user': False}}
        result = analyzer._calculate_contribution_insights(project)
        assert result['contribution_level'] == 'Significant Contributor' and result['percentile'] == 60.0
        
        # Regular contributor (line 280) - below 50th percentile
        project['repository_context']['all_authors_stats'] = {
            'contributor_1': {'commits': 10, 'is_target_user': False}, 
            'contributor_2': {'commits': 8, 'is_target_user': False}, 
            'contributor_3': {'commits': 6, 'is_target_user': False},
            'target_user': {'commits': 2, 'is_target_user': True}, 
            'contributor_4': {'commits': 4, 'is_target_user': False}}
        assert analyzer._calculate_contribution_insights(project)['contribution_level'] == 'Contributor'
        
        # Unknown user
        empty_project = create_mock_project_data()
        empty_project['repository_context']['all_authors_stats'] = {}
        assert RepositoryAnalyzer("unknown")._calculate_contribution_insights(empty_project)['contribution_level'] == 'Unknown'
    
    def test_full_insights_generation(self):
        analyzer = RepositoryAnalyzer("testuser")
        
        # Empty list
        assert analyzer.generate_project_insights([]) == []
        
        # Full insights
        data = [create_mock_project_data("R1", 10, 500), create_mock_project_data("R2", 5, 200)]
        result = analyzer.generate_project_insights(data)
        assert len(result) == 2 and result[0]['importance_rank'] == 1
        assert all(k in result[0] for k in ['contribution_analysis', 'collaboration_insights', 'testing_insights'])
        
        # Testing insights
        project = create_mock_project_data()
        project['user_commits'] = [{'modified_files': [
            {'filename': 'test_main.py', 'added_lines': 50, 'deleted_lines': 0},
            {'filename': 'main.py', 'added_lines': 100, 'deleted_lines': 10}]}]
        result = analyzer._generate_testing_insights(project)
        assert result['test_files_modified'] == 1 and result['has_tests']
        
        # Collaboration insights
        project = create_mock_project_data(total_contributors=1)
        project['repository_context']['total_commits_all_authors'] = len(project['user_commits'])
        result = analyzer._generate_collaboration_insights(project)
        assert not result['is_collaborative'] and result['team_size'] == 1

    def test_infer_user_role_no_activity(self):
        analyzer = RepositoryAnalyzer("testuser")
        project_no_activity = create_mock_project_data()
        project_no_activity['statistics'] = {
            'user_lines_added': 0,
            'user_lines_deleted': 0,
            'user_files_modified': 0
        }
        result = analyzer.infer_user_role(project_no_activity)
        assert result['role'] == 'No Activity Detected'
        assert 'No meaningful contribution activity' in result['blurb']

    def test_infer_user_role_feature_developer(self):
        analyzer = RepositoryAnalyzer("testuser")
        project_feature_dev = create_mock_project_data()
        project_feature_dev['statistics'] = {
            'user_lines_added': 600,
            'user_lines_deleted': 100,
            'user_files_modified': 100
        }
        result = analyzer.infer_user_role(project_feature_dev)
        assert result['role'] == 'Feature Developer'
        assert 'substantial amount of new code' in result['blurb']

    def test_infer_user_role_code_refiner(self):
        analyzer = RepositoryAnalyzer("testuser")
        project_refiner = create_mock_project_data()
        project_refiner['statistics'] = {
            'user_lines_added': 100,
            'user_lines_deleted': 500,
            'user_files_modified': 100
        }
        result = analyzer.infer_user_role(project_refiner)
        assert result['role'] == 'Code Refiner'
        assert 'refining the existing codebase' in result['blurb']

    def test_infer_user_role_maintainer(self):
        analyzer = RepositoryAnalyzer("testuser")
        project_maintainer = create_mock_project_data()
        project_maintainer['statistics'] = {
            'user_lines_added': 100,
            'user_lines_deleted': 100,
            'user_files_modified': 500
        }
        result = analyzer.infer_user_role(project_maintainer)
        assert result['role'] == 'Maintainer'
        assert 'modifying existing files' in result['blurb']

    def test_infer_user_role_general_contributor(self):
        analyzer = RepositoryAnalyzer("testuser")
        project_general = create_mock_project_data()
        project_general['statistics'] = {
            'user_lines_added': 300,
            'user_lines_deleted': 300,
            'user_files_modified': 300
        }
        result = analyzer.infer_user_role(project_general)
        assert result['role'] == 'General Contributor'
        assert 'balanced contribution pattern' in result['blurb']

    def test_infer_user_role_feature_developer_threshold(self):
        analyzer = RepositoryAnalyzer("testuser")
        project_edge = create_mock_project_data()
        project_edge['statistics'] = {
            'user_lines_added': 501,  # Just over 50%
            'user_lines_deleted': 249,
            'user_files_modified': 250
        }
        result = analyzer.infer_user_role(project_edge)
        assert result['role'] == 'Feature Developer'

    def test_infer_user_role_code_refiner_threshold(self):
        analyzer = RepositoryAnalyzer("testuser")
        project_edge = create_mock_project_data()
        project_edge['statistics'] = {
            'user_lines_added': 200,
            'user_lines_deleted': 401,  # Just over 40%
            'user_files_modified': 399
        }
        result = analyzer.infer_user_role(project_edge)
        assert result['role'] == 'Code Refiner'