import pytest
import orjson
from pathlib import Path
import tempfile
from anytree import Node
from repository_processor import RepositoryProcessor

# Helper function to create a basic repo node
def create_repo_node(name: str ="test_repo") -> Node:
    repo_node: Node = Node(name, type="directory")
    Node(".git", parent=repo_node, type="directory")
    return repo_node


class TestRepositoryProcessorBasics:
    # Tests for initialization and basic functionality
    
    def test_initialization(self) -> None:
        # Test processor initializes with correct attributes
        processor:RepositoryProcessor = RepositoryProcessor("test_user", [b"data1", b"data2"])
        assert processor.username == "test_user"
        assert len(processor.binary_data_array) == 2
        assert processor.temp_dirs == []
    
    def test_extract_git_folder_missing_git_node(self) -> None:
        # Test error when .git folder is missing
        repo_node: Node = Node("test_repo", type="directory")
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        with pytest.raises(ValueError, match="No .git folder found"):
            processor._extract_git_folder(repo_node)
    
    def test_extract_git_folder_creates_structure(self) -> None:
        # Test that .git folder structure is created
        repo_node: Node = create_repo_node()
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        try:
            temp_path: Path = processor._extract_git_folder(repo_node)
            assert temp_path.exists()
            assert (temp_path / ".git").exists()
            assert len(processor.temp_dirs) == 1
        finally:
            processor._cleanup_temp_dirs()

class TestRebuildGitTree:
    # Tests for _rebuild_git_tree method
    def test_rebuild_creates_files(self) -> None:
        # Test files are created from binary data
        git_node: Node = Node(".git", type="directory")
        Node("config", parent=git_node, type="file", binary_index=0)
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [b"test config data"])
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path: Path = Path(temp_dir)
            processor._rebuild_git_tree(git_node, temp_path)
            config_file: Path = temp_path / "config"
            assert config_file.exists()
            assert config_file.read_bytes() == b"test config data"
    
    def test_rebuild_creates_nested_structure(self) -> None:
        # Test nested directory structure is created correctly
        git_node: Node = Node(".git", type="directory")
        refs_dir: Node = Node("refs", parent=git_node, type="directory")
        heads_dir: Node = Node("heads", parent=refs_dir, type="directory")
        Node("main", parent=heads_dir, type="file", binary_index=0)
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [b"main branch ref"])
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path: Path = Path(temp_dir)
            processor._rebuild_git_tree(git_node, temp_path)
            main_file: Path = temp_path / "refs" / "heads" / "main"
            assert main_file.exists()
            assert main_file.read_bytes() == b"main branch ref"

class TestProcessRepositoriesJSON:
    # Tests for process_repositories method and JSON output
    def test_json_structure_single_repo(self) -> None:
        # Test JSON structure for single repository
        repo_node: Node = create_repo_node()
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        result: bytes = processor.process_repositories([repo_node])
        data: list = orjson.loads(result)
        
        assert isinstance(result, bytes)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["repository_name"] == "test_repo"
        assert data[0]["status"] == "success"
        assert "repository_path" in data[0]
    
    def test_json_multiple_repositories(self) -> None:
        # Test JSON output for multiple repositories
        repo1: Node = create_repo_node("repo1")
        repo2: Node = create_repo_node("repo2")
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        result: bytes = processor.process_repositories([repo1, repo2])
        data: list = orjson.loads(result)
        
        assert len(data) == 2
        assert data[0]["repository_name"] == "repo1"
        assert data[1]["repository_name"] == "repo2"

class TestCleanupAndErrorHandling:
    # Tests for cleanup and error handling
    def test_cleanup_on_error(self) -> None:
        # Test temp directories are cleaned up even on error
        repo_node: Node = Node("bad_repo", type="directory")
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        with pytest.raises(ValueError):
            processor.process_repositories([repo_node])
        assert len(processor.temp_dirs) == 0
    
    def test_cleanup_removes_directories(self) -> None:
        # Test cleanup removes all temporary directories
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        temp_dir1: str = tempfile.mkdtemp()
        temp_dir2: str = tempfile.mkdtemp()
        processor.temp_dirs = [temp_dir1, temp_dir2]
        processor._cleanup_temp_dirs()
        
        assert not Path(temp_dir1).exists()
        assert not Path(temp_dir2).exists()
        assert len(processor.temp_dirs) == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])