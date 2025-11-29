from typing import Any, Dict, List
import pytest
from pathlib import Path
import tempfile
from anytree import Node
from repository_processor import RepositoryProcessor

# Get test file directory and navigate to test repo - works on all OS
TEST_FILE_DIR = Path(__file__).parent
TEST_REPO_PATH = TEST_FILE_DIR / "test_main_dir" / "capstone_team12_testrepo"


def create_repo_node(name: str = "capstone_team12_testrepo") -> Node:
    """Create repo node pointing to test repository"""
    repo_node: Node = Node(name, type="directory", path=str(TEST_REPO_PATH))
    Node(".git", parent=repo_node, type="directory", path=str(TEST_REPO_PATH / ".git"))
    return repo_node


class TestRepositoryProcessorBasics:
    
    def test_initialization(self) -> None:
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [b"data1", b"data2"])
        assert processor.username == "test_user"
        assert len(processor.binary_data_array) == 2
        assert processor.temp_dirs == []
    
    def test_extract_git_folder_missing_git_node(self) -> None:
        repo_node: Node = Node("test_repo", type="directory", path="/fake/path")
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        with pytest.raises(ValueError, match="No .git folder found"):
            processor._extract_git_folder(repo_node)
    
    def test_extract_git_folder_creates_structure(self) -> None:
        repo_node: Node = create_repo_node()
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        try:
            temp_path: Path = processor._extract_git_folder(repo_node)
            assert temp_path.exists() and (temp_path / ".git").exists()
            assert len(processor.temp_dirs) == 1
        finally:
            processor._cleanup_temp_dirs()


class TestRebuildGitTree:

    def test_rebuild_creates_files(self) -> None:
        git_node: Node = Node(".git", type="directory")
        Node("config", parent=git_node, type="file", binary_index=0)
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [b"test config data"])
        with tempfile.TemporaryDirectory() as temp_dir:
            processor._rebuild_git_tree(git_node, Path(temp_dir))
            assert (Path(temp_dir) / "config").read_bytes() == b"test config data"
    
    def test_rebuild_creates_nested_structure(self) -> None:
        git_node: Node = Node(".git", type="directory")
        refs_dir: Node = Node("refs", parent=git_node, type="directory")
        heads_dir: Node = Node("heads", parent=refs_dir, type="directory")
        Node("main", parent=heads_dir, type="file", binary_index=0)
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [b"main branch ref"])
        with tempfile.TemporaryDirectory() as temp_dir:
            processor._rebuild_git_tree(git_node, Path(temp_dir))
            assert (Path(temp_dir) / "refs" / "heads" / "main").read_bytes() == b"main branch ref"
    
    def test_rebuild_with_missing_binary_index(self) -> None:
        git_node: Node = Node(".git", type="directory")
        Node("config", parent=git_node, type="file")
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [b"data"])
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError, match="missing binary_index attribute"):
                processor._rebuild_git_tree(git_node, Path(temp_dir))
    
    def test_rebuild_with_invalid_binary_index(self) -> None:
        git_node: Node = Node(".git", type="directory")
        Node("config", parent=git_node, type="file", binary_index=99)
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [b"data"])
        with tempfile.TemporaryDirectory() as temp_dir:
            processor._rebuild_git_tree(git_node, Path(temp_dir))
            assert not (Path(temp_dir) / "config").exists()


class TestProcessRepositories:
    
    def test_process_repositories_returns_list_of_dicts(self) -> None:
        repo_node: Node = create_repo_node()
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        result: List[Dict[str, Any]] = processor.process_repositories([repo_node])
        assert isinstance(result, list) and len(result) == 1 and isinstance(result[0], dict)
    
    def test_process_repositories_has_expected_keys(self) -> None:
        repo_node: Node = create_repo_node()
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        result: List[Dict[str, Any]] = processor.process_repositories([repo_node])
        assert all(k in result[0] for k in ['repository_name', 'repository_path', 'status'])
    
    def test_process_with_actual_username(self) -> None:
        # Covers lines 43-46, 90-151, 174 by using real repo with actual commits
        if not TEST_REPO_PATH.exists():
            pytest.skip("Test repository not found")
        
        processor: RepositoryProcessor = RepositoryProcessor("maddydeg", [])
        repo_node: Node = Node("capstone_team12_testrepo", type="directory")
        result: Dict[str, Any] = processor._extract_all_repository_data(repo_node, TEST_REPO_PATH)
        
        assert result['status'] == 'success'
        assert len(result['user_commits']) > 0
        assert result['statistics']['user_lines_added'] >= 0
        assert result['repository_context']['total_commits_all_authors'] > 0


class TestErrorHandlingAndCleanup:
    
    def test_extract_repository_data_handles_errors(self) -> None:
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        result: Dict[str, Any] = processor._extract_all_repository_data(
            Node("bad_repo", type="directory"), Path("/nonexistent")
        )
        assert result['status'] == 'error' and 'error_message' in result
    
    def test_cleanup_on_error(self) -> None:
        repo_node: Node = Node("bad_repo", type="directory", path="/nonexistent")
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        with pytest.raises(ValueError, match="No .git folder found"):
            processor.process_repositories([repo_node])
        assert len(processor.temp_dirs) == 0
    
    def test_cleanup_removes_directories(self) -> None:
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        temp_dir1, temp_dir2 = tempfile.mkdtemp(), tempfile.mkdtemp()
        processor.temp_dirs = [temp_dir1, temp_dir2]
        processor._cleanup_temp_dirs()
        assert not Path(temp_dir1).exists() and not Path(temp_dir2).exists()
    
    def test_cleanup_handles_nonexistent_directory(self) -> None:
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        processor.temp_dirs = ["/nonexistent/temp/dir"]
        processor._cleanup_temp_dirs()
        assert len(processor.temp_dirs) == 0
    
    def test_cleanup_handles_permission_error(self) -> None:
        # Covers lines 258-259 (exception handling in cleanup)
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        temp_dir: str = tempfile.mkdtemp()
        processor.temp_dirs = [temp_dir]
        
        import unittest.mock as mock
        with mock.patch('shutil.rmtree', side_effect=PermissionError("Mocked error")):
            processor._cleanup_temp_dirs()
        
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


class TestDateRangeCalculation:
    
    def test_calculate_date_range_with_dates(self) -> None:
        from datetime import datetime
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        dates = [datetime(2024, 1, 1, 10, 0, 0), datetime(2024, 1, 15, 14, 30, 0)]
        result: Dict[str, Any] = processor._calculate_date_range(dates)
        assert result['start_date'] == "2024-01-01T10:00:00"
        assert result['end_date'] == "2024-01-15T14:30:00"
        assert result['duration_days'] == 14
    
    def test_calculate_date_range_empty_list(self) -> None:
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        result: Dict[str, Any] = processor._calculate_date_range([])
        assert result['start_date'] is None and result['duration_days'] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])