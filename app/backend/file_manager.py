from pathlib import Path
import zipfile
import  tempfile
import shutil

class FileManager:
    def __init__ (self):
        self.max_size_bytes = 4 * 1024 * 1024 * 1024 #4gb
        self.temp_extract_dir = None
        self.file_objects = []

    def _load_from_filepath(self, filepath):
        
        try:
            self.file_objects = []
            path = self._validate_path(filepath)
            self.file_objects = self._load_files(path)

            if not self.file_objects:
                return {
                    'status' : 'error',
                    'message' : 'No valid files found',
                    'files' : []
                }
            
            return{
                'status' : 'success',
                'message' : f'loaded {len(self.file_objects)} file(s)',
                'files' : self.file_objects
            }
        
        except Exception as e:
            return {
                'status' : 'error',
                'message' : str(e),
                'error_type' : type(e).__name__,
                'files' : []
            }


    def _validate_path(self, filepath):
        # print(f"DEBUG: Raw input → {repr(filepath)}")
        filepath = filepath.strip().strip('"').strip("'")
        path = Path(filepath).expanduser().resolve()
        # print(f"DEBUG: Resolved path → {path}")
        # print(f"DEBUG: Exists? {path.exists()}")

        if not path.exists():
            raise FileNotFoundError(f"Path not found: {filepath}")
        
        if path.is_file() and self._is_rar_file(path):
            raise ValueError(f"RAR files are not supoprted: {filepath}")
        
        if path.is_file():
            size = path.stat().st_size
            if size > self.max_size_bytes:
                size_gb = size/(1024 ** 3)
                raise ValueError(f"File too large: {size_gb:.2f}GB (max 4GB)")
            
        elif path.is_dir():
            total_size = self._get_directory_size(path)
            if total_size > self.max_size_bytes:
                size_gb = total_size / (1024 ** 3) 
                raise ValueError(f"Folder too large: {size_gb:.2f}GB (max 4GB)")   
        return path
    

    def _load_files(self, path):
        file_objects = [] 
        #didn't use the file objects attribute here because I assign the result of this method to the attribue in the _load_from_filepath method anyway, and it's more explicit there.d

        if path.is_file() and path.suffix.lower() == '.zip':
            file_objects = self._extract_and_load_zip(path)
        
        elif path.is_file():
            file_obj = self._load_single_file(path)
            if file_obj:
                file_objects.append(file_obj)
        
        elif path.is_dir():
            for file_path in path.rglob('*'):
                if not file_path.is_file():
                    continue

                if self._is_rar_file(file_path):
                    continue

                if file_path.stat().st_size > self.max_size_bytes:
                    continue

                file_obj = self._load_single_file(file_path)
                if file_obj:
                    file_objects.append(file_obj)
        return file_objects 

                


    def _load_single_file(self, file_path):
        try:
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
        

    def _extract_and_load_zip(self, zip_path):
        file_objects = []

        self.temp_extract_dir = tempfile.mkdtemp()
        temp_path = Path(self.temp_extract_dir)
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_path)
            for file_path in temp_path.rglob('*'):
                if not file_path.is_file():
                    continue

                if self._is_rar_file(file_path):
                    continue

                if file_path.stat().st_size > self.max_size_bytes:
                    continue

                file_obj = self._load_single_file(file_path)
                if file_obj:
                    file_objects.append(file_obj)
            return file_objects
        
        except zipfile.BadZipFile:
            raise ValueError(f"invalid or corrupted ZIP file: {zip_path}")
        
        finally:
            if self.temp_extract_dir and Path(self.temp_extract_dir).exists():
                shutil.rmtree(self.temp_extract_dir)

    def _get_directory_size(self, path):
        total = 0
        for file_path in path.rglob('*'):
            if file_path.is_file():
                total += file_path.stat().st_size
        return total
    
    def _is_rar_file(self, path):
        return path.suffix.lower() in ['.rar', '.r00', '.r01']

   
if __name__ == "__main__":
    import os
    print(f"Current working directory: {os.getcwd()}")
    file_manager = FileManager()
    filepath = input("Enter file or folder path: ")
    result = file_manager._load_from_filepath(filepath)

    print("\n" + "="*60)
    if result['status'] == 'success':
        print(f"✓ {result['message']}")
        print("\nLoaded files:")
        # Access files via file_manager.file_objects
        for file_obj in file_manager.file_objects:
            size_kb = file_obj['size_bytes'] / 1024
            print(f"  • {file_obj['filename']} ({size_kb:.1f} KB)")
            print(f"    Extension: {file_obj['extension']}")
            print(f"    Path: {file_obj['path']}")
    else:
        print(f"✗ Error: {result['message']}")
    print("="*60)


