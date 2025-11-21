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


class TestRepositoryAnalyzer:
    
    def test_initialization(self) -> None:
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("test_user")
        assert analyzer.username == "test_user"
    
    def test_build_commit_info(self) -> None:
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
        assert commit_info['message'] == ""
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
        
        analyzer: RepositoryAnalyzer = RepositoryAnalyzer("eveline36") # Just looking at initial commits so using eveline36
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