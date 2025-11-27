from typing import Any, Dict, List, Set
from datetime import datetime

class RepositoryAnalyzer:
    # Analyzes repository data to extract project insights

    def __init__(self, username: str):
        self.username = username

    def generate_project_insights(self, project_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Generate insights for all projects

        # Filter out any projects that failed to process
        valid_projects: List[Dict[str, Any]] = [
            project for project in project_data if project.get('status') == 'success'
        ]

        if not valid_projects:
            return {
                'projects': [],
                'summary': {}
            }

        # Compute importance rankings (requires all valid projects for normalization)
        ranked_projects: List[Dict[str, Any]] = self.rank_importance_of_projects(valid_projects)

        # Generate insights for each project
        projects_insights: List[Dict[str, Any]] = []
        for idx, project in enumerate(ranked_projects):
            project_insight: Dict[str, Any] = {
                'repository_name': project.get('repository_name', 'Unknown'),
                'importance_rank': idx + 1,
                'importance_score': round(project.get('importance', 0), 4),
                'contribution_analysis': self._calculate_contribution_insights(project),
                'collaboration_insights': self._generate_collaboration_insights(project),
                'testing_insights': self._generate_testing_insights(project),
                'project_scope': self._generate_project_scope_insights(project)
            }
            projects_insights.append(project_insight)

        portfolio_summary: Dict[str, Any] = self._generate_portfolio_summary(projects_insights)

        return {
            'projects': projects_insights,
            'summary': portfolio_summary
        }
    
    def _calculate_contribution_insights(self, project: Dict[str, Any]) -> Dict[str,Any]:
        # Determines user's contribution rank and level within the project
        context: Dict[str, Any] = project.get('repository_context', {})
        all_authors_stats: Dict[str, Dict[str, int]] = context.get('all_authors_stats', {})

        # TODO: Rework this and processor to anonymize emails to ensure no PII is stored
        # For now, we find the user's email from all_authors_stats
        user_email: str | None = None
        for email in all_authors_stats.keys(): 
            if self.username.lower() in email.lower():
                user_email = email
                break

        if not user_email or user_email not in all_authors_stats:
            return {
                'contribution_level': 'Unknown',
                'rank_by_commits': None,
                'percentile': None,
            }

        # Sort authors by number of commits
        sorted_by_commits = sorted(
            all_authors_stats.items(),
            key=lambda item: item[1]['commits'],
            reverse=True
        )

        # Pull out just the emails in sorted order
        sorted_emails = [email for email, stats in sorted_by_commits]
        rank: int = sorted_emails.index(user_email) + 1  if user_email in sorted_emails else None

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

    def _generate_collaboration_insights(self, project: Dict[str, Any]) -> Dict[str, Any]:
        # Analyze collaboration patterns and team dynamics
        context: Dict[str, Any] = project.get('repository_context', {})
        total_contributors: int = context.get('total_contributors', 1)
        is_collaborative: bool = context.get('is_collaborative', False)

        # Calculate the user's share of total work
        user_commits: int = len(context.get('user_commits', []))
        total_commits: int = context.get('total_commits', user_commits)
        contribution_share: float = (user_commits / total_commits * 100) if total_commits > 0 else 0.0

        return {
            'is_collaborative': is_collaborative,
            'team_size': total_contributors,
            'user_contribution_share_percentage': round(contribution_share, 2)
        }
    
    def _generate_testing_insights(self, project: Dict[str, Any]) -> Dict[str, Any]:
        # Calculate the ratio of code to test files modified
        commits_data: List[Dict[str, Any]] = project.get('user_commits', [])
        
        test_files: int = 0
        code_files: int = 0
        test_lines_added: int = 0
        code_lines_added: int = 0

        # Potential test patterns, can be expanded later
        test_patterns = ['test_', '_test', 'tests/', '/tests/', '/test/','test/','spec_', '_spec', 'specs/', '/specs/', 'spec.', '.spec']

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

        # extract all values into lists
        commits_vals = [p.get('commit_count', 0) for p in projects]
        lines_vals = [p.get('statistics', {}).get('total_lines_added', 0) for p in projects]
        duration_vals = [p.get('duration_days', 0) for p in projects]

        # find min and max for each measure
        min_commits = min(commits_vals)
        max_commits = max(commits_vals)
        min_lines = min (lines_vals)
        max_lines = max(lines_vals)
        min_duration = min(duration_vals)
        max_duration = max(duration_vals)

        for project in projects:
            commits = project.get('commit_count', 0)
            lines = project.get('statistics', {}).get('total_lines_added', 0)
            duration = project.get('duration_days', 0)

            norm_commits = self.normalize_for_rankings(commits, max_commits, min_commits)
            norm_lines_added = self.normalize_for_rankings(lines, max_lines, min_lines)
            norm_duration = self.normalize_for_rankings(duration, max_duration, min_duration)

            project['importance'] = norm_commits + norm_lines_added + norm_duration

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
        
        projects = self.create_chronological_project_list(all_repo_data)
        ranked_projects = self.rank_importance_of_projects(projects)

        return ranked_projects[:3] if ranked_projects else []

    def _generate_project_scope_insights(self, project: Dict[str, Any]) -> Dict[str, Any]:
        # Determine the maturity and activity status of the project
        dates: Dict[str, Any] = project.get('dates', {})
        duration_days: int = dates.get('duration_days', 0)

        # Determine maturity level based on duration
        if duration_days < 30:
            maturity_level = 'Short-term'
        elif duration_days < 90:
            maturity_level = 'Medium-term'
        else:
            maturity_level = 'Long-term'
        
        end_date_str: str | None = dates.get('end_date')
        is_active: bool = False
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str)
                days_since_end = (datetime.now() - end_date).days
                is_active = days_since_end <= 30  # Active if ended within the last 30 days
            except (ValueError, TypeError):
                is_active = False
        
        return {
            'maturity_level': maturity_level,
            'is_active': is_active
        }

    def _generate_portfolio_summary(self, projects_insights: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Generate a summary for the entire portfolio of projects
        if not projects_insights:
            return {}
        
        total_projects: int = len(projects_insights)
        collaborative_projects: int = sum(1 for p in projects_insights if p.get('collaboration_insights', {}).get('is_collaborative', False))
        average_importance: float = sum(p.get('importance_score', 0) for p in projects_insights) / total_projects if total_projects > 0 else 0.0
        active_projects: int = sum(1 for p in projects_insights if p.get('project_scope', {}).get('is_active', False))

        durations: List[int] = [
            p.get('project_scope', {}).get('duration_days', 0) for p in projects_insights
        ]
        average_duration: float = sum(durations) / total_projects if total_projects > 0 else 0.0

        return {
            'total_projects': total_projects,
            'collaborative_projects': collaborative_projects,
            'average_importance_score': round(average_importance, 4),
            'active_projects': active_projects,
        }


    # This method may move in later implementation but is included to ensure overall functionality
    def create_chronological_project_list(self, all_repo_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # TODO: determine what parts of a project should be displayed on the timeline
        # ^ This will determine what needs to be returned here

        projects: List[Dict[str, Any]] = []

        for repo in all_repo_data:
            if repo.get('status') != 'success':
                continue
            
            start_date = repo.get('start_date')

            if not start_date or not isinstance(start_date, str):
                continue
            
            project_info = {
                'name': repo.get('repository_name', 'Unknown'),
                'start_date': start_date,
                'end_date': repo.get('end_date'),
                'duration_days': repo.get('duration_days', 0),
                'commit_count': repo.get('commit_count', 0),
                'is_collaborative': repo.get('is_collaborative', False),
                'total_lines_added': repo.get('statistics', {}).get('total_lines_added', 0),
                'total_lines_deleted': repo.get('statistics', {}).get('total_lines_deleted', 0),
                'files_modified': repo.get('statistics', {}).get('total_files_modified', 0)
            }

            projects.append(project_info)

        # Sort all projects by the start date
        if projects:
            projects.sort(key = lambda x: x['start_date'], reverse = True)

        return projects