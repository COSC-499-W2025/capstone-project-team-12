import sys
import os
import pickle
from typing import List, Dict, Any
from pathlib import Path
from anytree.importer import DictImporter
from anytree.exporter import DictExporter
from config_manager import ConfigManager
from database_manager import DatabaseManager

from cli_interface import CLI
from analysis_pipeline import AnalysisPipeline
from main_utils import *
from input_validation import *
from resume_builder import ResumeBuilder
from resume_editor import ResumeEditor
from portfolio_builder import PortfolioBuilder
from portfolio_editor import PortfolioEditor
from file_manager import FileManager
from tree_manager import TreeManager


    
def main() -> None:
    # Initialize CLI Interface
    cli = CLI()
    
    config_manager = ConfigManager()
    database_manager = DatabaseManager()
    resume_builder = ResumeBuilder()
    portfolio_builder = PortfolioBuilder()
    file_manager = FileManager()
    tree_manager = TreeManager()
    importer = DictImporter()
    exporter = DictExporter()
    
    cli.print_header("Artifact Mining App")
        
    has_file_access = config_manager.get_consent(
        key="file_access_consent", 
        prompt_text="Do you provide permission to access your file system?",
        component="accessing your local files",
        default=True
    )

    if not has_file_access:
        cli.print_status("File system access is required to run this app.", "error")
        sys.exit(0)

    while True:
        cli.print_separator()
        operation: str = cli.get_input(
            "\n  N  — analyse a new filepath"
            "\n  A  — view all past analyses"
            "\n  V  — view a particular analysis"
            "\n  R  — manage resumes"
            "\n  P  — manage portfolios"
            "\n  T  — edit thumbnail for an analysis"
            "\n  U  — update a past analysis"
            "\n  D  — delete a particular analysis"
            "\n  X  — delete all past analyses"
            "\n  Q  — quit"
            "\n\n> ").strip().lower()
        try:
            match(operation):
                case 'n':
                    filepath: str = cli.get_input("\n  Enter a file path to process:\n> ").strip()
                    try:
                        path: Path = validate_analysis_path(filepath)
                        cli.print_status(f"Path valid: {path}", "success")
                    except Exception as e:
                        cli.print_status(f"Invalid file path: {e}", "error")
                    
                    analysis_id = None
                    try:
                        pipeline = AnalysisPipeline(cli, config_manager, database_manager)
                        analysis_id = pipeline.run_analysis(str(path), return_id=True)
                    except Exception as e:
                        cli.print_status(f"Analysis pipeline error: {e}", "error")

                    if analysis_id:
                        cli.print_status("Generating resume and portfolio...", "info")
                        try: 
                            resume = generate_resume(analysis_id, database_manager, resume_builder, cli)
                        except Exception as e:
                            cli.print_status(f"Error generating resume: {e}", "error")
                        try:
                            portfolio = generate_portfolio(analysis_id, database_manager, portfolio_builder, cli)
                        except Exception as e:
                            cli.print_status(f"Error generating portfolio: {e}", "error")

                    img_response = cli.get_input("\n  Add a thumbnail for this analysis? (Y/n)\n> ")
                    if img_response.lower() not in ('n', 'no'):
                        try:
                            img_path: str = cli.get_input(
                                f"\n  Accepted formats: {accepted_formats}  |  Max size: 10MB"
                                "\n  Enter image filepath, or [Enter] to skip:\n> "
                            )
                            
                            if not img_path.strip():
                                cli.print_status("No thumbnail added.", "info")
                                continue

                            try:
                                img_valid_path: Path = validate_thumbnail_path(img_path)
                            except Exception as e:
                                raise RuntimeError(f"Image path error: {e}")
                            
                            try:
                                img_data: BinaryIO = read_image(img_valid_path)
                            except Exception as e:
                                raise RuntimeError(f"Error reading image: {e}")

                            try:
                                insert_thumbnail(database_manager, cli, analysis_id, img_data)
                                cli.print_status("Thumbnail added successfully.", "success")
                            except Exception as e:
                                raise RuntimeError(f"Failed to save thumbnail: {e}")

                        except RuntimeError as e:
                            cli.print_status(f"Thumbnail error: {e}", "warning")
                        except Exception as e:
                            cli.print_status(f"Unexpected thumbnail error: {e}", "warning")
                            continue
                    
                case 'a':
                    try:
                        cli.print_header("All Stored Analyses")
                        view_all_analyses(database_manager)
                    except Exception as e:
                        cli.print_status(f"Error retrieving analyses: {e}", "error")

                case 'v':
                    try:
                        analysis_id = cli.get_input("\n  Enter Analysis ID:\n> ").strip()
                        analysis_id = validate_uuid(analysis_id)
                        view_analysis_by_id(database_manager, cli, analysis_id)
                    except ValueError as e:
                        cli.print_status(f"Invalid UUID: {e}", "error")
                    except Exception as e:
                        cli.print_status(f"Error retrieving analysis: {e}", "error")

                case 'r':
                    try:
                        manage_resumes(cli, database_manager, resume_builder)
                    except Exception as e:
                        cli.print_status(f"Error managing resumes: {e}", "error")

                case 'p':
                    try:
                        manage_portfolios(cli, database_manager, portfolio_builder)
                    except Exception as e:
                        cli.print_status(f"Error managing portfolios: {e}", "error")
                
                case 't':
                    analysis_id: str = cli.get_input("\n  Enter Analysis ID:\n> ")
                    img_path: str = cli.get_input(
                        f"\n  Accepted formats: {accepted_formats}  |  Max size: 10MB"
                        "\n  Enter image filepath:\n> "
                    )
                    try:
                        try:
                            img_valid_path: Path = validate_thumbnail_path(img_path)
                        except Exception as e:
                            raise RuntimeError(f"Image path error: {e}")
                        
                        try:
                            img_data: BinaryIO = read_image(img_valid_path)
                        except Exception as e:
                            raise RuntimeError(f"Error reading image: {e}")

                        try:
                            insert_thumbnail(database_manager, cli, analysis_id, img_data)
                            cli.print_status("Thumbnail added successfully.", "success")
                        except Exception as e:
                            raise RuntimeError(f"Failed to save thumbnail: {e}")

                    except RuntimeError as e:
                        cli.print_status(f"Thumbnail error: {e}", "error")
                    except Exception as e:
                        cli.print_status(f"Unexpected thumbnail error: {e}", "warning")
                        continue
                
                case 'u':
                    cli.print_header("Update Existing Analysis")
                    analysis_id = cli.get_input("\n  Enter Analysis ID to update:\n> ").strip()
                    
                    try:
                        old_path = database_manager.get_analysis_filepath(analysis_id)
                        if not old_path:
                            raise ValueError("Analysis not found or has no associated file path.")
                    except Exception as e:
                        cli.print_status(f"{e}", "error")
                        
                    cli.print_status(f"Current path: {old_path}", "info")
                    
                    new_path = None
                    while True:
                        path_input = cli.get_input(
                            f"\n  Enter updated path, [Enter] to keep current, or 'b' to go back:\n> "
                        ).strip()
                        
                        if path_input.lower() == 'b':
                            new_path = None
                            break
                        
                        current_candidate = path_input if path_input else old_path
                            
                        if not os.path.exists(current_candidate):
                            cli.print_status("Path does not exist.", "error")
                            continue

                        if not compare_path(old_path, current_candidate):
                            cli.print_status("Update cancelled. Please re-enter path.", "warning")
                            continue
                        
                        new_path = current_candidate
                        break

                    if new_path is None:
                        continue

                    cli.print_status("Loading files...", "info")
                    load_result = file_manager.load_from_filepath(new_path)
                    if load_result['status'] == 'error':
                        cli.print_status(f"Error loading files: {load_result['message']}", "error")
                        continue
                    
                    new_tree = load_result['tree']
                    new_binary_list = load_result['binary_data']

                    try:
                        merged_tree, merged_binary_list = perform_update_merge(
                            analysis_id, new_tree, new_binary_list, database_manager, tree_manager, importer, exporter)
                        
                        if not merged_tree:
                            raise LookupError("Could not retrieve previous file data from database.")
                    
                    except Exception as e:
                        cli.print_status(f"{e}", "error")
                        continue

                    cli.print_status("Saving updated state...", "info")
                    merged_tree_dict = exporter.export(merged_tree)
                    merged_binary_blob = pickle.dumps(merged_binary_list)
                    
                    try:
                        database_manager.save_fileset(analysis_id, merged_binary_blob, merged_tree_dict, new_path)
                    except Exception as e:
                        cli.print_status("Failed to save updates to database.", "error")
                        continue
                    
                    cli.print_status("Update saved. Re-running analysis on updated files...", "success")
                    
                    try:
                        pipeline = AnalysisPipeline(cli, config_manager, database_manager)
                        pipeline.run_analysis(
                            filepath=new_path, 
                            return_id=False,
                            existing_analysis_id=analysis_id,
                            preloaded_tree=merged_tree,
                            preloaded_binary=merged_binary_list
                        )
                        cli.print_status("Analysis update complete.", "success")
                    except Exception as e:
                        cli.print_status(f"Error re-running analysis: {e}", "error")

                case 'd':
                    delete_confirmation = cli.get_input("\n  Delete a stored analysis? (y/n):\n> ").lower()
                    if delete_confirmation not in ('n', 'no'):
                        try:
                            analysis_id = cli.get_input("  Enter Analysis ID (or [Enter] to cancel):\n> ").strip()
                            if not analysis_id.strip():
                                cli.print_status("Deletion cancelled.", "info")
                                continue
                            analysis_id = validate_uuid(analysis_id)
                            delete_analysis_by_id(database_manager, cli, analysis_id)
                        except ValueError as e:
                            cli.print_status(f"Invalid UUID: {e}", "error")
                        except Exception as e:
                            cli.print_status(f"Error deleting analysis {analysis_id}: {e}", "error")

                case 'x':
                    try:
                        delete_confirmation = cli.get_input("\n  Type 'CONFIRM DELETE' to erase all analyses (case-sensitive):\n> ")
                        if delete_confirmation == "CONFIRM DELETE":
                            delete_all_analyses(database_manager)
                            cli.print_status("All analyses deleted.", "success")
                        else:
                            cli.print_status("Confirmation not matched — nothing deleted.", "warning")
                    except Exception as e:
                        cli.print_status(f"Error deleting analyses: {e}", "error")

                case 'q':
                    sys.exit(0)

                case _:
                    cli.print_status("Unrecognised option.", "error")

            print("\n  Press [Enter] to return to the main menu")
            input()

        except KeyboardInterrupt:
            cli.print_status("Operation cancelled.", "warning")
    
            


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n  Exiting...")