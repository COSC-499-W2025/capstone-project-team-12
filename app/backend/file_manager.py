from pathlib import Path
from typing import Any, Dict, List, Tuple
import zipfile
import tempfile
import shutil
from anytree import Node, RenderTree

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

            for subpath in sorted(path.rglob('*')):
                # Ensure all subdirectories are represented, even if empty
                if subpath.is_dir():
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
        self.temp_extract_dir = tempfile.mkdtemp()
        temp_path: Path = Path(self.temp_extract_dir)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_path)

            # don't create duplicate ZIP node if it’s already root
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

            folder_nodes = {str(temp_path): zip_node}

            for file_path in sorted(temp_path.rglob('*')):
                if not file_path.is_file():
                    continue

                if self._is_rar_file(file_path):
                    continue

                if file_path.stat().st_size > self.max_size_bytes:
                    continue

                parent_folder_node: Node = self._get_or_create_folder_nodes(
                    file_path.parent, folder_nodes, temp_path, zip_node
                )

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
            if self.temp_extract_dir and Path(self.temp_extract_dir).exists():
                shutil.rmtree(self.temp_extract_dir)

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

