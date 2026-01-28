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
        resolver: AuthorIdentityResolver = AuthorIdentityResolver()
        # Initalize data collectors
        commits_data: List[Dict[str, Any]] = []
        user_dates: List[datetime] = []
        canonical_stats: Dict[str, Dict[str, int]] = {}
        target_user_canonical_id: Optional[str] = None

        # User statistics
        user_files_modified: int = 0
        user_lines_added: int = 0
        user_lines_deleted: int = 0
        change_types: Set[str] = set()

        # Repository-wide statistics
        repo_total_commits: int = 0
        repo_total_lines_added: int = 0
        repo_total_lines_deleted: int = 0
        repo_total_files_modified: int = 0
        
        # Single pass through all commits
        for commit in repo.traverse_commits():
            repo_total_commits += 1

            author_name: str = commit.author.name if commit.author and commit.author.name else ""
            author_email: str = commit.author.email.lower() if commit.author and commit.author.email else ""
            # Resolve canonical author identity
            canonical_id: str = resolver.get_canonical_id(author_name, author_email)

            # Track stats for a new author
            if canonical_id not in canonical_stats:
                canonical_stats[canonical_id] = {
                    'commits': 0,
                    'lines_added': 0,
                    'lines_deleted': 0,
                    'files_modified': 0
                }
            
            # Check if this commit belongs to the target user by username or email
            is_user_commit: bool = resolver.is_target_user(author_email, self.username, self.user_email)
            if is_user_commit and target_user_canonical_id is None:
                target_user_canonical_id = canonical_id

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
            
            canonical_stats[canonical_id]['commits'] += 1
            canonical_stats[canonical_id]['lines_added'] += commit_lines_added
            canonical_stats[canonical_id]['lines_deleted'] += commit_lines_deleted
            canonical_stats[canonical_id]['files_modified'] += commit_files

            # Only consider the commits of the user for detailed data
            if is_user_commit: 
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

        # Anonymize contributor keys and track stats
        anonymized_stats = {}
        contributor_index: int = 1
        for canonical_id, stats in canonical_stats.items():
            is_target_user: bool = (canonical_id == target_user_canonical_id)
            key: str = 'target_user' if is_target_user else f'contributor_{contributor_index}'
            anonymized_stats[key] = {
                'commits': stats['commits'],
                'lines_added': stats['lines_added'],
                'lines_deleted': stats['lines_deleted'],
                'files_modified': stats['files_modified'],
                'is_target_user': is_target_user
            }

            if not is_target_user:
                contributor_index += 1

        is_collaborative: bool = len(canonical_stats) > 1 if canonical_stats else len(commits_data) < repo_total_commits

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
                'total_contributors': len(canonical_stats),
                'total_commits_all_authors': repo_total_commits,
                'repo_total_lines_added': repo_total_lines_added,
                'repo_total_lines_deleted': repo_total_lines_deleted,
                'repo_total_files_modified': repo_total_files_modified,
                'all_authors_stats': anonymized_stats,
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


class AuthorIdentityResolver:
    """
    Handles the resolution of author identities across multiple email addresses, full names, and usernames.
    """

    def __init__(self) -> None:
        self.identity_map: Dict[str, str] = {}

    def _extract_username_from_email(self, email: str) -> str:
        """
        Extracts the username from an email address.
        GitHub noreply emails are handled to extract the actual username.
        Regular emails return the part before the "@" symbol.
        """
        if '+' in email and email.endswith('@users.noreply.github.com'):
            return email.split('+')[1].split('@')[0].lower()
        return email.split('@')[0].lower()

    def get_canonical_id(self, author_name: str, author_email: str) -> str:
        """
        Returns a canonical identifier for the author based on their name and email.
        If the author has been seen before with different emails or names, it resolves to a single ID.
        """
        email_key = author_email.lower()
        name_key = author_name.lower()
        username_key = self._extract_username_from_email(author_email)

        # Check if any of the identifiers are already mapped
        for key in [email_key, name_key, username_key]:
            if key in self.identity_map:
                canonical_id = self.identity_map[key]
                # Map all identifiers to the canonical ID
                self.identity_map[email_key] = canonical_id
                self.identity_map[name_key] = canonical_id
                self.identity_map[username_key] = canonical_id
                return canonical_id

        # If not seen before, create a new canonical ID
        canonical_id = f"username:{username_key}" if username_key else f"email:{email_key}"
        self.identity_map[email_key] = canonical_id
        self.identity_map[name_key] = canonical_id
        self.identity_map[username_key] = canonical_id
        return canonical_id

    def is_target_user(self, author_email: str, target_username: str, target_email: Optional[str] = None) -> bool:
        """
        Determines if the given author email corresponds to the target user by username or email.

        Given that the email may be a GitHub privacy email, it extracts the username for comparison.
        User has provided their personal email and GitHub username, so we just need to check these 2 possibilities. 
        """

        # Extracted username from both email types, GitHub privacy will give the username for GitHub
        # There is a chance that the user's personal email username matches their GitHub username, but this is rare.
        author_username = self._extract_username_from_email(author_email)
        if author_username == target_username.lower():
            return True
        
        # If the email on the commit was the user's personal email, check that as well
        if target_email and author_email.lower() == target_email.lower():
            return True
        return False
       