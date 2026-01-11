import pytest
from unittest.mock import MagicMock, patch
from anytree import Node
from analysis_pipeline import AnalysisPipeline

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
    #forcing hte file manager to return error
    mock_fm.return_value.load_from_filepath.return_value = {"status": "error", "message": "fail"}
    pipeline.run_analysis("fake_path")
    pipeline.cli.print_status.assert_any_call("Load Error: fail", "error")

@patch("analysis_pipeline.FileManager")
@patch("analysis_pipeline.TreeProcessor")
@patch("analysis_pipeline.LocalLLMClient")

def test_successful_save(mock_llm, mock_tp, mock_fm, pipeline):
    """Tests that the pipeline actually triggers a database save on success"""
    #success event 
    mock_fm.return_value.load_from_filepath.return_value = {
        "status": "success", 
        "tree": Node("root"), 
        "binary_data": []
    }

    #create fake results
    mock_llm.return_value.generate_summary.return_value = "Summary"
    pipeline.run_analysis("valid_path")

    assert pipeline.database_manager.create_new_result.called #check if asked db for new entry
    assert pipeline.database_manager.save_resume_points.called #check that summary was sent to be saved