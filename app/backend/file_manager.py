from pathlib import Path
from typing import Any, Dict, List, Tuple
import zipfile
import tempfile
import shutil
from anytree import Node, RenderTree
import os

class FileManager:
    def __init__(self):
        self.max_size_bytes: int = 4 * 1024 * 1024 * 1024  # 4GB
        self.temp_extract_dir: str | None = None
        self.file_tree: Node | None = None
        self.file_objects: List[Dict[str, Any]] = []
        self.binary_data_array: List[bytes] = []

    def load_from_filepath(self, filepath: str | Path) -> Dict[str, Any]:
        try:
            self.file_objects = []
            self.binary_data_array = []
            self.file_tree = None

            # Accept both string and Path inputs
            path: Path = Path(filepath).resolve()

            if not path.exists():
                raise FileNotFoundError(f"Path not found: {path}")

            # Create root node
            root_name: str = path.name if path.name else "root"
            self.file_tree = Node(
                root_name,
                type="directory",
                filepath=str(path),
                is_repo_head=False
            )

            # Load files and build tree
            self._load_files(path, self.file_tree)

            if not self.file_objects:
                return {
                    'status': 'error',
                    'message': 'No valid files found'
                }

            return {
                'status': 'success',
                'message': f'Loaded {len(self.file_objects)} file(s)',
                'tree': self.file_tree,
                'binary_data': self.binary_data_array
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'error_type': type(e).__name__
            }

    def _load_files(self, path: Path, parent_node: Node) -> None:
        # Handle single ZIP file directly
        if path.is_file() and path.suffix.lower() == '.zip':
            self._extract_and_load_zip(path, parent_node)

        # Handle single regular file
        elif path.is_file():
            if self._is_rar_file(path): #added line to deal with user uploading single rar file 
                return

            # Skip large single files and mark as invalid
            if path.stat().st_size > self.max_size_bytes:
                print(f"Skipping {path.name}: exceeds max file size limit ({self.max_size_bytes} bytes)")
                return


            file_obj, binary_index = self._load_single_file(path)
            if file_obj:
                Node(
                    file_obj['filename'],
                    parent=parent_node,
                    type="file",
                    binary_index=binary_index,
                    file_data=file_obj,
                    classification=None,
                    extension=file_obj['extension']
                )
                self.file_objects.append(file_obj)

        # Handle directories (now includes empty ones)
        elif path.is_dir():
            folder_nodes: Dict[str, Node] = {str(path): parent_node}
            all_subpaths = []
            
            # DEBUG: Counters
            debug_stats = {
                'total_items': 0,
                'hidden_items': 0,
                'git_folders': 0,
                'directories': 0,
                'files': 0,
                'permission_errors': 0
            }
            
            def walk_dir(dir_path: Path, depth=0):
                indent = "  " * depth
                print(f"{indent}Scanning: {dir_path.name}", flush=True)
                
                try:
                    items = list(dir_path.iterdir())
                    print(f"{indent}  Found {len(items)} items", flush=True)
                    
                    for item in items:
                        debug_stats['total_items'] += 1
                        all_subpaths.append(item)

                        # DEBUG: Log item details
                        is_hidden = item.name.startswith('.')
                        if is_hidden:
                            debug_stats['hidden_items'] += 1
                            print(f"{indent}  [HIDDEN] {item.name} (is_dir={item.is_dir()})", flush=True)

                        # Handle .git (accept directory or file)
                        if item.name == '.git':
                            git_path = item.resolve()
                            print(f"DEBUG: .git detected at {git_path} (is_dir={item.is_dir()}, is_file={item.is_file()})")

                            debug_stats['git_folders'] += 1

                        # Recurse into directories
                        if item.is_dir():
                            debug_stats['directories'] += 1
                            walk_dir(item, depth + 1)
                        else:
                            debug_stats['files'] += 1

                            
                except PermissionError as e:
                    debug_stats['permission_errors'] += 1
                    print(f"{indent}  [PERMISSION DENIED] {dir_path}: {e}", flush=True)
                except Exception as e:
                    print(f"{indent}  [ERROR] {dir_path}: {type(e).__name__}: {e}", flush=True)
            
            print("\n" + "="*60, flush=True)
            print("DEBUG: Starting directory walk...", flush=True)
            print("="*60, flush=True)
            walk_dir(path)
            
            print("\n" + "="*60, flush=True)
            print("DEBUG: Walk complete - Statistics:", flush=True)
            print("="*60, flush=True)
            for key, value in debug_stats.items():
                print(f"  {key}: {value}", flush=True)
            print(f"  Total paths collected: {len(all_subpaths)}", flush=True)
            print(f"  Unique paths: {len(set(all_subpaths))}", flush=True)
            
            # DEBUG: List all hidden items found
            hidden_items = [p for p in all_subpaths if p.name.startswith('.')]
            print(f"\n  All hidden items found:", flush=True)
            for hidden in hidden_items:
                print(f"    - {hidden.name} ({'dir' if hidden.is_dir() else 'file'})", flush=True)
            
            # DEBUG: Check if .git specifically made it into the list
            git_folders_in_list = [p for p in all_subpaths if p.name == '.git']
            print(f"\n  .git folders in all_subpaths: {len(git_folders_in_list)}", flush=True)
            for git in git_folders_in_list:
                print(f"    - {git}", flush=True)
            
            print("="*60 + "\n", flush=True)
            
            
            for subpath in sorted(all_subpaths):
                # DEBUG: Track what happens to .git folders
                if subpath.name == '.git':
                    parent_folder_node = self._get_or_create_folder_nodes(
                        subpath.parent, folder_nodes, path, parent_node
                    )

                    # Always attach a Node for .git
                    git_node = Node(
                        ".git",
                        parent=parent_folder_node,          # attach under repo root
                        type="directory",
                        filepath=str(subpath),
                        is_repo_head=False           # still can mark repo root separately
                    )

                    folder_nodes[str(subpath)] = git_node

                    print(f"DEBUG: Processing .git folder: {subpath}", flush=True)
                
                # added this to skip MAC artifacts when extracing zip files made with a mac
                if self._is_mac_artifact(subpath):
                    if subpath.name == '.git':
                        print(f"  ⚠️  .git skipped by _is_mac_artifact check!", flush=True)
                    continue
                
                # Ensure all subdirectories are represented, even if empty
                if subpath.is_dir():
                    if subpath.name == '.git':
                        print(f"  ✓ .git recognized as directory, calling _get_or_create_folder_nodes", flush=True)
                    self._get_or_create_folder_nodes(subpath, folder_nodes, path, parent_node)
                    continue
                
                # Skip unsupported or invalid files
                if self._is_rar_file(subpath):
                    continue

                if subpath.stat().st_size > self.max_size_bytes:
                    continue

                # Create or get parent folder node
                parent_folder_node: Node = self._get_or_create_folder_nodes(
                    subpath.parent, folder_nodes, path, parent_node
                )

                # If ZIP, extract instead of loading as binary
                if subpath.suffix.lower() == '.zip':
                    self._extract_and_load_zip(subpath, parent_folder_node)
                    continue

                # Load regular file
                file_obj, binary_index  = self._load_single_file(subpath)
                if file_obj:
                    Node(
                        file_obj['filename'],
                        parent=parent_folder_node,
                        type="file",
                        binary_index=binary_index,
                        file_data=file_obj,
                        classification=None,
                        extension=file_obj['extension']
                    )
                    self.file_objects.append(file_obj)



    def _get_or_create_folder_nodes(
        self,
        folder_path: Path,
        folder_nodes: Dict[str, Node],
        root_path: Path,
        root_node: Node,
    ) -> Node:
        folder_str: str = str(folder_path)

        if folder_str in folder_nodes:
            return folder_nodes[folder_str]

        if folder_path == root_path:
            return root_node

        parent_folder_node: Node = self._get_or_create_folder_nodes(
            folder_path.parent, folder_nodes, root_path, root_node
        )

        folder_node: Node = Node(
            folder_path.name,
            parent=parent_folder_node,
            type="directory",
            filepath=folder_str,
            is_repo_head=False
        )
        folder_nodes[folder_str] = folder_node

        return folder_node

    def _load_single_file(self, file_path: Path) -> Tuple[Dict[str, Any] | None, int | None]:
        try:
            with open(file_path, 'rb') as f:
                binary_data: bytes = f.read()

                binary_index: int = len(self.binary_data_array)
                self.binary_data_array.append(binary_data)

            file_obj = {
                'filename': file_path.name,
                'filepath': str(file_path.absolute()),
                'size_bytes': len(binary_data),
                'extension': file_path.suffix.lower(),
                'binary_index': binary_index
            }
            return file_obj, binary_index
        except Exception as e:
            print(f"Warning: could not load {file_path}: {e}")
            return None, None


    def _extract_and_load_zip(self, zip_path: Path, parent_node: Node) -> None:

        # Create a temporary directory for extraction
        temp_extract_dir = tempfile.mkdtemp()
        temp_path: Path = Path(temp_extract_dir)

        try:
            # Extract the ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_path)

            # Create a ZIP node (unless parent_node is already the ZIP root)
            if parent_node.name != zip_path.name:
                zip_node = Node(
                    zip_path.name,
                    parent=parent_node,
                    type="zip",
                    filepath=str(zip_path),
                    is_repo_head=False
                )
            else:
                zip_node = parent_node

            # Keep track of folder nodes in this ZIP extraction
            folder_nodes = {str(temp_path): zip_node}

            # Walk through all files and folders
            for file_path in sorted(temp_path.rglob('*')):
                if self._is_mac_artifact(file_path):
                    continue  # skip macOS artifacts (when zip files are created on MAC there are also metadata files created which we want to ignore)

                if file_path.is_dir():
                    continue  # directories handled when creating folder nodes

                if self._is_rar_file(file_path):
                    continue  # skip RAR files

                if file_path.stat().st_size > self.max_size_bytes:
                    continue  # skip oversized files

                # Ensure parent folder node exists
                parent_folder_node: Node = self._get_or_create_folder_nodes(
                    file_path.parent, folder_nodes, temp_path, zip_node
                )

                # Handle nested ZIP recursively
                if file_path.suffix.lower() == '.zip':
                    self._extract_and_load_zip(file_path, parent_folder_node)
                    continue

                # Load regular file
                file_obj, binary_index = self._load_single_file(file_path)
                if file_obj:
                    Node(
                        file_obj['filename'],
                        parent=parent_folder_node,
                        type="file",
                        binary_index=binary_index,
                        file_data=file_obj,
                        extension=file_obj['extension'],
                        classification=None
                    )
                    self.file_objects.append(file_obj)

        except zipfile.BadZipFile:
            raise ValueError(f"Invalid or corrupted ZIP file: {zip_path}")

        finally:
            # Clean up the temporary extraction folder
            if Path(temp_extract_dir).exists():
                shutil.rmtree(temp_extract_dir)


    def get_binary_array(self, filepath: str | Path | None = None ) -> list[bytes] | None:
        try:
            # if function is called with a filepath
            if filepath:
                load_result = self.load_from_filepath(filepath)
                if load_result('status') != 'success':
                    print(f"Error loading file(s): {load_result.get('message')}")
                    return None
            
            # else check if binary array and tree are initialized. 
            elif not self.binary_data_array or not self.file_tree:
                print("Binary data not initialized. Please call load_from_filepath() first.")
                return None

            # success 
            return self.binary_data_array

        except Exception as e:
            print(f"get_bin_array failed: {e}")
            return None


    def _is_rar_file(self, path: Path) -> bool:
        return path.suffix.lower() in ['.rar', '.r00', '.r01']

    # Helper method to determine if file is a mac artifact
    def _is_mac_artifact(self, path: Path) -> bool:
        return (
            path.parts[0] == "__MACOSX"
            or path.name.startswith("._")
        )

    def print_tree(self) -> None:
        if not self.file_tree:
            print("No tree loaded")
            return

        for pre, _, node in RenderTree(self.file_tree):
            if node.type == "file":
                size_kb : float = node.file_data['size_bytes'] / 1024
                print(f"{pre}{node.name} ({size_kb:.1f} KB)")
            else:
                print(f"{pre}{node.name}/")



#to test the function of this class 
if __name__ == "__main__":
    import os
    print(f"Current working directory: {os.getcwd()}")
    
    file_manager = FileManager()
    filepath = input("Enter file or folder path: ")
    result = file_manager.load_from_filepath(filepath)

    print("\n" + "="*60)
    if result['status'] == 'success':
        print(f"✓ {result['message']}")
        print("\nTree structure:")
        file_manager.print_tree()
        
        print("\n" + "-"*60)
        print("Flat file list:")
        for file_obj in file_manager.file_objects:
            size_kb = file_obj['size_bytes'] / 1024
            binary_index = file_obj.get('binary_index')
            print(f"  • {file_obj['filename']} ({size_kb:.1f} KB) [binary_index={binary_index}]")

        print("\n" + "-"*60)
        print(f"Total binary objects stored: {len(file_manager.binary_data_array)}")

        get_binary_array_test = input("Would you like to retrieve the binary array? y/n")

        if get_binary_array_test == "y":
            result_array = file_manager.get_binary_array()
            print(result_array)


    else:
        print(f"✗ Error: {result['message']}")
    print("="*60)