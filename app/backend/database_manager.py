import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from db_utils import DB_connector
from metadata_analyzer import AnalysisResults

class DatabaseManager:
    def __init__(self):
        """Initialize database connection."""
        self.db = DB_connector()
    
    def create_new_result(self) -> str:
        """Create a new result entry and return its result_id UUID (str)."""
        try:
            query = """
                INSERT INTO Results (result_id)
                VALUES (uuid_generate_v4())
                RETURNING result_id;
            """
            result = self.db.execute_query(query, fetch=True)
            
            if result and len(result) > 0:
                result_id = str(result[0][0])
                print(f"Created new result with ID: {result_id}")
                return result_id
            else:
                raise Exception("Failed to generate result_id")
                
        except Exception as e:
            print(f"Error creating new result: {e}")
            raise
    
    def save_repository_analysis(
        self,
        result_id: str,
        processed_git_repos: Any,
        timeline: List[Dict[str, Any]]
    ) -> bool:
        """Save repository analysis results to the database and return success status (bool)."""
        try:
            project_insights = {
                "repositories": processed_git_repos,
                "timeline": timeline,
                "total_projects": len(timeline) if timeline else 0
            }
            
            query = """
                UPDATE Results
                SET project_insights = %s
                WHERE result_id = %s;
            """
            
            self.db.execute_query(
                query,
                (json.dumps(project_insights), uuid.UUID(result_id)),
                fetch=False
            )
            
            print(f"Saved repository analysis for result_id: {result_id}")
            return True
            
        except Exception as e:
            print(f"Error saving repository analysis: {e}")
            return False
    
    def save_tracked_data(
        self,
        result_id: str,
        metadata_results: Dict[str, Dict[str, Any]],
        bow_cache: Optional[List[List[str]]] = None
    ) -> bool:
        """Save raw metadata and BoW cache to Tracked_Data table and return success status (bool)."""
        try:
            tracked_data = {
                "metadata_stats": metadata_results,
                "bow_cache": bow_cache if bow_cache else None,
                "timestamp": datetime.now().isoformat()
            }
            
            query = """
                INSERT INTO Tracked_Data (result_id, metadata_stats, bow_cache)
                VALUES (%s, %s, %s);
            """
            
            self.db.execute_query(
                query,
                (
                    uuid.UUID(result_id),
                    json.dumps(tracked_data["metadata_stats"]),
                    json.dumps(tracked_data["bow_cache"]) if bow_cache else None
                ),
                fetch=False
            )
            
            print(f"Saved tracked data for result_id: {result_id}")
            return True
            
        except Exception as e:
            print(f"Error saving tracked data: {e}")
            return False
    
    
    def close(self):
        """Close the database connection."""
        self.db.close_connection()