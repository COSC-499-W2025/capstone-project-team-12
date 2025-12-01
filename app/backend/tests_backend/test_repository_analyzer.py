from typing import Any, Dict, List
import pytest
from pathlib import Path
from datetime import datetime
from repository_analyzer import RepositoryAnalyzer

TEST_FILE_DIR = Path(__file__).parent
TEST_REPO_PATH = TEST_FILE_DIR / "test_main_dir" / "capstone_team12_testrepo"


def create_mock_project_data(
    repo_name: str = "TestRepo", user_commits_count: int = 5, lines_added: int = 100,
    duration_days: int = 30, start_date: str = "2024-01-01T00:00:00", total_contributors: int = 1
) -> Dict[str, Any]:
    """Helper to create mock project data"""
    return {
        'status': 'success', 'repository_name': repo_name,
        'user_commits': [{'hash': f'h{i}', 'date': start_date, 'modified_files': [
            {'filename': f'f{i}.py', 'change_type': 'MODIFY', 'added_lines': lines_added // user_commits_count,
             'deleted_lines': 10, 'source_code': 'import os\nimport sys'}
        ]} for i in range(user_commits_count)],
        'statistics': {'user_files_modified': user_commits_count, 'user_lines_added': lines_added,
                       'user_lines_deleted': 50, 'change_types': {'MODIFY', 'ADD'}},
        'repository_context': {
            'total_contributors': total_contributors, 'total_commits_all_authors': user_commits_count * 2,
            'repo_total_lines_added': lines_added * 2, 'repo_total_lines_deleted': 100,
            'repo_total_files_modified': user_commits_count * 2, 'is_collaborative': total_contributors > 1,
            'all_authors_stats': {'testuser@example.com': {'commits': user_commits_count, 'lines_added': lines_added,
                                                            'lines_deleted': 50, 'files_modified': user_commits_count}}
        },
        'dates': {'start_date': start_date, 'end_date': start_date, 'duration_days': duration_days,
                  'duration_seconds': duration_days * 86400}
    }


class TestRepositoryAnalyzer:
    
    def test_initialization_and_chronological_list(self) -> None:
        analyzer = RepositoryAnalyzer("test_user")
        assert analyzer.username == "test_user"
        
        # Test chronological sorting
        data = [create_mock_project_data('A', start_date='2024-01-01T00:00:00'),
                create_mock_project_data('B', start_date='2024-03-01T00:00:00')]
        projects = analyzer.create_chronological_project_list(data)
        assert len(projects) == 2 and projects[0]['name'] == 'B'
        
        # Test filtering and edge cases (covers line 394)
        data_with_errors = [create_mock_project_data('Good'),
                            {'status': 'error', 'repository_name': 'Bad'},
                            {'status': 'success', 'repository_name': 'NoDate', 'dates': {'start_date': None}}]
        projects = analyzer.create_chronological_project_list(data_with_errors)
        assert len(projects) == 1
        assert analyzer.create_chronological_project_list([]) == []
    
    def test_ranking_and_importance(self):
        analyzer = RepositoryAnalyzer("testuser")
        assert RepositoryAnalyzer.normalize_for_rankings(5, 10, 0) == 0.5
        assert RepositoryAnalyzer.normalize_for_rankings(5, 5, 5) == 0
        
        projects = [create_mock_project_data("Low", 5, 100, 5),
                    create_mock_project_data("High", 10, 500, 10)]
        ranked = analyzer.rank_importance_of_projects(projects)
        assert ranked[0]['repository_name'] == 'High'
        
        top3 = analyzer.get_most_important_projects([*projects, create_mock_project_data("Mid", 8, 300, 8)])
        assert len(top3) == 3 and top3[0]['repository_name'] == 'High'
        assert analyzer.get_most_important_projects([]) == []
    
    def test_import_extraction(self):
        analyzer = RepositoryAnalyzer("testuser")
        
        # Python imports with date updates (covers lines 123, 125)
        project = create_mock_project_data("RepoA")
        project['user_commits'] = [
            {'date': '2024-01-01T00:00:00', 'modified_files': [{'filename': 'a.py', 'source_code': 'import os'}]},
            {'date': '2024-01-10T00:00:00', 'modified_files': [{'filename': 'b.py', 'source_code': 'import os\nfrom math import sin'}]},
            {'date': None, 'modified_files': [{'filename': 'c.py', 'source_code': 'import sys'}]},  # Line 78
            {'date': 'bad', 'modified_files': [{'filename': 'd.py', 'source_code': 'import json'}]},  # Lines 82-83
        ]
        imports = analyzer.extract_repo_import_stats(project)
        assert imports["os"]["start_date"] == "2024-01-01T00:00:00"
        assert imports["os"]["end_date"] == "2024-01-10T00:00:00"
        
        # Multi-language imports
        project['user_commits'][0]['modified_files'][0] = {
            'filename': "b.py", 'source_code': "import numpy as np, pandas\nfrom os.path import join"
        }
        imports = analyzer.extract_repo_import_stats(project)
        assert all(imp in imports for imp in ["numpy", "pandas", "os.path"])
        
        project['user_commits'][0]['modified_files'][0] = {
            'filename': "app.js", 'source_code': 'import fs from "fs";'
        }
        assert "fs" in analyzer.extract_repo_import_stats(project)
        
        project['user_commits'][0]['modified_files'][0] = {
            'filename': "Main.java", 'source_code': "import java.util.List;"
        }
        assert "java.util.List" in analyzer.extract_repo_import_stats(project)
        
        project['user_commits'][0]['modified_files'][0] = {
            'filename': "main.cpp", 'source_code': "#include <iostream>"
        }
        assert "iostream" in analyzer.extract_repo_import_stats(project)
    
    def test_import_aggregation_and_sorting(self):
        analyzer = RepositoryAnalyzer("testuser")
        
        # Test error handling (covers lines 162-163)
        original = analyzer.extract_repo_import_stats
        analyzer.extract_repo_import_stats = lambda p: (_ for _ in ()).throw(Exception("Test"))
        result = analyzer.get_all_repo_import_stats([create_mock_project_data("Repo1")])
        assert 'error' in result[0]
        analyzer.extract_repo_import_stats = original
        
        # Test sorting (covers lines 188-217)
        summaries = [
            {"repository_name": "A", "imports_summary": {
                "os": {"start_date": "2024-01-02T00:00:00", "end_date": "2024-01-02T00:00:00", "frequency": 1, "duration_days": 0},
                "sys": {"start_date": "2024-01-05T00:00:00", "end_date": "2024-01-05T00:00:00", "frequency": 2, "duration_days": 0}}},
            {"repository_name": "B", "imports_summary": {
                "math": {"start_date": "2024-01-10T00:00:00", "end_date": "2024-01-10T00:00:00", "frequency": 3, "duration_days": 0}}}
        ]
        sorted_all = analyzer.sort_all_repo_imports_chronologically(summaries)
        assert len(sorted_all) == 3 and sorted_all[0]["import"] == "math" and "start_dt" not in sorted_all[0]
        
        sorted_single = analyzer.sort_repo_imports_in_chronological_order(summaries[0])
        assert list(sorted_single["imports_summary"].keys()) == ["sys", "os"]
    
    def test_contribution_insights(self):
        analyzer = RepositoryAnalyzer("testuser")
        
        # Sole contributor
        project = create_mock_project_data(total_contributors=1)
        result = analyzer._calculate_contribution_insights(project)
        assert result['contribution_level'] == 'Sole Contributor'
        
        # Top contributor (line 274)
        project = create_mock_project_data(total_contributors=3)
        project['repository_context']['all_authors_stats'] = {
            'testuser@example.com': {'commits': 10}, 'u1@ex.com': {'commits': 5}, 'u2@ex.com': {'commits': 3}}
        assert analyzer._calculate_contribution_insights(project)['contribution_level'] == 'Top Contributor'
        
        # Major contributor (line 276) - need 76th percentile or higher
        project['repository_context']['all_authors_stats'] = {
            'testuser@example.com': {'commits': 9}, 'u1@ex.com': {'commits': 10}, 'u2@ex.com': {'commits': 5},
            'u3@ex.com': {'commits': 4}, 'u4@ex.com': {'commits': 2}}
        result = analyzer._calculate_contribution_insights(project)
        assert result['contribution_level'] == 'Significant Contributor' and result['percentile'] == 60.0
        
        # Regular contributor (line 280) - below 50th percentile
        project['repository_context']['all_authors_stats'] = {
            'u1@ex.com': {'commits': 10}, 'u2@ex.com': {'commits': 8}, 'u3@ex.com': {'commits': 6},
            'testuser@example.com': {'commits': 2}, 'u4@ex.com': {'commits': 4}}
        assert analyzer._calculate_contribution_insights(project)['contribution_level'] == 'Contributor'
        
        # Unknown user
        assert RepositoryAnalyzer("unknown")._calculate_contribution_insights(project)['contribution_level'] == 'Unknown'
    
    def test_full_insights_generation(self):
        analyzer = RepositoryAnalyzer("testuser")
        
        # Empty list
        assert analyzer.generate_project_insights([]) == []
        
        # Full insights
        data = [create_mock_project_data("R1", 10, 500), create_mock_project_data("R2", 5, 200)]
        result = analyzer.generate_project_insights(data)
        assert len(result) == 2 and result[0]['importance_rank'] == 1
        assert all(k in result[0] for k in ['contribution_analysis', 'collaboration_insights', 'testing_insights'])
        
        # Testing insights
        project = create_mock_project_data()
        project['user_commits'] = [{'modified_files': [
            {'filename': 'test_main.py', 'added_lines': 50, 'deleted_lines': 0},
            {'filename': 'main.py', 'added_lines': 100, 'deleted_lines': 10}]}]
        result = analyzer._generate_testing_insights(project)
        assert result['test_files_modified'] == 1 and result['has_tests']
        
        # Collaboration insights
        project = create_mock_project_data(total_contributors=1)
        project['repository_context']['total_commits_all_authors'] = len(project['user_commits'])
        result = analyzer._generate_collaboration_insights(project)
        assert not result['is_collaborative'] and result['team_size'] == 1
