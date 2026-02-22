import os
import pickle
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
    Returns True if paths are deemed 'similar enough' or if the user confirms the difference.
    Returns False if they are different and user rejects the confirmation.
    """
    old_name = Path(old_path).name
    new_name = Path(new_path).name
    
    # Check if folder names match
    if old_name != new_name:
        # TODO: Implement robust path comparison (check drive/mount points) 
        # We primarily want to make sure it isn't majorly different like different drive/ different system folder
        # (Desktop/Documents/etc)
        
        print(f"\n[WARNING] The new path '{new_name}' looks different from the old path '{old_name}'.")
        cli = CLI()
        confirm = cli.get_input("Are you sure this is the correct update? (y/n): ").lower()
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
        all_analyses: List[Dict] = database_manager.get_all_results_summary()
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