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
    
    config_manager = ConfigManager() # Initialize Config Manager
    database_manager = DatabaseManager()  # Initialize Database Manager
    resume_builder = ResumeBuilder()    # Initialize Resume Builder
    portfolio_builder = PortfolioBuilder()  # Initialize Portfolio Builder
    file_manager = FileManager()
    tree_manager = TreeManager()
    importer = DictImporter()
    exporter = DictExporter()
    
    cli.print_header("Artifact Mining App")
        
    has_file_access = config_manager.get_consent(
        key="file_access_consent", 
        prompt_text="Do you provide permission to access your file system?",
        component="accessing your local files" ,
        default=True  # We default to YES to allow for basic app functionality, but users can easily revoke if they want 
    )

    if not has_file_access:
        print("Access to files is required.")
        sys.exit(0)

        #MAIN LOOP
    while True:
        cli.print_separator("-")
        operation: str = cli.get_input(
            """Press: \n\t
            -'N' to perform analysis on new filepath\n\t
            -'A' to view all past analysis.\n\t
            -'V' to view particular analysis.\n\t
            -'R' to view and manage resumes\n\t
            -'P' to view and manage portfolios\n\t
            -'T' to edit or update thumbnail for past analysis\n\t
            -'U' to update a past analysis.\n\t
            -'D' to delete particular analysis.\n\t
            -'X' to delete all past analysis.\n\t
            -'Q' to quit app\n""").strip().lower() 
        try:
            match(operation):
                case 'n':
                    #Analysis Filepath and analysis handling
                    filepath: str = cli.get_input("Enter a file path to process: \n> ").strip()
                    try:
                        path: Path = validate_analysis_path(filepath)
                        cli.print_status(f"Path valid: {path}", "success")
                    except Exception as e:
                        cli.print_status(f"File path is not valid: {e}", "error")
                    
                    try:
                        #analysis pipeline starting, moved to another file
                        pipeline = AnalysisPipeline(cli, config_manager, database_manager)
                        analysis_id = pipeline.run_analysis(str(path),return_id=True) #Return the new analysis id so it can be used to add image to analysis
                    except Exception as e:
                        cli.print_status(f"Analysis Pipeline Error: {e}", "error")
                        


                    # Auto generate resume and portfolio after analysis completion
                    if analysis_id:
                        cli.print_status("Generating resume and portfolio for this analysis...", "info")
                        try: 
                            resume = generate_resume(analysis_id, database_manager, resume_builder, cli)
                        except Exception as e:
                            cli.print_status(f"Error generating resume: {e}", "error")
                        try:
                            portfolio = generate_portfolio(analysis_id, database_manager, portfolio_builder, cli)
                        except Exception as e:
                            cli.print_status(f"Error generating portfolio: {e}", "error")

                    #Thumbnail handling
                    
                    #Prompt to add thumbnail
                    img_response = cli.get_input("Would you like to add a thumbnail to represent this analysis? (Y/n) \n")            
                    if img_response.lower() not in ('n','no'):
                        try:    
                            #Receive image filepath
                            img_path:str = cli.get_input(f"Accepted formats are: {accepted_formats} of maximum size 10MB.\n Please enter a filepath to a valid image (or press Enter to skip):\n")
                            
                            # If user opts to skip thumbnail addition, continue to main menu
                            if not img_path.strip():
                                cli.print_status("No thumbnail will be added for this analysis.", "info")
                                continue

                            #Validate image filepath 
                            try:
                                img_valid_path:Path = validate_thumbnail_path(img_path)
                            except Exception as e:
                                raise RuntimeError(f"Image filepath Error:{e}")
                            
                            #Read image
                            try:
                                img_data:BinaryIO = read_image(img_valid_path)
                            except Exception as e:
                                raise RuntimeError(f"Error reading image:{e}")
                            #Save Image to db
                            try:
                                insert_thumbnail(database_manager,cli,analysis_id,img_data)
                                cli.print_status(f"Image added successfully!","success")
                            except Exception as e:
                                raise RuntimeError(f"Failed to add image to db:{e}")
                        except RuntimeError as e:
                            cli.print_status(f"Thumbnail Association failed:{e}","warning")
                        except Exception as e:
                            cli.print_status(f"Unhandled Thumbnail Error:{e} \n Returning to main menu", "warning")
                            continue
                    
                            
                case 'a':
                    # View all saved insights from database
                    try:
                        cli.print_header("All Stored Analysis Summary")
                        view_all_analyses(database_manager)
                    except Exception as e:
                        cli.print_status(f"Error retrieving all analysis: {e}", "error")
                case 'v':
                    try:    
                        analysis_id = cli.get_input("Enter Analysis ID: ").strip()
                        analysis_id = validate_uuid(analysis_id)
                        view_analysis_by_id(database_manager,cli,analysis_id)        
                    except ValueError as e:
                        cli.print_status(f"UUID Error:{e}", "error")
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
                    analysis_id:str = cli.get_input("Enter Analysis ID to add/edit the thumbnail of:")
                    img_path:str = cli.get_input(f"Accepted formats are: {accepted_formats} of maximum size 10MB.\n Please enter a filepath to a valid image:\n")
                    try:       
                        #Validate image filepath 
                        try:
                            img_valid_path:Path = validate_thumbnail_path(img_path)
                        except Exception as e:
                            raise RuntimeError(f"Image filepath Error:{e}")
                        
                        #Read image
                        try:
                            img_data:BinaryIO = read_image(img_valid_path)
                        except Exception as e:
                            raise RuntimeError(f"Error reading image:{e}")
                        #Save Image to db
                        try:
                            insert_thumbnail(database_manager,cli,analysis_id,img_data)
                            cli.print_status(f"Image added successfully!","success")
                        except Exception as e:
                            raise RuntimeError(f"Failed to add image to db:{e}")
                    except RuntimeError as e:
                        cli.print_status(f"Thumbnail Association failed:{e}","error")
                    except Exception as e:
                        cli.print_status(f"Unhandled Thumbnail Error:{e} \n Returning to main menu", "warning")
                        continue   
                
                case 'u':
                    # TODO functionality to update past analysis (incremental requirment)
                    print("\n--- Update Existing Analysis ---")
                    analysis_id = cli.get_input("Enter Analysis ID to update: ").strip()
                    
                    # 1. Fetch info
                    try:
                        old_path = database_manager.get_analysis_filepath(analysis_id)
                        if not old_path:
                            raise ValueError("Analysis ID not found or has no associated file path.")
                    except Exception as e:
                        cli.print_status(f"{e}","error")
                        
                    print(f"Current file path for this analysis: {old_path}")
                    
                    new_path = None
                    # Loop until a valid, confirmed path is chosen or user explicitly backs out
                    while True:
                        path_input = cli.get_input(f"Enter updated file path (Press Enter to use '{old_path}' or 'b' to go back to main menu): ").strip()
                        
                        if path_input.lower() == 'b':
                            new_path = None # Signal to abort
                            break
                        
                        current_candidate = path_input if path_input else old_path
                            
                        if not os.path.exists(current_candidate):
                            cli.print_status("Error: The specified path does not exist.", "error")
                            continue # Ask again

                        # USE EXTRACTED HELPER from main_utils
                        if not compare_path(old_path, current_candidate):
                            cli.print_status("Update cancelled. Please re-enter path.", "warning")
                            continue # Loop back to ask for path again
                        
                        # Valid path selected
                        new_path = current_candidate
                        break

                    # If user aborted with 'b'
                    if new_path is None:
                        continue

                    print("\nLoading new files...")
                    # 4. Load NEW files
                    load_result = file_manager.load_from_filepath(new_path)
                    if load_result['status'] == 'error':
                        cli.print_status(f"Error loading files: {load_result['message']}", "error")
                        continue
                    
                    new_tree = load_result['tree']
                    new_binary_list = load_result['binary_data']

                    # USE EXTRACTED HELPER for merging/db logic
                    try:
                        merged_tree, merged_binary_list = perform_update_merge(
                            analysis_id, new_tree, new_binary_list, database_manager, tree_manager, importer, exporter)
                        
                        if not merged_tree:
                            raise LookupError("Error: Could not retrieve previous file data from database.")
                    
                    except Exception as e:
                        cli.print_status(f"{e}", "error")
                        continue

                    # 7. Save merged result
                    print("Saving updated state to database...")
                    merged_tree_dict = exporter.export(merged_tree)
                    merged_binary_blob = pickle.dumps(merged_binary_list)
                    
                    try:
                        database_manager.save_fileset(analysis_id, merged_binary_blob, merged_tree_dict, new_path)
                    except Exception as e:
                        cli.print_status("Failed to save updates to database.", "error")
                        continue
                    
                    cli.print_status("Update successful! Re-running analysis on updated files...", "success")         
                    
                    # 8. Re-run analysis pipeline on the MERGED data
                    try:
                        pipeline = AnalysisPipeline(cli, config_manager, database_manager)
                        # Call the updated run_analysis with the merged data
                        pipeline.run_analysis(
                            filepath=new_path, 
                            return_id=False,
                            existing_analysis_id=analysis_id,
                            preloaded_tree=merged_tree,
                            preloaded_binary=merged_binary_list
                        )
                        cli.print_status("Analysis update complete.", "success")
                    except Exception as e:
                        cli.print_status(f"Error re-running analysis pipeline: {e}", "error")

                case 'd':
                    # Delete specific analysis from database
                    delete_confirmation = cli.get_input("\nDelete a stored analysis? (y/n): ").lower()
                    if delete_confirmation not in ('n', 'no'):
                        try:
                            analysis_id = cli.get_input("Enter Analysis ID to delete: (or press Enter to cancel)").strip()
                            if not analysis_id.strip():
                                cli.print_status("Deletion cancelled.", "info")
                                continue
                            analysis_id = validate_uuid(analysis_id)
                            delete_analysis_by_id(database_manager,cli,analysis_id)
                        except ValueError as e:
                            cli.print_status(f"UUID Error:{e}","error")
                        except Exception as e:
                            cli.print_status(f"Error deleting analysis with ID {analysis_id}: {e}", "error")
                case 'x':
                    # Delete analyses from database
                    try:
                        delete_confirmation = cli.get_input("\nType 'CONFIRM DELETE' to erase of all past analyses in database (case-sensitive):")
                        if delete_confirmation == "CONFIRM DELETE":
                            delete_all_analyses(database_manager)
                            cli.print_status("All all analyses deleted from database.", "success")
                        else:
                            cli.print_status("Improper confirmation, No analyses deleted.","warning")
                    except Exception as e:
                        cli.print_status(f"Error deleting analyses: {e}", "error")
                case 'q':
                    sys.exit(0)
                case _:
                    cli.print_status("Invalid operation input","error")
            print("Press Enter key to return to main menu")
            input()
        except KeyboardInterrupt:
            cli.print_status("Keyboard Interrupt detected, Aborting process", "warning")
    
            


if __name__ == "__main__":
    main()