from typing import Dict, Any, List

class PortfolioEditor:
    """
    This class provides functionalities to edit portfolios after generation.
    Allows inline editing of existing content rather than full replacement.
    """

    def __init__(self, cli):
        self.cli = cli

    def edit_portfolio(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit the portfolio based on user inputs - lets user edit each section

        Args:
            portfolio (Dict[str, Any]): The generated portfolio data          
        Returns:
            Dict[str, Any]: The edited portfolio data
        """
        self.cli.print_header("Portfolio Editor")
        while True:
            choice = self.cli.get_input(
                """Portfolio Edit Options - Please select a section to edit: \n\t
                -'P' Edit Project Details.\n\t
                -'S' Edit Skills & Technologies.\n\t
                -'D' Done Editing.\n""").strip().lower()

            try:
                match(choice):
                    case 'p':
                        portfolio['projects_detail'] = self._edit_projects(portfolio.get('projects_detail', []))
                    case 's':
                        portfolio['skill_timeline'] = self._edit_skill_timeline(portfolio.get('skill_timeline', {}))
                    case 'd':
                        self.cli.print_status("Finished editing portfolio.", "success")
                        break
                    case _:
                        self.cli.print_status("Invalid choice. Please select a valid option.", "warning")

            except Exception as e:
                self.cli.print_status(f"Error during portfolio editing: {e}", "error")
                continue

        return portfolio

    def _edit_projects(self, current_projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Edit details of projects in the portfolio
        
        Args:
            current_projects (List[Dict[str, Any]]): The current list of detailed projects        
        Returns:
            List[Dict[str, Any]]: The edited list of projects
        """
        self.cli.print_header("Edit Project Details")

        if not current_projects:
            self.cli.print_status("No projects available to edit.", "warning")
            return current_projects
        
        while True:
            for idx, project in enumerate(current_projects, 1):
                print(f"\n{idx}. {project.get('name', 'Unnamed Project')}")
                print(f"   Timeline: {project.get('date_range', 'No Date Range')}")
                print(f"   Duration: {project.get('duration_days', 0)} days")
                role = project.get('user_role', {})
                if role.get('role'):
                    print(f"   Role: {role.get('role')}")
            
            project_choice = self.cli.get_input("\nSelect a project number to edit or type 'done' to finish: \n> ").strip().lower()
            
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
        Edit a single project's details with inline editing capability
        
        Args:
            project (Dict[str, Any]): The project data to edit
            
        Returns:
            Dict[str, Any]: The edited project data
        """
        self.cli.print_status(f"Editing Project: {project.get('name', 'Unnamed Project')}", "info")

        while True:
            print("\n" + "="*80)
            print("CURRENT PROJECT DETAILS:")
            print("="*80)
            print(f"Name: {project.get('name', 'Unknown')}")
            print(f"Date Range: {project.get('date_range', 'N/A')}")
            print(f"Duration: {project.get('duration_days', 0)} days")
            
            # Display role information
            user_role = project.get('user_role', {})
            print(f"\nRole: {user_role.get('role', 'N/A')}")
            print(f"Role Description: {user_role.get('blurb', 'N/A')}")
            
            # Display frameworks
            frameworks = project.get('frameworks', [])
            if frameworks:
                print(f"\nFrameworks ({len(frameworks)} total):")
                for fw in frameworks[:10]:
                    print(f"   • {fw.get('name', 'Unknown')} (used {fw.get('frequency', 0)}x)")
                if len(frameworks) > 10:
                    print(f"   ... and {len(frameworks) - 10} more")
            
            # Display contribution info
            contribution = project.get('contribution', {})
            print(f"\nContribution Level: {contribution.get('level', 'Unknown')}")
            if contribution.get('is_collaborative'):
                print(f"Team Size: {contribution.get('team_size', 1)} contributors")
                print(f"Your Rank: #{contribution.get('rank', 'N/A')} ({contribution.get('percentile', 'N/A')}th percentile)")
            
            print("="*80)
            
            project_choice = self.cli.get_input(
                """\nWhich section would you like to edit? \n\t
                    -'N' Edit Name.\n\t
                    -'D' Edit Date Range.\n\t
                    -'R' Edit Role.\n\t
                    -'B' Edit Role Description.\n\t
                    -'F' Edit Frameworks.\n\t
                    -'C' Edit Contribution Level.\n\t
                    -'Q' Done Editing This Project.\n> """).strip().lower()
            
            try:
                match(project_choice):
                    case 'n':
                        project = self._edit_field(project, 'name', "project name")
                    
                    case 'd':
                        print(f"\nCurrent: {project.get('date_range', 'N/A')}")
                        print("Format: 'MMM YYYY - MMM YYYY' or 'MMM YYYY - Present'")
                        new_value = self._get_edited_text(project.get('date_range', ''))
                        if new_value and '-' in new_value:
                            project['date_range'] = new_value
                            self.cli.print_status("Date range updated.", "success")
                        elif new_value:
                            self.cli.print_status("Invalid format (must contain '-'). No changes made.", "warning")
                    
                    case 'r':
                        if 'user_role' not in project:
                            project['user_role'] = {}
                        current_role = project['user_role'].get('role', '')
                        print(f"\nCurrent Role: {current_role}")
                        new_value = self._get_edited_text(current_role)
                        if new_value:
                            project['user_role']['role'] = new_value
                            self.cli.print_status("Role updated.", "success")
                    
                    case 'b':
                        if 'user_role' not in project:
                            project['user_role'] = {}
                        current_blurb = project['user_role'].get('blurb', '')
                        print(f"\nCurrent Description: {current_blurb}")
                        new_value = self._get_edited_text(current_blurb)
                        if new_value:
                            project['user_role']['blurb'] = new_value
                            self.cli.print_status("Role description updated.", "success")
                    
                    case 'f':
                        project = self._edit_project_frameworks(project)
                    
                    case 'c':
                        project = self._edit_contribution_level(project)
                    
                    case 'q':
                        self.cli.print_status("Finished editing project.", "success")
                        break
                    
                    case _:
                        self.cli.print_status("Invalid choice.", "warning")
                        
            except Exception as e:
                self.cli.print_status(f"Error during project editing: {e}", "error")
        
        return project

    def _edit_field(self, data_dict: Dict[str, Any], field_name: str, display_name: str) -> Dict[str, Any]:
        """
        Generic field editor with inline editing capability
        
        Args:
            data_dict: Dictionary containing the field
            field_name: Key name in dictionary
            display_name: Human-readable name for display           
        Returns:
            Updated dictionary
        """
        current_value = data_dict.get(field_name, '')
        print(f"\nCurrent {display_name}: {current_value}")
        new_value = self._get_edited_text(current_value)
        
        if new_value:
            data_dict[field_name] = new_value
            self.cli.print_status(f"{display_name.capitalize()} updated.", "success")
        
        return data_dict

    def _get_edited_text(self, current_text: str) -> str:
        """
        Get edited text from user with inline editing support
        
        Args:
            current_text: Current text value         
        Returns:
            Edited text or empty string if no change
        """
        print("\nOptions:")
        print("  - Press Enter to keep current text")
        print("  - Type new text to completely replace")
        print(f"\nCurrent text: {current_text}")
        
        user_input = self.cli.get_input("\n> ").strip()
        
        if not user_input:
            # Keep current
            return ""
        else:
            # Complete replacement
            return user_input

    def _edit_project_frameworks(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit frameworks for a project
        
        Args:
            project: Project dictionary           
        Returns:
            Updated project dictionary
        """
        frameworks = project.get('frameworks', [])
        framework_names = [fw.get('name', '') for fw in frameworks]
        framework_names_lower = [name.lower() for name in framework_names]
        
        while True:
            print(f"\nCurrent Frameworks ({len(frameworks)} total):")
            for fw in frameworks[:15]:
                print(f"   • {fw.get('name', 'Unknown')} (frequency: {fw.get('frequency', 0)})")
            if len(frameworks) > 15:
                print(f"   ... and {len(frameworks) - 15} more")
            
            fw_choice = self.cli.get_input("\nType framework name to add, type existing name to remove, or 'done': \n> ").strip()
            
            if fw_choice.lower() == 'done':
                break
            
            if fw_choice.lower() in framework_names_lower:
                # Remove framework
                idx = framework_names_lower.index(fw_choice.lower())
                actual_name = framework_names[idx]
                confirm = self.cli.get_input(f"Remove '{actual_name}'? (y/n): \n> ").strip().lower()
                if confirm == 'y':
                    frameworks.pop(idx)
                    framework_names.pop(idx)
                    framework_names_lower.pop(idx)
                    self.cli.print_status(f"Removed: {actual_name}", "success")
            elif fw_choice:
                # Add new framework
                frameworks.append({'name': fw_choice, 'frequency': 1})
                framework_names.append(fw_choice)
                framework_names_lower.append(fw_choice.lower())
                self.cli.print_status(f"Added: {fw_choice}", "success")
        
        project['frameworks'] = frameworks
        return project

    def _edit_contribution_level(self, project: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit contribution level description
        
        Args:
            project: Project dictionary           
        Returns:
            Updated project dictionary
        """
        contribution = project.get('contribution', {})
        current_level = contribution.get('level', 'Unknown')
        
        print(f"\nCurrent Contribution Level: {current_level}")
        print("\nSuggested levels: Major Contributor, Primary Contributor, Core Contributor, Contributing Member, Minor Contributor")
        
        new_level = self._get_edited_text(current_level)
        if new_level:
            if 'contribution' not in project:
                project['contribution'] = {}
            project['contribution']['level'] = new_level
            self.cli.print_status("Contribution level updated.", "success")
        
        return project

    def _edit_growth_metrics(self, growth_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Placeholder in case growth metrics editing is needed in future. So far it does 
        not seem necessary since metrics are computed from statistics and probably shouldn't be fudged. 
        """

    def _edit_skill_timeline(self, skill_timeline: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit skill timeline section
        
        Args:
            skill_timeline: Skill timeline dictionary         
        Returns:
            Updated skill timeline dictionary
        """
        self.cli.print_header("Edit Skills & Technologies")
        
        while True:
            high_level = skill_timeline.get('high_level_skills', [])
            languages = skill_timeline.get('language_progression', [])
            
            print("\n" + "="*80)
            print(f"High-Level Skills ({len(high_level)} total):")
            print(", ".join(high_level[:20]))
            if len(high_level) > 20:
                print(f"... and {len(high_level) - 20} more")
            
            print(f"\nLanguages ({len(languages)} total):")
            for lang in languages[:10]:
                print(f"   • {lang.get('name', 'Unknown')} - {lang.get('percentage', 0):.1f}%")
            print("="*80)
            
            choice = self.cli.get_input(
                """\nWhat would you like to edit? \n\t
                    -'S' Edit High-Level Skills.\n\t
                    -'L' Edit Languages.\n\t
                    -'Q' Done Editing Skills.\n> """).strip().lower()
            
            try:
                match(choice):
                    case 's':
                        skill_timeline['high_level_skills'] = self._edit_skills_list(high_level)
                    
                    case 'l':
                        skill_timeline['language_progression'] = self._edit_languages_list(languages)
                    
                    case 'q':
                        self.cli.print_status("Finished editing skills.", "success")
                        break
                    
                    case _:
                        self.cli.print_status("Invalid choice.", "warning")
                        
            except Exception as e:
                self.cli.print_status(f"Error editing skills: {e}", "error")
        
        return skill_timeline

    def _edit_skills_list(self, current_skills: List[str]) -> List[str]:
        """Edit list of high-level skills"""
        skills_lower = [s.lower() for s in current_skills]
        
        while True:
            print(f"\nCurrent Skills ({len(current_skills)} total):")
            print(", ".join(current_skills))
            
            skill_input = self.cli.get_input("\nType skill to add/remove, or 'done': \n> ").strip()
            
            if skill_input.lower() == 'done':
                break
            
            if skill_input.lower() in skills_lower:
                idx = skills_lower.index(skill_input.lower())
                actual_skill = current_skills[idx]
                confirm = self.cli.get_input(f"Remove '{actual_skill}'? (y/n): \n> ").strip().lower()
                if confirm == 'y':
                    current_skills.pop(idx)
                    skills_lower.pop(idx)
                    self.cli.print_status(f"Removed: {actual_skill}", "success")
            elif skill_input:
                current_skills.append(skill_input)
                skills_lower.append(skill_input.lower())
                self.cli.print_status(f"Added: {skill_input}", "success")
        
        return current_skills

    def _edit_languages_list(self, current_languages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Edit list of programming languages"""
        lang_names = [lang.get('name', '') for lang in current_languages]
        lang_names_lower = [name.lower() for name in lang_names]
        
        while True:
            print(f"\nCurrent Languages ({len(current_languages)} total):")
            for lang in current_languages[:15]:
                print(f"   • {lang.get('name', 'Unknown')} - {lang.get('percentage', 0):.1f}% ({lang.get('file_count', 0)} files)")
            if len(current_languages) > 15:
                print(f"   ... and {len(current_languages) - 15} more")
            
            lang_input = self.cli.get_input("\nType language to add/remove, or 'done': \n> ").strip()
            
            if lang_input.lower() == 'done':
                break
            
            if lang_input.lower() in lang_names_lower:
                idx = lang_names_lower.index(lang_input.lower())
                actual_name = lang_names[idx]
                confirm = self.cli.get_input(f"Remove '{actual_name}'? (y/n): \n> ").strip().lower()
                if confirm == 'y':
                    current_languages.pop(idx)
                    lang_names.pop(idx)
                    lang_names_lower.pop(idx)
                    self.cli.print_status(f"Removed: {actual_name}", "success")
            elif lang_input:
                current_languages.append({'name': lang_input, 'file_count': 0, 'percentage': 0.0})
                lang_names.append(lang_input)
                lang_names_lower.append(lang_input.lower())
                self.cli.print_status(f"Added: {lang_input}", "success")
        
        return current_languages