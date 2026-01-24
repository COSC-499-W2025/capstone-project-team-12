from pathlib import Path
import tempfile
import shutil
from anytree import Node
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
from pydriller import Repository
from pydriller.domain.commit import Commit

class RepositoryProcessor:
    # Rebuilds .git folders from binary data and extracts raw repository information

    def __init__(self, username: str, binary_data_array: List[bytes], user_email: str = None) -> None:
        self.username: str = username.lower()
        self.binary_data_array: List[bytes] = binary_data_array
        self.user_email: str = user_email.lower() if user_email else None
        self.temp_dirs: List[str] = []

    def process_repositories(self, repo_nodes: List[Node]) -> List[Dict[str, Any]]:
        # Extracts raw repository data from each repository node
        raw_data_list: List[Dict[str, Any]] = []
        
        try:
            for repo_node in repo_nodes:
                # First need to rebuild .git folder for PyDriller to access commits
                git_folder_path: Path = self._extract_git_folder(repo_node)
                
                # Extract the raw repository data using PyDriller
                raw_data: Dict[str, Any] = self._extract_all_repository_data(repo_node, git_folder_path)
                raw_data_list.append(raw_data)

        finally:
            # Clean up temporary directories
            self._cleanup_temp_dirs()

        return raw_data_list

    def _extract_all_repository_data(self, repo_node: Node, git_folder_path: Path) -> Dict[str, Any]:
        # Analyze a single repository using PyDriller to extract commit information
        try:
            repo: Repository = Repository(str(git_folder_path), include_remotes=True)
            
            commits_result: Dict[str, Any] = self._extract_commits_data(repo)
            user_dates: List[datetime] = commits_result['user_dates']
            date_range: Dict[str, Any] = self._calculate_date_range(user_dates)

            return {
                # Basic Information for the repository
                'repository_name': repo_node.name if repo_node.name else "Unknown",
                'repository_path': str(git_folder_path) if git_folder_path else "Unknown",
                'status': 'success',

                # Extracted Data
                'user_commits': commits_result['user_commits_data'],
                'statistics': commits_result['user_statistics'],
                'repository_context': commits_result['repository_context'],
                'dates': date_range,
            }
        except Exception as e:
            return {
                'repository_name': repo_node.name,
                'repository_path': str(git_folder_path),
                'status': 'error',
                'error_message': str(e)
            }

    def _extract_commits_data(self, repo: Repository) -> Dict[str, Any]:
        # Traverse commits and extracts user commits, statistics, and repo context
        
        # Initalize data collectors
        commits_data: List[Dict[str, Any]] = []
        user_dates: List[datetime] = []
        all_authors_stats: Dict[str, Dict[str, int]] = {}
        user_emails: Set[str] = set()

        # Initialize statistic accumulators
        user_files_modified: int = 0
        user_lines_added: int = 0
        user_lines_deleted: int = 0
        change_types: Set[str] = set()

        # Initialize all user stats
        repo_total_commits: int = 0
        repo_total_lines_added: int = 0
        repo_total_lines_deleted: int = 0
        repo_total_files_modified: int = 0
        
        # Single pass through all commits
        for commit in repo.traverse_commits():
            repo_total_commits += 1

            commit_email: str = commit.author.email.lower() if commit.author and commit.author.email else ""

            # Will return the Github privacy email with username so extract username (ex: 12345+yourusername@users.noreply.github.com)
            commit_username: str = commit.author.email.split('@')[0].split('+')[-1].lower()

            # Track stats for all users if first time seeing this author
            if commit_email not in all_authors_stats:
                all_authors_stats[commit_email] = {
                    'commits': 0,
                    'lines_added': 0,
                    'lines_deleted': 0,
                    'files_modified': 0
                }
            
            # Check if this commit belongs to the target user by username or email
            is_user_commit: bool = (commit_username == self.username) or (self.user_email and commit_email == self.user_email)

            # Calculate stats for this commit
            commit_lines_added: int = 0
            commit_lines_deleted: int = 0
            commit_files: int = 0

            for mod in (commit.modified_files or []):
                commit_files += 1
                commit_lines_added += mod.added_lines if mod.added_lines is not None else 0
                commit_lines_deleted += mod.deleted_lines if mod.deleted_lines is not None else 0
                
                # Update repo-wide stats
                repo_total_lines_added += mod.added_lines if mod.added_lines is not None else 0
                repo_total_lines_deleted += mod.deleted_lines if mod.deleted_lines is not None else 0
                repo_total_files_modified += 1
                
                # Track change types for the user
                if is_user_commit and mod.change_type:
                    change_types.add(mod.change_type.name)
            
            all_authors_stats[commit_email]['commits'] += 1
            all_authors_stats[commit_email]['lines_added'] += commit_lines_added
            all_authors_stats[commit_email]['lines_deleted'] += commit_lines_deleted
            all_authors_stats[commit_email]['files_modified'] += commit_files

            # Only consider the commits of the user for detailed data
            if is_user_commit: 

                # Track user emails incase personal and private versions are used
                user_emails.add(commit_email)

                # Builds the commit info
                commit_info = self._build_commit_info(commit)
                commits_data.append(commit_info)

                # Track project dates
                if commit.author_date:
                    user_dates.append(commit.author_date)
                
                # Update all statistics within the traversal to ensure single pass
                user_files_modified += commit_files
                user_lines_added += commit_lines_added
                user_lines_deleted += commit_lines_deleted

        is_collaborative: bool = len(all_authors_stats) > 1 if all_authors_stats else len(commits_data) < repo_total_commits

        # Combine multiple user emails if needed
        if len(user_emails) > 1:
            combined_stats: Dict[str, int] = {
                'commits': 0,
                'lines_added': 0,
                'lines_deleted': 0,
                'files_modified': 0
            }

            for email in user_emails:
                if email in all_authors_stats:
                    for key in combined_stats:
                        combined_stats[key] += all_authors_stats[email][key]
                    del all_authors_stats[email]
            
            combined_key: str = self.user_email if self.user_email else self.username
            all_authors_stats[combined_key] = combined_stats

        return {
            'user_commits_data': commits_data,
            'user_dates': user_dates,
            'user_statistics': {
                'user_files_modified': user_files_modified,
                'user_lines_added': user_lines_added,
                'user_lines_deleted': user_lines_deleted,
                'change_types': change_types
            },
            'repository_context': {
                'total_contributors': len(all_authors_stats),
                'total_commits_all_authors': repo_total_commits,
                'repo_total_lines_added': repo_total_lines_added,
                'repo_total_lines_deleted': repo_total_lines_deleted,
                'repo_total_files_modified': repo_total_files_modified,
                'all_authors_stats': all_authors_stats,
                'is_collaborative': is_collaborative
            }
        }


    def _build_commit_info(self, commit: Commit) -> Dict[str, Any]:
        # builds the basic info for individual commits
        return {
            'hash': commit.hash if commit.hash else "Unknown",
            'date': commit.author_date.isoformat() if commit.author_date else "Unknown",
            'modified_files': [
                {
                    'filename': mod.filename if mod.filename else "Unknown",
                    'change_type': mod.change_type.name if mod.change_type else "UNKNOWN",
                    'added_lines': mod.added_lines if mod.added_lines is not None else 0,
                    'deleted_lines': mod.deleted_lines if mod.deleted_lines is not None else 0,
                    'source_code': mod.source_code if mod.source_code else ""
                }
                for mod in (commit.modified_files or [])
            ]
        }

    def _calculate_date_range(self, user_dates: List[datetime]) -> Dict[str, Any]:
        # Calculate the start and end dates along with duration in days
        if not user_dates:
            return {
                'start_date': None,
                'end_date': None,
                'duration_days': 0,
                'duration_seconds': 0
            }
        
        start_date: datetime = min(user_dates)
        end_date: datetime = max(user_dates)
        duration_days: int = (end_date - start_date).days

        return {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'duration_days': duration_days,
            'duration_seconds': int((end_date - start_date).total_seconds())
        }

    # The methods below are for the building and destruction of temporary .git folders
    def _extract_git_folder(self, repo_node: Node) -> Path:
        # In order for PyDriller to access the commits, this rebuilds the .git folder for each repository temporarily
        temp_dir: str = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        temp_path: Path = Path(temp_dir)

        git_node: Optional[Node] = None
        for child in repo_node.children: # Check all children for git node since repo_node is attached to .git parent
            if child.name == ".git":
                git_node = child
                break
        
        if not git_node: 
            raise ValueError("No .git folder found in the repository node.")
        
        git_path: Path = temp_path / ".git"
        git_path.mkdir(parents=True, exist_ok=True) # Create .git directory in temp location
        self._rebuild_git_tree(git_node, git_path) # recursive method to build all sub folder in .git for PyDriller

        return temp_path

    def _rebuild_git_tree(self, git_node: Node, current_path: Path) -> None:
        # Where we actually reconstruct .git file so PyDriller can access needed files
        for child in git_node.children:
            if hasattr(child, 'type'):
                if child.type == 'file':
                    if not hasattr(child, 'binary_index'):
                        raise ValueError(f"File node '{child.name}' missing binary_index attribute")
                    #Write file from binary data
                    file_path: Path = current_path / child.name
                    binary_index: int = child.binary_index

                    if binary_index < len(self.binary_data_array):
                        binary_data: bytes = self.binary_data_array[binary_index]
                        file_path.write_bytes(binary_data)

                elif child.type == 'directory':
                    dir_path: Path = current_path / child.name
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self._rebuild_git_tree(child, dir_path)

    def _cleanup_temp_dirs(self) -> None:
        for temp_dir in self.temp_dirs:
            try:
                if Path(temp_dir).exists():
                    shutil.rmtree(temp_dir)
            
            except Exception as e:
                print(f"Warning: Could not remove temporary directory {temp_dir}: {e}")
        
        self.temp_dirs = []
