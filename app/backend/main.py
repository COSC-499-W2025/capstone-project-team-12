import sys
from typing import List, Dict, Any
from pathlib import Path
from config_manager import ConfigManager
from database_manager import DatabaseManager

from cli_interface import CLI
from analysis_pipeline import AnalysisPipeline
from main_utils import *
from input_validation import *
from resume_builder import ResumeBuilder


    
def main() -> None:
    # Initialize CLI Interface
    cli = CLI()
    
    config_manager = ConfigManager() # Initialize Config Manager
    database_manager = DatabaseManager()  # Initialize Database Manager
    resume_builder = ResumeBuilder()    # Initialize Resume Builder
    
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
            -'A' to view all past results.\n\t
            -'V' to view particular result.\n\t
            -'G' to generate resume from past result.\n\t
            -'U' to update a past result.\n\t
            -'D' to delete particular result.\n\t
            -'R' to delete all past results.\n\t
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
                    img_response = cli.get_input("Would you like to add a thumbnail to represent this result? (y/N) \n")            
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
                        cli.print_header("All Stored Results Summary")
                        view_all_results(database_manager)
                    except Exception as e:
                        cli.print_status(f"Error retrieving all results: {e}", "error")
                case 'v':
                    try:    
                        result_id = cli.get_input("Enter Result ID: ").strip()
                        result_id = validate_uuid(result_id)
                        view_result_by_id(database_manager,cli,result_id)        
                    except ValueError as e:
                        cli.print_status(f"UUID Error:{e}", "error")
                    except Exception as e:
                        cli.print_status(f"Error retrieving result: {e}", "error")
                case 'g':
                    # Generate new resume
                    try:
                        result_id = cli.get_input("Enter Result ID to generate resume from: ").strip()
                        result_id = validate_uuid(result_id)

                        resume = resume_builder.create_resume_from_result_id(database_manager, cli, result_id)
                        if resume:
                            resume_builder.display_resume(resume, cli)

                    except ValueError as e:
                        cli.print_status(f"UUID Error:{e}", "error")
                    except Exception as e:
                        cli.print_status(f"Error generating resume: {e}", "error")
                    
                case 'u':
                    # TODO functionality to update past result (incremental requirment)
                    print() #Place holder to satisfy match-case syntax
                case 'd':
                    # Delete specific result from database
                    delete_result = cli.get_input("\nDelete a stored result? (y/n): ").lower()
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