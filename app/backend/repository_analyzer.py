from pathlib import Path
from pydriller import Repository
from pydriller.domain.commit import Commit
from anytree import Node
from typing import Any, Dict, List, Set
from datetime import datetime

class RepositoryAnalyzer:
    # Analyzes repository data to extract project insights

    def __init__(self, username: str):
        self.username = username

    def analyze_repository(self, repo_node: Node, git_folder_path: Path) -> Dict[str, Any]:
        # Analyze a single repository using PyDriller to extract commit information
        try:
            repo: Repository = Repository(str(git_folder_path))
            
            # Initalize data collectors
            commits_data: List[Dict[str, Any]] = []
            user_dates: List[datetime] = []
            all_authors_stats: Dict[str, Dict[str, int]] = {}

            user_email: str | None = None

            # Initialize statistic accumulators
            total_files_modified: int = 0
            total_lines_added: int = 0
            total_lines_deleted: int = 0
            change_types: Set[str] = set()

            # Initialize all user stats
            all_commits_total: int = 0
            repo_total_lines_added: int = 0
            repo_total_lines_deleted: int = 0
            repo_total_files_modified: int = 0
            
            # TODO: how to use commit info to rank importance of project
            # ^ can look at types, total lines added/deleted, # of files modified?
            
            # Traverse commits here to ensure only a single pass
            for commit in repo.traverse_commits():
                all_commits_total += 1

                commit_email: str = commit.author.email.lower() if commit.author and commit.author.email else ""

                # Will return the Github privacy email with username so extract username (ex: 12345+yourusername@users.noreply.github.com)
                commit_username: str = commit.author.email.split('@')[0].split('+')[-1].lower()

                # Track stats for all users
                if commit_email not in all_authors_stats:
                    all_authors_stats[commit_email] = {
                        'commits': 0,
                        'lines_added': 0,
                        'lines_deleted': 0,
                        'files_modified': 0
                    }
                
                commit_lines_added = 0
                commit_lines_deleted = 0
                commit_files = 0
                for mod in (commit.modified_files or []):
                    commit_files += 1
                    commit_lines_added += mod.added_lines if mod.added_lines is not None else 0
                    commit_lines_deleted += mod.deleted_lines if mod.deleted_lines is not None else 0
                    repo_total_lines_added += mod.added_lines if mod.added_lines is not None else 0
                    repo_total_lines_deleted += mod.deleted_lines if mod.deleted_lines is not None else 0
                    repo_total_files_modified += 1
                    if commit_username == self.username:
                        if mod.change_type:
                            change_types.add(mod.change_type.name)
                
                all_authors_stats[commit_email]['commits'] += 1
                all_authors_stats[commit_email]['lines_added'] += commit_lines_added
                all_authors_stats[commit_email]['lines_deleted'] += commit_lines_deleted
                all_authors_stats[commit_email]['files_modified'] += commit_files

                # Only consider the commits of the user for analysis
                if commit_username == self.username:
                    # Builds the commit info
                    user_email = commit_email  # Capture user's actual email (GitHub privacy or personal)
                    commit_info = self._build_commit_info(commit)
                    commits_data.append(commit_info)

                    # Track project dates
                    if commit.author_date:
                        user_dates.append(commit.author_date)
                    
                    # Update all statistics within the traversal to ensure single pass
                    total_files_modified += commit_files
                    total_lines_added += commit_lines_added
                    total_lines_deleted += commit_lines_deleted
            # Calculate metrics
            user_contribution_rank: Dict[str, Any] = self._calculate_contribution_rank(
                all_authors_stats,
                user_email
            )
            test_ratio: Dict[str, Any] = self._calculate_code_test_ratio(commits_data)
            date_range: Dict[str, Any] = self._calculate_date_range(user_dates)
            is_collaborative: bool = len(all_authors_stats) > 1 if all_authors_stats else len(commits_data) < all_commits_total

            return {
                # Basic Information for the repository
                'repository_name': repo_node.name if repo_node.name else "Unknown",
                'repository_path': str(git_folder_path) if git_folder_path else "Unknown",
                'status': 'success',

                # Project type (individual vs collaborative)
                'commits': commits_data if commits_data else "Unknown",
                'commit_count': len(commits_data) if commits_data else 0,
                'is_collaborative': is_collaborative,

                # Use date_range Dict[str, Any] found from helper method
                **date_range,

                # derived statistics from commits
                'statistics': {
                    'total_files_modified': total_files_modified,
                    'total_lines_added': total_lines_added,
                    'total_lines_deleted': total_lines_deleted,
                    'change_types': list(change_types)
                },
                'repository_context': {
                    'total_contributors': len(all_authors_stats),
                    'total_commits_all_authors': all_commits_total,
                    'repo_total_lines_added': repo_total_lines_added,
                    'repo_total_lines_deleted': repo_total_lines_deleted,
                    'repo_total_files_modified': repo_total_files_modified,
                    
                },
                'user_contribution_rank': user_contribution_rank, # Reflects teamwork insights
                'code_vs_test_ratio': test_ratio
            }
        except Exception as e:
            return {
                'repository_name': repo_node.name,
                'repository_path': str(git_folder_path),
                'status': 'error',
                'error_message': str(e)
            }

    def _build_commit_info(self, commit: Commit) -> Dict[str, Any]:
        # builds the basic info for individual commits
        return {
            'hash': commit.hash if commit.hash else "Unknown",
            'date': commit.author_date.isoformat() if commit.author_date else "Unknown", 
            'message': commit.msg if commit.msg else "",
            'modified_files': [
                {
                    'filename': mod.filename if mod.filename else "Unknown",
                    'change_type': mod.change_type.name if mod.change_type else "UNKNOWN",
                    'added_lines': mod.added_lines if mod.added_lines is not None else 0,
                    'deleted_lines': mod.deleted_lines if mod.deleted_lines is not None else 0
                }
                for mod in (commit.modified_files or [])
            ]
        }

    def _calculate_date_range(self, dates: List[datetime]) -> Dict[str, Any]:
        # Calculate the start and end date for timeline and duration
        if not dates:
            return{
                'start_date': None,
                'end_date': None,
                'duration_days': None,
                'duration_seconds': None
            }
        
        start_date: datetime = min(dates)
        end_date: datetime = max(dates)
        duration: datetime = end_date - start_date

        return{
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'duration_days': duration.days,
            'duration_seconds': int(duration.total_seconds())
        }
    
    def _calculate_contribution_rank(self, all_authors_stats: Dict[str, Dict[str, int]], user_email: str | None) -> Dict[str,Any]:
        # Calculate the user's contribution rank among all authors
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
        if start_date is not None:
            projects.sort(key = lambda x: x['start_date'], reverse = True)

        return projects