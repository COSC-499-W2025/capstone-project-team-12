from typing import Any, Dict, List, Set
from datetime import datetime
import re

class RepositoryAnalyzer:
    # Analyzes repository data to extract project insights

    def __init__(self, username: str):
        self.username = username

    # Regex patterns for import statements in various languages
    # Python: from X import Y -> captures X; import X, Y -> captures X, Y
    PYTHON_IMPORT_RE = re.compile(r'^\s*(?:from\s+([a-zA-Z0-9_\.]+)\s+import|import\s+([a-zA-Z0-9_\., ]+))', re.MULTILINE)

    # JavaScript/TypeScript: import X from 'module' or require('module') -> captures 'module'
    JS_IMPORT_RE = re.compile(r'^\s*import\s+(?:.*?\s+from\s+)?["\']([^"\']+)["\']|^\s*const\s+\w+\s*=\s*require\(["\']([^"\']+)["\']\)', re.MULTILINE)

    # Java: import package.Class; -> captures package.Class
    JAVA_IMPORT_RE = re.compile(r'^\s*import\s+([\w\.]+);', re.MULTILINE)

    # C/C++: #include <header> or #include "header" -> captures header
    C_IMPORT_RE = re.compile(r'^\s*#include\s*[<"]([^>"]+)[>"]', re.MULTILINE)

    # If none of the above, here is a generic pattern to capture common import/include statements
    GENERIC_IMPORT_RE = re.compile(r'\b(import|require|include)\b.*?[\'"<]([\w\./-]+)[\'">]', re.MULTILINE)


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
                'contribution_analysis': self._calculate_contribution_insights(project),
                'collaboration_insights': self._generate_collaboration_insights(project),
                'testing_insights': self._generate_testing_insights(project),
                'imports_summary': self.extract_repo_import_stats(project)
            }
            projects_insights.append(project_insight)

        return projects_insights

    def extract_repo_import_stats(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts the import statistics for all files modified by the user in one repo.
        Uses the modified files from the raw data extracted in the processor
        Returns a dict with repository_name and imports_summary. For each import, we track:
        - frequency
        - start_date
        - end_date
        - duration_days

        Doing this allows us to find skills and technologies the user has worked with over time.
        """
        repo_name = project.get('repository_name', 'Unknown')
        commits_data: List[Dict[str, Any]] = project.get('user_commits', [])
        imports_data: Dict[str, Dict[str, Any]] = {}

        # Loop through all commits in the raw data
        for commit in commits_data:
            commit_date_str = commit.get('date')
            if not commit_date_str:
                continue
            
            try:
                commit_date = datetime.fromisoformat(commit_date_str)
            except (ValueError, TypeError):
                continue

            # Loop through all modified files in the commit
            for mod in commit.get('modified_files', []):
                src = mod.get('source_code', '')
                if not src.strip():
                    continue

                # Get file extension to determine language
                filename = mod.get('filename', 'unknown')
                ext = filename.split('.')[-1].lower() if '.' in filename else ""

                # Extract imports based on programming language using regex patterns
                imports: List[str] = []
                if ext == "py":
                    matches = self.PYTHON_IMPORT_RE.findall(src)
                    for m_from, m_imp in matches:
                        if m_from:
                            imports.append(m_from)
                        elif m_imp:
                            imports += [i.split(" as ")[0].strip() for i in m_imp.split(',')]
                elif ext in {"js", "ts"}:
                    matches = self.JS_IMPORT_RE.findall(src)
                    for m in matches:
                        imports.append(m[0] or m[1])
                elif ext == "java":
                    imports += self.JAVA_IMPORT_RE.findall(src)
                elif ext in {"c", "cpp", "h", "hpp"}:
                    imports += self.C_IMPORT_RE.findall(src)

                # imports_data is a dict with per-import statistics
                for imp in imports:
                    if imp not in imports_data:
                        imports_data[imp] = {
                            "frequency": 0,
                            "start_date": commit_date,
                            "end_date": commit_date
                        }
                    imports_data[imp]["frequency"] += 1
                    if commit_date < imports_data[imp]["start_date"]:
                        imports_data[imp]["start_date"] = commit_date
                    if commit_date > imports_data[imp]["end_date"]:
                        imports_data[imp]["end_date"] = commit_date

        # Convert dates and calculate duration
        for imp, data in imports_data.items():
            start = data["start_date"]
            end = data["end_date"]
            data["start_date"] = start.isoformat() if start else None
            data["end_date"] = end.isoformat() if end else None
            data["duration_days"] = (end - start).days if start and end else None

        return imports_data   

    def get_all_repo_import_stats(self, project_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get the import statistics for all repos that were modified by the user.
        Returns a list of dicts (one per repository), each containing:
        - repository_name
        - imports_summary (as defined in extract_repo_import_stats)
        """

        repo_summaries: List[Dict[str, Any]] = []

        for project in project_data:
            if project.get('status') != 'success':
                repo_summaries.append({
                    "repository_name": project.get('repository_name', 'Unknown'),
                    "imports_summary": {},
                    "error": project.get('error_message', 'Unknown error')
                })
                continue
            
            try:
                imports_summary = self.extract_repo_import_stats(project)
                repo_summaries.append({
                    "repository_name": project.get('repository_name', 'Unknown'),
                    "imports_summary": imports_summary
                })
            except Exception as e:
                repo_summaries.append({
                    "repository_name": project.get('repository_name', 'Unknown'),
                    "imports_summary": {},
                    "error": str(e)
                })

        return repo_summaries
    
    def sort_repo_imports_in_chronological_order(self, repo_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sorts the imports of a single repo in chronological order by start_date DESC
        """
        imports = repo_summary.get("imports_summary", {})

        sorted_imports = sorted(imports.items(), key=lambda item: datetime.fromisoformat(item[1]["start_date"]) if item[1].get("start_date") else datetime.min, reverse=True)
        repo_summary["imports_summary"] = {imp: stats for imp, stats in sorted_imports}

        return repo_summary
    
    
    def sort_all_repo_imports_chronologically(self, all_repo_summaries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes the full list from get_all_repo_import_stats() and sorts all imports across all repositories in chronological order 
        (by start_date DESC)
        """
        aggregated = []

        for repo_summary in all_repo_summaries:
            repo_name = repo_summary["repository_name"]
            imports_summary = repo_summary.get("imports_summary", {})

            for imp, stats in imports_summary.items():
                start_str = stats.get("start_date")
                start_dt = (
                    datetime.fromisoformat(start_str)
                    if start_str else datetime.min
                )

                aggregated.append({
                    "import": imp,
                    "repository_name": repo_name,
                    "start_date": stats.get("start_date"),
                    "end_date": stats.get("end_date"),
                    "duration_days": stats.get("duration_days"),
                    "frequency": stats.get("frequency"),
                    "start_dt": start_dt,   # keep this only for sorting
                })

        aggregated.sort(key=lambda x: x["start_dt"], reverse=True)

        # remove the helper datetime object before returning
        for entry in aggregated:
            entry.pop("start_dt", None)

        return aggregated 

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
        percentile: float = ((total_authors - rank + 1) / total_authors) * 100 if rank else None

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
            if repo.get('status') != 'success':
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

    