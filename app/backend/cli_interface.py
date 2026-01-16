import sys

class CLI:
    def __init__(self):
        pass

    def print_separator(self, char="=", length=60):
        print(char * length)

    def print_header(self, title):
        print("\n" + "=" * 60)
        print(f" {title.upper()}")
        print("=" * 60)

    def print_status(self, message, status="info"):
        symbols = {"success": "[+]", "error": "[-]", "warning": "[!]", "info": "[*]"}
        symbol = symbols.get(status, "[*]")
        print(f"{symbol} {message}")

    def get_input(self, prompt: str) -> str: #for testing we swap to get_input so that it doesnt actually ask
        return input(prompt)

    def print_privacy_notice(self):
        print("\n" + "*" * 60)
        print(" PRIVACY NOTICE")
        print("*" * 60)
        print("The application can use an Online LLM to generate summaries.")
        print("1. ONLINE: Sends processed vectors (No raw code) to external server.")
        print("   - Pros: Faster, higher quality summary.")
        print("   - Cons: Data leaves your machine.")
        print("2. LOCAL: Runs entirely on your device.")
        print("   - Pros: 100% Private.")
        print("   - Cons: Slower (up to 5 mins per attempt), requires RAM.")
        print("-" * 60)

    def display_skill_selection_menu(self, detected_skills: list) -> list:
        """
        Display a menu for the user to select technical skills to highlight in the summary.
        
        Args:
            detected_skills: List of detected skill names from metadata analysis
            
        Returns:
            List of selected skill names (max 3)
        """
        MAX_SKILLS = 3
        selected_skills = []
        available_skills = list(detected_skills)  # Make a copy to allow adding custom skills
        
        print("\n" + "=" * 60)
        print(" SKILL HIGHLIGHTING")
        print("=" * 60)
        print("Select up to 3 technical skills to emphasize in your summary.")
        print("Commands:")
        print("  - Enter numbers (e.g., '0 2') to toggle skill selection")
        print("  - Type 'add <Skill Name>' to add a custom skill")
        print("  - Type 'P' to proceed with current selection")
        print("-" * 60)
        
        while True:
            # Display current selection
            print(f"\nCurrent Selection ({len(selected_skills)}/{MAX_SKILLS}): ", end="")
            if selected_skills:
                print(", ".join(selected_skills))
            else:
                print("(none)")
            
            # Display available skills with indices
            print("\nDetected Skills:")
            for idx, skill in enumerate(available_skills):
                marker = "[X]" if skill in selected_skills else "[ ]"
                print(f"  {idx}. {marker} {skill}")
            
            user_input = self.get_input("\n> ").strip()
            
            if not user_input:
                continue
            
            # Check for proceed command
            if user_input.upper() == "P":
                break
            
            # Check for add command
            if user_input.lower().startswith("add "):
                custom_skill = user_input[4:].strip()
                if custom_skill:
                    if custom_skill in available_skills:
                        print(f"Skill '{custom_skill}' already exists in the list.")
                    else:
                        available_skills.append(custom_skill)
                        # Auto-select if under limit
                        if len(selected_skills) < MAX_SKILLS:
                            selected_skills.append(custom_skill)
                            print(f"Added and selected: {custom_skill}")
                        else:
                            print(f"Added: {custom_skill} (selection limit reached, toggle to select)")
                continue
            
            # Try to parse as numbers for toggling
            try:
                indices = [int(x) for x in user_input.split()]
                for idx in indices:
                    if 0 <= idx < len(available_skills):
                        skill = available_skills[idx]
                        if skill in selected_skills:
                            selected_skills.remove(skill)
                            print(f"Deselected: {skill}")
                        else:
                            if len(selected_skills) < MAX_SKILLS:
                                selected_skills.append(skill)
                                print(f"Selected: {skill}")
                            else:
                                print(f"Cannot select '{skill}': Maximum {MAX_SKILLS} skills allowed.")
                    else:
                        print(f"Invalid index: {idx}")
            except ValueError:
                print("Invalid input. Enter numbers, 'add <Skill>', or 'P' to proceed.")
        
        return selected_skills