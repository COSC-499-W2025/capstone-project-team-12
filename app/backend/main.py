import sys
from typing import List, Dict, Any
from pathlib import Path
from config_manager import ConfigManager
from database_manager import DatabaseManager

from cli_interface import CLI
from analysis_pipeline import AnalysisPipeline
from main_utils import *
from input_validation import *


    
def main() -> None:
    # Initialize CLI Interface
    cli = CLI()
    
    config_manager = ConfigManager() # Initialize Config Manager
    database_manager = DatabaseManager()  # Initialize Database Manager
    
    
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
            -'U' to update a past result.\n\t
            -'D' to delete particular result.\n\t
            -'R' to delete all past results.\n\t
            -'Q' to quit app\n""").strip().lower() 
        try:
            match(operation):
                case 'n':
                    filepath: str = cli.get_input("Enter a file path to process: \n> ").strip()
                    try:
                        path: Path = validate_path(filepath)
                        cli.print_status(f"Path valid: {path}", "success")
                        
                        #analysis pipeline starting, moved to another file
                        pipeline = AnalysisPipeline(cli, config_manager, database_manager)
                        pipeline.run_analysis(str(path))            
                    
                    except Exception as e:
                        cli.print_status(f"File path is not valid: {e}", "error")
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