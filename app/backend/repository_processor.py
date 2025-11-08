from pathlib import Path
import tempfile
import shutil
from anytree import Node
from typing import Any, Dict, List, Optional
from pydriller import Repository

class RepositoryProcessor:
    def __init__(self, username: str, binary_data_array) -> None:
        self.username: str = username
        self.binary_data_array: List[bytes] = binary_data_array
        self.temp_dirs: List[str] = []

    def process_repositories(self, repo_nodes: List[Node]) -> List[Dict[str, Any]]:
        # Analyzes each repository node and extracts relevant information
        processed_data: List[Dict[str, Any]] = []
        try:
            for repo_node in repo_nodes:
                git_folder_path = self._extract_git_folder(repo_node) # This path is to the temporary .git folder that was rebuilt
                analysis: Dict[str, Any] = self._analyze_repository(repo_node, git_folder_path) # May change from Dict[str, Any] 
                processed_data.append(analysis)

        finally:
            # Clean up temporary directories
            self._cleanup_temp_dirs()

        return processed_data

    def _extract_git_folder(self, repo_node: Node) -> Path:
        # In order for PyDriller to access the commits, this rebuilds the .git folder for each repository temporarily
        temp_dir: str = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        temp_path: Path = Path(temp_dir)

        git_node: Optional[Node] = None
        for child in repo_node.children: # Check all children for git node since repo_node is attached to .git parent
            if child.name == ".git":
                git_node = child
                break
        
        if not git_node: 
            raise ValueError("No .git folder found in the repository node.")
        
        git_path: Path = temp_path / ".git"
        git_path.mkdir(parents=True, exist_ok=True) # Create .git directory in temp location
        self._rebuild_git_tree(git_node, git_path) # recursive method to build all sub folder in .git for PyDriller

        return temp_path

    def _rebuild_git_tree(self, git_node: Node, current_path: Path) -> None:
        # Where we actually reconstruct .git file so PyDriller can access needed files
        for child in git_node.children:
            if hasattr(child, 'type'):
                if child.type == 'file':

                    #Write file from binary data
                    file_path: Path = current_path / child.name
                    binary_index: int = child.binary_index

                    if binary_index < len(self.binary_data_array):
                        binary_data: bytes = self.binary_data_array[binary_index]
                        file_path.write_bytes(binary_data)

                elif child.type == 'directory':
                    dir_path: Path = current_path / child.name
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self._rebuild_git_tree(child, dir_path)

    def _analyze_repository(self, repo_node: Node, git_folder_path: Path) -> Dict[str, Any]:
        # Analyze a single repository using PyDriller to extract commit information
        # TODO: Expand on this method to extract data specific to research needs
        try:
            repo = Repository(str(git_folder_path))
            commits_data = []
            
            for commit in repo.traverse_commits():
                # Safely extract author information with fallbacks
                commit_info = {
                    'hash': commit.hash if commit.hash else "Unknown",
                    'author': commit.author.name if commit.author and commit.author.name else "Unknown",
                    'author_email': commit.author.email if commit.author and commit.author.email else "unknown@unknown.com",
                    'date': commit.author_date.isoformat() if commit.author_date else "Unknown",
                    'message': commit.msg if commit.msg else "",
                    'modified_files': [
                        {
                            'filename': mod.filename if mod.filename else "Unknown",
                            'change_type': mod.change_type.name if mod.change_type else "UNKNOWN",
                            'added_lines': mod.added_lines if mod.added_lines is not None else 0,
                            'deleted_lines': mod.deleted_lines if mod.deleted_lines is not None else 0
                        }
                        for mod in (commit.modified_files or [])
                    ]
                }
                commits_data.append(commit_info)

            return {
                'repository_name': repo_node.name if repo_node.name else "Unknown",
                'repository_path': str(git_folder_path),
                'status': 'success',
                'commits': commits_data,
                'commit_count': len(commits_data)
            }
        except Exception as e:
            return {
                'repository_name': repo_node.name,
                'repository_path': str(git_folder_path),
                'status': 'error',
                'error_message': str(e)
            }


    def _cleanup_temp_dirs(self) -> None:
        for temp_dir in self.temp_dirs:
            try:
                if Path(temp_dir).exists():
                    shutil.rmtree(temp_dir)
            
            except Exception as e:
                print(f"Warning: Could not remove temporary directory {temp_dir}: {e}")
        
        self.temp_dirs = []
