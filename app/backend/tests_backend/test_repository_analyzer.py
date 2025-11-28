from typing import Any, Dict, List
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock
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

    def test_create_chronological_list(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        all_repo_data: List[Dict[str, Any]] = [
            create_mock_project_data('Project A', start_date='2024-01-01T00:00:00'),
            create_mock_project_data('Project B', start_date='2024-03-01T00:00:00')
        ]

        projects: List[Dict[str, Any]] = analyzer.create_chronological_project_list(all_repo_data)

        assert len(projects) == 2
        assert projects[0]['name'] == 'Project B'  # More recent first

    def test_create_chronological_list_filters_errors(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        all_repo_data: List[Dict[str, Any]] = [
            create_mock_project_data('Good'),
            {'status': 'error', 'repository_name': 'Bad'}
        ]

        projects: List[Dict[str, Any]] = analyzer.create_chronological_project_list(all_repo_data)

        assert len(projects) == 1

    def test_create_chronological_list_empty(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        projects: List[Dict[str, Any]] = analyzer.create_chronological_project_list([])

        assert len(projects) == 0

    def test_normalize_for_rankings_normal_case(self):
        result = RepositoryAnalyzer.normalize_for_rankings(5, 10, 0)
        assert result == 0.5

    def test_normalize_for_rankings_zero_denominator(self):
        result = RepositoryAnalyzer.normalize_for_rankings(5, 5, 5)
        assert result == 0

    def test_rank_importance_of_projects(self):
        analyzer = RepositoryAnalyzer("testuser")
        projects = [
            create_mock_project_data("Low", user_commits_count=5, lines_added=100, duration_days=5),
            create_mock_project_data("Medium", user_commits_count=8, lines_added=300, duration_days=8),
            create_mock_project_data("High", user_commits_count=10, lines_added=500, duration_days=10),
        ]
        
        ranked = analyzer.rank_importance_of_projects(projects)
        
        # Make sure our importance key exists
        for p in ranked:
            assert 'importance' in p
        
        # third project listed should be first after getting ranked 
        assert ranked[0]['repository_name'] == 'High'

    def test_get_top3_most_important_projects(self):
        analyzer = RepositoryAnalyzer("testuser")
        all_repo_data = [
            create_mock_project_data('A', user_commits_count=5, lines_added=200, duration_days=5, start_date='2024-02-01T00:00:00'),
            create_mock_project_data('B', user_commits_count=8, lines_added=300, duration_days=8, start_date='2024-03-01T00:00:00'),
            create_mock_project_data('C', user_commits_count=2, lines_added=100, duration_days=2, start_date='2024-04-01T00:00:00'),
            create_mock_project_data('D', user_commits_count=10, lines_added=500, duration_days=10, start_date='2024-01-01T00:00:00'),
        ]

        top3 = analyzer.get_most_important_projects(all_repo_data)
        assert len(top3) == 3
        assert top3[0]['repository_name'] == 'D'

    def test_get_most_important_projects_empty(self):
        analyzer = RepositoryAnalyzer("testuser")
        top3 = analyzer.get_most_important_projects([])
        assert top3 == []

    def test_extract_repo_import_stats_python_basic(self):
        analyzer = RepositoryAnalyzer("testuser")
        project = create_mock_project_data("RepoA")
        project['user_commits'][0]['modified_files'][0]['filename'] = "a.py"
        project['user_commits'][0]['modified_files'][0]['source_code'] = "import os\nfrom math import sin"
        # Clear other commits to avoid default imports
        for i in range(1, len(project['user_commits'])):
            project['user_commits'][i]['modified_files'][0]['source_code'] = ""

        imports_summary = analyzer.extract_repo_import_stats(project)
        assert "os" in imports_summary and "math" in imports_summary
        assert imports_summary["os"]["frequency"] == 1

    def test_extract_repo_import_stats_multiple_languages(self):
        analyzer = RepositoryAnalyzer("testuser")
        
        # Test Python aliases
        project = create_mock_project_data("RepoB")
        project['user_commits'][0]['modified_files'][0] = {
            'filename': "b.py", 'source_code': "import numpy as np, pandas as pd\nfrom os.path import join"
        }
        imports_summary = analyzer.extract_repo_import_stats(project)
        assert all(imp in imports_summary for imp in ["numpy", "pandas", "os.path"])
        
        # Test JavaScript
        project['user_commits'][0]['modified_files'][0] = {
            'filename': "app.js", 'source_code': 'import fs from "fs";\nimport { join } from "path";'
        }
        imports_summary = analyzer.extract_repo_import_stats(project)
        assert "fs" in imports_summary and "path" in imports_summary
        
        # Test Java
        project['user_commits'][0]['modified_files'][0] = {
            'filename': "Example.java", 'source_code': "import java.util.List;\nimport java.io.File;"
        }
        imports_summary = analyzer.extract_repo_import_stats(project)
        assert "java.util.List" in imports_summary and "java.io.File" in imports_summary
        
        # Test C++
        project['user_commits'][0]['modified_files'][0] = {
            'filename': "main.cpp", 'source_code': "#include <iostream>\n#include <vector>"
        }
        imports_summary = analyzer.extract_repo_import_stats(project)
        assert "iostream" in imports_summary and "vector" in imports_summary

    def test_extract_repo_import_stats_dates(self):
        analyzer = RepositoryAnalyzer("testuser")
        project = create_mock_project_data("RepoC")
        project['user_commits'] = [
            {'date': '2024-01-01T00:00:00', 'modified_files': [{'filename': 'a.py', 'source_code': 'import os'}]},
            {'date': '2024-01-10T00:00:00', 'modified_files': [{'filename': 'b.py', 'source_code': 'from math import sqrt'}]}
        ]

        imports_summary = analyzer.extract_repo_import_stats(project)
        assert imports_summary["os"]["start_date"] == "2024-01-01T00:00:00"
        assert imports_summary["math"]["duration_days"] == 0

    def test_extract_all_repo_import_stats_aggregates_repos(self):
        analyzer = RepositoryAnalyzer("testuser")
        project_data = [create_mock_project_data("Repo1"), create_mock_project_data("Repo2")]
        result = analyzer.get_all_repo_import_stats(project_data)
        assert len(result) == 2 and all("imports_summary" in r for r in result)

    def test_sort_imports_in_chronological_order(self):
        analyzer = RepositoryAnalyzer("testuser")
        repo_summary = {
            "repository_name": "RepoX",
            "imports_summary": {
                "os": {"start_date": "2024-01-02T00:00:00", "end_date": "2024-01-02T00:00:00", "frequency": 1, "duration_days": 0},
                "sys": {"start_date": "2024-01-05T00:00:00", "end_date": "2024-01-05T00:00:00", "frequency": 1, "duration_days": 0},
            }
        }
        sorted_summary = analyzer.sort_repo_imports_in_chronological_order(repo_summary)
        assert list(sorted_summary["imports_summary"].keys()) == ["sys", "os"]  # sys is newer, so is first

    def test_insights_generation(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        
        # Test full project insights
        project_data = [
            create_mock_project_data("Repo1", user_commits_count=10, lines_added=500),
            create_mock_project_data("Repo2", user_commits_count=5, lines_added=200)
        ]
        result = analyzer.generate_project_insights(project_data)
        assert len(result) == 2 and result[0]['importance_rank'] == 1
        assert all(k in result[0] for k in ['contribution_analysis', 'collaboration_insights', 'testing_insights', 'imports_summary'])
        
        # Test contribution insights - sole contributor
        project = create_mock_project_data(total_contributors=1)
        result = analyzer._calculate_contribution_insights(project)
        assert result['contribution_level'] == 'Sole Contributor' and result['rank_by_commits'] == 1
        
        # Test contribution insights - ranked
        project = create_mock_project_data(user_commits_count=8, total_contributors=5)
        project['repository_context']['all_authors_stats'] = {
            'testuser@example.com': {'commits': 8}, 'user1@example.com': {'commits': 10},
            'user2@example.com': {'commits': 5}, 'user3@example.com': {'commits': 3}, 'user4@example.com': {'commits': 2}
        }
        result = analyzer._calculate_contribution_insights(project)
        assert result['rank_by_commits'] == 2 and result['percentile'] == 60.0
        
        # Test collaboration insights
        project = create_mock_project_data(total_contributors=1)
        project['repository_context']['total_commits_all_authors'] = len(project['user_commits'])
        result = analyzer._generate_collaboration_insights(project)
        assert not result['is_collaborative'] and result['team_size'] == 1 and result['user_contribution_share_percentage'] == 100.0
        
        # Test testing insights
        project = create_mock_project_data()
        project['user_commits'] = [{'modified_files': [
            {'filename': 'test_main.py', 'added_lines': 50, 'deleted_lines': 0},
            {'filename': 'main.py', 'added_lines': 100, 'deleted_lines': 10}
        ]}]
        result = analyzer._generate_testing_insights(project)
        assert result['test_files_modified'] == 1 and result['testing_percentage_files'] == 50.0 and result['has_tests']

    def test_edge_cases(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        
        # Empty lists
        assert analyzer.generate_project_insights([]) == []
        
        # Unknown user
        result = RepositoryAnalyzer("unknownuser")._calculate_contribution_insights(create_mock_project_data())
        assert result['contribution_level'] == 'Unknown'
        
        # Error handling
        result = analyzer.get_all_repo_import_stats([create_mock_project_data("Repo1"), {'status': 'error', 'repository_name': 'BadRepo'}])
        assert len(result) == 2 and 'error' in result[1]
