import os
import sys
import subprocess
from pathlib import Path
from anytree import Node
from tree_processor import TreeProcessor
from typing import List,BinaryIO, Dict, Any
from file_manager import FileManager
from tree_processor import TreeProcessor
from repository_processor import RepositoryProcessor
from metadata_extractor import MetadataExtractor
from metadata_analyzer import MetadataAnalyzer
from repository_analyzer import RepositoryAnalyzer
from text_preprocessor import text_preprocess
from pii_remover import remove_pii
from cache.bow_cache import BoWCache, BoWCacheKey
from topic_vectors import generate_topic_vectors
import hashlib


file_data_list : List = []

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

    backend_root = Path(__file__).resolve().parent
    tests_path = backend_root / "tests_backend"
    
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

        print(result.stdout)
        
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

#pass entry by provided id from file_data_array
def get_bin_data_by_Id(bin_Idx:int)->BinaryIO|None:
    if file_data_list is None or len(file_data_list) == 0:
        print("Empty List: Initialize by calling File")
        return None
    return file_data_list[bin_Idx]

def get_bin_data_by_IdList(bin_Idx_list:List[int])->List[BinaryIO]:
    #check if files are loaded
    if file_data_list is None or len(file_data_list) == 0:
        print("Empty List: Initialize by calling File")
        return None
    
    #collect binaries    
    response_List: List[BinaryIO|None] = []
    for bin_Idx in bin_Idx_list:
        response_List.append(get_bin_data_by_Id(bin_Idx))
    return response_List

def convert_binary_to_text(node_array:List[Node])->List[BinaryIO|None]:
    """ Converts binary data to text strings for text preprocessing """
    text_data_list: List[str] = []
    bin_Idx_list: List[int] = []
    for node in node_array:
        bin_Id = node.file_data['binary_index']
        bin_Idx_list.append(bin_Id)
    text_data_list = [str(x) for x in get_bin_data_by_IdList(bin_Idx_list)]
    return text_data_list

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

                        # Store binary data globally for text preprocessing access
                        global file_data_list
                        file_data_list = fm_result.get("binary_data", [])
                        if not file_data_list:
                            print("FileManager returned no binary data. Text preprocessing may fail.")
                        else:
                            print(f"Loaded {len(file_data_list)} binary file(s) into global file_data_list.")


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

                        binary_data: List[bytes] = fm_result.get("binary_data")
                        if not isinstance(binary_data, list):
                            print("Warning: FileManager returned no binary data or in unexpected format. Proceeding with empty binary array.")
                            binary_data = []
                        
                        metadata_extractor: MetadataExtractor = MetadataExtractor()
                        metadata_results: Dict[str, Dict[str, Any]] = metadata_extractor.extract_all_metadata(processed_tree, binary_data)
                        
                        print("Metadata extracted successfully in Metadata Manager.\n")
                        
                        total_files: int = len(metadata_results)
                        if total_files > 0:
                            print(f"   Processed metadata for {total_files} files")

                        metadata_analyzer: MetadataAnalyzer = MetadataAnalyzer(metadata_results)
                        analysis_results = metadata_analyzer.analyze_all()
                        print("Metadata analysis completed successfully in Metadata Analyzer.\n")

                        git_repos: List[Node] = tree_processor.get_git_repos() #check for git repos before processing repos

                        # Run text preprocessing pipeline + store pipeline results in BoW Cache
                        try:
                            text_nodes: List[Node] = tree_processor.get_text_files()
                            if text_nodes:
                                print(f"Found {len(text_nodes)} text files. Running BoW pipeline...")

                                # with the current setup, we assume all text files use the same preprocessing steps
                                preprocess_signature = {
                                    "lemmatizer": True,
                                    "stopwords": "nltk_english_default",
                                    "pii_removal": True,
                                    "filters": ["text"]
                                }

                                # build repo_id by hashing joined file paths
                                file_paths = [getattr(text_file, "filepath", str(text_file.name)) for text_file in text_nodes]
                                joined_paths = "|".join(file_paths)
                                repo_id = hashlib.md5(joined_paths.encode()).hexdigest()

                                # no git commit info for text files
                                head_commit = None

                                # initialize cache and key
                                key = BoWCacheKey(repo_id, head_commit, preprocess_signature)
                                cache = BoWCache()

                                # check cache for existing BoW
                                if cache.has(key):
                                    print(f"Cache hit for BoW (repo_id={repo_id})")
                                    cached = cache.get(key)
                                    if cached is not None:
                                        return cached # return cached BoW
                                    print("Cache corrupted or unreadable - regenerating...")

                                # if we reach here, we have a cache miss
                                print("Cache miss - running text preprocessing pipeline...")

                                # convert binary data to text data to use in for preprocessing
                                # text_data: List[str] = convert_binary_to_text(text_nodes)
                                
                                # # run text preprocessing
                                # processed_docs = text_preprocess(text_data)
                                # anonymized_docs = remove_pii(processed_docs)
                                # final_bow: list[list[str]] = anonymized_docs

                                # # save to cache
                                # cache.set(key, final_bow)

                                # print(f"Successfully built BoW for {len(final_bow)} document(s) and saved it to Cache. Ready for text analysis.\n")

                                # print("Running topic modeling...")

                                # lda_model, doc_topic_vectors, topic_term_vectors = generate_topic_vectors(final_bow)

                                # print("Successfully generated topic vectors.")
                                # print(f"- Number of documents: {len(doc_topic_vectors)}")
                                # print(f"- Number of topics: {len(topic_term_vectors)}")
                                # print("Text analysis complete.\n")
                                
                            else:
                                print("No text files found to preprocess.")
                        except Exception as e:
                            print(f"Error during text/PII processing: {e}")


                    if git_repos:
                        # prompt user for github username to link repos
                        github_username: str = input("Git repositories detected in the file tree. Please enter your GitHub username to link them. To skip this processing, please press enter: \n> ").strip()
                        if github_username:
                            # Validate binary data from FileManager before passing it on
                            repo_processor: RepositoryProcessor = RepositoryProcessor(
                                username=github_username,
                                binary_data_array=binary_data
                            )
                            try:
                                raw_repo_data: List[Dict[str, Any]] = repo_processor.process_repositories(git_repos)
                                print(f"Processed {len(raw_repo_data)} Git repositories successfully in Repository Processor.\n")

                                repo_analyzer: RepositoryAnalyzer = RepositoryAnalyzer(github_username)
                                analyzed_repos: Dict[str, Any] = repo_analyzer.generate_project_insights(raw_repo_data)
                                print(f"Analyzed {len(analyzed_repos)} Git repositories successfully in Repository Analyzer.\n")
                                
                                # Print detailed info for each repository
                                print("\n=== Repository Details ===\n")
                                print(analyzed_repos)

                                # Print generated timelines
                                print("\n=== Project and Skill Timelines===\n")
                                all_imports = repo_analyzer.get_all_repo_import_stats(raw_repo_data)
                                skill_timeline = repo_analyzer.sort_all_repo_imports_chronologically(all_imports)
                                print(f"Skills: {skill_timeline}\n")

                                project_timeline = repo_analyzer.create_chronological_project_list(raw_repo_data)
                                print(f"Projects: {project_timeline}\n")
                            except Exception as e:
                                # Catch unexpected errors during repository processing so the app doesn't crash
                                print(f"Repository processing failed: {e}")


                        else:
                            print("Skipping Git repository linking as no username was provided.\n")

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