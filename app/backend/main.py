import os
import sys
import subprocess
from pathlib import Path
from file_manager import FileManager

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
    
