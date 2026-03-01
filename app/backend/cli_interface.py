import sys

class CLI:
    def __init__(self):
        pass

    def print_separator(self, char="─", length=60):
        print(char * length)

    def print_header(self, title):
        print("\n" + "=" * 60)
        print(f" {title.upper()}")
        print("=" * 60)

    def print_status(self, message, status="info"):
        symbols = {
            "success": "[+]",
            "error":   "[-]",
            "warning": "[!]",
            "info":    "[*]"
        }
        symbol = symbols.get(status, "→")
        print(f"  {symbol}  {message}")

    def get_input(self, prompt: str) -> str:
        return input(prompt)

    def print_privacy_notice(self):
        print("\n" + "*" * 60)
        print(" PRIVACY NOTICE")
        print("*" * 60)
        print("  Summaries can be generated using an online or local LLM.\n")
        print("  ONLINE  — Sends processed data (no raw code) to an external server.")
        print("            Faster and higher quality, but data leaves your machine.\n")
        print("  LOCAL   — Runs entirely on your device.")
        print("            Fully private, but slower (up to 5 min) and requires RAM.")
        print("─" * 60)

    def display_skill_selection_menu(self, detected_skills: list) -> list:
        MAX_SKILLS = 3
        selected_skills = []
        available_skills = list(detected_skills)

        print("\n" + "=" * 60)
        print(" SKILL HIGHLIGHTING")
        print("=" * 60)
        print("  Choose up to 3 skills to highlight in your summary.\n")
        print("  Commands:")
        print("    <number>      toggle a skill        (e.g. 0 2)")
        print("    a <skill>     add a custom skill    (e.g. a Docker)")
        print("    [Enter]       confirm and continue")
        print("─" * 60)

        while True:
            print(f"\n  Selected ({len(selected_skills)}/{MAX_SKILLS}): ", end="")
            print(", ".join(selected_skills) if selected_skills else "(none)")

            print("\n  Available Skills:")
            for idx, skill in enumerate(available_skills):
                marker = "[X]" if skill in selected_skills else "[ ]"
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
                            self.print_status(f"Added and selected '{add_skill}'.", "success")
                        else:
                            self.print_status(f"Added '{add_skill}' — selection limit reached, toggle to select.", "info")
                continue

            try:
                indices = [int(x) for x in user_input.split()]
                for idx in indices:
                    if 0 <= idx < len(available_skills):
                        skill = available_skills[idx]
                        if skill in selected_skills:
                            selected_skills.remove(skill)
                            self.print_status(f"Deselected '{skill}'.", "info")
                        else:
                            if len(selected_skills) < MAX_SKILLS:
                                selected_skills.append(skill)
                                self.print_status(f"Selected '{skill}'.", "success")
                            else:
                                self.print_status(f"Cannot select '{skill}' — limit of {MAX_SKILLS} reached.", "warning")
                    else:
                        self.print_status(f"No skill at index {idx}.", "error")
            except ValueError:
                self.print_status("Unrecognised input. Enter a number, 'a <skill>', or [Enter] to confirm.", "error")

        return selected_skills

    def display_topic_review_menu(self, topic_keywords):
        self.print_header("Topic Keywords Review")
        print(f"  {'ID':<5}  {'Keywords'}")
        print("  " + "─" * 56)

        for topic in topic_keywords:
            topic_id = topic.get('topic_id', 'N/A')
            keywords = topic.get('keywords', [])
            keywords_str = ', '.join(keywords) if keywords else '(none)'
            print(f"  {topic_id:<5}  {keywords_str}")

        print("  " + "─" * 56)
        print("\n  These keywords were extracted from your files to guide the LLM.\n")

        while True:
            choice = self.get_input("  [E]dit,  [I]nfo,  or [Enter] to proceed\n> ").strip().lower()
            if choice == '':
                return 'P'
            elif choice == 'e':
                return 'E'
            elif choice == 'i':
                print("\n" + "=" * 60)
                print(" TOPIC EXTRACTION INFO")
                print("=" * 60)
                print("  Topics are themes identified across your files.\n")
                print("  WHY IT MATTERS:")
                print("    The LLM uses these topics to understand what your files are about.")
                print("    More accurate topics lead to better, more relevant summaries.")
                print("─" * 60)
            else:
                self.print_status("Unrecognised input. Press [Enter] to proceed, 'e' to edit, or 'i' for info.", "warning")

    def get_topic_edit_action(self, topic_keywords):
        valid_ids = {topic['topic_id'] for topic in topic_keywords}

        topic_id_input = self.get_input("\n  Enter the Topic ID to edit:\n> ").strip()

        try:
            topic_id = int(topic_id_input)
        except ValueError:
            self.print_status(f"'{topic_id_input}' is not a valid ID.", "error")
            return (None, None, None)

        if topic_id not in valid_ids:
            self.print_status(f"Topic ID {topic_id} not found.  Valid IDs: {sorted(valid_ids)}", "error")
            return (None, None, None)

        while True:
            action = self.get_input("\n  [R]emove topic,  [M]odify keywords,  or [Enter] to cancel\n> ").strip().lower()
            if action == '':
                return (None, None, None)
            elif action in ['r', 'm']:
                break
            self.print_status("Unrecognised input. Enter 'r' to remove, 'm' to modify, or [Enter] to cancel.", "warning")

        if action == 'r':
            return (topic_id, 'remove', None)
        else:
            new_keywords_input = self.get_input("\n  Enter new keywords, comma-separated:\n> ").strip()
            new_keywords = [kw.strip() for kw in new_keywords_input.split(',') if kw.strip()]
            return (topic_id, 'replace', new_keywords)

    def display_topic_edit_details(self, topic_dict):
        topic_id = topic_dict.get('topic_id', 'N/A')
        keywords = topic_dict.get('keywords', [])

        self.print_header(f"Editing Topic {topic_id}")
        print("  Keywords:")
        print("  " + "─" * 40)

        if keywords:
            for idx, keyword in enumerate(keywords):
                print(f"    {idx}:  {keyword}")
        else:
            print("    (none)")

        print("  " + "─" * 40)
        print("\n  Commands:")
        print("    <#>       replace keyword at index    (e.g. 0)")
        print("    r <#>     remove keyword at index     (e.g. r 2)")
        print("    a         add a new keyword")
        print("    all       replace all keywords")
        print("    d         delete this topic entirely")
        print("    b         save and go back")
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
                self.print_status("Invalid index — enter a number after 'r' (e.g. r 2).", "error")
                return ('invalid', None)
        else:
            try:
                index = int(user_input)
                return ('replace_one', index)
            except ValueError:
                self.print_status(f"Unrecognised command: '{user_input}'.  Valid commands: #, r #, a, all, d, b.", "error")
                return ('invalid', None)