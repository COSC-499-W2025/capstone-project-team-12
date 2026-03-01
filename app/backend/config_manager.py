import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    def __init__(self, config_dir: str = "configs", config_file: str = "user_prefs.json"):
        self.config_dir = Path(config_dir)
        self.config_path = self.config_dir / config_file
        self.preferences = self._load_prefs()

    def _load_prefs(self) -> Dict[str, Any]:
        """Load preferences from JSON, or return empty dict if not found."""
        if not self.config_path.exists():
            return {}
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def save_prefs(self, new_prefs: Dict[str, Any]) -> None:
        """Update internal state and write to JSON file."""
        self.preferences.update(new_prefs)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.preferences, f, indent=4)
        except IOError as e:
            print(f"[!] Warning: Could not save preferences: {e}")

    def get_consent(self, key: str, prompt_text: str, component: str = "this feature", default: bool = True) -> bool:
        """Ask for consent, acknowledging previous choices with specific component context."""
        previous_val = self.preferences.get(key)

        # SCENARIO 1: No history (first run)
        if previous_val is None:
            prompt_display = f"{prompt_text} ({'Y/n' if default else 'y/N'}) \n> "

            while True:
                user_input = input(prompt_display).strip().lower()

                if user_input == "" and default is not None:
                    self.save_prefs({key: default})
                    return default
                elif user_input in ("y", "yes"):
                    self.save_prefs({key: True})
                    return True
                elif user_input in ("n", "no"):
                    self.save_prefs({key: False})
                    return False
                print("[!] Unrecognised input. Please enter 'y' or 'n'.")

        # SCENARIO 2: Previously consented
        elif previous_val is True:
            print(f"\n[*] You previously consented to {component}.")
            confirm_prompt = f"    Do you still consent? ({'Y/n' if default else 'y/N'}) \n> "
            confirm = input(confirm_prompt).strip().lower()

            if confirm == "" and default is not None:
                if not default:
                    print("[-] Consent revoked.")
                    self.save_prefs({key: False})
                return default
            elif confirm in ("n", "no"):
                print("[-] Consent revoked.")
                self.save_prefs({key: False})
                return False
            elif confirm in ("y", "yes"):
                return True
            else:
                print("[!] Unrecognised input. Keeping previous consent.")
                return previous_val

        # SCENARIO 3: Previously denied
        elif previous_val is False:
            print(f"\n[*] You previously denied consent for {component}.")
            confirm_prompt = f"    Do you want to grant consent now? ({'Y/n' if default else 'y/N'}) \n> "
            change = input(confirm_prompt).strip().lower()

            if change in ("y", "yes"):
                print("[+] Consent granted.")
                self.save_prefs({key: True})
                return True
            elif change == "" and default is not None:
                if default:
                    print("[+] Consent granted.")
                    self.save_prefs({key: True})
                    return True
                else:
                    print("[-] Consent remains revoked.")
                    return False
            elif change in ("n", "no"):
                print("[-] Consent remains revoked.")
                return False
            else:
                print("[!] Unrecognised input. Keeping previous consent.")
                return previous_val