import sys
from pathlib import Path
from typing import List, Dict, Any

from config_manager import ConfigManager
from database_manager import DatabaseManager
from display_helpers import display_project_insights, display_project_summary, display_project_timeline
from cli_interface import CLI
from analysis_pipeline import AnalysisPipeline

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
    
def main() -> None:
    # Initialize CLI Interface
    cli = CLI()
    
    config_manager = ConfigManager() # Initialize Config Manager
    database_manager = DatabaseManager()  # Initialize Database Manager
    
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
                
                #analysis pipeline starting, moved to another file
                pipeline = AnalysisPipeline(cli, config_manager, database_manager)
                pipeline.run_analysis(str(path))

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