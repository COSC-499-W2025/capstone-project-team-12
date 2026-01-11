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