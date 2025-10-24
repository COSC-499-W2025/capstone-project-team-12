from pathlib import Path
import zipfile
import tempfile
import shutil
from anytree import Node, RenderTree

class FileManager:
    def __init__(self):
        self.max_size_bytes = 4 * 1024 * 1024 * 1024  # 4GB
        self.temp_extract_dir = None
        self.file_tree = None
        self.file_objects = []

    def load_from_filepath(self, filepath):
        try:
            self.file_objects = []
            self.file_tree = None

            # Accept both string and Path inputs
            path = Path(filepath).resolve()

            if not path.exists():
                raise FileNotFoundError(f"Path not found: {path}")

            # Create root node
            root_name = path.name if path.name else "root"
            self.file_tree = Node(
                root_name,
                type="directory",
                path=str(path),
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
                'tree': self.file_tree
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'error_type': type(e).__name__
            }

    def _load_files(self, path, parent_node):
        # Handle single ZIP file directly
        if path.is_file() and path.suffix.lower() == '.zip':
            self._extract_and_load_zip(path, parent_node)

        # Handle single regular file
        elif path.is_file():
            file_obj = self._load_single_file(path)
            if file_obj:
                Node(
                    file_obj['filename'],
                    parent=parent_node,
                    type="file",
                    file_data=file_obj,
                    classification=None,
                    extension=file_obj['extension']
                )
                self.file_objects.append(file_obj)

        # Handle directories (now includes empty ones)
        elif path.is_dir():
            folder_nodes = {str(path): parent_node}

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
                parent_folder_node = self._get_or_create_folder_nodes(
                    subpath.parent, folder_nodes, path, parent_node
                )

                # If ZIP, extract instead of loading as binary
                if subpath.suffix.lower() == '.zip':
                    self._extract_and_load_zip(subpath, parent_folder_node)
                    continue

                # Load regular file
                file_obj = self._load_single_file(subpath)
                if file_obj:
                    Node(
                        file_obj['filename'],
                        parent=parent_folder_node,
                        type="file",
                        file_data=file_obj,
                        classification=None,
                        extension=file_obj['extension']
                    )
                    self.file_objects.append(file_obj)



    def _get_or_create_folder_nodes(self, folder_path, folder_nodes, root_path, root_node):
        folder_str = str(folder_path)

        if folder_str in folder_nodes:
            return folder_nodes[folder_str]

        if folder_path == root_path:
            return root_node

        parent_folder_node = self._get_or_create_folder_nodes(folder_path.parent, folder_nodes, root_path, root_node)

        folder_node = Node(
            folder_path.name,
            parent=parent_folder_node,
            type="directory",
            path=folder_str,
            is_repo_head=False
        )
        folder_nodes[folder_str] = folder_node

        return folder_node

    def _load_single_file(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                binary_data = f.read()
            return {
                'filename': file_path.name,
                'path': str(file_path.absolute()),
                'binary_data': binary_data,
                'size_bytes': len(binary_data),
                'extension': file_path.suffix.lower()
            }
        except Exception as e:
            print(f"Warning: could not load {file_path}: {e}")
            return None

    def _extract_and_load_zip(self, zip_path, parent_node):
        self.temp_extract_dir = tempfile.mkdtemp()
        temp_path = Path(self.temp_extract_dir)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_path)

            # don't create duplicate ZIP node if it’s already root
            if parent_node.name != zip_path.name:
                zip_node = Node(
                    zip_path.name,
                    parent=parent_node,
                    type="zip",
                    path=str(zip_path),
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

                parent_folder_node = self._get_or_create_folder_nodes(
                    file_path.parent, folder_nodes, temp_path, zip_node
                )

                file_obj = self._load_single_file(file_path)
                if file_obj:
                    Node(
                        file_obj['filename'],
                        parent=parent_folder_node,
                        type="file",
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


    def _is_rar_file(self, path):
        return path.suffix.lower() in ['.rar', '.r00', '.r01']

    def print_tree(self):
        if not self.file_tree:
            print("No tree loaded")
            return

        for pre, _, node in RenderTree(self.file_tree):
            if node.type == "file":
                size_kb = node.file_data['size_bytes'] / 1024
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
            print(f"  • {file_obj['filename']} ({size_kb:.1f} KB)")
    else:
        print(f"✗ Error: {result['message']}")
    print("="*60)

