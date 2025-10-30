import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any
from anytree import Node
from file_manager import FileManager
from tree_processor import TreeProcessor

def validate_path(filepath: str) -> Path:
    max_size_bytes: int = 4 * 1024 * 1024 * 1024  # 4gb limit

    def _is_rar_file(path: Path) -> bool:
        return path.suffix.lower() in ['.rar', '.r00', '.r01']
    
    #helper method to find the total size of directory
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

    #remove quotations marks if user pastes file path in as input
    filepath = filepath.strip().strip('"').strip("'")
    if not filepath:
        raise ValueError("Filepath cannot be empty")
    
    #to ensure that directory looks at paths absolutely
    try:
        path: Path = Path(filepath).expanduser().resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid file path: {e}")

    if not path.exists():
        raise FileNotFoundError(f"Path not found: {filepath}")
    
    #pass path to helper method to check if it is a RAR file
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

    #if path given is a directory    
    elif path.is_dir():
        #helper method to get directory size
        total_size: int = _get_directory_size(path)
        if total_size > max_size_bytes:
            size_gb: float = total_size / (1024 ** 3)
            raise ValueError(f"Folder too large: {size_gb:.2f}GB (max 4GB)")   
    return path
    

def run_all_backend_tests() -> None:
    print("\nRunning all backend tests\n")
    tests_path: str = "app/backend/tests_backend"
    
    # Check if tests directory exists
    if not Path(tests_path).exists():
        print(f"Tests directory not found at {tests_path}")
        return
    
    try:
        result: subprocess.CompletedProcess = subprocess.run(
            ["pytest", "-v", tests_path], 
            check=False,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
       # check=False means don't crash if pytest fails - we will handle the error ourselves
        if result.returncode == 0: # 0 if all tests passed
            print("\nAll tests passed.")
        else:
            print("\nSome tests failed.")
    except KeyboardInterrupt:
        print("\n\nTest execution cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error running tests: {e}") # catches the error if something goes wrong instead of crashing program


def main() -> None:
    try:
        choice: str = input("Would you like to run all backend tests? (y/n) \n> ").strip().lower()

        if choice in ("y", "yes"):
            run_all_backend_tests()
            sys.exit(0)

        elif choice in ("n", "no"):
            while True: # looping so that prompts get asked until the user is successful or the user does not want to try again
                filepath: str = input("\nEnter a file path to process: \n>").strip()
                try:
                    path: Path = validate_path(filepath) # validate using method above
                    print("\nPath is valid. Loading file in File Manager...\n")

                    file_manager: FileManager = FileManager()
                    
                    # fm_result type left as Dict[str, Any] because FileManager returns different structures depending on success/error
                    fm_result: Dict[str, str | Node | None] = file_manager.load_from_filepath(str(path))

                    # Handle KeyError - check if expected keys exist
                    if "status" not in fm_result:
                        print("FileManager did not return expected status.")
                        break

                    if fm_result["status"] == "success": # what is returned from load_from_filepath
                        print(f"File path loaded successfully in File Manager: {fm_result.get('message', 'No message')}\n")

                        if "tree" not in fm_result or fm_result["tree"] is None:  # makes sure FileManager returns a tree
                            print("ERROR: FileManager did not return a tree.")
                            break
                        file_tree: Node = fm_result["tree"] # if successful, store the root node of the tree

                        # Handle TreeProcessor exceptions
                        try:
                            tree_processor: TreeProcessor = TreeProcessor()
                            processed_tree: Node = tree_processor.process_file_tree(file_tree) # send the tree to Tree Processor
                            print("Tree processed successfully in Tree Processor.\n") # end here for now until file classifier is refactored
                        except (ValueError, TypeError, RuntimeError) as e:
                            print(f"Tree processing failed: {e}")
                            break
                        except Exception as e:
                            print(f"Error processing tree: {e}")
                            break

                    elif fm_result["status"] == "error":
                        print(f"There was an error loading the file to File Manager: {fm_result.get('message', 'Unknown error')}\n")

                    break
                
                except Exception as e:
                    print(f"\nFile path is not valid: {e}")
                    retry: str = input("\nWould you like to try again? (y/n) \n> ").strip().lower()

                    if retry in ("n", "no"):
                        print("\nExiting.")
                        break

        else:
            print("\nInput invalid - try again (y/n) ")

    except KeyboardInterrupt:
        print("\n\nExiting.")
        sys.exit(0)


if __name__ == "__main__":
    main()
