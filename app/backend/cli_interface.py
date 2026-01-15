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
        
        while True:
            choice = self.get_input("\nHere are the extracted keywords. Do you want to Proceed [P] or Edit [E]? \n> ").strip().upper()
            if choice in ['P', 'E']:
                return choice
            self.print_status("Invalid choice. Please enter 'P' to Proceed or 'E' to Edit.", "warning")

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
            action = self.get_input("\nDo you want to remove[R] this topic or Modify/Replace[M] it? \n> ").strip().upper()
            if action in ['R', 'M']:
                break
            self.print_status("Invalid choice. Please enter 'R' to Remove or 'M' to Modify.", "warning")
        
        if action == 'R':
            return (topic_id, 'remove', None)
        else:  #action == 'M'
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
        print("  Enter #   : Replace specific keyword (e.g., '0' to replace first keyword)")
        print("  rm #      : Remove specific keyword (e.g., 'rm 2' to remove third keyword)")
        print("  add       : Add a new keyword")
        print("  all       : Rewrite all keywords")
        print("  del       : Delete this entire topic")
        print("  back      : Confirm and go back to the main list")
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
        
        if user_input == 'back':
            return ('back', None)
        elif user_input == 'del':
            return ('del', None)
        elif user_input == 'all':
            return ('all', None)
        elif user_input == 'add':
            return ('add', None)
        elif user_input.startswith('rm '):
            # Remove specific keyword
            try:
                index = int(user_input[3:].strip())
                return ('remove_one', index)
            except ValueError:
                self.print_status("Invalid index. Please enter a valid number after 'rm'.", "error")
                return ('invalid', None)
        else:
            # Try to parse as a number for replace
            try:
                index = int(user_input)
                return ('replace_one', index)
            except ValueError:
                self.print_status(f"Invalid command: '{user_input}'. Please try again.", "error")
                return ('invalid', None)