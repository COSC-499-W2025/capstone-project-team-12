import os
import pickle
import difflib
from typing import List, Dict, Any, BinaryIO, Optional, Tuple
from pathlib import Path
from database_manager import DatabaseManager
from cli_interface import CLI
from display_helpers import display_project_insights, display_project_summary, display_project_timeline
from input_validation import validate_analysis_path, validate_thumbnail_path, validate_uuid
from resume_editor import ResumeEditor
from portfolio_editor import PortfolioEditor

# This file contains extracted implementations of various main.py's execution paths. 
# Allows for better abstraction and easy refactoring moving forward.

def compare_path(old_path: str, new_path: str) -> bool:
    """
    Compares the old path with the new path to determine if they are similar.
    
    Checks:
    1. Drive/Mount point
    2. Parent directory
    3. Folder name similarity
       - Uses SequenceMatcher to detect versioning (e.g. 'Project_v1' vs 'Project_v2').
       - If similarity > 0.6, we assume it's a version update and allow it.
       - If similarity < 0.6, we warn the user.
    
    Returns True if paths are deemed similar enough or if the user confirms the difference.
    """
    try:
            old = Path(old_path).resolve()
            new = Path(new_path).resolve()
    except Exception as e:
        print(f"Warning: Could not resolve paths for comparison: {e}")
        old = Path(old_path)
        new = Path(new_path)

    #cCalculate and print similarity immediately ---
    matcher = difflib.SequenceMatcher(None, old.name.lower(), new.name.lower())
    similarity = matcher.ratio()
    print(f"Folder name similarity: {int(similarity * 100)}%")

    warnings = []
    
    # 1. Check Drive/Mount Point
    if old.anchor != new.anchor:
        warnings.append(f"- DIFFERENT DRIVE: '{old.anchor}' vs '{new.anchor}'")

    # 2. Check Parent Directory
    if old.parent != new.parent:
        warnings.append(f"- MOVED LOCATION:\n  Old: {old.parent}\n  New: {new.parent}")

    # 3. Check Folder Name with Similarity Ratio
    if old.name != new.name:
        # Check if one is a complete substring of the other (e.g. 'Project' in 'Project_Backup')
        is_substring = (old.name.lower() in new.name.lower()) or (new.name.lower() in old.name.lower())

        if similarity < 0.6 and not is_substring:
            # Low similarity implies a completely different project
            warnings.append(f"- DIFFERENT FOLDER NAME (Similarity: {int(similarity*100)}%): '{old.name}' vs '{new.name}'")
        else:
            # High similarity implies a version update/rename. 
            print(f"\n[Info] Detected folder rename (Safe to proceed): '{old.name}' -> '{new.name}'")

    # If any warnings were collected, print them
    if warnings:
        print("\n[WARNING] The new path seems significantly different from the old path:")
        for w in warnings:
            print(w)
    
    # always prompt the user for confirmation
    cli = CLI()
    confirm = cli.get_input("\nAre you sure this is the correct update? (y/n): ").lower()
    if confirm != 'y':
        return False
            
    return True

def perform_update_merge(
    analysis_id: str, 
    new_tree, 
    new_binary_list, 
    db_manager, 
    tree_manager, 
    importer, 
    exporter
):
    """
    Handles the logic for retrieving old data, merging it with new data,
    and returning the merged results.
    """
    print("Fetching previous analysis state...")
    
    try:
        old_binary_blob, old_tree_dict = db_manager.get_fileset_data(analysis_id)
        if not old_binary_blob or not old_tree_dict:
            raise LookupError
    except Exception as e:
        raise e
    
    # Deserialize
    old_binary_list = pickle.loads(old_binary_blob)
    old_tree = importer.import_(old_tree_dict)

    print("Comparing and merging updates...")
    merged_tree, merged_binary_list = tree_manager.merge_trees(
        old_tree, old_binary_list, new_tree, new_binary_list
    )
    
    return merged_tree, merged_binary_list

def view_all_analyses(database_manager:DatabaseManager) -> None:
    try:
        all_analyses: List[Dict] = database_manager.get_all_analyses_summary()
    except Exception as e:
        raise LookupError(f"Main Utils Error: {e}")
    for res in all_analyses:
        print(f"Analysis ID: {res['analysis_id']}")
        print("\nMetadata insights:")
        print(f"{'Extension':<10} | {'Count':<8} | {'Size':<15} | {'Percentage':<8} | {'Category'}")
        print("-" * 70)
        
        meta_insights = res['metadata_insights']
        for ext, stats in meta_insights['extension_stats'].items():
            print(f"{ext:<10} | {stats['count']:<8} | {stats['total_size']:<15} | {stats['percentage']:<8}% | {stats['category']}")
        print(f"\nPrimary skills: {', '.join(meta_insights['primary_skills'])}\n")

def view_analysis_by_id(database_manager:DatabaseManager, cli:CLI, view_id:str,debug_data:bool = False) -> None:        
    analysis: Dict[str, Any] = database_manager.get_analysis_data(view_id)
    
    if analysis:
        
        cli.print_header(f"Analysis ID: {view_id}")
        # Check that results are saved properly
        # print(f"Topic vectors: {result['topic_vector']}")
        
        print("Resume points:")
        print(f"{analysis['resume_points']}")

        # Display the project insights
        project_insights = analysis.get('project_insights', {})
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
        


        print(f"\nPackage insights: {analysis['package_insights']}")
        print("\nMetadata insights:")
        print(f"{'Extension':<10} | {'Count':<8} | {'Size':<15} | {'Percentage':<8} | {'Category'}")
        print("-" * 70)
        for ext, stats in analysis['metadata_insights']['extension_stats'].items():
            print(f"{ext:<10} | {stats['count']:<8} | {stats['total_size']:<15} | {stats['percentage']:<8}% | {stats['category']}")
        
        try:
            thumbnail_result = database_manager.get_analysis_thumbnail(view_id)
            if thumbnail_result:
                cli.print_status(f"A Thumbnail is associated with this analysis!","info")
            else:
                cli.print_status(f"There is NO thumbnail associated with this analysis!","info")
        except Exception as e:
            cli.print_status(f"DB_Manager_Error{e}","error")
        #To Check that tracked data is saved properly
        if(debug_data):
            print(f"\nTracked data summary:")
            print(f"BoW cache: {analysis['tracked_data']['bow_cache']}")
            print(f"Project data: {analysis['tracked_data']['project_data']}")
            print(f"Package data: {analysis['tracked_data']['package_data']}")
            print(f"Metadata stats: {analysis['tracked_data']['metadata_stats']}")
        
    else:
        raise ValueError(f"No Analysis found with ID: {view_id}")

def delete_analysis_by_id(database_manager:DatabaseManager,cli:CLI,delete_id:str)->None:
    try:
        database_manager.delete_analysis(delete_id)
        cli.print_status(f"Analysis with ID {delete_id} deleted from database.", "success")
    except Exception as e:
        raise e

def insert_thumbnail(database_manager:DatabaseManager,cli:CLI,analysis_id:str,img_data:BinaryIO):
    if analysis_id is None:
        raise TypeError("Analysis id is None")
    try:
        database_manager.save_analysis_thumbnail(analysis_id,img_data)
    except Exception as e:
        raise e

def read_image(img_path:Path)->BinaryIO:
    try:
        with open(img_path, "rb") as file:
            img_data = file.read()
            return img_data
    except Exception as e:
        raise e

def delete_all_analyses(database_manager:DatabaseManager):
    try:
        database_manager.wipe_all_data()
    except Exception as e:
        raise e

# Helper method to display all analyses to let the user choose one
def _pick_analysis(cli:CLI, database_manager:DatabaseManager) -> Optional[str]:
    try:
        all_analyses = database_manager.get_all_analyses_summary()
    except Exception as e:
        cli.print_status(f"Failed to retrieve analyses: {e}", "error")
        return None
    if not all_analyses:
        cli.print_status("No analyses found in the database.", "info")
        return None
    
    print("\nAvailable analyses:")
    print(f"  {'#':<4} {'Analysis ID':<38} {'File Path'}")
    print("  " + "-" * 80)
    for idx, row in enumerate(all_analyses, 1):
        print(f"  {idx:<4} {row['analysis_id']:<38} {row.get('file_path', 'N/A')}")

    choice = cli.get_input("Enter the number of the analysis you want to select (or Enter to go back):\n ").strip()
    if not choice:
        return None

    if choice.isdigit() and 1 <= int(choice) <= len(all_analyses):
        return all_analyses[int(choice) - 1]['analysis_id']
    
    cli.print_status("Invalid selection.", "error")
    return None

# Helpers to fetch and display resume/portfolio data to let user pick
# Seperated because they rely on different calls to db manager
def _pick_resume(cli:CLI, database_manager:DatabaseManager, analysis_id:str) -> Optional[Dict]:
    try:
        resumes = database_manager.get_resumes_by_analysis_id(analysis_id)
    except LookupError:
        cli.print_status("No resumes found for this analysis.", "info")
        return None
    
    if len(resumes) == 1:
        return resumes[0]['resume_id'],resumes[0]['resume_data']

    print("\nAvailable resumes:")
    for idx, res in enumerate(resumes, 1):
        # Use the resume title if available, otherwise fallback to a generic name with the resume ID
        title = res.get('resume_title') or f"Resume {res['resume_id']}"
        print(f"{idx}. {title}")
    
    choice = cli.get_input("Enter the number of the resume you want to select (or Enter to go back):\n ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(resumes):
        return resumes[int(choice) - 1]['resume_id'],resumes[int(choice) - 1]['resume_data']

    if not choice:
        return None
    cli.print_status("Invalid selection.", "error")
    return None

def _pick_portfolio(cli:CLI, database_manager:DatabaseManager, analysis_id:str) -> Optional[Dict]:
    try:
        portfolios = database_manager.get_portfolios_by_analysis_id(analysis_id)
    except LookupError:
        cli.print_status("No portfolios found for this analysis.", "info")
        return None
    
    if len(portfolios) == 1:
        return portfolios[0]['portfolio_id'],portfolios[0]['portfolio_data']

    print("\nAvailable portfolios:")
    for idx, res in enumerate(portfolios, 1):
        # Use the portfolio title if available, otherwise fallback to a generic name with the portfolio ID
        title = res.get('portfolio_title') or f"Portfolio {res['portfolio_id']}"
        print(f"{idx}. {title}")
    choice = cli.get_input("Enter the number of the portfolio you want to select (or Enter to go back):\n ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(portfolios):
        return portfolios[int(choice) - 1]['portfolio_id'],portfolios[int(choice) - 1]['portfolio_data']
    if not choice:
        return None
    cli.print_status("Invalid selection.", "error")
    return None

# Below methods are for Resume and Portfolio 
def generate_resume(analysis_id: str, database_manager, resume_builder, cli) -> Optional[Tuple[int, Dict]]:
    try:
        resume = resume_builder.create_resume_from_analysis_id(database_manager, cli, analysis_id)
        resume_id = None
        if not resume:
            return None
        resume_id = database_manager.save_resume(analysis_id, resume)
        cli.print_status("Resume generated successfully.","success")
        return resume_id, resume
    except Exception as e:
        cli.print_status(f"Resume generation failed: {e}", "warning")
        return None
    
def generate_portfolio(analysis_id: str, database_manager, portfolio_builder, cli) -> Optional[Dict]:
    try:
        portfolio = portfolio_builder.create_portfolio_from_result_id(database_manager, cli, analysis_id)
        portfolio_id = None
        if not portfolio:
            return None
        portfolio_id = database_manager.save_portfolio(analysis_id, portfolio)
        cli.print_status("Portfolio generated successfully.","success")
        return portfolio_id, portfolio
    except Exception as e:
        cli.print_status(f"Portfolio generation failed: {e}", "warning")
        return None

# Sub menus for managing resumes and portfolios.
def manage_resumes(cli, database_manager, resume_builder) -> None:
    cli.print_header("Manage Resumes")

    # Outer loop to select analysis, inner loop to manage resumes for that analysis. Allows user to easily switch between analyses without going back to main menu each time.
    while True:
        analysis_id = _pick_analysis(cli, database_manager)
        if not analysis_id:
            # We assume no input means the user watns to return to main menu
            return
   
        # Sub menu for selecting the resume to proceed with
        result = _pick_resume(cli, database_manager, analysis_id)
        if not result:
            generate = cli.get_input("Would you like to generate a resume? (Y/n): ").strip()
            if generate.lower() == "n":
                break
            elif not generate or generate.lower() == "y" or generate.lower() == "yes":
                result = generate_resume(analysis_id, database_manager, resume_builder, cli)
                if not result:
                    break

        if not result:
            break

        resume_id, resume = result

        while True:
            action = cli.get_input("Select an action:\n- 'V' View Resume\n- 'E' Edit Resume\n- 'D' Delete Resume\n- 'G' Generate New Resume\n- 'B' Back to Analysis Selection\n").strip()
            if action.lower() == "v":
                resume_builder.display_resume(resume, cli)
            elif action.lower() == "e":
                resume = ResumeEditor(cli).edit_resume(resume)

                # Update the resume in the database after editing
                try:
                    database_manager.update_resume(resume_id, resume)
                    cli.print_status("Resume updated successfully!", "success")
                except Exception as e:
                    cli.print_status(f"Failed to update resume: {e}", "error")
            elif action.lower() == "d":
                confirm = cli.get_input("Are you sure you want to delete this resume? (y/N): ").strip()
                if confirm.lower() in ["y", "yes"]:
                    try:
                        database_manager.delete_resume(resume_id)
                        cli.print_status("Resume deleted successfully.", "success")
                    except Exception as e:
                        cli.print_status(f"Failed to delete resume: {e}", "error")
                    break
                else:
                    cli.print_status("Delete action cancelled.", "info")
            elif action.lower() == "g":
                result = generate_resume(analysis_id, database_manager, resume_builder, cli)
                if not result:
                    cli.print_status("Resume regeneration failed. Original resume is still intact.", "warning")
                else:
                    resume_id, resume = result
                    cli.print_status("New resume generated, you are now viewing the new resume.", "info")
                    
            elif action.lower() == "b":
                break
            else:
                cli.print_status("Invalid action. Please try again.", "warning")
def manage_portfolios(cli: CLI, database_manager: DatabaseManager, portfolio_builder) -> None:
    cli.print_header("Manage Portfolios")
    while True:
        analysis_id = _pick_analysis(cli, database_manager)
        if not analysis_id:
            # We assume no input means the user wants to return to main menu
            return

        # Sub menu for selecting the portfolio to proceed with
        result = _pick_portfolio(cli, database_manager, analysis_id)
        if not result:
            generate = cli.get_input("Would you like to generate a portfolio? (Y/n): ").strip()
            if generate.lower() == "n":
                break
            elif not generate or generate.lower() in ["y", "yes"]:
                result = generate_portfolio(analysis_id, database_manager, portfolio_builder, cli)
                if not result:
                    break
        if not result:
            break

        portfolio_id, portfolio = result

        while True:
            action = cli.get_input("Select an action:\n- 'V' View Portfolio\n- 'E' Edit Portfolio\n- 'D' Delete Portfolio\n- 'G' Generate New Portfolio\n- 'B' Back to Analysis Selection\n").strip()
            if action.lower() == "v":
                portfolio_builder.display_portfolio(portfolio, cli)
            elif action.lower() == "e":
                portfolio = PortfolioEditor(cli).edit_portfolio(portfolio)

                # Update the portfolio in the database after editing
                try:
                    database_manager.update_portfolio(portfolio_id, portfolio)
                    cli.print_status("Portfolio updated successfully!", "success")
                except Exception as e:
                    cli.print_status(f"Failed to update portfolio: {e}", "error")
            elif action.lower() == "d":
                confirm = cli.get_input("Are you sure you want to delete this portfolio? (y/N): ").strip()
                if confirm.lower() in ["y", "yes"]:
                    try:
                        database_manager.delete_portfolio(portfolio_id)
                        cli.print_status("Portfolio deleted successfully.", "success")
                    except Exception as e:
                        cli.print_status(f"Failed to delete portfolio: {e}", "error")
                    break
                else:
                    cli.print_status("Delete action cancelled.", "info")
            elif action.lower() == "g":
                result = generate_portfolio(analysis_id, database_manager, portfolio_builder, cli)
                if not result:
                    cli.print_status("Portfolio regeneration failed. Original portfolio is still intact.", "warning")
                else:
                    portfolio_id, portfolio = result
                    cli.print_status("New portfolio generated, you are now viewing the new portfolio.", "info")
            elif action.lower() == "b":
                break
            else:
                cli.print_status("Invalid action.", "warning")