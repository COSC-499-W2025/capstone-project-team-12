import orjson
from typing import Any, Dict, Optional
from dataclasses import is_dataclass, asdict

#subject to change once other components are implemented
def collect_stats(
        *,
        metadata_stats: Optional[Dict[str, Dict[str, Any]]] = None,
        text_analysis: Optional[dict[str, Any]] = None,
        project_analysis: Optional[dict[str, Any]] = None,
    ) -> str:
    
    try:
        pre_analysis_bundle: Dict[str, Any] = {
            "metadata_stats": _to_serializable(metadata_stats or {}),
            "text_analysis": _to_serializable(text_analysis or {}),
            "project_analysis": _to_serializable(project_analysis or {})
        }
        #create pre-analysis bundle that we store in db table, once created
        data = {
            "pre_analysis_bundle": pre_analysis_bundle,
        }
        #returns JSON string that are readable and sorted by key alphabetically
        return orjson.dumps(
            data,
            option=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS
        ).decode("utf-8")
    except orjson.JSONEncodeError as e:
        raise ValueError("Failed to serialize stats data") from e
    
    except Exception as e:
        raise RuntimeError("An unexpected error occurred while collecting stats") from e
#convert non-JSON-serializable types like sets and tuples into lists since orjson can't serialize sets or tuples
def _to_serializable(obj: Any) -> Any:
    #recusively goes through structures
    if is_dataclass(obj):
        return asdict(obj)
    elif isinstance(obj, dict):
        return {k: _to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_to_serializable(item) for item in obj]
    #if set, frozen set or tuple, make it a list
    elif isinstance(obj, (set, frozenset, tuple)):
        return list(obj)
    else:
        return obj