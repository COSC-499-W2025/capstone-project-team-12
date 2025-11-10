from typing import Any, Dict, List
import pytest
from pathlib import Path
import tempfile
from anytree import Node
from repository_processor import RepositoryProcessor

# Helper function to create a basic repo node pointing to real test repo
def create_repo_node(name: str = "capstone_team12_testrepo") -> Node:
    # Point to the actual test repo in your project
    test_repo_path = Path("/app/backend/tests_backend/test_main_dir/capstone_team12_testrepo")
    repo_node: Node = Node(name, type="directory", path=str(test_repo_path))
    Node(".git", parent=repo_node, type="directory", path=str(test_repo_path / ".git"))
    return repo_node


class TestRepositoryProcessorBasics:
    # Tests for initialization and basic functionality
    
    def test_initialization(self) -> None:
        # Test processor initializes with correct attributes
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [b"data1", b"data2"])
        assert processor.username == "test_user"
        assert len(processor.binary_data_array) == 2
        assert processor.temp_dirs == []
    
    def test_extract_git_folder_missing_git_node(self) -> None:
        # Test error when .git folder is missing
        repo_node: Node = Node("test_repo", type="directory", path="/fake/path")
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

class TestProcessRepositories:
    # Tests for process_repositories method - just check it doesn't crash
    def test_process_repositories_runs_without_error(self) -> None:
        # Test that it returns a list of dicts
        repo_node: Node = create_repo_node()
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        result: List[Dict[str, Any]] = processor.process_repositories([repo_node])
        
        # Check it returns a list
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], dict)

class TestAnalyzeRepository:
    # Tests for _analyze_repository method with PyDriller integration
    
    def test_analyze_repository_returns_error_for_empty_git(self) -> None:
        # Test that analysis returns error status for empty/invalid .git folder
        repo_node: Node = create_repo_node()
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        
        # Create empty temp directory (no actual .git contents)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path: Path = Path(temp_dir)
            (temp_path / ".git").mkdir()  # Create empty .git
            
            result: Dict[str, Any] = processor._analyze_repository(repo_node, temp_path)
            
            # Should return error since .git is empty/invalid
            assert result['status'] == 'error'
            assert 'error_message' in result
    
    def test_analyze_repository_handles_error_gracefully(self) -> None:
        # Test that analysis handles errors and returns error status
        repo_node: Node = Node("invalid_repo", type="directory", path="/nonexistent/path")
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        
        # Create a fake temp directory since _extract_git_folder would fail first
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path: Path = Path(temp_dir)
            result: Dict = processor._analyze_repository(repo_node, temp_path)
            
            assert result['status'] == 'error'
            assert result['repository_name'] == repo_node.name
            assert 'error_message' in result
            assert isinstance(result['error_message'], str)
    
    def test_analyze_repository_has_required_fields_on_error(self) -> None:
        # Test that error responses have all required fields
        repo_node: Node = Node("test_repo", type="directory", path="/fake/path")
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path: Path = Path(temp_dir)
            result: Dict = processor._analyze_repository(repo_node, temp_path)
            
            required_fields = ['repository_name', 'repository_path', 'status', 'error_message']
            for field in required_fields:
                assert field in result, f"Missing required field: {field}"
            

class TestProcessRepositoriesWithAnalysis:
    # Integration tests for full processing with PyDriller analysis
    
    def test_process_repositories_returns_valid_structure(self) -> None:
        # Test that process_repositories returns valid structure
        repo_node: Node = create_repo_node()
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        result: List[Dict[str, Any]] = processor.process_repositories([repo_node])
        
        assert isinstance(result, list)
        assert len(result) == 1
        
        repo_data = result[0]
        assert 'repository_name' in repo_data
        assert 'repository_path' in repo_data
        assert 'status' in repo_data
        
    
    def test_process_multiple_repositories(self) -> None:
        # Test processing multiple repositories
        repo_node1: Node = create_repo_node("repo1")
        repo_node2: Node = create_repo_node("repo2")
        
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        result: List[Dict[str, Any]] = processor.process_repositories([repo_node1, repo_node2])
        
        assert len(result) == 2
        assert result[0]['repository_name'] == "repo1"
        assert result[1]['repository_name'] == "repo2"
        
    
    def test_process_repositorie_has_status_field(self) -> None:
        # Test that return has status field
        repo_node: Node = create_repo_node()
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        result: List[Dict[str, Any]] = processor.process_repositories([repo_node])
        
        repo_data = result[0]
        
        assert 'status' in repo_data
        assert repo_data['status'] in ['success', 'error']
        

class TestCleanupAndErrorHandling:
    # Tests for cleanup and error handling
    def test_cleanup_on_error(self) -> None:
        # Test temp directories are cleaned up even on error
        repo_node: Node = Node("bad_repo", type="directory", path="/nonexistent")
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        
        with pytest.raises(ValueError, match="No .git folder found"):
            processor.process_repositories([repo_node])
        
        # Verify cleanup happened (temp_dirs should still be cleaned up in finally block)
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