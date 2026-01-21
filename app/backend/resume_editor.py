from typing import Dict, Any, List


class ResumeEditor:
    """
    This class provides functionalities to edit resumes after generation
    """

    def __init__(self, cli):
        self.cli = cli

    def edit_resume(self, resume: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit the resume based on user inputs - lets user edit each section of the resume
        Args:
            resume (Dict[str, Any]): The generated resume data
        Returns:
            Dict[str, Any]: The edited resume data
        """
        self.cli.print_header("Resume Editor")
        while True:
            choice = self.cli.get_input(
                """Resume Edit Options - Please select a section to edit: \n\t
                -'S' Edit Summary.\n\t
                -'P' Edit Projects.\n\t
                -'K' Edit Skills.\n\t
                -'L' Edit Languages.\n\t
                -'V' Preview Full Resume.\n\t
                -'D' Done Editing.\n""").strip().lower()

            try:
                match(choice):
                    case 's':
                        resume['summary'] = self._edit_summary(resume.get('summary', ''))
                    case 'p':
                        resume['projects'] = self._edit_projects(resume.get('projects', []))
                    case 'k':
                        resume['skills'] = self._edit_skills(resume.get('skills', []))
                    case 'l':
                        resume['languages'] = self._edit_languages(resume.get('languages', []))
                    case 'v':
                        self._preview_resume(resume)
                    case 'd':
                        self.cli.print_status("Finished editing resume.", "success")
                        break
                    case _:
                        self.cli.print_status("Invalid choice. Please select a valid option.", "warning")

            except Exception as e:
                self.cli.print_status(f"Error during resume editing: {e}", "error")
                continue

        return resume

    def _edit_summary(self, current_summary: str) -> str:
        """
        Edit the summary section of the resume
        Args:
            current_summary (str): The current summary text
        Returns:
            str: The edited summary text
        """
        self.cli.print_status(f"Current Summary: {current_summary}", "info")
        new_summary = self.cli.get_input("Enter new summary text and press Enter once complete. (or press Enter to keep current): \n> ").strip()
        return new_summary if new_summary else current_summary  

    def _edit_projects(self, current_projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Edit details of projects in the resume 
        Args:
            current_projects (List[Dict[str, Any]]): The current list of projects
        Returns:
            List[Dict[str, Any]]: The edited list of projects
        """
        self.cli.print_header("Edit Projects")

        if not current_projects:
            self.cli.print_status("No projects available to edit.", "warning")
            return current_projects
        
        while True:
            for idx, project in enumerate(current_projects, 1):
                print(f"{idx}. {project.get('name', 'Unnamed Project')}")
                print(f"   Date: {project.get('date_range', 'No Date Range')}")
                print(f"   Frameworks: {', '.join(project.get('frameworks', []))}")
                print(f"   Collaboration: {project.get('collaboration', 'No Collaboration Info')}\n")
            
            project_choice = self.cli.get_input("Select a project number to edit or type 'done' to finish editing projects: \n> ").strip().lower()
            
            if project_choice == 'done':
                break
            
            if project_choice.isdigit() and 1 <= int(project_choice) <= len(current_projects):
                project_idx = int(project_choice) - 1
                current_projects[project_idx] = self._edit_single_project(current_projects[project_idx])
            else:
                self.cli.print_status("Invalid choice. Please select a valid project number or 'done'.", "warning")
        
        return current_projects
    
    def _edit_single_project(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit a single project's details

        Args:
            project (Dict[str, Any]): The project data to edit

        Returns:
            Dict[str, Any]: The edited project data
        """
        self.cli.print_status(f"Editing Project: {project.get('name', 'Unnamed Project')}", "info")

        while True:

            # Printing all of the details again just so it is easily accessible to the user
            print("\nCurrent Details:")
            print(f"  Name: {project.get('name', 'Unknown')}")
            print(f"  Date Range: {project.get('date_range', 'N/A')}")
            print(f"  Frameworks: {', '.join(project.get('frameworks', []))}")
            print(f"  Collaboration: {project.get('collaboration', 'N/A')}")
            
            project_choice = self.cli.get_input(
                """Which section would you like to edit? \n\t
                    -'N' Edit Name.\n\t
                    -'D' Edit Date Range.\n\t
                    -'F' Edit Frameworks.\n\t
                    -'C' Edit Collaboration.\n\t
                    -'Q' Done Editing.\n""").strip().lower()
            
            try:
                match(project_choice):
                    case 'n':
                        print(f"\nCurrent Name: {project.get('name', 'Unknown')}")
                        new_name = self.cli.get_input("Enter new project name (or press Enter to keep current): \n> ").strip()
                        if new_name:
                            project['name'] = new_name
                            self.cli.print_status("Project name updated.", "success")
                    case 'd':
                        print(f"\nCurrent Date Range: {project.get('date_range', 'N/A')}")
                        print("\nFormat for date range: 'MMM YYYY - MMM YYYY' or 'MMM YYYY - Present'")
                        new_date_range = self.cli.get_input("Enter new date range, must include '-' (or press Enter to keep current): \n> ").strip()
                        if new_date_range and '-' in new_date_range:
                            project['date_range'] = new_date_range
                            self.cli.print_status("Project date range updated.", "success")
                        elif new_date_range:
                            self.cli.print_status("Invalid date range format, did not contain '-'. Update skipped.", "warning")
                    case 'f':
                        print(f"\nCurrent Frameworks: {', '.join(project.get('frameworks', []))}")
                        while True:
                            frameworks_input = self.cli.get_input("Type new framework to add, type current framework to remove, type done to finish editing frameworks): \n> ").strip()
                            if frameworks_input.lower() == 'done':
                                break
                            elif frameworks_input in project.get('frameworks', []):
                                confirm_remove = self.cli.get_input(f"Are you sure you want to remove the framework '{frameworks_input}'? (y/n): \n> ").strip().lower()
                                if confirm_remove == 'y':
                                    project['frameworks'].remove(frameworks_input)
                                    self.cli.print_status(f"Removed framework: {frameworks_input}", "success")
                            elif frameworks_input not in project.get('frameworks', []) and frameworks_input != '':
                                project.setdefault('frameworks', []).append(frameworks_input)
                                self.cli.print_status(f"Added framework: {frameworks_input}", "success")
                            
                    case 'c':
                        print(f"\nCurrent Collaboration Blurb: {project.get('collaboration', 'N/A')}")
                        new_collaboration = self.cli.get_input("Enter new collaboration details (or press Enter to keep current): \n> ").strip()
                        if new_collaboration:
                            project['collaboration'] = new_collaboration
                            self.cli.print_status("Project collaboration details updated.", "success")
                    case 'q':
                        self.cli.print_status("Finished editing project.", "success")
                        break
                    case _:
                        self.cli.print_status("Invalid choice. No changes made to project.", "warning")
            except Exception as e:
                self.cli.print_status(f"Error during project editing: {e}", "error")
        return project

    def _edit_skills(self, current_skills: List[str]) -> List[str]:
        """
        Edit the skills section of the resume. Allows user to remove current detected skills, or enter new skills.
        Args:
            current_skills (List[str]): The current list of skills
        Returns:
            List[str]: The edited list of skills
        """
        self.cli.print_header("Edit Skills")
        self.cli.print_status(f"\nCurrent Skills: {', '.join(current_skills)}", "info")

        #TODO: Currently the highlighted skills are not being stored in result_data. Once they are, we can add them here to also be considered.
        while True:
            skill_choice = self.cli.get_input("Type a skill to add, type a skill to remove, or type 'done' to finish editing skills: \n> ").strip()
            
            if skill_choice.lower() == 'done':
                break
            
            # If skill is in the list then remove it, else add it. Confirm with user before removing.
            if skill_choice in current_skills:
                confirm_remove = self.cli.get_input(f"Are you sure you want to remove the skill '{skill_choice}'? (y/n): \n> ").strip().lower()
                if confirm_remove == 'y':
                    current_skills.remove(skill_choice)
                    self.cli.print_status(f"Removed skill: {skill_choice}", "success")
                elif confirm_remove == 'n':
                    self.cli.print_status("No changes made.", "info")
                elif confirm_remove != 'y' and confirm_remove != 'n':
                    self.cli.print_status("Invalid input. No changes made.", "warning")

            elif skill_choice not in current_skills and skill_choice != '':
                current_skills.append(skill_choice)
                self.cli.print_status(f"Added skill: {skill_choice}", "success")

        return current_skills

    def _edit_languages(self, current_languages: List[Dict[str,Any]]) -> List[Dict[str,Any]]:
        """
        Edit the languages section of the resume. Allows user to remove current detected languages, or enter new languages.
        Args:
            current_languages (List[Dict[str,Any]]): The current list of languages
        Returns:
            List[Dict[str,Any]]: The edited list of languages
        """
        self.cli.print_header("Edit Languages")
        language_names = [lang['name'] for lang in current_languages]
        while True:
            # Display current languages each time so user can see updates
            self.cli.print_status(f"\nCurrent Languages: {', '.join(language_names)}", "info")
            language_choice = self.cli.get_input("Type a language to add, type a language to remove, or type 'done' to finish editing languages: \n> ").strip()
            
            if language_choice.lower() == 'done':
                break
            
            # If language is in the list then remove it, else add it. Confirm with user before removing.
            if language_choice in language_names:
                confirm_remove = self.cli.get_input(f"Are you sure you want to remove the language '{language_choice}'? (y/n): \n> ").strip().lower()
                if confirm_remove == 'y':
                    # Need to remove the full dict, not just the name string in the list
                    language_names.remove(language_choice)
                    current_languages.remove([lang for lang in current_languages if lang['name'] == language_choice][0])
                    self.cli.print_status(f"Removed language: {language_choice}", "success")
                elif confirm_remove == 'n':
                    self.cli.print_status("No changes made.", "info")
                elif confirm_remove != 'y' and confirm_remove != 'n':
                    self.cli.print_status("Invalid input. No changes made.", "warning")

            elif language_choice not in language_names and language_choice != '':
                language_names.append(language_choice)
                current_languages.append({'name': language_choice, 'file_count': 0})
                self.cli.print_status(f"Added language: {language_choice}", "success")

        return current_languages

    def _preview_resume(self, resume: Dict[str, Any]) -> None:
        """
        Preview the full resume in the CLI

        Args:
            resume (Dict[str, Any]): The resume data to preview
        """
        self.cli.print_header("Resume Preview")
        print(f"Summary:\n{resume.get('summary', 'No Summary')}\n")
        print("Skills:")
        print(', '.join(resume.get('skills', [])) + "\n")
        print("Languages:")
        all_language_names = [lang['name'] for lang in resume.get('languages', [])]
        print(', '.join(all_language_names) + "\n")
        print("Projects:")
        for project in resume.get('projects', []):
            print(f"- {project.get('name', 'Unnamed Project')} ({project.get('date_range', 'No Date Range')})")
            print(f"  Frameworks: {', '.join(project.get('frameworks', []))}")
            print(f"  Collaboration: {project.get('collaboration', 'No Collaboration Info')}\n")