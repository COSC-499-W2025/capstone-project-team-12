from typing import List, Dict, Any
from datetime import datetime

class ResumeGenerator:
    """
    Generates resume-formatted content from analyzed data.
    """

    def __init__(self, analyzed_repos: List[Dict[str, Any]], metadata_analysis: Dict[str, Any]):
        """
        Initializes the ResumeGenerator with analyzed data.
        """

        self.analyzed_repos = analyzed_repos
        self.metadata_analysis = metadata_analysis

    def generate_full_resume(self, top_n_project: int = 5) -> Dict[str, Any]:
        """
        Generates a full resume including summary, skills, projects, and experience.

        Args:
            top_n_project (int): Number of top projects to include in the resume.
        
        Returns:
            Dict[str, Any]: A dictionary containing the full resume content for API.
        """

        projects_included = self.analyzed_repos[:top_n_project]

        resume_content: Dict[str, Any] = {
            "resume_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "total_projects_analyzed": len(self.analyzed_repos),
            },
            "summary": self._format_professional_summary(),
            "skills": self._format_skills_section(),
            "projects": [self._format_project_section(project) for project in projects_included]
        }

        return resume_content

    