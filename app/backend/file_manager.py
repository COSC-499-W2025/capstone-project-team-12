from pathlib import Path
import zipfile
import tempfile
import shutil
from anytree import Node, RenderTree

class FileManager:
    def __init__ (self):
        self.max_size_bytes = 4 * 1024 * 1024 * 1024 #4gb
        self.temp_extract_dir = None
        self.file_tree = None  # Root node of the tree
        self.file_objects = []

    def load_from_filepath(self, filepath):
        try:
            self.file_objects = []
            self.file_tree = None           

            path = self._validate_path(filepath)

            #create root node for tree
            root_name = path.name if path.name else "root"
            self.file_tree = Node(root_name, type="directory", path=str(path))

            # Load files and build tree
            self._load_files(path, self.file_tree)

            if not self.file_objects:
                return {
                    'status': 'error',
                    'message': 'No valid files found'
                }
            
            return {
                'status': 'success',
                'message': f'loaded {len(self.file_objects)} file(s)',
                'tree': self.file_tree
            }
        
        except Exception as e:
            return {
                'status' : 'error',
                'message' : str(e),
                'error_type' : type(e).__name__
            }


    def _validate_path(self, filepath):
        # print(f"DEBUG: Raw input → {repr(filepath)}")

        #remove quotations marks if user pastes file path in as input
        filepath = filepath.strip().strip('"').strip("'")

        #to ensure that directory looks at paths absolutely
        path = Path(filepath).expanduser().resolve()

        # print(f"DEBUG: Resolved path → {path}")
        # print(f"DEBUG: Exists? {path.exists()}")


        if not path.exists():
            raise FileNotFoundError(f"Path not found: {filepath}")
        
        #pass path to helper method to check if it is a RAR file
        if path.is_file() and self._is_rar_file(path):
            raise ValueError(f"RAR files are not supported: {filepath}")
        
        if path.is_file():
            size = path.stat().st_size
            if size > self.max_size_bytes:
                size_gb = size/(1024 ** 3)
                raise ValueError(f"File too large: {size_gb:.2f}GB (max 4GB)")

        #if path given is a directory    
        elif path.is_dir():
            #helper method to get directory size
            total_size = self._get_directory_size(path)
            if total_size > self.max_size_bytes:
                size_gb = total_size / (1024 ** 3) 
                raise ValueError(f"Folder too large: {size_gb:.2f}GB (max 4GB)")   
        return path
    

    def _load_files(self, path, parent_node):

        #check if file is a compressed zip file, and pass to helper method accordingly
        if path.is_file() and path.suffix.lower() == '.zip':
            self._extract_and_load_zip(path, parent_node)
        
        elif path.is_file():
            file_obj = self._load_single_file(path)
            if file_obj:
                # Create node for this file
                Node(
                    file_obj['filename'],
                    parent=parent_node,
                    type="file",
                    file_data=file_obj
                )
                self.file_objects.append(file_obj)

        #if path is a directory, look at each file within it
        elif path.is_dir():
            
            # Create a dictionary to track folder nodes
            folder_nodes = {str(path): parent_node}      

            for file_path in sorted(path.rglob('*')):
                if not file_path.is_file():
                    continue

                if self._is_rar_file(file_path):
                    continue

                if file_path.stat().st_size > self.max_size_bytes:
                    continue

                #file_path.parent is an attribute of pathlib.path, not to be confused with parent nodes
                parent_folder_node = self._get_or_create_folder_nodes(
                    file_path.parent, folder_nodes, path, parent_node
                )

                
                file_obj = self._load_single_file(file_path)
                if file_obj:
                    Node(
                        file_obj['filename'],
                        parent=parent_folder_node,
                        type="file",
                        file_data=file_obj
                    )
                    self.file_objects.append(file_obj)

    def _get_or_create_folder_nodes(self, folder_path, folder_nodes, root_path, root_node):
        folder_str = str(folder_path)

        #if folder node already exists, return it
        if folder_str in folder_nodes:
            return folder_nodes[folder_str]
        
        #if this is the root folder
        if folder_path == root_path:
            return root_node
        
        #recursively create parent folders
        parent_folder_node = self._get_or_create_folder_nodes(folder_path.parent, folder_nodes, root_path, root_node)

        #Create this folder node
        folder_node = Node(
            folder_path.name,
            parent=parent_folder_node,
            type="directory",
            path=folder_str
        )
        folder_nodes[folder_str] = folder_node

        return folder_node



    def _load_single_file(self, file_path):
        try:
            #open files as binary so we can read binary data needed for later steps
            with open(file_path, 'rb') as f:
                binary_data = f.read()
            return {
                'filename' : file_path.name,
                'path': str(file_path.absolute()),
                'binary_data': binary_data,
                'size_bytes': len(binary_data),
                'extension': file_path.suffix.lower()
            }
        except Exception as e:
            print(f"Warning: could not load {file_path}: {e}")
            return None
        


    def _extract_and_load_zip(self, zip_path, parent_node):
        # Ttmporary directory to store the contents of zip file we will uncompress
        self.temp_extract_dir = tempfile.mkdtemp()
        temp_path = Path(self.temp_extract_dir)
        
        try:
            # use built in ZipFile library to extract contents
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_path)

            #create a zip container node
            zip_node = Node(
                zip_path.name,
                parent=parent_node,
                type="zip",
                path=str(zip_path)
            )

            #build tree for extracted contents
            folder_nodes = {str(temp_path): zip_node}
            
            for file_path in sorted(temp_path.rglob('*')):
                if not file_path.is_file():
                    continue
                
                if self._is_rar_file(file_path):
                    continue

                if file_path.stat().st_size > self.max_size_bytes:
                    continue

                #get or create parent folder node
                parent_folder_node = self._get_or_create_folder_nodes(
                    file_path.parent, folder_nodes, temp_path, zip_node
                )

                file_obj = self._load_single_file(file_path)
                if file_obj:
                    Node(
                        file_obj['filename'],
                        parent=parent_folder_node,
                        type="file",
                        file_data=file_obj
                    )
                    self.file_objects.append(file_obj)
        
        except zipfile.BadZipFile:
            raise ValueError(f"invalid or corrupted ZIP file: {zip_path}")
        
        finally:
            if self.temp_extract_dir and Path(self.temp_extract_dir).exists():
                shutil.rmtree(self.temp_extract_dir)

    #helper method to find the total size of directory
    def _get_directory_size(self, path):
        total = 0
        for file_path in path.rglob('*'):
            if file_path.is_file():
                total += file_path.stat().st_size
        return total
    
    #helper method to check if a file is a rar file
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

