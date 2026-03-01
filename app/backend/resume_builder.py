from typing import Dict, Any, Optional
import uuid
from cli_interface import CLI

from database_manager import DatabaseManager
from resume_data_processor import ResumeDataProcessor


class ResumeBuilder:
    """
    Main class for coordinating resume generation from analysis results.
    Handles resume building, database integration, and display.
    
    Example future database methods:
    - database_manager.save_resume(resume) -> stores all columns
    - database_manager.get_resume_by_id(resume_id) -> returns full resume
    - database_manager.update_resume_section(resume_id, section_name, data)
    """

    def create_resume_from_analysis_id(self, database_manager: DatabaseManager, cli: CLI, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Builds the resume from a stored result by fetching from the database

        Args:
            database_manager: DatabaseManager instance
            analysis_id: UUID of the result to generate resume from
            cli: the CLI interface
        
        Returns:
            Resume dictionary or None for status messages
        """

        try:
            cli.print_header(f"Retrieving result {analysis_id}...")

            # Fetch the result data from the db
            result_data = database_manager.get_analysis_data(analysis_id)

            if not result_data:
                cli.print_status("Result not found in database.", "error")
                return None

            cli.print_status("Generating resume...", "info")

            # Build the actual resume -> this resume contains all sections as separate Dict entries
            resume = self._build_resume(result_data, analysis_id=analysis_id)

            # Ensure resume has some content
            has_content = any([resume.get(section) for section in ['summary', 'projects', 'skills', 'languages']])

            if not has_content:
                cli.print_status("Generated resume is empty. Cannot save or display.", "error")
                return None

            else:
                cli.print_status("Resume generated successfully!", "success")

            return resume

        except Exception as e:
            cli.print_status(f"Error creating resume: {e}", "error")
            return None

    def _build_resume(self, result_data: Dict[str, Any], analysis_id: str) -> Dict[str, Any]:
        """
        Internal method to build the resume dictionary from result data

        Args:
            result_data: Dictionary containing all analysis results
            analysis_id: UUID of the analysis
        
        Returns:
            Resume dictionary with sections resume_id, analysis_id, summary, projects, skills, languages
            This structure maps directly to the planned database schema.
        """
        try:
            processor = ResumeDataProcessor(result_data)

            # Extract sections
            summary = processor.extract_summary()
            projects = processor.extract_top_projects(top_n=3)
            skills = processor.extract_metadata_skills()
            languages = processor.extract_languages()

            # Construct resume dictionary
            resume = {
                "analysis_id": analysis_id,
                "summary": summary,
                "projects": projects,
                "skills": skills,
                "languages": languages
            }

            return resume
        except Exception as e:
            print(f"Error building resume: {e}")
            return {}

    def display_resume(self, resume: Dict[str, Any], cli=None) -> None:
        """
        Display resume in CLI for testing/verification purposes
        Formats directly from JSON structure
        
        Args:
            resume: Resume dictionary
            cli: CLI interface for formatted display
        """
        try:
            cli.print_header("Generated Resume")
            
            # Display resume metadata
            print(f"Resume ID: {resume.get('resume_id', 'Unknown')}")
            print(f"Analysis ID: {resume.get('analysis_id', 'Unknown')}")
            print("")
            
            # Display summary section
            summary = resume.get('summary')
            if summary:
                print("SUMMARY")
                print("-" * 60)
                print(summary)
                print("")
            
            # Display projects section
            projects = resume.get('projects', [])
            if projects:
                print("PROJECTS")
                print("-" * 60)
                for idx, project in enumerate(projects, 1):
                    print(f"\n{idx}. {project.get('name', 'Unknown Project')}")
                    print(f"   {project.get('date_range', 'Dates unavailable')}")
                    print(f"   {project.get('collaboration', '')}")
                    
                    frameworks = project.get('frameworks', [])
                    if frameworks:
                        frameworks_str = ", ".join(frameworks)
                        print(f"   Technologies: {frameworks_str}")
                print("")
            
            # Display skills section
            skills = resume.get('skills', [])
            if skills:
                print("SKILLS")
                print("-" * 60)
                skills_str = ", ".join(skills)
                print(skills_str)
                print("")
            
            # Display languages section
            languages = resume.get('languages', [])
            if languages:
                print("PROGRAMMING LANGUAGES")
                print("-" * 60)
                for lang in languages:
                    print(f"  • {lang.get('name', 'Unknown')}: {lang.get('file_count', 0)} files")
                print("")
            
            print("=" * 60)
            
        except Exception as e:
            if cli:
                cli.print_status(f"Error displaying resume: {e}", "error")
            else:
                print(f"Error displaying resume: {e}")