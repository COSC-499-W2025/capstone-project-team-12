from pathlib import Path
import tempfile
import shutil
from anytree import Node
from typing import Any, Dict, List, Optional
import orjson 

class RepositoryProcessor:
    def __init__(self, username: str, binary_data_array) -> None:
        self.username: str = username
        self.binary_data_array: List[bytes] = binary_data_array
        self.temp_dirs: List[str] = []

    def process_repositories(self, repo_nodes: List[Node]) -> bytes:
        # Analyzes each repository node and extracts relevant information
        # Currently returns List[Dict[str, Any]] where each dict contains relevant commit information
        # This will be put into JSON format to be returned
        processed_data: List[Dict[str, Any]] = []
        try:
            for repo_node in repo_nodes:
                git_folder_path = self._extract_git_folder(repo_node) # This path is to the temporary .git folder that was rebuilt
                analysis: Dict[str, Any] = self._analyze_repository(repo_node, git_folder_path) # May change from Dict[str, Any] 
                processed_data.append(analysis)

        finally:
            # Clean up temporary directories
            self._cleanup_temp_dirs()

        json_data = orjson.dumps(processed_data, option=orjson.OPT_INDENT_2)
        return json_data    

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
        #Analyze a single repository using PyDriller.
        #TODO: Implement full analysis logic and PyDriller after debug
        # For now, return basic info to test that extraction works
        return {
            'repository_name': repo_node.name,
            'repository_path': str(git_folder_path),
            'status': 'success',
            'message': 'Git folder extracted successfully'
        }


    def _cleanup_temp_dirs(self) -> None:
        for temp_dir in self.temp_dirs:
            try:
                if Path(temp_dir).exists():
                    shutil.rmtree(temp_dir)
            
            except Exception as e:
                print(f"Warning: Could not remove temporary directory {temp_dir}: {e}")
        
        self.temp_dirs = []
