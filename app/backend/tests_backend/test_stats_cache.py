import pytest
import orjson
from stats_cache import collect_stats, _to_serializable


class TestCollectStats:
    """Test suite for collect_stats function"""
    
    def test_collect_stats_with_all_params(self):
        """Test collect_stats with all parameters provided"""
        metadata = {"file_count": 10, "total_size": 5000}
        text = {"keywords": ["python", "test"], "sentiment": 0.8}
        project = {"commits": 50, "contributors": 3}
        
        result = collect_stats(
            metadata_stats=metadata,
            text_analysis=text,
            project_analysis=project
        )
        
        #verify it's valid JSON
        parsed = orjson.loads(result)
        
        #check if the structure exists
        assert "pre_analysis_bundle" in parsed
        assert "metadata_stats" in parsed["pre_analysis_bundle"]
        assert "text_analysis" in parsed["pre_analysis_bundle"]
        assert "project_analysis" in parsed["pre_analysis_bundle"]
    
    def test_collect_stats_with_no_params(self):
        """Test collect_stats with no parameters"""
        result = collect_stats() #empty call
        
        parsed = orjson.loads(result)
        
        assert parsed["pre_analysis_bundle"]["metadata_stats"] == {}
        assert parsed["pre_analysis_bundle"]["text_analysis"] == {}
        assert parsed["pre_analysis_bundle"]["project_analysis"] == {}
    
    def test_collect_stats_returns_valid_json(self):
        """Test that output is valid JSON string"""
        result = collect_stats(metadata_stats={"key": "value"})
        
        parsed = orjson.loads(result)
        assert isinstance(parsed, dict)
    
    def test_collect_stats_w_sets_and_tuples(self):
        """Test that sets and tuples are converted to lists"""
        data = {
            "set": {1, 2, 3},
            "tuple": (4, 5, 6)
        }
        
        result = collect_stats(metadata_stats=data)
        parsed = orjson.loads(result) #turn json back to dict to check values
        stats = parsed["pre_analysis_bundle"]["metadata_stats"]
        
        #should all be lists now
        assert isinstance(stats["set"], list)
        assert isinstance(stats["tuple"], list)


class TestToSerializable:
    """Test suite for _to_serializable helper function"""
    
    def test_to_serializable_set(self):
        """Test converting set to list"""
        data = {1, 2, 3}
        result = _to_serializable(data)
        
        assert isinstance(result, list)
        assert set(result) == {1, 2, 3}
    
    def test_to_serializable_tuple(self):
        """Test converting tuple to list"""
        data = (1, 2, 3)
        result = _to_serializable(data)
        
        assert result == [1, 2, 3]
    
    def test_to_serializable_nested_structures(self):
        """Test deeply nested non-serializable structures"""
        data = {
            "level1": [
                {"level2": (1, 2, [3, 4])} #tuple inside dict inside list inside dict
            ]
        }
        result = _to_serializable(data)
        
        assert isinstance(result["level1"][0]["level2"], list)
        assert result["level1"][0]["level2"] == [1, 2, [3, 4]]