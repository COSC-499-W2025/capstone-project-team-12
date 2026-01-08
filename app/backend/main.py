import os
import sys
import subprocess
from pathlib import Path
from anytree import Node
from typing import List, BinaryIO, Dict, Any
import hashlib
import json
from file_manager import FileManager
from tree_processor import TreeProcessor
from repository_processor import RepositoryProcessor
from metadata_extractor import MetadataExtractor
from metadata_analyzer import MetadataAnalyzer
from repository_analyzer import RepositoryAnalyzer
from combined_preprocess import combined_preprocess
from pii_remover import remove_pii
from cache.bow_cache import BoWCache, BoWCacheKey
from topic_vectors import generate_topic_vectors
from stats_cache import collect_stats
from llm_online import OnlineLLMClient
from llm_local import LocalLLMClient
from config_manager import ConfigManager
from database_manager import DatabaseManager
from display_helpers import display_project_insights, display_project_summary, display_project_timeline
from cli_interface import CLI

file_data_list: List = []
file_access_consent: bool = None 
online_llm_consent: bool = None 

def validate_path(filepath: str) -> Path:
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

    filepath = filepath.strip().strip('"').strip("'")
    if not filepath:
        raise ValueError("Filepath cannot be empty")
    
    try:
        path: Path = Path(filepath).expanduser().resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid file path: {e}")

    if not path.exists():
        raise FileNotFoundError(f"Path not found: {filepath}")
    
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
    

def get_bin_data_by_Id(bin_Idx:int)->BinaryIO|None:
    global file_data_list
    #helper method still uses print
    if file_data_list is None or len(file_data_list) == 0:
        print("Empty List: Initialize by calling File") 
        return None
    return file_data_list[bin_Idx]

def get_bin_data_by_IdList(bin_Idx_list:List[int])->List[BinaryIO]:
    global file_data_list
    if file_data_list is None or len(file_data_list) == 0:
        print("Empty List: Initialize by calling File")
        return None
    
    response_List: List[BinaryIO|None] = []
    for bin_Idx in bin_Idx_list:
        response_List.append(get_bin_data_by_Id(bin_Idx))
    return response_List

def get_bin_data_by_Nodes(nodes:List[Node])->[BinaryIO|None]:
    if nodes is None:
        raise ValueError("Error preparing datalist in main!: No nodes given!")
        return
    
    IdList: List[int] = []
    for node in nodes:
        IdList.append(node.file_data['binary_index'])
    return get_bin_data_by_IdList(IdList)

def binary_to_str(bin_data:List[BinaryIO])-> List[str]:
    result = []
    for data in bin_data:
        try:
            result.append(data.decode('utf-8', errors='ignore') if data else '')
        except (AttributeError, UnicodeDecodeError):
            result.append('')
    return result

def main() -> None:
    # Initialize CLI Interface
    cli = CLI()
    
    config_manager = ConfigManager() # Initialize Config Manager
    database_manager = DatabaseManager()  # Initialize Database Manager
    # database_manager.wipe_all_data()  # Wipe existing data for fresh start
    
    try:
        cli.print_header("Artifact Mining App")
        
        has_file_access = config_manager.get_consent(
            key="file_access_consent", 
            prompt_text="Do you provide permission to access your file system?",
            component="accessing your local files"  
        )

        if not has_file_access:
            print("Access to files is required.")
            sys.exit(0)

        # MAIN LOOP 
        while True: 
            cli.print_separator("-")
            filepath: str = cli.get_input("Enter a file path to process ('q' to quit, 'd' to view database): \n> ").strip()
            
            if filepath.lower() == 'q':
                print("Exiting.")
                sys.exit(0)

            if filepath.lower() == 'd':
                break

            try:
                path: Path = validate_path(filepath)
                cli.print_status(f"Path valid: {path}", "success")
                cli.print_status("Loading file manager...", "info")

                file_manager: FileManager = FileManager()
                
                fm_result: Dict[str, str | Node | None] = file_manager.load_from_filepath(str(path))

                if "status" not in fm_result:
                    cli.print_status("FileManager did not return expected status.", "error")
                    break

                if fm_result["status"] == "success": 
                    cli.print_status(f"File Manager: {fm_result.get('message', 'No message')}", "success")

                    global file_data_list
                    file_data_list = fm_result.get("binary_data", [])
                    if not file_data_list:
                        cli.print_status("No binary data returned. Text preprocessing may fail.", "warning")
                    else:
                        cli.print_status(f"Loaded {len(file_data_list)} binary file(s).", "success")

                    if "tree" not in fm_result or fm_result["tree"] is None:
                        cli.print_status("FileManager did not return a tree.", "error")
                        break
                    file_tree: Node = fm_result["tree"] 

                    try:
                        tree_processor: TreeProcessor = TreeProcessor()
                        processed_tree: Node = tree_processor.process_file_tree(file_tree)
                        cli.print_status("Tree structure processed successfully.", "success")
                    except (ValueError, TypeError, RuntimeError) as e:
                        cli.print_status(f"Tree processing failed: {e}", "error")
                        break
                    except Exception as e:
                        cli.print_status(f"Error processing tree: {e}", "error")
                        break

                    binary_data: List[bytes] = fm_result.get("binary_data")
                    if not isinstance(binary_data, list):
                        cli.print_status("Warning: Binary data format unexpected. Proceeding empty.", "warning")
                        binary_data = []
                    
                    cli.print_header("Metadata Analysis")
                    metadata_extractor: MetadataExtractor = MetadataExtractor()
                    metadata_results: Dict[str, Dict[str, Any]] = metadata_extractor.extract_all_metadata(processed_tree, binary_data)
                    
                    total_files: int = len(metadata_results)
                    if total_files > 0:
                        cli.print_status(f"Processed metadata for {total_files} files", "success")

                    metadata_analyzer: MetadataAnalyzer = MetadataAnalyzer(metadata_results)
                    metadata_analysis = metadata_analyzer.analyze_all()
                    
                    print("\n--- File Extension Statistics ---")
                    print(f"{'Extension':<10} | {'Count':<8} | {'Size':<15} | {'Percentage':<8} | {'Category'}")
                    print("-" * 70)
                    for ext, stats in metadata_analysis['extension_stats'].items():
                        print(f"{ext:<10} | {stats['count']:<8} | {stats['total_size']:<15} | {stats['percentage']:<8}% | {stats['category']}")

                    git_repos: List[Node] = tree_processor.get_git_repos() 

                    doc_topic_vectors: list = []
                    topic_term_vectors: list = []
                    timeline: list = []
                    dictionary = None
                    lda_model = None
                    final_bow = []

                    try:
                        text_nodes: List[Node] = tree_processor.get_text_files()
                        code_nodes: List[Node] = tree_processor.get_code_files()
                        
                        if text_nodes or code_nodes:
                            cli.print_header("Content Analysis")
                            cli.print_status(f"Found {len(text_nodes)} text files and {len(code_nodes)} code files.", "info")
                            cli.print_status("Running Bag-of-Words (BoW) pipeline...", "info")

                            preprocess_signature = {
                                "lemmatizer": True,
                                "stopwords": "nltk_english_default",
                                "pii_removal": True,
                                "filters": ["text", "code"],
                                "normalize_code": True
                            }

                            all_nodes: List[Node] = text_nodes + code_nodes
                            file_paths = [getattr(file, "filepath", str(file.name)) for file in all_nodes]
                            joined_paths = "|".join(file_paths)
                            repo_id = hashlib.md5(joined_paths.encode()).hexdigest()
                            head_commit = None

                            key = BoWCacheKey(repo_id, head_commit, preprocess_signature)
                            cache = BoWCache()
                            final_bow: List[List[str]] = []

                            if cache.has(key):
                                cached = cache.get(key)
                                if cached is not None:
                                    final_bow = cached
                                    cli.print_status(f"Cache hit! Retrieved BoW for {len(final_bow)} documents.", "success")
                                else: 
                                    cli.print_status("Cache corrupted - regenerating...", "warning")

                            if not cache.has(key) or cached is None:
                                cli.print_status("Cache miss - processing text...", "info")
                                text_binary_data = get_bin_data_by_Nodes(text_nodes) if text_nodes else []
                                code_binary_data = get_bin_data_by_Nodes(code_nodes) if code_nodes else []
                                text_data = binary_to_str(text_binary_data) if text_nodes else []
                                code_data = binary_to_str(code_binary_data) if code_nodes else []

                                processed_docs = combined_preprocess(text_nodes, text_data, code_nodes, code_data, normalize=True)
                                anonymized_docs = remove_pii(processed_docs)
                                final_bow = anonymized_docs
                                cache.set(key, final_bow)
                                cli.print_status(f"Processed and cached {len(final_bow)} documents.", "success")

                            cli.print_status("Generating topic models...", "info")
                            lda_model, dictionary, doc_topic_vectors, topic_term_vectors = generate_topic_vectors(final_bow)
                            cli.print_status(f"Generated {len(topic_term_vectors)} topics from {len(doc_topic_vectors)} documents.", "success")

                            print("\n--- Top Topics Identified ---")
                            for i in range(min(5, len(topic_term_vectors))):
                                top_words = lda_model.show_topic(i, topn=5)
                                words_str = ", ".join([word for word, prob in top_words])
                                print(f"Topic {i}: {words_str}")
                            
                        else:
                            cli.print_status("No text/code files found to process.", "warning")
                    except Exception as e:
                        cli.print_status(f"Error during content analysis: {e}", "error")

                    processed_git_repos: List[Dict[str, Any]] = None
                    analyzed_repos: List[Dict[str, Any]] = None

                    if git_repos:
                        cli.print_header("Repository Linking")
                        print(f"Detected {len(git_repos)} git repositories.")

                        github_username: str = cli.get_input("Enter GitHub username to link (Press Enter to skip): \n> ").strip().lower()
                        
                        if github_username:
                            user_email: str = cli.get_input("Enter GitHub email associated with the account: \n> ").strip().lower()

                            repo_processor: RepositoryProcessor = RepositoryProcessor(
                                username=github_username,
                                binary_data_array=binary_data,
                                user_email=user_email if user_email else None
                            )
                            
                            try:
                                processed_git_repos = repo_processor.process_repositories(git_repos)
                                if not processed_git_repos:
                                    cli.print_status("No repositores to process.", "error")
                                else:
                                    cli.print_status("Repositories processed successfully.", "success")
                                    
                                    analyzer = RepositoryAnalyzer(github_username)

                                    #Generate the insights for ALL projects (not just what is displayed to allow for storage in db)
                                    analyzed_repos = analyzer.generate_project_insights(processed_git_repos)

                                    if not analyzed_repos:
                                        cli.print_status("No successful repository analyses.", "warning")
                                    else:
                                        cli.print_status(f"Analyzed {len(analyzed_repos)} repositories.", "success")
                                        
                                        # Generate the project timeline
                                        timeline = analyzer.create_chronological_project_list(processed_git_repos)

                                        # when generate_project_insights is run, the returned values are sorted by importance already
                                        display_project_summary(analyzed_repos, top_n=3)

                                        # display the detailed insights only for top 3 projects
                                        display_project_insights(analyzed_repos, top_n=3)

                                        display_project_timeline(timeline)
                                    
                            except Exception as e:
                                cli.print_status(f"Repository processing failed: {e}", "error")
                                import traceback
                                traceback.print_exc()
                        else:
                            cli.print_status("Skipping Git linking.", "info")
                    
                    text_analysis_data = {
                        "num_documents": len(doc_topic_vectors),
                        "num_topics": len(topic_term_vectors),
                        "doc_topic_vectors": doc_topic_vectors,
                        "topic_term_vectors": topic_term_vectors
                    } if doc_topic_vectors else {}
                    
                    project_analysis_data = {
                        "analyzed_insights": analyzed_repos if analyzed_repos else [],
                        "timeline": timeline if timeline else []
                    } if git_repos else []
                    
                    try:
                        cli.print_header("AI Summary Generation")
                        cli.print_status("Collecting analysis statistics...", "info")
                        data_bundle = collect_stats(
                            metadata_stats=metadata_results,
                            metadata_analysis=metadata_analysis,
                            text_analysis=text_analysis_data,
                            project_analysis=project_analysis_data
                        )
                        
                        topn_keywords = 10
                        topic_keywords = []
                        if lda_model is not None and dictionary is not None:
                            num_topics = len(topic_term_vectors) if topic_term_vectors else 0
                            for topic_id in range(num_topics):
                                words = [w for (w, _) in lda_model.show_topic(topic_id, topn=topn_keywords)]
                                topic_keywords.append({"topic_id": topic_id, "keywords": words})

                        doc_top_topics = []
                        for doc_idx, vec in enumerate(doc_topic_vectors or []):
                            if not vec:
                                doc_top_topics.append({"doc_id": doc_idx, "top_topics": []})
                                continue
                            top_pairs = sorted([(i, p) for i, p in enumerate(vec)], key=lambda x: x[1], reverse=True)[:2]
                            doc_top_topics.append({
                                "doc_id": doc_idx,
                                "top_topics": [{"topic_id": i, "prob": float(p)} for i, p in top_pairs]
                            })

                        topic_vector_bundle = {
                            "topic_keywords": topic_keywords,
                            "top_topics": doc_top_topics,
                        }
                        
                        cli.print_privacy_notice()

                        online_consent = config_manager.get_consent(
                            key="online_llm_consent",
                            prompt_text="Do you consent to using the ONLINE LLM?",
                            component="sending data to the Online LLM"
                        )

                        if online_consent:
                            cli.print_status("Mode: Online LLM", "success")
                            try:
                                llm_client = OnlineLLMClient()
                            except ValueError as e:
                                cli.print_status(f"Online Init failed: {e}. Falling back to Local.", "error")
                                llm_client = LocalLLMClient()
                        else:
                            cli.print_status("Mode: Local LLM", "success")
                            llm_client = LocalLLMClient()
                        
                        cli.print_status("Generating project summary (this may take a moment)...", "info")
                        
                        try:
                            medium_summary = llm_client.generate_summary(topic_vector_bundle)
                            cli.print_header("Standard Summary")
                            print(medium_summary)
                            print("=" * 60 + "\n")
                            
                        except Exception as e:
                            cli.print_status(f"Error generating summary: {e}", "error")
                    
                    except Exception as e:
                        cli.print_status(f"Error collecting statistics: {e}", "error")

                elif fm_result["status"] == "error":
                    cli.print_status(f"Load Error: {fm_result.get('message', 'Unknown error')}", "error")
                
                # save tracked data and insights to database
                try:
                    result_id: int = database_manager.create_new_result() # create new result entry in the database
                    # save tracked data
                    database_manager.save_tracked_data(result_id, metadata_results, final_bow, processed_git_repos)

                    # save insights
                    database_manager.save_metadata_analysis(result_id, metadata_analysis)
                    database_manager.save_text_analysis(result_id, doc_topic_vectors, topic_term_vectors)
                    database_manager.save_repository_analysis(result_id, project_analysis_data)
                    database_manager.save_resume_points(result_id, medium_summary)
                except Exception as e:
                    cli.print_status(f"Error saving result to database: {e}", "error")
                    result_id = -1


                # Ask to continue
                cont = cli.get_input("\nProcess another file? (y/n): ").lower()
                if cont in ('y', 'yes'):
                    continue
            
            except Exception as e:
                cli.print_status(f"File path is not valid: {e}", "error")
                retry: str = cli.get_input("\nTry again? (y/n) \n> ").strip().lower()
                if retry in ("n", "no"):
                    print("\nExiting.")
                    break

        else:
            print("\nInput invalid - try again (y/n) ")

        # View all saved insights from database
        try:
            view_results = cli.get_input("View all stored results? (y/n): ").lower()
            if view_results in ('y', 'yes'):
                all_results: List[Dict] = database_manager.get_all_results_summary()
                cli.print_header("All Stored Results Summary")
                for res in all_results:
                    print(f"Result ID: {res['result_id']}")
                    print("\nMetadata insights:")
                    print(f"{'Extension':<10} | {'Count':<8} | {'Size':<15} | {'Percentage':<8} | {'Category'}")
                    print("-" * 70)
                    
                    meta_insights = res['metadata_insights']
                    for ext, stats in meta_insights['extension_stats'].items():
                        print(f"{ext:<10} | {stats['count']:<8} | {stats['total_size']:<15} | {stats['percentage']:<8}% | {stats['category']}")
                    print(f"\nPrimary skills: {', '.join(meta_insights['primary_skills'])}\n")
        except Exception as e:
            cli.print_status(f"Error retrieving all results: {e}", "error")
        
        # View specific result by ID
        view_result = cli.get_input("\nView a specific result by ID? (y/n): ").lower()
        if view_result in ('y', 'yes'):
            while True:
                try:
                    view_id = cli.get_input("Enter Result ID: ").strip()
                    result: Dict[str, Any] = database_manager.get_result_by_id(view_id)
                    if result:
                        cli.print_header(f"Result ID: {view_id}")
                        # Check that results are saved properly
                        # print(f"Topic vectors: {result['topic_vector']}")
                        print("Resume points:")
                        print(f"{result['resume_points']}")

                        # Display the project insights
                        project_insights = result.get('project_insights', {})
                        if project_insights:
                            analyzed_repos = project_insights.get('analyzed_insights',[])
                            timeline = project_insights.get('timeline', [])

                            if analyzed_repos:
                                display_project_summary(analyzed_repos, top_n=3)
                                display_project_insights(analyzed_repos, top_n=3)
                                display_project_timeline(timeline)
                            
                            else:
                                print("\n=== Project Insights ===")
                                print("No project insights available.")
                        else:
                            print("\n=== Project Insights ===")
                            print("No project data available.")
                        


                        print(f"\nPackage insights: {result['package_insights']}")
                        print("\nMetadata insights:")
                        print(f"{'Extension':<10} | {'Count':<8} | {'Size':<15} | {'Percentage':<8} | {'Category'}")
                        print("-" * 70)
                        for ext, stats in result['metadata_insights']['extension_stats'].items():
                            print(f"{ext:<10} | {stats['count']:<8} | {stats['total_size']:<15} | {stats['percentage']:<8}% | {stats['category']}")
                        
                        # Check that tracked data is saved properly
                        # print(f"\nTracked data summary:")
                        # print(f"BoW cache: {result['tracked_data']['bow_cache']}")
                        # print(f"Project data: {result['tracked_data']['project_data']}")
                        # print(f"Package data: {result['tracked_data']['package_data']}")
                        # print(f"Metadata stats: {result['tracked_data']['metadata_stats']}")
                        
                        # Ask to continue
                        cont_view = cli.get_input("\nView another stored result? (y/n): ").lower()
                        if cont_view not in ('y', 'yes'):
                            break

                    else:
                        cli.print_status(f"No result found with ID: {view_id}", "error")
                        retry_view = cli.get_input("Try again? (y/n): ").strip().lower()
                        if retry_view in ('n', 'no'):
                            break

                except ValueError:
                    cli.print_status("Invalid ID entered.", "error")
                except Exception as e:
                    cli.print_status(f"Error retrieving result: {e}", "error")

        # Delete results from database
        try:
            delete_results = cli.get_input("\nDelete all stored results? (y/n): ").lower()
            if delete_results in ('y', 'yes'):
                database_manager.wipe_all_data()
                cli.print_status("All results deleted from database.", "success")
        except Exception as e:
            cli.print_status(f"Error deleting results: {e}", "error")

        # Delete specific result from database
        delete_result = cli.get_input("\nDelete a stored result? (y/n): ").lower()
        if delete_result in ('y', 'yes'):
            while True:
                try:
                    result_id_to_delete = cli.get_input("Enter Result ID to delete: ").strip()
                    database_manager.delete_result(result_id_to_delete)
                    cli.print_status(f"Result with ID {result_id_to_delete} deleted from database.", "success")
                    
                    # Ask to continue
                    cont_del = cli.get_input("\nDelete another stored result? (y/n): ").lower()
                    if cont_del not in ('y', 'yes'):
                        break
                except Exception as e:
                    cli.print_status(f"Error deleting result with ID {result_id_to_delete}: {e}", "error")
    except KeyboardInterrupt:
        print("\n\nExiting.")
        sys.exit(0)

if __name__ == "__main__":
    main()