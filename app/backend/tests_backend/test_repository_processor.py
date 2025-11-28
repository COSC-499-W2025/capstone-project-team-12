from typing import Any, Dict, List
import pytest
from pathlib import Path
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch
from anytree import Node
from repository_processor import RepositoryProcessor
from pydriller.domain.commit import Commit


# Test repository path constant
TEST_REPO_PATH: Path = Path("tests_backend/test_main_dir/capstone_team12_testrepo")


def create_repo_node(name: str = "capstone_team12_testrepo") -> Node:
    """Helper function to create a basic repo node"""
    repo_node: Node = Node(name, type="directory", path=str(TEST_REPO_PATH))
    Node(".git", parent=repo_node, type="directory", path=str(TEST_REPO_PATH / ".git"))
    return repo_node


def create_mock_commit(
    commit_hash: str = "abc123",
    author_email: str = "testuser@example.com",
    author_date: datetime = datetime(2024, 1, 15),
    modified_files_data: List[Dict[str, Any]] = None
) -> Mock:
    """Helper function to create mock commit objects"""
    commit = Mock(spec=Commit)
    commit.hash = commit_hash
    commit.author = Mock()
    commit.author.email = author_email
    commit.author_date = author_date
    
    if modified_files_data is None:
        modified_files_data = [
            {
                'filename': 'test.py',
                'change_type': 'MODIFY',
                'added_lines': 10,
                'deleted_lines': 2,
                'source_code': 'print("hello")'
            }
        ]
    
    mock_files = []
    for file_data in modified_files_data:
        mock_file = Mock()
        mock_file.filename = file_data.get('filename', 'unknown')
        mock_file.change_type = Mock()
        mock_file.change_type.name = file_data.get('change_type', 'MODIFY')
        mock_file.added_lines = file_data.get('added_lines', 0)
        mock_file.deleted_lines = file_data.get('deleted_lines', 0)
        mock_file.source_code = file_data.get('source_code', '')
        mock_files.append(mock_file)
    
    commit.modified_files = mock_files
    return commit


class TestRepositoryProcessor:
    
    def test_initialization(self) -> None:
        processor: RepositoryProcessor = RepositoryProcessor("TestUser", [b"data1", b"data2"])
        assert processor.username == "testuser"  # Lowercase conversion
        assert len(processor.binary_data_array) == 2
        assert processor.temp_dirs == []
    
    def test_extract_git_folder(self) -> None:
        # Test missing .git node
        repo_node: Node = Node("test_repo", type="directory", path="/fake/path")
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        with pytest.raises(ValueError, match="No .git folder found"):
            processor._extract_git_folder(repo_node)
        
        # Test creates structure
        repo_node = Node("test_repo", type="directory")
        git_node: Node = Node(".git", parent=repo_node, type="directory")
        Node("config", parent=git_node, type="file", binary_index=0)
        processor = RepositoryProcessor("test_user", [b"test config"])
        try:
            temp_path: Path = processor._extract_git_folder(repo_node)
            assert temp_path.exists() and (temp_path / ".git").exists()
            assert len(processor.temp_dirs) == 1
        finally:
            processor._cleanup_temp_dirs()
    
    def test_rebuild_git_tree(self) -> None:
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [b"test config data", b"main branch ref"])
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path: Path = Path(temp_dir)
            
            # Test creates files
            git_node: Node = Node(".git", type="directory")
            Node("config", parent=git_node, type="file", binary_index=0)
            processor._rebuild_git_tree(git_node, temp_path)
            assert (temp_path / "config").read_bytes() == b"test config data"
            
            # Test creates nested structure
            git_node = Node(".git", type="directory")
            refs_dir: Node = Node("refs", parent=git_node, type="directory")
            heads_dir: Node = Node("heads", parent=refs_dir, type="directory")
            Node("main", parent=heads_dir, type="file", binary_index=1)
            processor._rebuild_git_tree(git_node, temp_path)
            assert (temp_path / "refs" / "heads" / "main").read_bytes() == b"main branch ref"
    
    def test_build_commit_info(self) -> None:
        processor: RepositoryProcessor = RepositoryProcessor("testuser", [])
        
        # Test complete data
        commit = create_mock_commit()
        commit_info = processor._build_commit_info(commit)
        assert commit_info['hash'] == "abc123"
        assert commit_info['date'] == "2024-01-15T00:00:00"
        assert len(commit_info['modified_files']) == 1
        assert commit_info['modified_files'][0]['filename'] == "test.py"
        
        # Test None values
        commit = Mock()
        commit.hash = None
        commit.author_date = None
        commit.modified_files = None
        commit_info = processor._build_commit_info(commit)
        assert commit_info['hash'] == "Unknown"
        assert commit_info['date'] == "Unknown"
        assert commit_info['modified_files'] == []
    
    def test_calculate_date_range(self) -> None:
        processor: RepositoryProcessor = RepositoryProcessor("testuser", [])
        
        # Test normal range
        dates: List[datetime] = [datetime(2024, 1, 1), datetime(2024, 1, 15), datetime(2024, 1, 10)]
        result = processor._calculate_date_range(dates)
        assert result['start_date'] == "2024-01-01T00:00:00"
        assert result['end_date'] == "2024-01-15T00:00:00"
        assert result['duration_days'] == 14
        
        # Test empty list
        result = processor._calculate_date_range([])
        assert result['start_date'] is None and result['duration_days'] == 0
    
    def test_extract_commits_data(self) -> None:
        processor: RepositoryProcessor = RepositoryProcessor("testuser", [])
        mock_repo = Mock()
        
        # Test single user
        commits = [
            create_mock_commit("hash1", "testuser@example.com", datetime(2024, 1, 1)),
            create_mock_commit("hash2", "testuser@example.com", datetime(2024, 1, 5))
        ]
        mock_repo.traverse_commits.return_value = commits
        result = processor._extract_commits_data(mock_repo)
        assert len(result['user_commits_data']) == 2
        assert result['user_statistics']['user_lines_added'] == 20
        assert result['repository_context']['is_collaborative'] == False
        
        # Test multiple users
        commits = [
            create_mock_commit("hash1", "testuser@example.com", datetime(2024, 1, 1)),
            create_mock_commit("hash2", "otheruser@example.com", datetime(2024, 1, 2)),
            create_mock_commit("hash3", "testuser@example.com", datetime(2024, 1, 3))
        ]
        mock_repo.traverse_commits.return_value = commits
        result = processor._extract_commits_data(mock_repo)
        assert len(result['user_commits_data']) == 2
        assert result['repository_context']['total_contributors'] == 2
        assert result['repository_context']['is_collaborative'] == True
        
        # Test GitHub privacy email
        commits = [create_mock_commit("hash1", "12345+testuser@users.noreply.github.com", datetime(2024, 1, 1))]
        mock_repo.traverse_commits.return_value = commits
        result = processor._extract_commits_data(mock_repo)
        assert len(result['user_commits_data']) == 1
    
    @patch('repository_processor.Repository')
    def test_extract_all_repository_data(self, mock_repo_class) -> None:
        processor: RepositoryProcessor = RepositoryProcessor("testuser", [])
        repo_node: Node = Node("test_repo")
        git_path: Path = Path("/fake/path")
        
        # Test success case
        mock_repo_instance = Mock()
        mock_repo_class.return_value = mock_repo_instance
        commits = [create_mock_commit("hash1", "testuser@example.com", datetime(2024, 1, 1))]
        mock_repo_instance.traverse_commits.return_value = commits
        result = processor._extract_all_repository_data(repo_node, git_path)
        assert result['status'] == 'success'
        assert result['repository_name'] == "test_repo"
        assert all(k in result for k in ['user_commits', 'statistics', 'repository_context', 'dates'])
        
        # Test error case
        mock_repo_class.side_effect = Exception("Repository error")
        result = processor._extract_all_repository_data(repo_node, git_path)
        assert result['status'] == 'error'
        assert 'error_message' in result
    
    @patch.object(RepositoryProcessor, '_extract_git_folder')
    @patch.object(RepositoryProcessor, '_extract_all_repository_data')
    @patch.object(RepositoryProcessor, '_cleanup_temp_dirs')
    def test_process_repositories(self, mock_cleanup, mock_extract_data, mock_extract_git) -> None:
        processor: RepositoryProcessor = RepositoryProcessor("testuser", [])
        repo_node: Node = Node("test_repo")
        
        # Test success case
        mock_extract_git.return_value = Path("/fake/path")
        mock_extract_data.return_value = {'status': 'success', 'repository_name': 'test_repo', 'user_commits': []}
        result = processor.process_repositories([repo_node])
        assert isinstance(result, list) and len(result) == 1
        assert result[0]['status'] == 'success'
        
        # Test cleanup on error
        mock_extract_git.side_effect = Exception("Test error")
        with pytest.raises(Exception):
            processor.process_repositories([repo_node])
        mock_cleanup.assert_called()
    
    def test_cleanup_removes_directories(self) -> None:
        processor: RepositoryProcessor = RepositoryProcessor("test_user", [])
        temp_dir1: str = tempfile.mkdtemp()
        temp_dir2: str = tempfile.mkdtemp()
        
        processor.temp_dirs = [temp_dir1, temp_dir2]
        processor._cleanup_temp_dirs()
        
        assert not Path(temp_dir1).exists()
        assert not Path(temp_dir2).exists()
        assert len(processor.temp_dirs) == 0