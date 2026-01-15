def ask_confirm_all(projects):
    print(f"\nYou have {len(projects)} projects selected for analysis:")
    for p in projects:
        print(f"- {p['repository_name']}")

    response = input(
        "\nDo you want to proceed with analysis for all of these? (Y/n): "
    ).strip().lower()

    return response in ("", "y", "yes")


def ask_project_selection(projects):
    print("\nSelect which projects to proceed with:")
    for i, p in enumerate(projects, start=1):
        print(f"{i}. {p['repository_name']}")

    print("\nType the numbers separated by spaces (e.g., 1 3 4):")

    while True:
        try:
            choices = input("> ").strip().split()
            if not choices:
                raise ValueError("No projects selected.")

            indices = sorted(set(int(c) for c in choices))

            if any(i < 1 or i > len(projects) for i in indices):
                raise ValueError("One or more selections are out of range.")

            return [projects[i - 1] for i in indices]

        except ValueError as e:
            print(f"❌ {e} Try again.")


def choose_projects_for_analysis(projects):
    proceed_all = ask_confirm_all(projects)

    if proceed_all:
        print("\nProceeding with all projects.\n")
        return projects

    selected = ask_project_selection(projects)

    print("\nProceeding with analysis for:")
    for p in selected:
        print(f"- {p['repository_name']}")

    return selected
