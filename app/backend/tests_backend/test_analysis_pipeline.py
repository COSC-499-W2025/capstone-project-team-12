import pytest
from anytree import Node
from analysis_pipeline import AnalysisPipeline
from unittest.mock import MagicMock, patch, call


@pytest.fixture
def pipeline():
    #mock the dependencies
    return AnalysisPipeline(MagicMock(), MagicMock(), MagicMock())

def test_data_helpers(pipeline):
    """Tests if the pipeline can correctly fetch and convert binary data"""
    pipeline.file_data_list = [b"Hello World"]
    assert pipeline.get_bin_data_by_Id(0) == b"Hello World"
    assert pipeline.binary_to_str([b"test"]) == ["test"]

@patch("analysis_pipeline.FileManager")
def test_file_load_failure(mock_fm, pipeline):
    """Tests that the pipeline stops if the file fails to load"""
    #forcing the file manager to return error
    mock_fm.return_value.load_from_filepath.return_value = {"status": "error", "message": "fail"}
    pipeline.run_analysis("fake_path")
    # Updated expectation to match actual output from _prepare_data_for_analysis
    pipeline.cli.print_status.assert_any_call("Load Error: fail", "error")

@patch("analysis_pipeline.LocalLLMClient")
@patch("analysis_pipeline.RepoDetector")
@patch("analysis_pipeline.FileManager")
# Patch internal methods to prevent crashing on dummy data
@patch("analysis_pipeline.AnalysisPipeline.classify_files")
@patch("analysis_pipeline.AnalysisPipeline.run_metadata_analysis_pipeline")
@patch("analysis_pipeline.AnalysisPipeline.run_topic_analysis_pipeline")
@patch("analysis_pipeline.AnalysisPipeline.run_repo_analysis_pipeline")
def test_successful_save(mock_repo, mock_topic, mock_meta, mock_classify, mock_fm, mock_rd, mock_llm, pipeline):
    """Tests that the pipeline actually triggers a database save on success"""
    # success event 
    # mock_fm is correctly the 3rd argument from bottom (FileManager)
    mock_fm.return_value.load_from_filepath.return_value = {
        "status": "success", 
        "tree": Node("root"), 
        "binary_data": []
    }

    # Setup mocks to return safe dummy data
    # Updated: classify_files returns 4 values (text, code, repos, binary)
    mock_classify.return_value = ([], [], [], [])
    mock_meta.return_value = ({}, {})
    mock_topic.return_value = (None, None, [], [], [])
    mock_repo.return_value = ([], [], [], [])

    # create fake results
    mock_llm.return_value.generate_summary.return_value = "Summary"
    pipeline.run_analysis("valid_path")

    assert pipeline.database_manager.create_analyses.called #check if asked db for new entry
    assert pipeline.database_manager.save_resume_points.called #check that summary was sent to be saved

def test_reviews_proceed_immediately(pipeline):
    """Tests that if user chooses to proceed immediately, the pipeline continues"""
    initial_bundle = {
        'topic_keywords': [
            {'topic_id': 0, 'keywords': ['data', 'code']},
            {'topic_id': 1, 'keywords': ['user', 'login']}
        ]
    }
    #user inputs p
    pipeline.cli.display_topic_review_menu.return_value = 'P'

    result = pipeline.review_topic_bundle(initial_bundle)

    assert result == initial_bundle
    pipeline.cli.print_status.assert_called_with("Proceeding with current topics.", "success")


def test_reviews_delete_topic(pipeline):
    """Tests that it correctly deletes a topic"""
    initial_bundle = {
        'topic_keywords': [
            {'topic_id': 0, 'keywords': ['data', 'code']},
            {'topic_id': 1, 'keywords': ['user', 'login']}
        ]
    }

    #we want to edit, then , then we input 1, then we select del, then p
    pipeline.cli.display_topic_review_menu.side_effect = ['E', 'P']
    pipeline.cli.get_input.return_value = '1'  #topic to delete
    pipeline.cli.get_granular_input.return_value = ('del', None)

    result = pipeline.review_topic_bundle(initial_bundle)
    final_topics = result['topic_keywords']
    assert len(final_topics) == 1
    assert final_topics[0]['topic_id'] == 0
    pipeline.cli.print_status.assert_any_call("Topic 1 has been deleted.", "success")


def test_review_manual_editing(pipeline):
    """Test the manual editing/granular edits workflow"""
    initial_bundle = {
        'topic_keywords': [{'topic_id': 0, 'keywords': ['bad', 'middle']}]
    }

    #from main menu, E then P after edits
    pipeline.cli.display_topic_review_menu.side_effect = ['E', 'P']
    
    pipeline.cli.get_input.side_effect = ["0", "better", "good"]

    pipeline.cli.get_granular_input.side_effect = [
        ('replace_one', 0), 
        ('add', None), 
        ('back', None)
    ]

    result = pipeline.review_topic_bundle(initial_bundle)

    keywords = result['topic_keywords'][0]['keywords']
    assert keywords[0] == 'better'  #replaced
    assert keywords[1] == 'middle'  #same
    assert keywords[2] == 'good'    #added