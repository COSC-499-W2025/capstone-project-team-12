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
        print("  - 'a <Skill>' or '+ <Skill>' to add a custom skill")
        print("  - [Enter] to finish and proceed")
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
            
            # Empty input (Enter) proceeds
            if not user_input:
                break
            
            # Check for add command: 'a <Skill>', '+ <Skill>', or 'add <Skill>'
            add_skill = None
            if user_input.lower().startswith("a "):
                add_skill = user_input[2:].strip()
            elif user_input.startswith("+ "):
                add_skill = user_input[2:].strip()
            elif user_input.lower().startswith("add "):
                add_skill = user_input[4:].strip()
            
            if add_skill is not None:
                if add_skill:
                    if add_skill in available_skills:
                        print(f"Skill '{add_skill}' already exists in the list.")
                    else:
                        available_skills.append(add_skill)
                        # Auto-select if under limit
                        if len(selected_skills) < MAX_SKILLS:
                            selected_skills.append(add_skill)
                            print(f"Added and selected: {add_skill}")
                        else:
                            print(f"Added: {add_skill} (selection limit reached, toggle to select)")
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
                print("Invalid input. Enter numbers, 'a <Skill>', or [Enter] to finish.")
        
        return selected_skills
    def display_topic_review_menu(self, topic_keywords):
        """
        Displays the current list of topics in a table format and prompts user to proceed or edit
        
        Args:
            topic_keywords: List of dicts with 'topic_id' and 'keywords' keys.
            
        Returns:
            str: User's choice - 'P' for Proceed or 'E' for Edit.
        """
        self.print_header("Topic Keywords Review")
        print(f"{'ID':<5} | {'Keywords'}")
        print("-" * 60)
        
        for topic in topic_keywords:
            topic_id = topic.get('topic_id', 'N/A')
            keywords = topic.get('keywords', [])
            keywords_str = ', '.join(keywords) if keywords else '(no keywords)'
            print(f"{topic_id:<5} | {keywords_str}")
        
        print("-" * 60)
        
        print("\nHere are the extracted keywords.")

        while True:
            choice = self.get_input("[E]dit, [I]nfo, or [Enter] to Proceed \n> ").strip().lower()
            if choice == '':
                return 'P'
            elif choice == 'e':
                return 'E'
            elif choice == 'i':
                print("\n" + "=" * 60)
                print(" TOPIC EXTRACTION INFO")
                print("=" * 60)
                print("WHAT THIS IS:")
                print("  These keywords are extracted from your files to identify common themes.")
                print("\nWHY THIS MATTERS:")
                print("  - Context: These topics guide the LLM on what the files are about.")
                print("  - Accuracy: Better topics mean better, more relevant summaries.")
                print("-" * 60)
            else:
                self.print_status("Invalid choice. Press [Enter] to Proceed, 'e' to Edit, or 'i' for Info.", "warning")

    def get_topic_edit_action(self, topic_keywords):
        """
        Prompts user for topic editing action (remove or modify).
        
        Args:
            topic_keywords: List of dicts with 'topic_id' and 'keywords' keys.
            
        Returns:
            tuple: (topic_id, action, new_keywords) where:
                - topic_id (int): The ID of the topic to modify
                - action (str): 'remove' or 'replace'
                - new_keywords (list or None): New keywords list if action is 'replace', None otherwise
            Returns (None, None, None) if the topic ID is invalid.
        """
        #get valid topic IDs
        valid_ids = {topic['topic_id'] for topic in topic_keywords}
        
        #ask for Topic ID
        topic_id_input = self.get_input("\nEnter the Topic ID you want to change: \n> ").strip()
        
        try:
            topic_id = int(topic_id_input)
        except ValueError:
            self.print_status(f"Invalid input. '{topic_id_input}' is not a valid number.", "error")
            return (None, None, None)
        
        if topic_id not in valid_ids:
            self.print_status(f"Topic ID {topic_id} does not exist. Valid IDs: {sorted(valid_ids)}", "error")
            return (None, None, None)
        
        #ask for action
        while True:
            action = self.get_input("\n[R]emove, [M]odify, or [Enter] to cancel \n> ").strip().lower()
            #empty input (Enter) cancels/goes back
            if action == '':
                return (None, None, None)
            elif action in ['r', 'm']:
                break
            self.print_status("Invalid choice. 'r' to Remove, 'm' to Modify, or [Enter] to cancel.", "warning")
        
        if action == 'r':
            return (topic_id, 'remove', None)
        else:  #action == 'm'
            new_keywords_input = self.get_input("\nEnter the new comma-separated keywords: \n> ").strip()
            new_keywords = [kw.strip() for kw in new_keywords_input.split(',') if kw.strip()]
            return (topic_id, 'replace', new_keywords)

    def display_topic_edit_details(self, topic_dict):
        """
        Displays the keywords for a given topic with their list indices and a menu of edit options.
        
        Args:
            topic_dict: A dict with 'topic_id' and 'keywords' keys.
        """
        topic_id = topic_dict.get('topic_id', 'N/A')
        keywords = topic_dict.get('keywords', [])
        
        self.print_header(f"Editing Topic {topic_id}")
        print("Current Keywords:")
        print("-" * 40)
        
        if keywords:
            for idx, keyword in enumerate(keywords):
                print(f"  {idx}: {keyword}")
        else:
            print("  (no keywords)")
        
        print("-" * 40)
        print("\nEdit Options:")
        print("  #         : Replace specific keyword (e.g., '0' to replace first keyword)")
        print("  r #       : Remove specific keyword (e.g., 'r 2' to remove third keyword)")
        print("  a         : Add a new keyword")
        print("  all       : Rewrite all keywords")
        print("  d         : Delete this entire topic")
        print("  b         : Confirm and go back to the main list")
        print("-" * 40)

    def get_granular_input(self):
        """
        Captures the user's granular edit choice for a topic.
        
        Returns:
            tuple: (action_type, index_or_none) where:
                - action_type (str): 'replace_one', 'remove_one', 'add', 'all', 'del', 'back', or 'invalid'
                - index_or_none (int or None): The keyword index for 'replace_one' or 'remove_one' actions
        """
        user_input = self.get_input("\nEnter your choice: \n> ").strip().lower()
        
        #snow supports single letter or word
        if user_input == 'b' or user_input == 'back':  #
            return ('back', None)
        elif user_input == 'd' or user_input == 'del':  # delete (legacy support)
            return ('del', None)
        elif user_input == 'all':
            return ('all', None)
        elif user_input == 'a' or user_input == 'add':  # add (legacy support)
            return ('add', None)
        elif user_input.startswith('r ') or user_input.startswith('rm '):  # remove specific (legacy support)
            # Handle both 'r #' and 'rm #'
            try:
                if user_input.startswith('rm '):
                    index = int(user_input[3:].strip())
                else:
                    index = int(user_input[2:].strip())
                return ('remove_one', index)
            except ValueError:
                self.print_status("Invalid index. Please enter a valid number after 'r'.", "error")
                return ('invalid', None)
        else:
            # Try to parse as a number for replace
            try:
                index = int(user_input)
                return ('replace_one', index)
            except ValueError:
                self.print_status(f"Invalid command: '{user_input}'. Use #, r #, a, d, all, or b.", "error")
                return ('invalid', None)
