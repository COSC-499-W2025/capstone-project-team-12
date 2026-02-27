import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def cli():
    mock = MagicMock()
    mock.get_input.return_value = ""
    return mock

@pytest.fixture
def db_manager():
    return MagicMock()

@pytest.fixture
def resume_builder():
    return MagicMock()

@pytest.fixture
def portfolio_builder():
    return MagicMock()


# ── generate_resume ───────────────────────────────────────────────────────────

class TestGenerateResume:
    def setup_method(self):
        from main_utils import generate_resume
        self.fn = generate_resume

    def test_success_returns_id_and_resume(self, db_manager, resume_builder, cli):
        resume_builder.create_resume_from_analysis_id.return_value = {"skills": ["Python"]}
        db_manager.save_resume.return_value = 7

        result = self.fn("aid-1", db_manager, resume_builder, cli)

        assert result == (7, {"skills": ["Python"]})
        db_manager.save_resume.assert_called_once_with("aid-1", {"skills": ["Python"]})

    def test_builder_returns_none_should_return_none_not_tuple(self, db_manager, resume_builder, cli):
        resume_builder.create_resume_from_analysis_id.return_value = None
        result = self.fn("aid-1", db_manager, resume_builder, cli)
        assert result is None
        db_manager.save_resume.assert_not_called()

    def test_builder_returns_empty_dict_should_return_none_not_tuple(self, db_manager, resume_builder, cli):
        """Empty dict is falsy — save_resume is skipped but a tuple is still returned."""
        resume_builder.create_resume_from_analysis_id.return_value = {}
        result = self.fn("aid-1", db_manager, resume_builder, cli)
        assert result is None
        db_manager.save_resume.assert_not_called()

    def test_exception_returns_none_with_warning(self, db_manager, resume_builder, cli):
        resume_builder.create_resume_from_analysis_id.side_effect = Exception("boom")
        result = self.fn("aid-1", db_manager, resume_builder, cli)
        assert result is None
        cli.print_status.assert_called_once()
        assert cli.print_status.call_args[0][1] == "warning"

    def test_save_not_called_when_builder_returns_none(self, db_manager, resume_builder, cli):
        resume_builder.create_resume_from_analysis_id.return_value = None
        self.fn("aid-1", db_manager, resume_builder, cli)
        db_manager.save_resume.assert_not_called()


# ── generate_portfolio ────────────────────────────────────────────────────────

class TestGeneratePortfolio:
    def setup_method(self):
        from main_utils import generate_portfolio
        self.fn = generate_portfolio

    def test_success_returns_id_and_portfolio(self, db_manager, portfolio_builder, cli):
        portfolio_builder.create_portfolio_from_result_id.return_value = {"projects": ["X"]}
        db_manager.save_portfolio.return_value = 3
        result = self.fn("aid-1", db_manager, portfolio_builder, cli)
        assert result == (3, {"projects": ["X"]})

    def test_builder_returns_none_should_return_none_not_tuple(self, db_manager, portfolio_builder, cli):
        portfolio_builder.create_portfolio_from_result_id.return_value = None
        result = self.fn("aid-1", db_manager, portfolio_builder, cli)
        assert result is None
        db_manager.save_portfolio.assert_not_called()

    def test_exception_returns_none(self, db_manager, portfolio_builder, cli):
        portfolio_builder.create_portfolio_from_result_id.side_effect = RuntimeError("fail")
        result = self.fn("aid-1", db_manager, portfolio_builder, cli)
        assert result is None


# ── _pick_analysis ────────────────────────────────────────────────────────────

class TestPickAnalysis:
    def setup_method(self):
        from main_utils import _pick_analysis
        self.fn = _pick_analysis

    def test_returns_none_when_db_empty(self, cli, db_manager):
        db_manager.get_all_analyses_summary.return_value = []
        assert self.fn(cli, db_manager) is None

    def test_valid_selection_returns_correct_id(self, cli, db_manager):
        db_manager.get_all_analyses_summary.return_value = [
            {"analysis_id": "uuid-1", "file_path": "/a"},
            {"analysis_id": "uuid-2", "file_path": "/b"},
        ]
        cli.get_input.return_value = "2"
        assert self.fn(cli, db_manager) == "uuid-2"

    def test_out_of_range_returns_none(self, cli, db_manager):
        db_manager.get_all_analyses_summary.return_value = [{"analysis_id": "uuid-1", "file_path": "/a"}]
        cli.get_input.return_value = "99"
        assert self.fn(cli, db_manager) is None

    def test_empty_input_returns_none(self, cli, db_manager):
        db_manager.get_all_analyses_summary.return_value = [{"analysis_id": "uuid-1", "file_path": "/a"}]
        cli.get_input.return_value = ""
        assert self.fn(cli, db_manager) is None

    def test_db_error_returns_none(self, cli, db_manager):
        db_manager.get_all_analyses_summary.side_effect = Exception("db down")
        assert self.fn(cli, db_manager) is None


# ── _pick_resume ──────────────────────────────────────────────────────────────

class TestPickResume:
    def setup_method(self):
        from main_utils import _pick_resume
        self.fn = _pick_resume

    def test_single_resume_returned_directly_without_prompt(self, cli, db_manager):
        db_manager.get_resumes_by_analysis_id.return_value = [
            {"resume_id": 1, "resume_data": {"summary": "dev"}}
        ]
        result = self.fn(cli, db_manager, "aid-1")
        assert result == (1, {"summary": "dev"})
        cli.get_input.assert_not_called()  # should NOT prompt user if only one

    def test_multiple_resumes_valid_selection(self, cli, db_manager):
        db_manager.get_resumes_by_analysis_id.return_value = [
            {"resume_id": 1, "resume_data": {}, "resume_title": "A"},
            {"resume_id": 2, "resume_data": {"x": 1}, "resume_title": "B"},
        ]
        cli.get_input.return_value = "2"
        result = self.fn(cli, db_manager, "aid-1")
        assert result[0] == 2

    def test_empty_list_from_db_does_not_crash(self, cli, db_manager):
        db_manager.get_resumes_by_analysis_id.return_value = []
        result = self.fn(cli, db_manager, "aid-1")
        assert result is None

    def test_lookup_error_returns_none(self, cli, db_manager):
        db_manager.get_resumes_by_analysis_id.side_effect = LookupError("none")
        assert self.fn(cli, db_manager, "aid-1") is None

    def test_empty_input_returns_none(self, cli, db_manager):
        db_manager.get_resumes_by_analysis_id.return_value = [
            {"resume_id": 1, "resume_data": {}, "resume_title": "A"},
            {"resume_id": 2, "resume_data": {}, "resume_title": "B"},
        ]
        cli.get_input.return_value = ""
        assert self.fn(cli, db_manager, "aid-1") is None


# ── _pick_portfolio ───────────────────────────────────────────────────────────

class TestPickPortfolio:
    def setup_method(self):
        from main_utils import _pick_portfolio
        self.fn = _pick_portfolio

    def test_single_portfolio_returned_directly(self, cli, db_manager):
        db_manager.get_portfolios_by_analysis_id.return_value = [
            {"portfolio_id": 5, "portfolio_data": {"url": "x.com"}}
        ]
        result = self.fn(cli, db_manager, "aid-1")
        assert result == (5, {"url": "x.com"})
        cli.get_input.assert_not_called()

    def test_empty_list_does_not_crash(self, cli, db_manager):
        db_manager.get_portfolios_by_analysis_id.return_value = []
        result = self.fn(cli, db_manager, "aid-1")
        assert result is None

    def test_lookup_error_returns_none(self, cli, db_manager):
        db_manager.get_portfolios_by_analysis_id.side_effect = LookupError("nope")
        assert self.fn(cli, db_manager, "aid-1") is None


# ── manage_resumes ────────────────────────────────────────────────────────────

class TestManageResumes:
    def _run(self, cli, db_manager, resume_builder):
        from main_utils import manage_resumes
        manage_resumes(cli, db_manager, resume_builder)

    def test_exits_cleanly_when_no_analyses(self, cli, db_manager, resume_builder):
        db_manager.get_all_analyses_summary.return_value = []
        self._run(cli, db_manager, resume_builder)  # must not raise or loop forever

    def test_view_resume(self, cli, db_manager, resume_builder):
        resume_data = {"summary": "dev"}
        db_manager.get_all_analyses_summary.return_value = [{"analysis_id": "aid-1", "file_path": "/a"}]
        db_manager.get_resumes_by_analysis_id.return_value = [{"resume_id": 1, "resume_data": resume_data}]
        cli.get_input.side_effect = ["1", "v", "b", ""]  # pick, view, back, exit outer loop
        self._run(cli, db_manager, resume_builder)
        resume_builder.display_resume.assert_called_once_with(resume_data, cli)

    def test_delete_resume_confirmed(self, cli, db_manager, resume_builder):
        db_manager.get_all_analyses_summary.return_value = [{"analysis_id": "aid-1", "file_path": "/a"}]
        db_manager.get_resumes_by_analysis_id.return_value = [{"resume_id": 9, "resume_data": {}}]
        cli.get_input.side_effect = ["1", "d", "y", ""]
        self._run(cli, db_manager, resume_builder)
        db_manager.delete_resume.assert_called_once_with(9)

    def test_delete_resume_cancelled(self, cli, db_manager, resume_builder):
        db_manager.get_all_analyses_summary.return_value = [{"analysis_id": "aid-1", "file_path": "/a"}]
        db_manager.get_resumes_by_analysis_id.return_value = [{"resume_id": 9, "resume_data": {}}]
        cli.get_input.side_effect = ["1", "d", "n", "b", ""]
        self._run(cli, db_manager, resume_builder)
        db_manager.delete_resume.assert_not_called()

    def test_generate_new_resume(self, cli, db_manager, resume_builder):
        db_manager.get_all_analyses_summary.return_value = [{"analysis_id": "aid-1", "file_path": "/a"}]
        db_manager.get_resumes_by_analysis_id.return_value = [{"resume_id": 1, "resume_data": {}}]
        resume_builder.create_resume_from_analysis_id.return_value = {"summary": "new"}
        db_manager.save_resume.return_value = 2
        cli.get_input.side_effect = ["1", "g", "b", ""]
        self._run(cli, db_manager, resume_builder)
        db_manager.save_resume.assert_called()

    def test_no_resumes_prompts_generate_declined(self, cli, db_manager, resume_builder):
        """When no resumes exist, user is prompted to generate — declining should exit gracefully."""
        db_manager.get_all_analyses_summary.return_value = [{"analysis_id": "aid-1", "file_path": "/a"}]
        db_manager.get_resumes_by_analysis_id.side_effect = LookupError("none")
        cli.get_input.side_effect = ["1", "n"]
        self._run(cli, db_manager, resume_builder)
        resume_builder.create_resume_from_analysis_id.assert_not_called()


# ── manage_portfolios ─────────────────────────────────────────────────────────

class TestManagePortfolios:
    def _run(self, cli, db_manager, portfolio_builder):
        from main_utils import manage_portfolios
        manage_portfolios(cli, db_manager, portfolio_builder)

    def test_exits_cleanly_when_no_analyses(self, cli, db_manager, portfolio_builder):
        db_manager.get_all_analyses_summary.return_value = []
        self._run(cli, db_manager, portfolio_builder)

    def test_view_portfolio(self, cli, db_manager, portfolio_builder):
        portfolio_data = {"projects": ["X"]}
        db_manager.get_all_analyses_summary.return_value = [{"analysis_id": "aid-1", "file_path": "/a"}]
        db_manager.get_portfolios_by_analysis_id.return_value = [{"portfolio_id": 1, "portfolio_data": portfolio_data}]
        cli.get_input.side_effect = ["1", "v", "b", ""]
        self._run(cli, db_manager, portfolio_builder)
        portfolio_builder.display_portfolio.assert_called_once_with(portfolio_data, cli)

    def test_delete_portfolio_confirmed(self, cli, db_manager, portfolio_builder):
        db_manager.get_all_analyses_summary.return_value = [{"analysis_id": "aid-1", "file_path": "/a"}]
        db_manager.get_portfolios_by_analysis_id.return_value = [{"portfolio_id": 4, "portfolio_data": {}}]
        cli.get_input.side_effect = ["1", "d", "y", ""]
        self._run(cli, db_manager, portfolio_builder)
        db_manager.delete_portfolio.assert_called_once_with(4)

    def test_delete_portfolio_cancelled(self, cli, db_manager, portfolio_builder):
        db_manager.get_all_analyses_summary.return_value = [{"analysis_id": "aid-1", "file_path": "/a"}]
        db_manager.get_portfolios_by_analysis_id.return_value = [{"portfolio_id": 4, "portfolio_data": {}}]
        cli.get_input.side_effect = ["1", "d", "n", "b", ""]
        self._run(cli, db_manager, portfolio_builder)
        db_manager.delete_portfolio.assert_not_called()

    def test_no_portfolios_prompts_generate_declined(self, cli, db_manager, portfolio_builder):
        db_manager.get_all_analyses_summary.return_value = [{"analysis_id": "aid-1", "file_path": "/a"}]
        db_manager.get_portfolios_by_analysis_id.side_effect = LookupError("none")
        cli.get_input.side_effect = ["1", "n"]
        self._run(cli, db_manager, portfolio_builder)
        portfolio_builder.create_portfolio_from_result_id.assert_not_called()