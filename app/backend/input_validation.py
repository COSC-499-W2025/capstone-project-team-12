from uuid import UUID
from pathlib import Path
from typing import Set

#Global variable defining accepted image formats, both functionality and prompts will update automatically if changed.
accepted_formats:Set[str] = [".apng",".avif",".gif",".jpeg",".svg",".webp"]


def is_valid_path(filepath:str)->Path:
    """
    Summary:
        Validates user's input path. Input path must be a valid filepath. Does NOT consider our design constraints only checks for validity.
    Params
        - User inputted filepath as string
    Return:
        os.path object
    """
     #Input cleaning
    filepath = filepath.strip().strip('"').strip("'")
    
    #Check if empty
    if filepath is None or "":
        raise ValueError("Filepath cannot be empty")
    
    #try to make a valid absolute path based on input path
    try:
        path: Path = Path(filepath).expanduser().resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid file path: {e}")
    
    #check if path exists
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {filepath}")    


def validate_analysis_path(filepath: str) -> Path:
    """
    Summary:
        Validates user's input path for analysis. Input path must be a valid filepath. Does consider design constraints i.e: Cannot contain files more then 4GB and must not be a rar file (zip file allowed).
    Params: 
        - User inputted filepath as string
    Return:
        os.path object
    """
    max_size_bytes: int = 4 * 1024 * 1024 * 1024  # 4gb limit

    def _is_rar_file(path: Path) -> bool:
        return path.suffix.lower() in ['.rar', '.r00', '.r01']
    
    def _get_directory_size(path: Path) -> int:
        total: int = 0
        try:
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    try:
                        total += file_path.stat().st_size
                    except (OSError, PermissionError) as e:
                        print(f"Cannot access file {file_path}: {e}")
                        continue
        except (OSError, PermissionError) as e:
            raise ValueError(f"Cannot access directory: {e}")
        return total

    try:
        path:Path = is_valid_path(filepath)
    except Exception as e:
        print(f"Path error:{e}")
        raise
    
    if path.is_file() and _is_rar_file(path):
        raise ValueError(f"RAR files are not supported: {filepath}")
    
    if path.is_file():
        try:
            size: int = path.stat().st_size
            if size > max_size_bytes:
                size_gb: float = size/(1024 ** 3)
                raise ValueError(f"File too large: {size_gb:.2f}GB (max 4GB)")
        except (OSError, PermissionError) as e:
            raise ValueError(f"Cannot access file: {e}")

    elif path.is_dir():
        total_size: int = _get_directory_size(path)
        if total_size > max_size_bytes:
            size_gb: float = total_size / (1024 ** 3)
            raise ValueError(f"Folder too large: {size_gb:.2f}GB (max 4GB)")   
    return path

def validate_thumbnail_path(filepath:str)->Path:
    """
    Summary:
        Validates user's input path for thumbnail image. Input path must be a valid filepath. Does consider design constraints i.e: Accepted image formats and image size.
    Params: 
        - User inputted filepath as string
    Return:
        os.path object
    """
    max_img_size_bytes:int = 10*1024*1024 #10MB Limit
    
    def is_valid_format(filepath:Path)->bool:
        if filepath.suffix().lower() in accepted_formats:
            return True
        else:
            return False
    
    try:
        path:Path = is_valid_path(filepath)
    except Exception as e:
        raise RuntimeError(f"Path Error: {e}")
    
    if path.is_dir():
        raise IsADirectoryError(f"Path is not a file but a directory")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file")
    
    #check if image as an accepted format
    #formats based on types supported by all of Chrome,Firefox,Opera,Safari and Edge
    if not is_valid_format():
        raise TypeError(f"Not an accepted image format. Accepted formats are:{accepted_formats}")
    
    try:
        size: int = path.stat().st_size
        if size > max_img_size_bytes:
            size_mb: float = size/(1024 ** 2)
            raise ValueError(f"File too large: {size_mb:.2f}MB (max 10MB)")
    except (OSError, PermissionError) as e:
        raise ValueError(f"Cannot access file: {e}")
    
    return path

def validate_uuid(uuid:str)-> str:
    result = UUID(uuid) #Try creating an UUID obj, if it fails we know its either wrong version or invalid
    if result:
        return uuid
    else:
        raise ValueError('Invalid UUID')