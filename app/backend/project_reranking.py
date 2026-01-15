def display_ranking(projects):
    print("\nCurrent project ranking:")
    for idx, p in enumerate(projects, 1):
        print(f"{idx}) {p['repository_name']} (Score: {p.get('importance_score', 'N/A'):.2f})")
    print()

# Swap based manual reordering
def manual_reorder(projects):
    while True:
        display_ranking(projects)
        swap_input = input("Enter two numbers to swap (e.g., 2 4) or 'done' to finish: ").strip()
        if swap_input.lower() == "done":
            break
        try:
            a, b = map(int, swap_input.split())
            if 1 <= a <= len(projects) and 1 <= b <= len(projects):
                projects[a-1], projects[b-1] = projects[b-1], projects[a-1]
            else:
                print("Invalid numbers. Try again.")
        except:
            print("Invalid input. Enter two numbers separated by a space.")

def rerank_projects(projects):
    # Define preset weight configurations
    weight_presets = {
        "1": {"name": "Balanced", "commits": 0.33, "lines_added": 0.33, "duration": 0.34},
        "2": {"name": "Commit-heavy", "commits": 0.6, "lines_added": 0.2, "duration": 0.2},
        "3": {"name": "Longevity-focused", "commits": 0.2, "lines_added": 0.2, "duration": 0.6},
        "4": {"name": "Lines-added-heavy", "commits": 0.2, "lines_added": 0.6, "duration": 0.2},
    }

    display_ranking(projects)
    
    print("Would you like to:")
    print("1) Adjust metric weights (data-driven)")
    print("2) Manually reorder projects")
    print("3) Keep current ranking")
    
    choice = input("Choice: ").strip()
    
    if choice == "1":
        print("\nSelect a ranking preset:")
        for key, preset in weight_presets.items():
            print(f"{key}) {preset['name']}")
        preset_choice = input("Choice: ").strip()
        if preset_choice in weight_presets:
            projects_sorted = compute_scores(projects, weight_presets[preset_choice])
            display_ranking(projects_sorted)
            return projects_sorted
        else:
            print("Invalid preset choice. Keeping current ranking.")
            display_ranking(projects)
            return projects
    
    elif choice == "2":
        manual_reorder(projects)
        print("\nFinal manual ranking:")
        display_ranking(projects)
        return projects
    
    elif choice == "3":
        print("\nKeeping current ranking:")
        display_ranking(projects)
        return projects
    
    else:
        print("Invalid choice. Exiting.")
        return projects