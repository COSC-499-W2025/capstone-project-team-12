from typing import List,Dict,Any, BinaryIO
from database_manager import DatabaseManager
from cli_interface import CLI
from display_helpers import display_project_insights, display_project_summary, display_project_timeline
from pathlib import Path

# This file contains extracted implementations of various main.py's execution paths. Allows for better abstraction easy refactoring moving forward.



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
        
        # Check that tracked data is saved properly
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
        database_manager.save_result_thumbnail(result_id,img_data)
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