import pytest
from typing import Dict, Any, List

from project_reranking import (
    normalize,
    compute_scores,
    assign_importance_ranks,
    rerank_projects
)

from project_selection import choose_projects_for_analysis

# Helpers to create mock projects

def mock_project(
    name: str,
    commits: int,
    lines: int,
    duration: int,
) -> Dict[str, Any]:
    return {
        "repository_name": name,
        "user_commits": [{}] * commits,
        "statistics": {"user_lines_added": lines},
        "dates": {"duration_days": duration},
    }


@pytest.fixture
def sample_projects() -> List[Dict[str, Any]]:
    return [
        mock_project("A", commits=5, lines=100, duration=10),
        mock_project("B", commits=10, lines=300, duration=20),
        mock_project("C", commits=2, lines=50, duration=5),
    ]


# -------- Project Reranking Tests --------
def test_normalize_basic():
    values = [0, 5, 10]
    result = normalize(values)
    assert result == [0.0, 0.5, 1.0]


# compute_scores
def test_compute_scores_orders_correctly(sample_projects):
    weights = {"commits": 0.33, "lines_added": 0.33, "duration": 0.34}

    ranked = compute_scores(sample_projects, weights)

    assert ranked[0]["repository_name"] == "B"
    assert ranked[-1]["repository_name"] == "C"

    for p in ranked:
        assert "importance_score" in p
        assert 0 <= p["importance_score"] <= 1


def test_compute_scores_equal_weights_matches_average(sample_projects):
    weights = {"commits": 1/3, "lines_added": 1/3, "duration": 1/3}
    ranked = compute_scores(sample_projects, weights)

    scores = [p["importance_score"] for p in ranked]
    assert scores == sorted(scores, reverse=True)


# assign importance ranks
def test_assign_importance_ranks():
    projects = [
        {"repository_name": "X"},
        {"repository_name": "Y"},
        {"repository_name": "Z"},
    ]

    ranked = assign_importance_ranks(projects)

    assert ranked[0]["importance_rank"] == 1
    assert ranked[1]["importance_rank"] == 2
    assert ranked[2]["importance_rank"] == 3


# rerank_projects
def test_rerank_projects_preset(monkeypatch, sample_projects):
    # Choose option 1 → preset 4 (code additions focused)
    inputs = iter(["1", "4"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    ranked = rerank_projects(sample_projects)

    assert ranked[0]["repository_name"] == "B"
    assert ranked[0]["importance_rank"] == 1
    assert all("importance_score" in p for p in ranked)


def test_rerank_projects_keep_current(monkeypatch, sample_projects):
    inputs = iter(["3"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    ranked = rerank_projects(sample_projects)

    assert ranked == sample_projects


# -------- Project Selection for Analysis Tests --------
def test_choose_projects_proceed_all(monkeypatch, sample_projects):
    monkeypatch.setattr("builtins.input", lambda _: "")

    result = choose_projects_for_analysis(sample_projects)
    assert result == sample_projects


def test_choose_projects_subset(monkeypatch, sample_projects):
    inputs = iter(["n", "1 3"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    result = choose_projects_for_analysis(sample_projects)

    assert len(result) == 2
    assert result[0]["repository_name"] == "A"
    assert result[1]["repository_name"] == "C"
