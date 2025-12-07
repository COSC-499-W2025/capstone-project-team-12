from typing import Dict, List, Any

def display_project_insights(analyzed_repos: List[Dict[str, Any]], top_n: int = 3) -> None:
    """
    Display detailed project insights for the top N projects.
    This function is used by both main.py and database viewing to ensure consistent output.
    
    Args:
        analyzed_repos: List of project insights (already sorted by importance)
        top_n: Number of projects to display detailed insights for (default 3)
    """
    if not analyzed_repos:
        print("\n=== Project Insights ===")
        print("No project insights available.")
        return
    
    # Display only top N projects with detailed insights
    projects_to_display = analyzed_repos[:top_n]
    
    print("\n=== Detailed Project Insights ===")
    print(f"Showing top {len(projects_to_display)} of {len(analyzed_repos)} projects\n")
    
    for project in projects_to_display:
        print(f"\n{'='*60}")
        print(f"Repository: {project.get('repository_name', 'Unknown')}")
        print(f"Importance Rank: #{project.get('importance_rank', 'N/A')}")
        print(f"Importance Score: {project.get('importance_score', 0)}")
        print(f"{'='*60}")
        
        # Contribution Analysis
        contrib = project.get("contribution_analysis", {})
        print("\n> Contribution Insights:")
        print(f"  - Contribution Level: {contrib.get('contribution_level', 'Unknown')}")
        print(f"  - Rank (by commits): {contrib.get('rank_by_commits', 'N/A')}")
        print(f"  - Percentile: {contrib.get('percentile', 'N/A')}%")
        
        # Collaboration Analysis
        collab = project.get("collaboration_insights", {})
        print("\n> Collaboration Insights:")
        print(f"  - Team Size: {collab.get('team_size', 0)}")
        print(f"  - Collaborative Project: {collab.get('is_collaborative', False)}")
        print(f"  - User Contribution Share: {collab.get('user_contribution_share_percentage', 0)}%")
        
        # Testing Analysis
        test = project.get("testing_insights", {})
        print("\n> Testing Insights:")
        print(f"  - Test Files Modified: {test.get('test_files_modified', 0)}")
        print(f"  - Code Files Modified: {test.get('code_files_modified', 0)}")
        print(f"  - Testing % (files): {test.get('testing_percentage_files', 0)}%")
        print(f"  - Test Lines Added: {test.get('test_lines_added', 0)}")
        print(f"  - Code Lines Added: {test.get('code_lines_added', 0)}")
        print(f"  - Testing % (lines): {test.get('testing_percentage_lines', 0)}%")
        print(f"  - Has Tests: {test.get('has_tests', False)}")
        
        # Imports Summary (limit to top 10, sorted by frequency)
        imports = project.get("imports_summary", {})
        print("\n> Key Technologies Used:")
        if imports:
            # Sort by frequency and take top 10
            sorted_imports = sorted(
                imports.items(), 
                key=lambda x: x[1].get('frequency', 0), 
                reverse=True
            )[:10]
            
            for imp, stats in sorted_imports:
                freq = stats.get('frequency', 0)
                duration = stats.get('duration_days', 0)
                print(f"  • {imp}: used {freq} times over {duration} days")
        else:
            print("  No external libraries detected.")


def display_project_summary(ranked_projects: List[Dict[str, Any]], top_n: int = 3) -> None:
    """
    Display a summary table of the most important projects.
    
    Args:
        ranked_projects: List of projects with importance scores (sorted)
        top_n: Number of projects to display (default 3)
    """
    display_count = min(top_n, len(ranked_projects))
    
    if display_count == 0:
        print("\n=== Most Important Projects ===")
        print("No valid projects found to rank.")
        return
    
    print("\n=== Most Important Projects ===")
    for i, proj in enumerate(ranked_projects[:display_count], start=1):
        stats = proj.get("statistics", {})
        dates = proj.get("dates", {})
        
        print(f"{i}. Repo: {proj.get('repository_name', 'Unknown')}")
        print(f"   Score: {round(proj.get('importance', 0), 4)}")
        print(f"   Commits: {len(proj.get('user_commits', []))}")
        print(f"   Lines Added: {stats.get('user_lines_added', 0)}")
        print(f"   Duration: {dates.get('duration_days', 0)} days\n")


def display_project_timeline(timeline: List[Dict[str, Any]]) -> None:
    """
    Display project timeline in chronological order.
    
    Args:
        timeline: List of project timeline data
    """
    if not timeline:
        print("\n=== Project Timeline ===")
        print("No timeline data available.")
        return
    
    print("\n=== Project Timeline ===")
    for project in timeline:
        start = project.get('start_date', 'Unknown')
        end = project.get('end_date', 'Unknown')
        print(f"• {project.get('name', 'Unknown')}: {start} -> {end}")
