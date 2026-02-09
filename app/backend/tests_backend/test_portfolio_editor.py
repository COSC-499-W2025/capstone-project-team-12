import pytest
from portfolio_editor import PortfolioEditor


class TestPortfolioEditor:

    @pytest.fixture
    def mock_cli(self, mocker):
        """Mock CLI interface used by PortfolioEditor"""
        cli = mocker.Mock()
        cli.get_input = mocker.Mock()
        cli.print_header = mocker.Mock()
        cli.print_status = mocker.Mock()
        return cli

    @pytest.fixture
    def sample_portfolio(self):
        """Sample portfolio data for testing"""
        return {
            "projects_detail": [
                {
                    "name": "Galaga Clone",
                    "date_range": "Jan 2024 - Mar 2024",
                    "duration_days": 60,
                    "user_role": {
                        "role": "Developer",
                        "blurb": "Built gameplay and scoring systems."
                    },
                    "frameworks": [
                        {"name": "Unity", "frequency": 50},
                        {"name": "C#", "frequency": 120},
                        {"name": "Git", "frequency": 30},
                    ],
                    "contribution": {
                        "level": "Primary Contributor",
                        "is_collaborative": True,
                        "team_size": 3,
                        "rank": 1,
                        "percentile": 95
                    }
                }
            ],
            "skill_timeline": {
                "high_level_skills": ["Python", "React", "SQL"],
                "language_progression": [
                    {"name": "Python", "file_count": 20, "percentage": 50.0},
                    {"name": "JavaScript", "file_count": 10, "percentage": 25.0},
                ]
            }
        }

 
    # _get_edited_text
    def test_get_edited_text_keep_current(self, mock_cli):
        editor = PortfolioEditor(mock_cli)
        mock_cli.get_input.return_value = ""
        assert editor._get_edited_text("Current") == ""

    def test_get_edited_text_replace(self, mock_cli):
        editor = PortfolioEditor(mock_cli)
        mock_cli.get_input.return_value = "New Value"
        assert editor._get_edited_text("Current") == "New Value"

    def test_get_edited_text_strips_whitespace(self, mock_cli):
        editor = PortfolioEditor(mock_cli)
        mock_cli.get_input.return_value = "   New Value   "
        assert editor._get_edited_text("Current") == "New Value"

  
    # _edit_field
    def test_edit_field_updates_when_non_empty(self, mock_cli):
        editor = PortfolioEditor(mock_cli)
        data = {"name": "Old"}
        mock_cli.get_input.return_value = "New"
        result = editor._edit_field(data, "name", "project name")
        assert result["name"] == "New"

    def test_edit_field_no_change_when_empty(self, mock_cli):
        editor = PortfolioEditor(mock_cli)
        data = {"name": "Old"}
        mock_cli.get_input.return_value = ""
        result = editor._edit_field(data, "name", "project name")
        assert result["name"] == "Old"

    def test_edit_field_missing_key_adds_key(self, mock_cli):
        editor = PortfolioEditor(mock_cli)
        data = {}
        mock_cli.get_input.return_value = "Value"
        result = editor._edit_field(data, "name", "project name")
        assert result["name"] == "Value"


    # _edit_projects

    def test_edit_projects_empty_list(self, mock_cli):
        editor = PortfolioEditor(mock_cli)
        result = editor._edit_projects([])
        assert result == []
        mock_cli.print_status.assert_called_with("No projects available to edit.", "warning")

    def test_edit_projects_invalid_selection(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        projects = sample_portfolio["projects_detail"].copy()

        # invalid index then done
        mock_cli.get_input.side_effect = ["99", "done"]
        result = editor._edit_projects(projects)
        assert result[0]["name"] == "Galaga Clone"

    def test_edit_projects_non_numeric_selection(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        projects = sample_portfolio["projects_detail"].copy()

        mock_cli.get_input.side_effect = ["abc", "done"]
        result = editor._edit_projects(projects)
        assert result[0]["name"] == "Galaga Clone"

    def test_edit_projects_valid_selection_edits_project(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        projects = sample_portfolio["projects_detail"].copy()

        # Select project 1, edit name, quit project, done projects
        mock_cli.get_input.side_effect = [
            "1",
            "n", "New Project Name",
            "q",
            "done"
        ]

        result = editor._edit_projects(projects)
        assert result[0]["name"] == "New Project Name"


    # _edit_single_project basic fields

    def test_edit_single_project_edit_name(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        project = sample_portfolio["projects_detail"][0].copy()

        mock_cli.get_input.side_effect = [
            "n", "Updated Name",
            "q"
        ]
        result = editor._edit_single_project(project)
        assert result["name"] == "Updated Name"

    def test_edit_single_project_keep_name(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        project = sample_portfolio["projects_detail"][0].copy()

        mock_cli.get_input.side_effect = [
            "n", "",
            "q"
        ]
        result = editor._edit_single_project(project)
        assert result["name"] == "Galaga Clone"

    def test_edit_single_project_edit_date_range_valid(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        project = sample_portfolio["projects_detail"][0].copy()

        mock_cli.get_input.side_effect = [
            "d", "Feb 2024 - May 2024",
            "q"
        ]
        result = editor._edit_single_project(project)
        assert result["date_range"] == "Feb 2024 - May 2024"

    def test_edit_single_project_edit_date_range_invalid_no_dash(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        project = sample_portfolio["projects_detail"][0].copy()

        mock_cli.get_input.side_effect = [
            "d", "InvalidDate",
            "q"
        ]
        result = editor._edit_single_project(project)
        assert result["date_range"] == "Jan 2024 - Mar 2024"

    def test_edit_single_project_edit_role_creates_user_role_if_missing(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        project = sample_portfolio["projects_detail"][0].copy()
        project.pop("user_role", None)

        mock_cli.get_input.side_effect = [
            "r", "Team Lead",
            "q"
        ]
        result = editor._edit_single_project(project)
        assert result["user_role"]["role"] == "Team Lead"

    def test_edit_single_project_edit_blurb_creates_user_role_if_missing(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        project = sample_portfolio["projects_detail"][0].copy()
        project.pop("user_role", None)

        mock_cli.get_input.side_effect = [
            "b", "I did everything",
            "q"
        ]
        result = editor._edit_single_project(project)
        assert result["user_role"]["blurb"] == "I did everything"


    # _edit_project_frameworks

    def test_edit_project_frameworks_add(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        project = sample_portfolio["projects_detail"][0].copy()

        mock_cli.get_input.side_effect = [
            "Pytest",
            "done"
        ]

        result = editor._edit_project_frameworks(project)
        assert any(fw["name"] == "Pytest" for fw in result["frameworks"])

    def test_edit_project_frameworks_remove_case_insensitive(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        project = sample_portfolio["projects_detail"][0].copy()

        mock_cli.get_input.side_effect = [
            "unity", "y",
            "done"
        ]

        result = editor._edit_project_frameworks(project)
        assert not any(fw["name"] == "Unity" for fw in result["frameworks"])

    def test_edit_project_frameworks_cancel_removal(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        project = sample_portfolio["projects_detail"][0].copy()

        mock_cli.get_input.side_effect = [
            "Unity", "n",
            "done"
        ]

        result = editor._edit_project_frameworks(project)
        assert any(fw["name"] == "Unity" for fw in result["frameworks"])

    def test_edit_project_frameworks_empty_input_ignored(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        project = sample_portfolio["projects_detail"][0].copy()

        before = len(project["frameworks"])

        mock_cli.get_input.side_effect = [
            "",
            "done"
        ]

        result = editor._edit_project_frameworks(project)
        assert len(result["frameworks"]) == before


    # _edit_contribution_level

    def test_edit_contribution_level_updates_existing(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        project = sample_portfolio["projects_detail"][0].copy()

        mock_cli.get_input.return_value = "Major Contributor"
        result = editor._edit_contribution_level(project)

        assert result["contribution"]["level"] == "Major Contributor"

    def test_edit_contribution_level_creates_contribution_if_missing(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        project = sample_portfolio["projects_detail"][0].copy()
        project.pop("contribution", None)

        mock_cli.get_input.return_value = "Core Contributor"
        result = editor._edit_contribution_level(project)

        assert "contribution" in result
        assert result["contribution"]["level"] == "Core Contributor"

    def test_edit_contribution_level_no_change_on_empty(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        project = sample_portfolio["projects_detail"][0].copy()

        mock_cli.get_input.return_value = ""
        result = editor._edit_contribution_level(project)

        assert result["contribution"]["level"] == "Primary Contributor"


    # edit_skill_timeline tests

    def test_edit_skills_list_add(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        skills = sample_portfolio["skill_timeline"]["high_level_skills"].copy()

        mock_cli.get_input.side_effect = [
            "Docker",
            "done"
        ]
        result = editor._edit_skills_list(skills)
        assert "Docker" in result

    def test_edit_skills_list_remove_case_insensitive(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        skills = sample_portfolio["skill_timeline"]["high_level_skills"].copy()

        mock_cli.get_input.side_effect = [
            "python", "y",
            "done"
        ]
        result = editor._edit_skills_list(skills)
        assert "Python" not in result

    def test_edit_skills_list_cancel_removal(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        skills = sample_portfolio["skill_timeline"]["high_level_skills"].copy()

        mock_cli.get_input.side_effect = [
            "Python", "n",
            "done"
        ]
        result = editor._edit_skills_list(skills)
        assert "Python" in result

    def test_edit_skills_list_empty_input_ignored(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        skills = sample_portfolio["skill_timeline"]["high_level_skills"].copy()

        before = skills.copy()

        mock_cli.get_input.side_effect = [
            "",
            "done"
        ]
        result = editor._edit_skills_list(skills)
        assert result == before

  
    # _edit_languages_list

    def test_edit_languages_list_add(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        langs = sample_portfolio["skill_timeline"]["language_progression"].copy()

        mock_cli.get_input.side_effect = [
            "TypeScript",
            "done"
        ]
        result = editor._edit_languages_list(langs)

        assert any(
            lang["name"] == "TypeScript" and lang["file_count"] == 0 and lang["percentage"] == 0.0
            for lang in result
        )

    def test_edit_languages_list_remove_case_insensitive(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        langs = sample_portfolio["skill_timeline"]["language_progression"].copy()

        mock_cli.get_input.side_effect = [
            "javascript", "y",
            "done"
        ]
        result = editor._edit_languages_list(langs)
        assert not any(lang["name"] == "JavaScript" for lang in result)

    def test_edit_languages_list_cancel_removal(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        langs = sample_portfolio["skill_timeline"]["language_progression"].copy()

        mock_cli.get_input.side_effect = [
            "JavaScript", "n",
            "done"
        ]
        result = editor._edit_languages_list(langs)
        assert any(lang["name"] == "JavaScript" for lang in result)

    def test_edit_languages_list_empty_input_ignored(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        langs = sample_portfolio["skill_timeline"]["language_progression"].copy()
        before = langs.copy()

        mock_cli.get_input.side_effect = [
            "",
            "done"
        ]
        result = editor._edit_languages_list(langs)
        assert result == before

    
    # _edit_skill_timeline
    
    def test_edit_skill_timeline_edit_skills(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        timeline = sample_portfolio["skill_timeline"].copy()

        mock_cli.get_input.side_effect = [
            "s",
            "Docker", "done",
            "q"
        ]
        result = editor._edit_skill_timeline(timeline)

        assert "Docker" in result["high_level_skills"]

    def test_edit_skill_timeline_edit_languages(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        timeline = sample_portfolio["skill_timeline"].copy()

        mock_cli.get_input.side_effect = [
            "l",
            "Rust", "done",
            "q"
        ]
        result = editor._edit_skill_timeline(timeline)

        assert any(lang["name"] == "Rust" for lang in result["language_progression"])

    def test_edit_skill_timeline_invalid_choice(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        timeline = sample_portfolio["skill_timeline"].copy()

        mock_cli.get_input.side_effect = [
            "x",
            "q"
        ]
        editor._edit_skill_timeline(timeline)

        mock_cli.print_status.assert_any_call("Invalid choice.", "warning")


    # edit_portfolio (main menu)

    def test_edit_portfolio_full_flow(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        portfolio = sample_portfolio.copy()

        mock_cli.get_input.side_effect = [
            "p",
            "1",
            "n", "New Name",
            "q",
            "done",
            "s",
            "s",
            "Docker", "done",
            "q",
            "d"
        ]

        result = editor.edit_portfolio(portfolio)

        assert result["projects_detail"][0]["name"] == "New Name"
        assert "Docker" in result["skill_timeline"]["high_level_skills"]

    def test_edit_portfolio_invalid_choice(self, mock_cli, sample_portfolio):
        editor = PortfolioEditor(mock_cli)
        portfolio = sample_portfolio.copy()

        mock_cli.get_input.side_effect = [
            "x",
            "d"
        ]

        editor.edit_portfolio(portfolio)
        mock_cli.print_status.assert_any_call(
            "Invalid choice. Please select a valid option.", "warning"
        )

    def test_edit_portfolio_missing_sections_created(self, mock_cli):
        """
        Ensures missing keys don't crash the editor.
        - projects_detail defaults to []
        - skill_timeline defaults to {}
        """
        editor = PortfolioEditor(mock_cli)
        portfolio = {}

        mock_cli.get_input.side_effect = [
            "p",   # should safely show "No projects available"
            "s",   # edit skills timeline with empty dict
            "q",   # exit skill editing
            "d"
        ]

        result = editor.edit_portfolio(portfolio)
        assert "projects_detail" in result
        assert "skill_timeline" in result

    def test_edit_portfolio_exception_handling_does_not_crash(self, mock_cli, sample_portfolio):
        """
        Forces an exception during menu input.
        Should be caught and not crash the loop.
        """
        editor = PortfolioEditor(mock_cli)
        portfolio = sample_portfolio.copy()

        mock_cli.get_input.side_effect = [
            "p",
            Exception("Boom"),
            "d"
        ]

        result = editor.edit_portfolio(portfolio)
        assert result is not None
        mock_cli.print_status.assert_any_call(
            "Error during portfolio editing: Boom", "error"
        )

    def test_edit_single_project_prints_frameworks_and_role(self, mock_cli, sample_portfolio, capsys):
        editor = PortfolioEditor(mock_cli)
        project = sample_portfolio["projects_detail"][0].copy()

        mock_cli.get_input.side_effect = ["q"]
        editor._edit_single_project(project)

        captured = capsys.readouterr()
        assert "CURRENT PROJECT DETAILS" in captured.out
        assert "Frameworks" in captured.out
        assert "Role:" in captured.out

    def test_edit_skill_timeline_prints_sections(self, mock_cli, sample_portfolio, capsys):
        editor = PortfolioEditor(mock_cli)
        timeline = sample_portfolio["skill_timeline"].copy()

        mock_cli.get_input.side_effect = ["q"]
        editor._edit_skill_timeline(timeline)

        captured = capsys.readouterr()
        assert "High-Level Skills" in captured.out
        assert "Languages" in captured.out