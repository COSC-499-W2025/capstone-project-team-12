import sys

class CLI:
    def __init__(self):
        pass

    def print_separator(self, char="─", length=60):
        print(char * length)

    def print_header(self, title):
        print("\n" + "┌" + "─" * 58 + "┐")
        print(f"│  {title.upper():<56}│")
        print("└" + "─" * 58 + "┘")

    def print_status(self, message, status="info"):
        symbols = {
            "success": "✓",
            "error":   "✗",
            "warning": "⚠",
            "info":    "→"
        }
        symbol = symbols.get(status, "→")
        print(f"  {symbol}  {message}")

    def get_input(self, prompt: str) -> str:
        return input(prompt)

    def print_privacy_notice(self):
        print("\n" + "┌" + "─" * 58 + "┐")
        print("│  PRIVACY NOTICE" + " " * 42 + "│")
        print("└" + "─" * 58 + "┘")
        print("  This app can use an online LLM to generate summaries.\n")
        print("  ONLINE  — Sends processed vectors (no raw code) externally.")
        print("            Faster, higher quality output.\n")
        print("  LOCAL   — Runs entirely on your device.")
        print("            100% private. Slower (up to 5 min), requires RAM.")
        print("─" * 60)

    def display_skill_selection_menu(self, detected_skills: list) -> list:
        MAX_SKILLS = 3
        selected_skills = []
        available_skills = list(detected_skills)

        print("\n" + "┌" + "─" * 58 + "┐")
        print("│  SKILL HIGHLIGHTING" + " " * 38 + "│")
        print("└" + "─" * 58 + "┘")
        print("  Select up to 3 skills to emphasise in your summary.\n")
        print("  Commands:")
        print("    <number>      toggle a skill  (e.g. 0 2)")
        print("    a <Skill>     add a custom skill")
        print("    [Enter]       confirm and continue")
        print("─" * 60)

        while True:
            print(f"\n  Selected ({len(selected_skills)}/{MAX_SKILLS}): ", end="")
            print(", ".join(selected_skills) if selected_skills else "(none)")

            print("\n  Detected Skills:")
            for idx, skill in enumerate(available_skills):
                marker = "[✓]" if skill in selected_skills else "[ ]"
                print(f"    {idx}.  {marker}  {skill}")

            user_input = self.get_input("\n> ").strip()

            if not user_input:
                break

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
                        self.print_status(f"'{add_skill}' is already in the list.", "warning")
                    else:
                        available_skills.append(add_skill)
                        if len(selected_skills) < MAX_SKILLS:
                            selected_skills.append(add_skill)
                            self.print_status(f"Added and selected: {add_skill}", "success")
                        else:
                            self.print_status(f"Added: {add_skill}  (limit reached — toggle to select)", "info")
                continue

            try:
                indices = [int(x) for x in user_input.split()]
                for idx in indices:
                    if 0 <= idx < len(available_skills):
                        skill = available_skills[idx]
                        if skill in selected_skills:
                            selected_skills.remove(skill)
                            self.print_status(f"Deselected: {skill}", "info")
                        else:
                            if len(selected_skills) < MAX_SKILLS:
                                selected_skills.append(skill)
                                self.print_status(f"Selected: {skill}", "success")
                            else:
                                self.print_status(f"Cannot select '{skill}' — maximum {MAX_SKILLS} skills allowed.", "warning")
                    else:
                        self.print_status(f"Invalid index: {idx}", "error")
            except ValueError:
                self.print_status("Invalid input. Enter numbers, 'a <Skill>', or [Enter] to finish.", "error")

        return selected_skills

    def display_topic_review_menu(self, topic_keywords):
        self.print_header("Topic Keywords Review")
        print(f"  {'ID':<5}  {'Keywords'}")
        print("  " + "─" * 56)

        for topic in topic_keywords:
            topic_id = topic.get('topic_id', 'N/A')
            keywords = topic.get('keywords', [])
            keywords_str = ', '.join(keywords) if keywords else '(no keywords)'
            print(f"  {topic_id:<5}  {keywords_str}")

        print("  " + "─" * 56)
        print("\n  These are the keywords extracted from your files.\n")

        while True:
            choice = self.get_input("  [E]dit,  [I]nfo,  or [Enter] to proceed\n> ").strip().lower()
            if choice == '':
                return 'P'
            elif choice == 'e':
                return 'E'
            elif choice == 'i':
                print("\n" + "┌" + "─" * 58 + "┐")
                print("│  TOPIC EXTRACTION INFO" + " " * 35 + "│")
                print("└" + "─" * 58 + "┘")
                print("  Keywords are extracted from your files to identify themes.\n")
                print("  WHY IT MATTERS:")
                print("    These topics guide the LLM on what your files are about.")
                print("    Better topics produce more accurate, relevant summaries.")
                print("─" * 60)
            else:
                self.print_status("Invalid choice. Press [Enter] to proceed, 'e' to edit, 'i' for info.", "warning")

    def get_topic_edit_action(self, topic_keywords):
        valid_ids = {topic['topic_id'] for topic in topic_keywords}

        topic_id_input = self.get_input("\n  Enter the Topic ID to change:\n> ").strip()

        try:
            topic_id = int(topic_id_input)
        except ValueError:
            self.print_status(f"'{topic_id_input}' is not a valid number.", "error")
            return (None, None, None)

        if topic_id not in valid_ids:
            self.print_status(f"Topic ID {topic_id} not found.  Valid IDs: {sorted(valid_ids)}", "error")
            return (None, None, None)

        while True:
            action = self.get_input("\n  [R]emove,  [M]odify,  or [Enter] to cancel\n> ").strip().lower()
            if action == '':
                return (None, None, None)
            elif action in ['r', 'm']:
                break
            self.print_status("Invalid choice. 'r' to remove, 'm' to modify, or [Enter] to cancel.", "warning")

        if action == 'r':
            return (topic_id, 'remove', None)
        else:
            new_keywords_input = self.get_input("\n  Enter new comma-separated keywords:\n> ").strip()
            new_keywords = [kw.strip() for kw in new_keywords_input.split(',') if kw.strip()]
            return (topic_id, 'replace', new_keywords)

    def display_topic_edit_details(self, topic_dict):
        topic_id = topic_dict.get('topic_id', 'N/A')
        keywords = topic_dict.get('keywords', [])

        self.print_header(f"Editing Topic {topic_id}")
        print("  Current Keywords:")
        print("  " + "─" * 40)

        if keywords:
            for idx, keyword in enumerate(keywords):
                print(f"    {idx}:  {keyword}")
        else:
            print("    (no keywords)")

        print("  " + "─" * 40)
        print("\n  Commands:")
        print("    <#>       replace a keyword     (e.g. 0)")
        print("    r <#>     remove a keyword      (e.g. r 2)")
        print("    a         add a new keyword")
        print("    all       rewrite all keywords")
        print("    d         delete this entire topic")
        print("    b         confirm and go back")
        print("  " + "─" * 40)

    def get_granular_input(self):
        user_input = self.get_input("\n> ").strip().lower()

        if user_input in ('b', 'back'):
            return ('back', None)
        elif user_input in ('d', 'del'):
            return ('del', None)
        elif user_input == 'all':
            return ('all', None)
        elif user_input in ('a', 'add'):
            return ('add', None)
        elif user_input.startswith('r ') or user_input.startswith('rm '):
            try:
                index = int(user_input[3:].strip() if user_input.startswith('rm ') else user_input[2:].strip())
                return ('remove_one', index)
            except ValueError:
                self.print_status("Invalid index — enter a number after 'r'.", "error")
                return ('invalid', None)
        else:
            try:
                index = int(user_input)
                return ('replace_one', index)
            except ValueError:
                self.print_status(f"Unknown command: '{user_input}'.  Use #, r #, a, d, all, or b.", "error")
                return ('invalid', None)