import os
import pickle
import difflib
from typing import List, Dict, Any, BinaryIO
from pathlib import Path
from database_manager import DatabaseManager
from cli_interface import CLI
from display_helpers import display_project_insights, display_project_summary, display_project_timeline
from input_validation import validate_analysis_path, validate_thumbnail_path, validate_uuid

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
    old_binary_blob, old_tree_dict = db_manager.get_fileset_data(analysis_id)
    
    if not old_binary_blob or not old_tree_dict:
        return None, None

    # Deserialize
    old_binary_list = pickle.loads(old_binary_blob)
    old_tree = importer.import_(old_tree_dict)

    print("Comparing and merging updates...")
    merged_tree, merged_binary_list = tree_manager.merge_trees(
        old_tree, old_binary_list, new_tree, new_binary_list
    )
    
    return merged_tree, merged_binary_list

def view_all_results(database_manager:DatabaseManager) -> None:
    all_results: List[Dict] = database_manager.get_all_results_summary()
    for res in all_results:
        print(f"Analysis ID: {res['analysis_id']}")
        print("\nMetadata insights:")
        print(f"{'Extension':<10} | {'Count':<8} | {'Size':<15} | {'Percentage':<8} | {'Category'}")
        print("-" * 70)
        
        meta_insights = res['metadata_insights']
        for ext, stats in meta_insights['extension_stats'].items():
            print(f"{ext:<10} | {stats['count']:<8} | {stats['total_size']:<15} | {stats['percentage']:<8}% | {stats['category']}")
        print(f"\nPrimary skills: {', '.join(meta_insights['primary_skills'])}\n")

def view_result_by_id(database_manager:DatabaseManager, cli:CLI, view_id:str,debug_data:bool = False) -> None:        
    result: Dict[str, Any] = database_manager.get_analysis_data(view_id)
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
        
        try:
            result = database_manager.get_analysis_thumbnail(view_id)
            if result:
                cli.print_status(f"A Thumbnail is associated with this analysis!","info")
            else:
                cli.print_status(f"There is NO thumbnail associated with this analysis!","info")
        except Exception as e:
            cli.print_status(f"DB_Manager_Error{e}","error")
        #To Check that tracked data is saved properly
        if(debug_data):
            print(f"\nTracked data summary:")
            print(f"BoW cache: {result['tracked_data']['bow_cache']}")
            print(f"Project data: {result['tracked_data']['project_data']}")
            print(f"Package data: {result['tracked_data']['package_data']}")
            print(f"Metadata stats: {result['tracked_data']['metadata_stats']}")
        
    else:
        raise ValueError(f"No result found with ID: {view_id}")

def delete_result_by_id(database_manager:DatabaseManager,cli:CLI,delete_id:str)->None:
    result = database_manager.delete_analysis(delete_id)
    if result:
        cli.print_status(f"Result with ID {delete_id} deleted from database.", "success")
    else:
        raise RuntimeError("Failed to delete entry")

def insert_thumbnail(database_manager:DatabaseManager,cli:CLI,result_id:str,img_data:BinaryIO):
    if result_id is None:
        raise TypeError("Result id is None")
    try:
        database_manager.save_analysis_thumbnail(result_id,img_data)
    except Exception as e:
        raise e

def read_image(img_path:Path)->BinaryIO:
    try:
        with open(img_path, "rb") as file:
            img_data = file.read()
            return img_data
    except Exception as e:
        raise e

def delete_all_results(database_manager:DatabaseManager):
    database_manager.wipe_all_data()