from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import Counter

class ResumeDataProcessor: 
    """
    This class helps to extract and process data from all 
    analysis results for resume generation.
    """

    def __init__(self, result_data: Dict[str, Any]):
        """
        Initializes with complete result data passed from the resume builder

        Args:
            result_data: Dictionary containing all analysis results
        """
        self.result_data = result_data

    def extract_summary(self) -> Optional[str]:
        """
        Extract the LLM-generate summary. This will be used as the summary for
        the entire resume.
        #TODO: LLM Prompt may need to be updated to better match this function

        Returns:
            Summary bullet points, or None if not available due to issue with 
            LLM summary
        """
        try: 
            resume_points = self.result_data.get('resume_points')
            if resume_points and isinstance(resume_points, dict):
                return resume_points.get('medium summary')
            return None

        except Exception as e:
            print(f"Error extracting summary: {e}")
            return None

    def extract_metadata_skills(self) -> List[str]:
        """
        Extract the top overall skills from metadata analysis (primary_skills)
        Returns:
            List of skill strings
        """
        try: 
            skills = []
            # Get the primary skills from metadata
            metadata_insights = self.result_data.get('metadata_insights', {})
            if metadata_insights and isinstance(metadata_insights, dict):
                primary_skills = metadata_insights.get('primary_skills', [])
                skills.extend(primary_skills)

            return skills
        except Exception as e:
            print(f"Error extracting skills: {e}")
            return []

    def extract_languages(self) -> List[Dict[str, Any]]:
        """
        Extract the programming languages with proficiency metrics from metadata

        Returns:
            List of language dictionaries with name and percentage
        """
        try:
            metadata_insights = self.result_data.get('metadata_insights', {})

            if not metadata_insights or not isinstance(metadata_insights, dict):
                return []

            language_stats = metadata_insights.get('language_stats', {})

            if not language_stats:
                return []

            # Convert to list and sort by file count percentage
            languages = []
            for lang_name, lang_data in language_stats.items():
                if lang_data.get('language') != 'N/A':
                    languages.append({
                        'name': lang_data.get('language', lang_name),
                        'file_count': lang_data.get('file_count')
                    })

            # Sort by file count
            languages.sort(key=lambda x: x['file_count'], reverse = True)

            return languages

        except Exception as e:
            print(f"Error extracting languages: {e}")
            return []
    
    def extract_top_projects(self, top_n: int = 3) -> List[Dict[str, Any]]:
        """
        Extract top n project based on importance ranking.
        #TODO: Currently the team is adding support to allow users
        to pick which projects they want to include. May change some of this implementation

        Returns:
            List of project dictionaries with resume-relevant fields
        """
        try:
            project_insights = self.result_data.get('project_insights',{})

            if not project_insights:
                return []
            
            analyzed_insights = project_insights.get('analyzed_insights', [])

            if not analyzed_insights:
                return []

            # This is what may need to be changes pending changes made this week
            top_projects = analyzed_insights[:top_n]

            resume_projects = []
            for project in top_projects:
                resume_project = self._format_project_for_resume(project)
                if resume_project:
                    resume_projects.append(resume_project)
            
            return resume_projects
        
        except Exception as e:
            print(f"Error extracting projects: {e}")
            return []

    def _format_project_for_resume(self, project: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Format single project to only include resume-relevant fields

        Args:
            project: Project data from analyzed_insights

        Returns:
            Formatted project dictionary or None if there is no project data
        """
        try:
            repo_name = project.get('repository_name', 'Unknown Project')
            dates = project.get('dates', {})
            stats = project.get('statistics', {})
            collab_insights = project.get('collaboration_insights', {})
            imports = project.get('imports_summary', {})
            user_role = project.get('user_role')
            # Get top 5 frameworks from the imports
            top_frameworks = self._get_top_frameworks(imports, top_n = 5)

            # Get collaboration blurb, or use basic fallback to ensure there is something for the resume
            collaboration_blurb = user_role.get('blurb', "")

            # Format the date range for the resume
            start_date = dates.get('start_date')
            end_date = dates.get('end_date')
            date_range = self._format_date_range(start_date, end_date)

            return{
                'name': repo_name,
                'date_range': date_range,
                'frameworks': top_frameworks,
                'collaboration': collaboration_blurb,
            }

        except Exception as e:
            print(f"Error formatting project: {e}")
            return None
    
    def _get_top_frameworks(self, imports: Dict[str, Any], top_n: int) -> List[str]:
        """
        Extract top N (5) frameworks/libraries from imports summary

        Args:
            imports: imports_summary dictionary
            top_n: Number of top frameworks to return

        Returns:
            List of framework names
        """
        try:
            if not imports:
                return []
            
            # Sort by frequency
            sorted_imports = sorted(imports.items(), key=lambda x: x[1].get('frequency', 0), reverse=True)

            # Return just import name for the top 5 
            return [imp[0] for imp in sorted_imports[:top_n]]

        except Exception as e:
            print(f"Error extracting frameworks: {e}")
            return []
    

    def _format_date_range(self, start_date: Optional[str], end_date: Optional[str]) -> str:
        """
        Format date range in resume style (e.g., "Jan 2025 - Present")
        
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
            start_formatted = start.strftime("%b %Y")
            
            if not end_date:
                return f"{start_formatted} - Present"
            
            end = datetime.fromisoformat(end_date)
            
            # Check if end date is within last 30 days (consider as "Present")
            days_since_end = (datetime.now() - end).days
            if days_since_end <= 30:
                return f"{start_formatted} - Present"
            
            end_formatted = end.strftime("%b %Y")
            return f"{start_formatted} - {end_formatted}"
            
        except Exception as e:
            print(f"Error formatting dates: {e}")
            return "Dates unavailable"

        
