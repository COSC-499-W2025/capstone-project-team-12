from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict


class PortfolioDataProcessor:
    """
    Extracts and processes detailed data from analysis results for portfolio generation.
    Unlike ResumeDataProcessor, this class extracts comprehensive project details and
    complete skill evolution data to demonstrate learning progression.
    """

    def __init__(self, result_data: Dict[str, Any]):
        """
        Initializes with complete result data passed from the portfolio builder

        Args:
            result_data: Dictionary containing all analysis results
        """
        self.result_data = result_data

    def extract_detailed_projects(self, top_n: int = 3) -> List[Dict[str, Any]]:
        """
        Extract top N projects with comprehensive details for deep-dive showcases.
        
        Args:
            top_n: Number of top projects to extract (default 3)
            
        Returns:
            List of detailed project dictionaries sorted chronologically
        """
        try:
            project_insights = self.result_data.get('project_insights', {})
            
            if not project_insights:
                return []
            
            analyzed_insights = project_insights.get('analyzed_insights', [])
            
            if not analyzed_insights:
                return []
            
            # Get top N projects
            top_projects = analyzed_insights[:top_n]
            
            # Format each project with full details
            detailed_projects = []
            for project in top_projects:
                detailed_project = self._format_detailed_project(project)
                if detailed_project:
                    detailed_projects.append(detailed_project)
            
            # Sort chronologically by start date to show learning progression
            detailed_projects.sort(key=lambda x: x.get('start_date_raw', ''))
            
            return detailed_projects
        
        except Exception as e:
            print(f"Error extracting detailed projects: {e}")
            return []

    def _format_detailed_project(self, project: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Format a single project with comprehensive details for portfolio showcase.
        
        Args:
            project: Project data from analyzed_insights
            
        Returns:
            Detailed project dictionary or None if formatting fails
        """
        try:
            repo_name = project.get('repository_name', 'Unknown Project')
            dates = project.get('dates', {})
            stats = project.get('statistics', {})
            collab_insights = project.get('collaboration_insights', {})
            imports = project.get('imports_summary', {})
            user_role = project.get('user_role', {})
            contribution_analysis = project.get('contribution_analysis', {})
            testing_insights = project.get('testing_insights', {})
            
            # Get ALL frameworks/libraries (not just top 5)
            all_frameworks = self._get_all_frameworks(imports)
            
            # Get user role information
            role = user_role.get('role', 'Unknown')
            role_blurb = user_role.get('blurb', "")
            
            # Get contribution level from contribution_analysis
            contribution_level = contribution_analysis.get('contribution_level', 'Unknown')
            rank = contribution_analysis.get('rank_by_commits')
            percentile = contribution_analysis.get('percentile')
            
            # Format dates
            start_date = dates.get('start_date')
            end_date = dates.get('end_date')
            date_range = self._format_date_range(start_date, end_date)
            duration_days = dates.get('duration_days', 0)
            
            # Get repository context for total project statistics
            repo_context = project.get('repository_context', {})
            
            # Count user commits
            user_commits = project.get('user_commits', [])
            user_commit_count = len(user_commits)
            
            # Extract total project stats from repository_context
            total_commits = repo_context.get('total_commits_all_authors', 0)
            total_files = repo_context.get('repo_total_files_modified', 0)
            total_additions = repo_context.get('repo_total_lines_added', 0)
            total_deletions = repo_context.get('repo_total_lines_deleted', 0)
            
            # Extract user stats from statistics field
            user_lines_added = stats.get('user_lines_added', 0)
            user_lines_deleted = stats.get('user_lines_deleted', 0)
            user_files_modified = stats.get('user_files_modified', 0)
            
            # Calculate net lines
            net_lines = total_additions - total_deletions
            user_net_lines = user_lines_added - user_lines_deleted
            
            # Get collaboration details
            is_collaborative = collab_insights.get('is_collaborative', False)
            team_size = collab_insights.get('team_size', 1)
            contribution_share = collab_insights.get('user_contribution_share_percentage', 0)
            
            # Get testing metrics
            has_tests = testing_insights.get('has_tests', False)
            test_coverage_files = testing_insights.get('testing_percentage_files', 0)
            test_coverage_lines = testing_insights.get('testing_percentage_lines', 0)
            test_files = testing_insights.get('test_files_modified', 0)
            code_files = testing_insights.get('code_files_modified', 0)
            
            return {
                'name': repo_name,
                'date_range': date_range,
                'start_date_raw': start_date,
                'end_date_raw': end_date,
                'duration_days': duration_days,
                'frameworks': all_frameworks,
                'user_role': {
                    'role': role,
                    'blurb': role_blurb
                },
                'contribution': {
                    'level': contribution_level,
                    'rank': rank,
                    'percentile': percentile,
                    'is_collaborative': is_collaborative,
                    'team_size': team_size,
                    'contribution_share': contribution_share
                },
                'statistics': {
                    'commits': total_commits,
                    'user_commits': user_commit_count,
                    'files': total_files,
                    'additions': total_additions,
                    'deletions': total_deletions,
                    'net_lines': net_lines,
                    'user_lines_added': user_lines_added,
                    'user_lines_deleted': user_lines_deleted,
                    'user_net_lines': user_net_lines,
                    'user_files_modified': user_files_modified
                },
                'testing': {
                    'has_tests': has_tests,
                    'test_files': test_files,
                    'code_files': code_files,
                    'coverage_by_files': test_coverage_files,
                    'coverage_by_lines': test_coverage_lines
                }
            }
        
        except Exception as e:
            print(f"Error formatting detailed project: {e}")
            return None

    def _get_all_frameworks(self, imports: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract ALL frameworks/libraries from imports summary with frequency data.
        
        Args:
            imports: imports_summary dictionary
            
        Returns:
            List of framework dictionaries with name and frequency, sorted by frequency
        """
        try:
            if not imports:
                return []
            
            frameworks = []
            for import_name, import_data in imports.items():
                frameworks.append({
                    'name': import_name,
                    'frequency': import_data.get('frequency', 0)
                })
            
            # Sort by frequency (most used first)
            frameworks.sort(key=lambda x: x['frequency'], reverse=True)
            
            return frameworks
        
        except Exception as e:
            print(f"Error extracting frameworks: {e}")
            return []

    def extract_skill_timeline(self, detailed_projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a comprehensive skill timeline showing evolution across all projects.
        Separates high-level skills (from metadata) and technical frameworks (from projects).
        
        Args:
            detailed_projects: List of detailed project dictionaries (top 3)
            
        Returns:
            Dictionary containing skill evolution data with separate high-level skills 
            and project-specific frameworks
        """
        try:
            # Get all high-level skills from metadata (e.g., "Backend Development", "DevOps")
            metadata_insights = self.result_data.get('metadata_insights', {})
            all_skills = metadata_insights.get('primary_skills', [])
            
            # Get language evolution
            language_stats = metadata_insights.get('language_stats', {})
            
            # Extract framework timeline from projects (e.g., "junit", "axios", "react")
            framework_timeline = self._create_framework_timeline(detailed_projects)
            
            # Create language progression (sorted by file count)
            language_progression = self._create_language_progression(language_stats)
            
            return {
                'high_level_skills': all_skills,
                'framework_timeline': framework_timeline,
                'language_progression': language_progression,
                'total_skills': len(all_skills),
                'total_frameworks': sum(len(proj_data['frameworks']) for proj_data in framework_timeline.values())
            }
        
        except Exception as e:
            print(f"Error extracting skill timeline: {e}")
            return {}

    def _create_framework_timeline(self, projects: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Create a timeline showing which frameworks/libraries were used in each project.
        Shows progression of technical tools across chronologically ordered projects.
        
        Args:
            projects: List of detailed projects (already chronologically sorted)
            
        Returns:
            Dictionary mapping project names to their framework data
        """
        try:
            framework_timeline = {}
            
            for project in projects:
                project_name = project.get('name', 'Unknown')
                frameworks = project.get('frameworks', [])
                date_range = project.get('date_range', 'Unknown')
                
                # Get top frameworks for this project (show top 8 for timeline)
                top_frameworks = [fw.get('name') for fw in frameworks[:8]]
                
                framework_timeline[project_name] = {
                    'frameworks': top_frameworks,
                    'total_frameworks': len(frameworks),
                    'date_range': date_range
                }
            
            return framework_timeline
        
        except Exception as e:
            print(f"Error creating framework timeline: {e}")
            return {}

    def _create_language_progression(self, language_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create a sorted list of programming languages with usage metrics.
        
        Args:
            language_stats: Language statistics from metadata
            
        Returns:
            List of language dictionaries with progression data
        """
        try:
            languages = []
            
            for lang_name, lang_data in language_stats.items():
                if lang_data.get('language') != 'N/A':
                    languages.append({
                        'name': lang_data.get('language', lang_name),
                        'file_count': lang_data.get('file_count', 0),
                        'percentage': lang_data.get('percentage', 0)
                    })
            
            # Sort by file count (descending)
            languages.sort(key=lambda x: x['file_count'], reverse=True)
            
            return languages
        
        except Exception as e:
            print(f"Error creating language progression: {e}")
            return []

    def calculate_growth_metrics(self, detailed_projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate growth metrics by comparing earliest vs. most recent project.
        Demonstrates learning progression and evolution of change across multiple dimensions.
        
        Args:
            detailed_projects: List of detailed projects (chronologically sorted)
            
        Returns:
            Dictionary containing comprehensive growth comparison metrics
        """
        try:
            if len(detailed_projects) < 2:
                return {
                    'has_comparison': False,
                    'message': 'Need at least 2 projects to show growth'
                }
            
            earliest_project = detailed_projects[0]
            latest_project = detailed_projects[-1]
            
            # Statistics for comparison
            earliest_stats = earliest_project.get('statistics', {})
            latest_stats = latest_project.get('statistics', {})
            
            # Calculate code volume growth
            commit_growth = self._calculate_percentage_change(
                earliest_stats.get('commits', 0),
                latest_stats.get('commits', 0)
            )
            
            file_growth = self._calculate_percentage_change(
                earliest_stats.get('files', 0),
                latest_stats.get('files', 0)
            )
            
            lines_growth = self._calculate_percentage_change(
                earliest_stats.get('net_lines', 0),
                latest_stats.get('net_lines', 0)
            )
            
            user_lines_growth = self._calculate_percentage_change(
                earliest_stats.get('user_net_lines', 0),
                latest_stats.get('user_net_lines', 0)
            )
            
            # Compare frameworks/technology adoption
            earliest_frameworks = len(earliest_project.get('frameworks', []))
            latest_frameworks = len(latest_project.get('frameworks', []))
            framework_growth = self._calculate_percentage_change(
                earliest_frameworks,
                latest_frameworks
            )
            
            # Compare testing practices
            earliest_testing = earliest_project.get('testing', {})
            latest_testing = latest_project.get('testing', {})
            
            earliest_test_coverage = earliest_testing.get('coverage_by_files', 0)
            latest_test_coverage = latest_testing.get('coverage_by_files', 0)
            test_coverage_growth = latest_test_coverage - earliest_test_coverage  # Absolute change
            
            testing_evolution = {
                'earliest_has_tests': earliest_testing.get('has_tests', False),
                'latest_has_tests': latest_testing.get('has_tests', False),
                'coverage_improvement': test_coverage_growth
            }
            
            # Compare collaboration complexity
            earliest_contribution = earliest_project.get('contribution', {})
            latest_contribution = latest_project.get('contribution', {})
            
            collaboration_evolution = {
                'earliest_solo': not earliest_contribution.get('is_collaborative', False),
                'latest_solo': not latest_contribution.get('is_collaborative', False),
                'earliest_team_size': earliest_contribution.get('team_size', 1),
                'latest_team_size': latest_contribution.get('team_size', 1),
                'earliest_level': earliest_contribution.get('level', 'Unknown'),
                'latest_level': latest_contribution.get('level', 'Unknown')
            }
            
            # Compare roles
            earliest_role = earliest_project.get('user_role', {}).get('role', 'Unknown')
            latest_role = latest_project.get('user_role', {}).get('role', 'Unknown')
            
            return {
                'has_comparison': True,
                'earliest_project': earliest_project.get('name'),
                'latest_project': latest_project.get('name'),
                'code_metrics': {
                    'commit_growth': commit_growth,
                    'file_growth': file_growth,
                    'lines_growth': lines_growth,
                    'user_lines_growth': user_lines_growth
                },
                'technology_metrics': {
                    'framework_growth': framework_growth,
                    'earliest_frameworks': earliest_frameworks,
                    'latest_frameworks': latest_frameworks
                },
                'testing_evolution': testing_evolution,
                'collaboration_evolution': collaboration_evolution,
                'role_evolution': {
                    'earliest_role': earliest_role,
                    'latest_role': latest_role,
                    'role_changed': earliest_role != latest_role
                }
            }
        
        except Exception as e:
            print(f"Error calculating growth metrics: {e}")
            return {'has_comparison': False, 'error': str(e)}

    def _calculate_percentage_change(self, old_value: float, new_value: float) -> float:
        """
        Calculate percentage change between two values.
        
        Args:
            old_value: Earlier value
            new_value: Later value
            
        Returns:
            Percentage change (positive or negative)
        """
        try:
            if old_value == 0:
                return 100.0 if new_value > 0 else 0.0
            
            change = ((new_value - old_value) / old_value) * 100
            return round(change, 1)
        
        except Exception as e:
            print(f"Error calculating percentage change: {e}")
            return 0.0

    def _format_date_range(self, start_date: Optional[str], end_date: Optional[str]) -> str:
        """
        Format date range in portfolio style (e.g., "Jan 2024 - Present")
        
        Args:
            start_date: ISO format start date string
            end_date: ISO format end date string
            
        Returns:
            Formatted date range string
        """
        try:
            if not start_date:
                return "Dates unavailable"
            
            # Parse ISO format dates
            start = datetime.fromisoformat(start_date)
            # Remove timezone info for formatting
            if start.tzinfo:
                start = start.replace(tzinfo=None)
            start_formatted = start.strftime("%b %Y")
            
            if not end_date:
                return f"{start_formatted} - Present"
            
            end = datetime.fromisoformat(end_date)
            if end.tzinfo:
                end = end.replace(tzinfo=None)
            
            # Check if end date is within last 30 days -> consider as "Present"
            days_since_end = (datetime.now() - end).days
            if days_since_end <= 30:
                return f"{start_formatted} - Present"
            
            end_formatted = end.strftime("%b %Y")
            return f"{start_formatted} - {end_formatted}"
            
        except Exception as e:
            print(f"Error formatting dates: {e}")
            return "Dates unavailable"