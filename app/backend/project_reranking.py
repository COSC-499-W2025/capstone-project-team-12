def normalize(values):
    min_val, max_val = min(values), max(values)
    if max_val - min_val == 0:
        return [0.5] * len(values)
    return [(v - min_val) / (max_val - min_val) for v in values]

# Compute weighted score
def compute_scores(projects, weights):
    commits_norm = normalize([len(p.get('user_commits', [])) for p in projects])
    lines_norm = normalize([p.get('statistics', {}).get('user_lines_added', 0) for p in projects])
    duration_norm = normalize([p.get('dates', {}).get('duration_days', 0) for p in projects])
    
    for i, p in enumerate(projects):
        p["importance_score"] = (
            commits_norm[i] * weights["commits"] +
            lines_norm[i] * weights["lines_added"] +
            duration_norm[i] * weights["duration"]
        )
    return sorted(projects, key=lambda x: x["importance_score"], reverse=True)


def display_ranking(projects):
    for idx, p in enumerate(projects, 1):
        score = p.get('importance_score')
        score_str = f"{score:.2f}" if isinstance(score, (int, float)) else str(score or "N/A")
        print(f"{idx}) {p['repository_name']} (Score: {score_str})")
    print()


def assign_importance_ranks(projects):
    for idx, project in enumerate(projects, start=1):
        project["importance_rank"] = idx
    return projects


# Swap-based manual reordering
def manual_reorder(projects):
    while True:
        print("\nCurrent Project Rankings:")
        display_ranking(projects)
        swap_input = input("> Enter two numbers to swap (e.g., 2 4) or 'done' to finish: ").strip()
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
        "3": {"name": "Project duration focused", "commits": 0.2, "lines_added": 0.2, "duration": 0.6},
        "4": {"name": "Code additions focused", "commits": 0.2, "lines_added": 0.6, "duration": 0.2},
    }

    display_ranking(projects)
    
    print("Would you like to:")
    print("1) Adjust metric weights (data-driven)")
    print("2) Manually reorder projects")
    print("3) Keep current ranking")
    
    choice = input("\n> Choice: ").strip()
    
    if choice == "1":
        print("\nSelect a ranking preset:")
        for key, preset in weight_presets.items():
            print(f"{key}) {preset['name']}")
        preset_choice = input("\n> Choice: ").strip()
        if preset_choice in weight_presets:
            projects_sorted = compute_scores(projects, weight_presets[preset_choice])
            assign_importance_ranks(projects_sorted)
            print(f"\nProjects ranked using '{weight_presets[preset_choice]['name']}' preset:")
            display_ranking(projects_sorted)
            return projects_sorted
        else:
            print("Invalid preset choice. Keeping current ranking.")
            display_ranking(projects)
            return projects
    
    elif choice == "2":
        manual_reorder(projects)
        assign_importance_ranks(projects)
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