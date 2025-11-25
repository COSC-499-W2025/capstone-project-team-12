from typing import Any, Dict, List
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock
from anytree import Node
from repository_analyzer import RepositoryAnalyzer
from pydriller import Repository


# Test repository path constant
TEST_REPO_PATH: Path = Path("tests_backend/test_main_dir/capstone_team12_testrepo")


def create_repo_node(name: str = "capstone_team12_testrepo") -> Node:
    repo_node: Node = Node(name, type="directory", path=str(TEST_REPO_PATH))
    Node(".git", parent=repo_node, type="directory", path=str(TEST_REPO_PATH / ".git"))
    return repo_node


class TestRepositoryAnalyzer:

    def test_initialization(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("test_user")
        assert analyzer.username == "test_user"

    def test_build_commit_info(self) -> None:
        # Uses mock commit object to test _build_commit_info

        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        commit: Mock = Mock()
        commit.hash = "abc123"
        commit.msg = "Test commit"
        commit.author_date = datetime(2024, 1, 15, 10, 30)

        mod_file: Mock = Mock()
        mod_file.filename = "test.py"
        mod_file.change_type = Mock()
        mod_file.change_type.name = "ADD"
        mod_file.added_lines = 10
        mod_file.deleted_lines = 2
        commit.modified_files = [mod_file]

        commit_info: Dict[str, Any] = analyzer._build_commit_info(commit)

        assert commit_info['hash'] == "abc123"
        assert commit_info['date'] == "2024-01-15T10:30:00"
        assert len(commit_info['modified_files']) == 1
        assert commit_info['modified_files'][0]['filename'] == "test.py"

    def test_build_commit_info_with_none_values(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        commit: Mock = Mock()
        commit.hash = None
        commit.msg = None
        commit.author_date = None
        commit.modified_files = None

        commit_info: Dict[str, Any] = analyzer._build_commit_info(commit)

        assert commit_info['hash'] == "Unknown"
        assert commit_info['modified_files'] == []

    def test_calculate_date_range(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        dates: List[datetime] = [
            datetime(2024, 1, 1),
            datetime(2024, 1, 15),
            datetime(2024, 1, 10)
        ]

        result: Dict[str, Any] = analyzer._calculate_date_range(dates)

        assert result['start_date'] == "2024-01-01T00:00:00"
        assert result['end_date'] == "2024-01-15T00:00:00"
        assert result['duration_days'] == 14

    def test_calculate_date_range_empty(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        result: Dict[str, Any] = analyzer._calculate_date_range([])

        assert result['start_date'] is None
        assert result['duration_days'] is None

    def test_analyze_repository_with_real_repo(self) -> None:
        if not TEST_REPO_PATH.exists() or not (TEST_REPO_PATH / ".git").exists():
            pytest.skip("Test repository not found")

        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("maddydeg") # Just looking at initial commits so using maddydeg
        repo_node: Node = create_repo_node()
        result: Dict[str, Any] = analyzer.analyze_repository(repo_node, TEST_REPO_PATH)

        assert 'status' in result
        assert result['repository_name'] == "capstone_team12_testrepo"

        if result['status'] == 'success':
            assert 'commit_count' in result
            assert 'statistics' in result

    def test_analyze_repository_invalid_path(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        repo_node: Node = Node("test_repo")
        result: Dict[str, Any] = analyzer.analyze_repository(repo_node, Path("/invalid"))

        assert result['status'] == 'error'
        assert 'error_message' in result

    def test_create_chronological_list(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        all_repo_data: List[Dict[str, Any]] = [
            {
                'status': 'success',
                'repository_name': 'Project A',
                'start_date': '2024-01-01T00:00:00',
                'commit_count': 10,
                'statistics': {'total_lines_added': 500}
            },
            {
                'status': 'success',
                'repository_name': 'Project B',
                'start_date': '2024-03-01T00:00:00',
                'commit_count': 5,
                'statistics': {'total_lines_added': 200}
            }
        ]

        projects: List[Dict[str, Any]] = analyzer.create_chronological_project_list(all_repo_data)

        assert len(projects) == 2
        assert projects[0]['name'] == 'Project B'  # More recent first



    def test_create_chronological_list_filters_errors(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("testuser")
        all_repo_data: List[Dict[str, Any]] = [
            {'status': 'success', 'repository_name': 'Good', 'start_date': '2024-01-01T00:00:00', 'statistics': {}},
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
            {'commit_count': 5, 'total_lines_added': 100, 'duration_days': 5},
            {'commit_count': 8, 'total_lines_added': 300, 'duration_days': 8},
            {'commit_count': 10, 'total_lines_added': 500, 'duration_days': 10},
        ]
        
        ranked = analyzer.rank_importance_of_projects(projects)
        
        # Make sure our importance key exists
        for p in ranked:
            assert 'importance' in p
        
        # third project listed should be first after getting ranked 
        assert ranked[0]['commit_count'] == 10


    def test_get_top3_most_important_projects(self):
        analyzer = RepositoryAnalyzer("testuser")
        all_repo_data = [
            {'status': 'success', 'repository_name': 'A', 'start_date': '2024-02-01T00:00:00',
            'commit_count': 5, 'duration_days': 5, 'statistics': {'total_lines_added': 200}},
            {'status': 'success', 'repository_name': 'B', 'start_date': '2024-03-01T00:00:00',
            'commit_count': 8, 'duration_days': 8, 'statistics': {'total_lines_added': 300}},
            {'status': 'success', 'repository_name': 'C', 'start_date': '2024-04-01T00:00:00',
            'commit_count': 2, 'duration_days': 2, 'statistics': {'total_lines_added': 100}},
            {'status': 'success', 'repository_name': 'D', 'start_date': '2024-01-01T00:00:00',
            'commit_count': 10, 'duration_days': 10, 'statistics': {'total_lines_added': 500}},
        ]

        top3 = analyzer.get_most_important_projects(all_repo_data)
        assert len(top3) == 3
        assert top3[0]['name'] == 'D'


    def test_get_most_important_projects_empty(self):
        analyzer = RepositoryAnalyzer("testuser")
        top3 = analyzer.get_most_important_projects([])
        assert top3 == []
    

    def test_extract_repo_import_stats_alias_and_multi_imports(self):
        analyzer = RepositoryAnalyzer("testuser")

        repo = Mock(spec=Repository)
        commit = Mock()
        commit.author = Mock(email="testuser")
        commit.author_date = datetime(2024, 1, 5)
        mod = Mock()
        mod.filename = "b.py"
        mod.source_code = "import numpy as np, pandas as pd\nfrom os.path import join as j, exists"
        commit.modified_files = [mod]
        repo.traverse_commits.return_value = [commit]

        result = analyzer.extract_repo_import_stats(repo, "RepoB")
        imports_summary = result["imports_summary"]

        assert "numpy" in imports_summary
        assert "pandas" in imports_summary
        assert "os.path.join" in imports_summary
        assert "os.path.exists" in imports_summary


    def test_extract_repo_import_stats_multiple_commits_and_dates(self):
        analyzer = RepositoryAnalyzer("testuser")
        repo = Mock(spec=Repository)

        commit1 = Mock()
        commit1.author = Mock(email="testuser")
        commit1.author_date = datetime(2024, 1, 1)
        mod1 = Mock()
        mod1.filename = "a.py"
        mod1.source_code = "import os"
        commit1.modified_files = [mod1]

        commit2 = Mock()
        commit2.author = Mock(email="testuser")
        commit2.author_date = datetime(2024, 1, 10)
        mod2 = Mock()
        mod2.filename = "b.py"
        mod2.source_code = "from math import sqrt"
        commit2.modified_files = [mod2]

        repo.traverse_commits.return_value = [commit1, commit2]

        result = analyzer.extract_repo_import_stats(repo, "RepoC")
        imports_summary = result["imports_summary"]

        assert imports_summary["os"]["start_date"] == "2024-01-01T00:00:00"
        assert imports_summary["os"]["end_date"] == "2024-01-01T00:00:00"
        assert imports_summary["math.sqrt"]["start_date"] == "2024-01-10T00:00:00"
        assert imports_summary["math.sqrt"]["end_date"] == "2024-01-10T00:00:00"
        assert imports_summary["math.sqrt"]["duration_days"] == 0


    def test_extract_repo_import_stats_js_imports(self):
        analyzer = RepositoryAnalyzer("testuser")
        repo = Mock(spec=Repository)
        commit = Mock()
        commit.author = Mock(email="testuser")
        commit.author_date = datetime(2024, 1, 3)
        mod = Mock()
        mod.filename = "app.js"
        mod.source_code = 'import fs from "fs";\nimport { join, resolve } from "path";'
        commit.modified_files = [mod]
        repo.traverse_commits.return_value = [commit]

        result = analyzer.extract_repo_import_stats(repo, "RepoJS")
        imports_summary = result["imports_summary"]

        assert "fs" in imports_summary
        assert "join" in imports_summary
        assert "resolve" in imports_summary
        assert imports_summary["fs"]["frequency"] == 1


    def test_extract_repo_import_stats_java_imports(self):
        analyzer = RepositoryAnalyzer("testuser")
        repo = Mock(spec=Repository)
        commit = Mock()
        commit.author = Mock(email="testuser")
        commit.author_date = datetime(2024, 1, 4)
        mod = Mock()
        mod.filename = "Example.java"
        mod.source_code = "import java.util.List;\nimport java.io.File;"
        commit.modified_files = [mod]
        repo.traverse_commits.return_value = [commit]

        result = analyzer.extract_repo_import_stats(repo, "RepoJava")
        imports_summary = result["imports_summary"]

        assert "java.util.List" in imports_summary
        assert "java.io.File" in imports_summary
        assert imports_summary["java.util.List"]["frequency"] == 1


    def test_extract_repo_import_stats_c_cpp_imports(self):
        analyzer = RepositoryAnalyzer("testuser")
        repo = Mock(spec=Repository)
        commit = Mock()
        commit.author = Mock(email="testuser")
        commit.author_date = datetime(2024, 1, 6)
        mod = Mock()
        mod.filename = "main.cpp"
        mod.source_code = "#include <iostream>\n#include <vector>"
        commit.modified_files = [mod]
        repo.traverse_commits.return_value = [commit]

        result = analyzer.extract_repo_import_stats(repo, "RepoCPP")
        imports_summary = result["imports_summary"]

        assert "iostream" in imports_summary
        assert "vector" in imports_summary
        assert imports_summary["iostream"]["frequency"] == 1


    def test_extract_all_repo_import_stats_aggregates_repos(self):
        analyzer = RepositoryAnalyzer("testuser")
        repo_node1 = create_repo_node("Repo1")
        repo_node2 = create_repo_node("Repo2")

        analyzer._extract_git_folder = Mock(side_effect=lambda node: "/fake/path/" + node.name)

        analyzer.extract_repo_import_stats = Mock(side_effect=lambda repo, name: {
            "repository_name": name,
            "imports_summary": {"os": {"frequency": 1, "start_date": "2024-01-02T00:00:00",
                                    "end_date": "2024-01-02T00:00:00", "duration_days": 0}}
        })

        result = analyzer.extract_all_repo_import_stats([repo_node1, repo_node2])

        assert len(result) == 2
        assert result[0]["repository_name"] == "Repo1"
        assert result[1]["repository_name"] == "Repo2"
        assert result[0]["imports_summary"]["os"]["frequency"] == 1
    

    def test_extract_repo_import_stats_python_basic(self):
        analyzer = RepositoryAnalyzer("testuser")
        repo = Mock(spec=Repository)
        commit = Mock()
        commit.author = Mock(email="testuser")
        commit.author_date = datetime(2024, 1, 2)
        mod = Mock()
        mod.filename = "a.py"
        mod.source_code = "import os\nfrom math import sin"
        commit.modified_files = [mod]
        repo.traverse_commits.return_value = [commit]

        result = analyzer.extract_repo_import_stats(repo, "RepoA")
        imports_summary = result["imports_summary"]

        assert result["repository_name"] == "RepoA"
        assert "os" in imports_summary
        assert "math.sin" in imports_summary
        assert imports_summary["os"]["frequency"] == 1
        assert imports_summary["math.sin"]["frequency"] == 1


    def test_sort_imports_in_chronological_order(self):
        analyzer = RepositoryAnalyzer("testuser")

        repo_summary = {
            "repository_name": "RepoX",
            "imports_summary": {
                "os": {"start_date": "2024-01-02T00:00:00", "end_date": "2024-01-02T00:00:00", "frequency": 1,
                    "duration_days": 0},
                "sys": {"start_date": "2024-01-05T00:00:00", "end_date": "2024-01-05T00:00:00", "frequency": 1,
                        "duration_days": 0},
            }
        }

        sorted_summary = analyzer.sort_imports_in_chronological_order(repo_summary)
        keys = list(sorted_summary["imports_summary"].keys())

        assert keys == ["sys", "os"]  # sys is newer -> first
    