from typing import Dict, Any, List
from prompt_toolkit import prompt 
import re

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
        """
        self.cli.print_status(f"Current Summary: {current_summary}", "info")
        return self._edit_text_field("Summary", current_summary, allow_multiline = True) 

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
                        project['name'] = self._edit_text_field("Project Name", project.get('name'), allow_multiline = False)
                        self.cli.print_status("Project name updated.", "success")
                    case 'd':
                        print(f"\nCurrent Date Range: {project.get('date_range', 'N/A')}")
                        print("\nFormat for date range: 'MMM YYYY - MMM YYYY' or 'MMM YYYY - Present'. Example: 'Jan 2020 - Dec 2021' or 'Jan 2020 - Present'")
                        while True:
                            new_date_range = self._edit_text_field("Date Range", project.get('date_range', ''), allow_multiline=False)
                            
                            # User cancelled or kept original
                            if new_date_range == project.get('date_range', ''):
                                break
                                
                            # Validate the new input
                            if self._validate_date_range(new_date_range):
                                project['date_range'] = new_date_range
                                self.cli.print_status("Project date range updated.", "success")
                                break
                            else:
                                self.cli.print_status(
                                    "Invalid format. Expected 'MMM YYYY - MMM YYYY' or 'MMM YYYY - Present'. For Example: 'Jan 2020 - Dec 2021' or 'Jan 2020 - Present'. Please try again or press Ctrl+C to cancel.", 
                                    "warning"
                                )
                    case 'f':
                        print(f"\nCurrent Frameworks: {', '.join(project.get('frameworks', []))}")
                        project['frameworks'] = self._edit_list_field("Frameworks", project.get('frameworks', []))
                            
                    case 'c':
                        print(f"\nCurrent Collaboration Blurb: {project.get('collaboration', 'N/A')}")
                        project['collaboration'] = self._edit_text_field("Collaboration", project.get('collaboration', ''), allow_multiline=False)
                        self.cli.print_status("Collaboration updated.", "success")
                    case 'q':
                        self.cli.print_status("Finished editing project.", "success")
                        break
                    case _:
                        self.cli.print_status("Invalid choice. No changes made to project.", "warning")
            except Exception as e:
                self.cli.print_status(f"Error during project editing: {e}", "error")
        return project

    def _validate_date_range(self, date_range: str) -> bool:
        """
        Validate the date range format (e.g., 'Jan 2020 - Dec 2021' or 'Jan 2020 - Present')
        """
        if not date_range or '-' not in date_range:
            return False
        
        # Pattern: MMM YYYY - MMM YYYY or MMM YYYY - Present
        pattern = r'^[A-Za-z]{3}\s+\d{4}\s*-\s*([A-Za-z]{3}\s+\d{4}|Present)$'
        
        if not re.match(pattern, date_range.strip(), re.IGNORECASE):
            return False
        
        # Additional validation: check if month abbreviations are valid
        valid_months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                    'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
        
        parts = date_range.strip().split('-')
        
        # Validate start date
        start_parts = parts[0].strip().split()
        if len(start_parts) == 2:
            month, year = start_parts
            if month.lower() not in valid_months:
                return False
            try:
                year_int = int(year)
                if year_int < 1900 or year_int > 2100:
                    return False
            except ValueError:
                return False
        
        # Validate end date (if not "Present")
        end_parts = parts[1].strip().split()
        if end_parts[0].lower() != 'present':
            if len(end_parts) == 2:
                month, year = end_parts
                if month.lower() not in valid_months:
                    return False
                try:
                    year_int = int(year)
                    if year_int < 1900 or year_int > 2100:
                        return False
                except ValueError:
                    return False
        
        return True


    def _edit_skills(self, current_skills: List[str]) -> List[str]:
        """
        Edit the skills section of the resume. Allows user to remove current detected skills, or enter new skills.
        """
        self.cli.print_header("Edit Skills")
        return self._edit_list_field("Skills", current_skills)

    def _edit_languages(self, current_languages: List[Dict[str,Any]]) -> List[Dict[str,Any]]:
        """
        Edit the languages section of the resume. Allows user to remove current detected languages, or enter new languages.
        """
        self.cli.print_header("Edit Languages")
        language_names = [lang['name'] for lang in current_languages]

        # Use helper to edit list of names
        edited_names = self._edit_list_field("Languages", language_names)

        # Reconstruct the Dict format
        result = []
        for name in edited_names:
            # Keep existing language with file_count if it exists
            existing = next((lang for lang in current_languages if lang['name'] == name), None)
            if existing:
                result.append(existing)
            else:
                result.append({'name': name, 'file_count': 0})
        
        return result
        

    def _edit_text_field(self, field_name: str, current_value: str, allow_multiline: bool = False) -> str:
        """
        Helper to edit a text field . For multiline inputs, prompt the user to edit previous or fully replace it.
        For single line outputs, we assume they are short enough to just provide the current one in an editable format so they
        can make any changes or just delete and replace it themselves.
        """
        if allow_multiline:
            edit_choice = self.cli.get_input(f"Would you like to [E]dit, [R]eplace, or press Enter to keep the current {field_name.lower()}?: \n> ").strip().lower()
            try:
                match(edit_choice):
                    case 'e':
                        """
                        With this library the user is able to create multiple lines by pressing enter. This gives them more control over
                        how the formatting will look of their resume. However, this does create the issue where Enter now does not immediatley submit their new input, 
                        which does differ from most other user input we currently have. This is why I used ESC then Enter, or we can create custom key bindings, but 
                        since this will change again once we have a frontend I wasnt sure if it was worth any additional efforts. 
                        """
                        self.cli.print_status(f"Edit {field_name.lower()} (ESC then Enter to finish editing, Ctrl+C to cancel):", "info")
                        try:
                            new_value = prompt('\n> ', default=current_value, multiline=True).strip()
                        except KeyboardInterrupt:
                            self.cli.print_status("Edit cancelled", "warning")
                            new_value = current_value
                    case 'r':
                        self.cli.print_status(f"Enter your new {field_name.lower()}")
                        try: 
                            new_value = prompt('\n> ',multiline = True)
                        except KeyboardInterrupt:
                            self.cli.print_status("Edit cancelled", "warning")
                            new_value = current_value
                    case '':
                        new_value = current_value
                    case _:
                        self.cli.print_status(f"Invalid option '{edit_choice}'. Keeping current {field_name.lower()}")
                        new_value = current_value
            except Exception as e:
                self.cli.print_status(f"Error during summary editing: {e}", "error")
                new_value = current_value
        else:
            # Single line editing, we always give them the previous option to edit or delete and replace themselves
            self.cli.print_status(f"Edit or replace the current {field_name.lower()} and press Enter to continue")
            try:
                new_value = prompt('\n> ', default = current_value)
            except KeyboardInterrupt:
                self.cli.print_status("Edit cancelled", "warning")
                new_value = current_value

        return new_value

    def _edit_list_field(self, field_name: str, current_items: List[str]) -> List[str]:
        """
        Helper to manage a list of items with add/remove pattern
        """
        items_lower = [item.lower() for item in current_items]

        while True:
            self.cli.print_status(f"\nCurrent {field_name}: {', '.join(current_items)}", "info")
            choice = self.cli.get_input(f"Type a {field_name.lower().rstrip('s')} to add/remove, or 'done' to finish: \n> ").strip()
            
            if choice.lower() == 'done':
                break
            
            if choice.lower() in items_lower:
                # Remove item
                actual_item = current_items[items_lower.index(choice.lower())]
                confirm = self.cli.get_input(
                    f"Remove '{actual_item}'? (y/n): \n> "
                ).strip().lower()
                
                if confirm == 'y':
                    current_items.remove(actual_item)
                    items_lower.remove(choice.lower())
                    self.cli.print_status(f"Removed: {actual_item}", "success")
            elif choice.lower() not in items_lower and choice:
                # Add item
                current_items.append(choice)
                items_lower.append(choice.lower())
                self.cli.print_status(f"Added: {choice}", "success")
        
        return current_items

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