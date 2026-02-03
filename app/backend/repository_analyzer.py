from typing import Any, Dict, List, Set
from datetime import datetime
import re

class RepositoryAnalyzer:
    # Analyzes repository data to extract project insights

    def __init__(self, username: str, user_email: str = None):
        self.username = username
        self.user_email = user_email if user_email else None

    def generate_project_insights(self, project_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Generate insights from extracted project data

        # Filter out any projects that failed to process
        valid_projects: List[Dict[str, Any]] = [
            project for project in project_data if project.get('status') == 'success'
        ]

        if not valid_projects:
            return []

        # Compute importance scores & rankings (requires all valid projects for normalization)
        ranked_projects: List[Dict[str, Any]] = self.rank_importance_of_projects(valid_projects)

        # Generate insights for each project
        projects_insights: List[Dict[str, Any]] = []
        for idx, project in enumerate(ranked_projects):
            project_insight: Dict[str, Any] = {
                'repository_name': project.get('repository_name', 'Unknown'),
                'importance_rank': idx + 1,
                'importance_score': round(project.get('importance', 0), 4),
                'user_commits': project.get('user_commits', []),  # Keep the list
                'statistics': project.get('statistics', {}),       # Keep stats
                'dates': project.get('dates', {}),                 # Keep dates
                'contribution_analysis': self._calculate_contribution_insights(project),
                'collaboration_insights': self._generate_collaboration_insights(project),
                'testing_insights': self._generate_testing_insights(project),
                'user_role': self.infer_user_role(project)
            }
            projects_insights.append(project_insight)

        return projects_insights


    def infer_user_role(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Infers a user's role in the project based on contribution metrics
        across all analyzed projects.
        """
        stats = project.get("statistics", {})
        lines_added = stats.get("user_lines_added", 0)
        lines_deleted = stats.get("user_lines_deleted", 0)
        files_modified = stats.get("user_files_modified", 0)

        total_line_activity = lines_added + lines_deleted + files_modified

        # avoid division by zero
        if total_line_activity == 0:
            return {
                "role": "No Activity Detected",
                "blurb": (
                    "No meaningful contribution activity was detected for this project."
                )
            }

        
        # find proportions of each activity type
        add_ratio = lines_added / total_line_activity
        delete_ratio = lines_deleted / total_line_activity
        modify_ratio = files_modified / total_line_activity

        # generate blurb based on role
        if add_ratio > 0.5:
            role = "Feature Developer"
            blurb = (
                "The user contributed a substantial amount of new code, indicating a strong role "
                "in implementing features and expanding the project’s functionality."
            )

        elif delete_ratio > 0.4:
            role = "Code Refiner"
            blurb = (
                "The user’s contributions focused heavily on refining the existing codebase. "
                "Rather than introducing large amounts of new code, they prioritized removing "
                "unnecessary or outdated lines, suggesting an emphasis on cleanup and optimization."
            )

        elif modify_ratio > 0.4:
            role = "Maintainer"
            blurb = (
                "Most of the user’s contributions involved modifying existing files, suggesting a "
                "maintenance-focused role aimed at improving correctness, readability, or performance."
            )

        else:
            role = "General Contributor"
            blurb = (
                "The user showed a balanced contribution pattern, engaging in a mix of additions, "
                "modifications, and deletions across the codebase."
            )

        return {
            "role": role,
            "blurb": blurb
        }


    def _generate_collaboration_insights(self, project: Dict[str, Any]) -> Dict[str, Any]:
        # Analyze collaboration patterns and team dynamics
        context: Dict[str, Any] = project.get('repository_context', {})
        total_contributors: int = context.get('total_contributors', 1)
        is_collaborative: bool = context.get('is_collaborative', False)

        # Calculate the user's share of total work
        user_commits: int = len(project.get('user_commits', []))
        total_commits: int = context.get('total_commits_all_authors', user_commits)
        contribution_share: float = (user_commits / total_commits * 100) if total_commits > 0 else 0.0

        return {
            'is_collaborative': is_collaborative,
            'team_size': total_contributors,
            'user_contribution_share_percentage': round(contribution_share, 2)
        }
    
    def _calculate_contribution_insights(self, project: Dict[str, Any]) -> Dict[str,Any]:
        # Determines user's contribution rank and level within the project
        context: Dict[str, Any] = project.get('repository_context', {})
        all_authors_stats: Dict[str, Dict[str, int]] = context.get('all_authors_stats', {})

        user_stats = all_authors_stats.get('target_user')
        
        if not user_stats:
            return {
                'contribution_level': 'Unknown',
                'rank_by_commits': None,
                'percentile': None,
            }

        user_commits: int = user_stats['commits']

        # Count how many authors have more commits than the user
        rank: int = 1
        for key, stats in all_authors_stats.items():
            if key != 'target_user' and stats['commits'] > user_commits:
                rank += 1

        total_authors: int = len(all_authors_stats)
        percentile: float = ((total_authors - rank) / total_authors) * 100 if rank else None

        # Determine contribution level based on rank
        if total_authors == 1:
            contribution_level = 'Sole Contributor'
        elif rank == 1:
            contribution_level = 'Top Contributor'
        elif percentile and percentile >= 75:
            contribution_level = 'Major Contributor'
        elif percentile and percentile >= 50:
            contribution_level = 'Significant Contributor'
        else:
            contribution_level = 'Contributor'
        
        return {
            'contribution_level': contribution_level,
            'rank_by_commits': rank,
            'percentile': round(percentile, 2) if percentile is not None else None,
        }
    
    def _generate_testing_insights(self, project: Dict[str, Any]) -> Dict[str, Any]:
        # Calculate the ratio of code to test files modified
        commits_data: List[Dict[str, Any]] = project.get('user_commits', [])
        
        test_files: int = 0
        code_files: int = 0
        test_lines_added: int = 0
        code_lines_added: int = 0

        # Potential test patterns, can be expanded later
        test_patterns = ['test_', '_test', 'tests/', '/tests/', '/test/','test/','test','tests','spec_', '_spec', 'specs/', '/specs/', 'spec.', '.spec']

        for commit in commits_data:
            for mod in commit.get('modified_files', []):
                filename: str = mod.get('filename', '').lower()
                added_lines: int = mod.get('added_lines', 0)

                if any(pattern in filename for pattern in test_patterns):
                    test_files += 1
                    test_lines_added += added_lines
                else:
                    code_files += 1
                    code_lines_added += added_lines

        total_files: int = test_files + code_files
        total_lines: int = test_lines_added + code_lines_added

        testing_percentage: float = (test_files / total_files * 100) if total_files > 0 else 0.0
        testing_lines_percentage: float = (test_lines_added / total_lines * 100) if total_lines > 0 else 0.0

        return {
            'test_files_modified': test_files,
            'code_files_modified': code_files,
            'testing_percentage_files': round(testing_percentage, 2),
            'test_lines_added': test_lines_added,
            'code_lines_added': code_lines_added,
            'testing_percentage_lines': round(testing_lines_percentage, 2),
            'has_tests': test_files > 0
        }
    

    def rank_importance_of_projects(self, projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """ Ranks project importance based on the number of commits from a user, the number of lines added by the user, and the
        duration of the project """

        # Extract all values into lists
        commits_vals = [len(p.get('user_commits', [])) for p in projects]
        lines_vals = [p.get('statistics', {}).get('user_lines_added', 0) for p in projects]
        duration_vals = [p.get('dates', {}).get('duration_days', 0) for p in projects]

        # Find min and max for each measure
        min_commits = min(commits_vals) if commits_vals else 0
        max_commits = max(commits_vals) if commits_vals else 0
        min_lines = min(lines_vals) if lines_vals else 0
        max_lines = max(lines_vals) if lines_vals else 0
        min_duration = min(duration_vals) if duration_vals else 0
        max_duration = max(duration_vals) if duration_vals else 0

        for project in projects:
            commits = len(project.get('user_commits', []))
            lines = project.get('statistics', {}).get('user_lines_added', 0)
            duration = project.get('dates', {}).get('duration_days', 0)

            norm_commits = self.normalize_for_rankings(commits, max_commits, min_commits)
            norm_lines_added = self.normalize_for_rankings(lines, max_lines, min_lines)
            norm_duration = self.normalize_for_rankings(duration, max_duration, min_duration)

            project['importance'] = ( norm_commits + norm_lines_added + norm_duration ) / 3

        return sorted(projects, key=lambda x: x['importance'], reverse=True)
    

    @staticmethod
    def normalize_for_rankings (x, x_max, x_min):
        """ normalize project contribution measures from 0-1 so large scale projects don't override smaller ones """
        if x_max - x_min == 0:
            return 0
        return (x - x_min) / (x_max - x_min)
    
    def get_most_important_projects(self, all_repo_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """ Returns info about the top 3 project from a list of projects based on the 'importance' key """
        if not all_repo_data:
            return []
        
        projects = [proj for proj in all_repo_data if proj.get('status') == 'success']
        ranked_projects = self.rank_importance_of_projects(projects)

        return ranked_projects[:3] if ranked_projects else []


    # This method may move in later implementation but is included to ensure overall functionality
    def create_chronological_project_list(self, all_repo_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # TODO: determine what parts of a project should be displayed on the timeline
        # ^ This will determine what needs to be returned here

        # all_repo_data is the raw data returned from the repository processor
        projects: List[Dict[str, Any]] = []

        for repo in all_repo_data:
            if repo.get('status') == 'failed': 
                continue

            dates = repo.get('dates',{})
            start_date = dates.get('start_date')

            if not start_date or not isinstance(start_date, str):
                continue
            
            project_info = {
                'name': repo.get('repository_name', 'Unknown'),
                'start_date': start_date,
                'end_date': dates.get('end_date'),
                'duration_days': dates.get('duration_days', 0)
            }

            projects.append(project_info)

        # Sort all projects by the start date (most recent first)
        if projects:
            projects.sort(key = lambda x: x['start_date'], reverse = True)

        return projects

    