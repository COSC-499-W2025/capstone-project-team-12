from typing import Any, Dict, List
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, MagicMock
from anytree import Node
from repository_analyzer import RepositoryAnalyzer

# Test repository path constant
TEST_REPO_PATH: Path = Path("tests_backend/test_main_dir/capstone_team12_testrepo")


def create_repo_node(name: str = "capstone_team12_testrepo") -> Node:
    repo_node: Node = Node(name, type="directory", path=str(TEST_REPO_PATH))
    Node(".git", parent=repo_node, type="directory", path=str(TEST_REPO_PATH / ".git"))
    return repo_node


def create_mock_project_data(
    repo_name: str = "TestRepo",
    user_commits_count: int = 5,
    lines_added: int = 100,
    duration_days: int = 30,
    start_date: str = "2024-01-01T00:00:00",
    end_date: str = "2024-01-31T00:00:00",
    total_contributors: int = 1,
    is_collaborative: bool = False
) -> Dict[str, Any]:
    """Helper function to create mock project data"""
    user_commits = [
        {
            'hash': f'hash{i}',
            'date': start_date,
            'modified_files': [
                {
                    'filename': f'file{i}.py',
                    'change_type': 'MODIFY',
                    'added_lines': lines_added // user_commits_count,
                    'deleted_lines': 10,
                    'source_code': 'import os\nimport sys'
                }
            ]
        }
        for i in range(user_commits_count)
    ]
    
    return {
        'status': 'success',
        'repository_name': repo_name,
        'user_commits': user_commits,
        'statistics': {
            'user_files_modified': user_commits_count,
            'user_lines_added': lines_added,
            'user_lines_deleted': 50,
            'change_types': {'MODIFY', 'ADD'}
        },
        'repository_context': {
            'total_contributors': total_contributors,
            'total_commits_all_authors': user_commits_count * 2,
            'repo_total_lines_added': lines_added * 2,
            'repo_total_lines_deleted': 100,
            'repo_total_files_modified': user_commits_count * 2,
            'all_authors_stats': {
                'testuser@example.com': {
                    'commits': user_commits_count,
                    'lines_added': lines_added,
                    'lines_deleted': 50,
                    'files_modified': user_commits_count
                }
            },
            'is_collaborative': is_collaborative
        },
        'dates': {
            'start_date': start_date,
            'end_date': end_date,
            'duration_days': duration_days,
            'duration_seconds': duration_days * 86400
        }
    }


class TestRepositoryAnalyzer:
    
    def test_initialization(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("test_user")
        assert analyzer.username == "test_user"
    
    def test_generate_project_insights(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        project_data = [
            create_mock_project_data("Repo1", user_commits_count=10, lines_added=500),
            create_mock_project_data("Repo2", user_commits_count=5, lines_added=200),
            {'status': 'error', 'repository_name': 'BadRepo'}
        ]
        
        result = analyzer.generate_project_insights(project_data)
        
        assert len(result) == 2  # Filters errors
        assert result[0]['repository_name'] == 'Repo1'
        assert result[0]['importance_rank'] == 1
        assert all(k in result[0] for k in ['contribution_analysis', 'collaboration_insights', 'testing_insights', 'imports_summary'])
    
    def test_contribution_insights(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        
        # Test sole contributor
        project = create_mock_project_data(total_contributors=1)
        result = analyzer._calculate_contribution_insights(project)
        assert result['contribution_level'] == 'Sole Contributor'
        assert result['rank_by_commits'] == 1
        
        # Test ranked contributor
        project = create_mock_project_data(user_commits_count=8, total_contributors=5)
        project['repository_context']['all_authors_stats'] = {
            'testuser@example.com': {'commits': 8},
            'user1@example.com': {'commits': 10},
            'user2@example.com': {'commits': 5},
            'user3@example.com': {'commits': 3},
            'user4@example.com': {'commits': 2}
        }
        result = analyzer._calculate_contribution_insights(project)
        assert result['rank_by_commits'] == 2
        assert result['percentile'] == 60.0
    
    def test_extract_repo_import_stats(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        project = create_mock_project_data()
        
        # Test basic import extraction
        project['user_commits'][0]['modified_files'][0]['source_code'] = "import os\nfrom math import sin"
        project['user_commits'][0]['modified_files'][0]['filename'] = "test.py"
        for i in range(1, len(project['user_commits'])):
            project['user_commits'][i]['modified_files'][0]['source_code'] = ""
        
        result = analyzer.extract_repo_import_stats(project)
        assert "os" in result and "math" in result
        assert result["os"]["frequency"] == 1
        
        # Test date tracking
        project['user_commits'] = [
            {'date': '2024-01-01T00:00:00', 'modified_files': [{'filename': 'a.py', 'source_code': 'import os'}]},
            {'date': '2024-01-10T00:00:00', 'modified_files': [{'filename': 'b.py', 'source_code': 'import os'}]}
        ]
        result = analyzer.extract_repo_import_stats(project)
        assert result["os"]["duration_days"] == 9
        assert result["os"]["frequency"] == 2
    
    def test_get_all_repo_import_stats_handles_errors(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        project_data = [
            create_mock_project_data("Repo1"),
            {'status': 'error', 'repository_name': 'BadRepo'}
        ]
        
        result = analyzer.get_all_repo_import_stats(project_data)
        
        assert len(result) == 2
        assert 'error' in result[1]
    
    def test_edge_cases(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        
        # Test empty lists
        assert analyzer.generate_project_insights([]) == []
        assert analyzer.get_most_important_projects([]) == []
        
        # Test multiple import languages
        project = create_mock_project_data()
        test_cases = [
            ('import fs from "fs";\nconst path = require("path");', "app.js", ["fs", "path"]),
            ("import java.util.List;", "Main.java", ["java.util.List"]),
            ("#include <iostream>", "main.cpp", ["iostream"])
        ]
        for source_code, filename, expected_imports in test_cases:
            project['user_commits'][0]['modified_files'][0]['source_code'] = source_code
            project['user_commits'][0]['modified_files'][0]['filename'] = filename
            result = analyzer.extract_repo_import_stats(project)
            assert all(imp in result for imp in expected_imports)
        
        # Test unknown user
        analyzer_unknown = RepositoryAnalyzer("unknownuser")
        result = analyzer_unknown._calculate_contribution_insights(create_mock_project_data())
        assert result['contribution_level'] == 'Unknown' and result['rank_by_commits'] is None
        
        # Test empty commits
        project = create_mock_project_data()
        project['user_commits'] = []
        assert analyzer.extract_repo_import_stats(project) == {}
        
        # Test invalid dates filtered
        all_repo_data = [
            create_mock_project_data('Valid'),
            {'status': 'success', 'repository_name': 'Invalid', 'dates': {'start_date': None}}
        ]
        assert len(analyzer.create_chronological_project_list(all_repo_data)) == 1
        
        # Test zero commits edge case
        project = create_mock_project_data()
        project['user_commits'] = []
        project['repository_context']['total_commits_all_authors'] = 0
        result = analyzer._generate_collaboration_insights(project)
        assert result['user_contribution_share_percentage'] == 0.0
    
    def test_collaboration_insights_solo_project(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        project = create_mock_project_data(total_contributors=1, is_collaborative=False)
        project['repository_context']['total_commits_all_authors'] = len(project['user_commits'])
        
        result = analyzer._generate_collaboration_insights(project)
        
        assert result['is_collaborative'] == False
        assert result['team_size'] == 1
        assert result['user_contribution_share_percentage'] == 100.0
    
    def test_testing_insights(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        project = create_mock_project_data()
        project['user_commits'] = [{
            'modified_files': [
                {'filename': 'test_main.py', 'added_lines': 50, 'deleted_lines': 0},
                {'filename': 'main.py', 'added_lines': 100, 'deleted_lines': 10}
            ]
        }]
        
        result = analyzer._generate_testing_insights(project)
        assert result['test_files_modified'] == 1
        assert result['testing_percentage_files'] == 50.0
        assert result['has_tests'] == True
    
    def test_rank_and_normalize(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        projects = [
            create_mock_project_data("Low", user_commits_count=2, lines_added=50, duration_days=10),
            create_mock_project_data("High", user_commits_count=10, lines_added=500, duration_days=90)
        ]
        
        ranked = analyzer.rank_importance_of_projects(projects)
        assert ranked[0]['repository_name'] == "High"
        assert all('importance' in p for p in ranked)
        
        # Test normalization
        assert RepositoryAnalyzer.normalize_for_rankings(5, 10, 0) == 0.5
        assert RepositoryAnalyzer.normalize_for_rankings(5, 5, 5) == 0
    
    def test_get_most_important_projects(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        all_repo_data = [
            create_mock_project_data("A", user_commits_count=5, lines_added=200),
            create_mock_project_data("B", user_commits_count=10, lines_added=500),
            create_mock_project_data("C", user_commits_count=7, lines_added=300),
            create_mock_project_data("D", user_commits_count=2, lines_added=50)
        ]
        
        top3 = analyzer.get_most_important_projects(all_repo_data)
        
        assert len(top3) == 3
        assert top3[0]['repository_name'] == 'B'
    
    def test_chronological_and_sorting(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        
        # Test chronological project list
        all_repo_data = [
            create_mock_project_data('Project A', start_date='2024-01-01T00:00:00'),
            create_mock_project_data('Project B', start_date='2024-03-01T00:00:00')
        ]
        projects = analyzer.create_chronological_project_list(all_repo_data)
        assert len(projects) == 2
        assert projects[0]['name'] == 'Project B'  # More recent first
        
        # Test repo imports sorting
        repo_summary = {
            "repository_name": "RepoX",
            "imports_summary": {
                "os": {"start_date": "2024-01-02T00:00:00", "frequency": 1, "duration_days": 0},
                "sys": {"start_date": "2024-01-05T00:00:00", "frequency": 1, "duration_days": 0}
            }
        }
        sorted_summary = analyzer.sort_repo_imports_in_chronological_order(repo_summary)
        assert list(sorted_summary["imports_summary"].keys()) == ["sys", "os"]
        
        # Test all repo imports sorting
        all_repo_summaries = [
            {"repository_name": "Repo1", "imports_summary": {"os": {"start_date": "2024-01-01T00:00:00", "frequency": 2, "duration_days": 0}}},
            {"repository_name": "Repo2", "imports_summary": {"sys": {"start_date": "2024-01-10T00:00:00", "frequency": 1, "duration_days": 0}}}
        ]
        result = analyzer.sort_all_repo_imports_chronologically(all_repo_summaries)
        assert len(result) == 2
        assert result[0]["import"] == "sys"
        assert "start_dt" not in result[0]