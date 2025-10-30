import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List
from anytree import Node
from file_manager import FileManager
from tree_processor import TreeProcessor
from repository_processor import RepositoryProcessor

def validate_path(filepath: str) -> Path:
        max_size_bytes: int = 4 * 1024 * 1024 * 1024  # 4gb limit

        def _is_rar_file(path: Path) -> bool:
            return path.suffix.lower() in ['.rar', '.r00', '.r01']
        
        #helper method to find the total size of directory
        def _get_directory_size(path: Path) -> int:
            total: int = 0
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    total += file_path.stat().st_size
            return total

        #remove quotations marks if user pastes file path in as input
        filepath = filepath.strip().strip('"').strip("'")

        #to ensure that directory looks at paths absolutely
        path: Path = Path(filepath).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(f"Path not found: {filepath}")
        
        #pass path to helper method to check if it is a RAR file
        if path.is_file() and _is_rar_file(path):
            raise ValueError(f"RAR files are not supported: {filepath}")
        
        if path.is_file():
            size: int = path.stat().st_size
            if size > max_size_bytes:
                size_gb: float = size/(1024 ** 3)
                raise ValueError(f"File too large: {size_gb:.2f}GB (max 4GB)")

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
    try:
        result: subprocess.CompletedProcess = subprocess.run(["pytest", "-v", tests_path], check=False) # runs tests as if you type the command in terminal
       # check=False means don't crash if pytest fails - we will handle the error ourselves
        if result.returncode == 0: # 0 if all tests passed
            print("\nAll tests passed.")
        else:
            print("\nSome tests failed.")
    except Exception as e:
        print(f"Error running tests: {e}") # catches the error if something goes wrong instead of crashing program


def main() -> None:
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

                if fm_result["status"] == "success": # what is returned from load_from_filepath
                    print(f"File path loaded successfully in File Manager: {fm_result['message']}\n")

                    if "tree" not in fm_result or fm_result["tree"] is None:  # makes sure FileManager returns a tree
                        print("ERROR: FileManager did not return a tree.")
                        break
                    file_tree: Node = fm_result["tree"] # if successful, store the root node of the tree

                    tree_processor: TreeProcessor = TreeProcessor()
                    processed_tree: Node = tree_processor.process_file_tree(file_tree) # send the tree to Tree Processor
                    print("Tree processed successfully in Tree Processor.\n") # end here for now until file classifier is refactored

                    git_repos: List[Node] = tree_processor.get_git_repos() #check for git repos before processing repos

                    if git_repos:
                        # prompt user for github username to link repos, loops to ensure valid input
                        github_username: str = input("Git repositories detected in the file tree. Please enter your GitHub username to link them. To skip this processing, please press enter: \n> ").strip()
                        if github_username:
                            repo_processor: RepositoryProcessor = RepositoryProcessor(
                                username=github_username,
                                binary_data_array=fm_result["binary_data"]
                            )

                            processed_git_repos: bytes = repo_processor.process_repositories(git_repos)
                            if processed_git_repos:
                                json_str: str = processed_git_repos.decode('utf-8')
                                print(f"repos successfully processed {json_str}")

                        else:
                            print("Skipping Git repository linking as no username was provided.\n")


                elif fm_result["status"] == "error":
                    print(f"There was an error loading the file to File Manager: {fm_result['message']}\n")

                break
            
            except Exception as e:
                print(f"\nFile path is not valid: {e}")
                retry: str = input("\nWould you like to try again? (y/n) \n> ").strip().lower()

                if retry in ("n", "no"):
                    print("\nExiting. Bye!")
                    break

    else:
        print("\nInput invalid - try again (y/n) ")


if __name__ == "__main__":
    main()
