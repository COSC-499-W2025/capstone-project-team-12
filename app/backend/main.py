import sys
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
        component="accessing your local files"  
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
            -'G' to generate resume or portfolio from past analysis.\n\t
            -'T' to edit or update thumbnail for past analysis\n\t
            -'U' to update a past analysis.\n\t
            -'D' to delete particular analysis.\n\t
            -'R' to delete all past analysis.\n\t
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
                        result_id = pipeline.run_analysis(str(path),return_id=True) #Return the new result id so it can be used to add image to result
                    except Exception as e:
                        cli.print_status(f"Analysis Pipeline Error: {e}", "error")
                        
                    #Thumbnail handling
                    
                    #Prompt to add thumbnail
                    img_response = cli.get_input("Would you like to add a thumbnail to represent this analysis? (y/N) \n")            
                    if img_response.lower() in ('y','yes'):
                        try:    
                            #Receive image filepath
                            img_path:str = cli.get_input(f"Accepted formats are: {accepted_formats} of maximum size 10MB.\n Please enter a filepath to a valid image:\n")
                            
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
                                insert_thumbnail(database_manager,cli,result_id,img_data)
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
                        view_all_results(database_manager)
                    except Exception as e:
                        cli.print_status(f"Error retrieving all analysis: {e}", "error")
                case 'v':
                    try:    
                        result_id = cli.get_input("Enter Analysis ID: ").strip()
                        result_id = validate_uuid(result_id)
                        view_result_by_id(database_manager,cli,result_id)        
                    except ValueError as e:
                        cli.print_status(f"UUID Error:{e}", "error")
                    except Exception as e:
                        cli.print_status(f"Error retrieving analysis: {e}", "error")
                case 'g':
                    # Generate new resume
                    try:
                        result_id = cli.get_input("Enter Analysis ID to generate Portfolio or Resume from: ").strip()
                        result_id = validate_uuid(result_id)

                        generation_type = cli.get_input("Would you like to generate a Portfolio or a Resume? (P/R): ").strip().lower()

                        if generation_type in ('r','resume'):
                            resume = resume_builder.create_resume_from_result_id(database_manager, cli, result_id)
                            if resume:
                                resume_builder.display_resume(resume, cli)
                                # Allow the user to edit the resume before saving
                                edit_choice:str = cli.get_input("Would you like to edit the resume before saving? (y/n): ").strip().lower()
                                if edit_choice in ('y', 'yes'):
                                    editor = ResumeEditor(cli)
                                    resume = editor.edit_resume(resume)

                        elif generation_type in ('p','portfolio'):
                            portfolio = portfolio_builder.create_portfolio_from_result_id(database_manager, cli, result_id)
                            if portfolio:
                                portfolio_builder.display_portfolio(portfolio, cli)

                                edit_choice:str = cli.get_input("Would you like to edit the portfolio before saving? (y/n): ").strip().lower()
                                if edit_choice in ('y', 'yes'):
                                    portfolio_editor = PortfolioEditor(cli)
                                    portfolio = portfolio_editor.edit_portfolio(portfolio)                     

                        else:
                            cli.print_status("Invalid generation type input","error")
                            
                    except ValueError as e:
                        cli.print_status(f"UUID Error:{e}", "error")
                    except Exception as e:              
                        cli.print_status(f"Error generating portfolio or resume: {e}", "error")
                
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
                    print("\n--- Update Existing Analysis ---")
                    analysis_id = cli.get_input("Enter Analysis ID to update: ").strip()
                    
                    # 1. Fetch info
                    old_path = database_manager.get_analysis_filepath(analysis_id)
                    if not old_path:
                        cli.print_status("Analysis ID not found or has no associated file path.", "error")
                        continue
                        
                    print(f"Current file path for this analysis: {old_path}")
                    
                    # 2. Get new path
                    new_path = cli.get_input(f"Enter updated file path (Press Enter to use '{old_path}'): ").strip()
                    if not new_path:
                        new_path = old_path
                        
                    if not os.path.exists(new_path):
                        cli.print_status("Error: The specified path does not exist.", "error")
                        continue

                    # 3. Logical Similarity Check (Basic)
                    old_name = Path(old_path).name
                    new_name = Path(new_path).name
                    
                    if old_name != new_name:
                        print(f"\n[WARNING] The new path '{new_name}' looks different from the old path '{old_name}'.")
                        confirm = cli.get_input("Are you sure this is the correct update? (y/n): ").lower()
                        if confirm != 'y':
                            cli.print_status("Update cancelled.", "warning")
                            continue

                    print("\nLoading new files...")
                    # 4. Load NEW files
                    load_result = file_manager.load_from_filepath(new_path)
                    if load_result['status'] == 'error':
                        cli.print_status(f"Error loading files: {load_result['message']}", "error")
                        continue
                    
                    new_tree = load_result['tree']
                    new_binary_list = load_result['binary_data']

                    # 5. Fetch OLD data from DB
                    print("Fetching previous analysis state...")
                    old_binary_blob, old_tree_dict = database_manager.get_fileset_data(analysis_id)
                    
                    if not old_binary_blob or not old_tree_dict:
                        cli.print_status("Error: Could not retrieve previous file data from database.", "error")
                        continue

                    # Deserialize
                    old_binary_list = pickle.loads(old_binary_blob)
                    old_tree = importer.import_(old_tree_dict)

                    # 6. Merge
                    print("Comparing and merging updates...")
                    merged_tree, merged_binary_list = tree_manager.merge_trees(
                        old_tree, old_binary_list, new_tree, new_binary_list
                    )

                    # 7. Save merged result
                    print("Saving updated state to database...")
                    merged_tree_dict = exporter.export(merged_tree)
                    merged_binary_blob = pickle.dumps(merged_binary_list)
                    
                    if database_manager.save_fileset(analysis_id, merged_binary_blob, merged_tree_dict, new_path):
                        cli.print_status("Update successful!", "success")
                        # Optional: Trigger re-analysis here if desired
                    else:
                        cli.print_status("Failed to save updates to database.", "error")

                case 'd':
                    # Delete specific analysis from database
                    delete_result = cli.get_input("\nDelete a stored analysis? (y/n): ").lower()
                    if delete_result in ('y', 'yes'):
                        try:
                            result_id = cli.get_input("Enter Result ID to delete: ").strip()
                            result_id = validate_uuid(result_id)
                            delete_result_by_id(database_manager,cli,result_id)
                        except ValueError as e:
                            cli.print_status(f"UUID Error:{e}","error")
                        except Exception as e:
                            cli.print_status(f"Error deleting result with ID {result_id}: {e}", "error")
                case'r':
                    # Delete results from database
                    try:
                        delete_results = cli.get_input("\nType 'CONFIRM DELETE' to erase of all past results in database (case-sensitive):")
                        if delete_results == "CONFIRM DELETE":
                            delete_all_results(database_manager)
                            cli.print_status("All results deleted from database.", "success")
                        else:
                            cli.print_status("Improper confirmation, No results deleted.","warning")
                    except Exception as e:
                        cli.print_status(f"Error deleting results: {e}", "error")
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