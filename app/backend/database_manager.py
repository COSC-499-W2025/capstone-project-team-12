import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from db_utils import DB_connector
from metadata_analyzer import MetadataAnalysis

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
            result = self.db.execute_update(query, returning=True)
            
            if result:
                result_id = str(result['result_id'])
                print(f"Created new result with ID: {result_id}")
                return result_id
            else:
                raise Exception("Failed to generate result_id")
                
        except Exception as e:
            print(f"Error creating new result: {e}")
            raise

    def save_metadata_analysis(
        self, 
        result_id: str, 
        analysis_results: MetadataAnalysis
    ) -> bool:
        """Save metadata analysis results to the database and return success status (bool)."""
        try:
            # Convert the dataclass to a dictionary for JSON serialization
            metadata_insights = {
                "basic_stats": analysis_results.basic_stats.__dict__,
                "extension_stats": {ext: stats.__dict__ for ext, stats in analysis_results.extension_stats.items()},
                "skill_stats": {skill: stats.__dict__ for skill, stats in analysis_results.skill_stats.items()},
                "primary_skills": analysis_results.primary_skills,
                "date_stats": analysis_results.date_stats.__dict__
            }

            query = """
                UPDATE Results
                SET metadata_insights = %s
                WHERE result_id = %s;
            """
            
            self.db.execute_update(
                query, 
                (json.dumps(metadata_insights, default=str), uuid.UUID(result_id))
            )
            
            print(f"Saved metadata analysis for result_id: {result_id}")
            return True
            
        except Exception as e:
            print(f"Error saving metadata analysis: {e}")
            return False

    def save_text_analysis(
        self,
        result_id: str,
        doc_topic_vectors: List[List[float]],
        topic_term_vectors: List[List[Tuple[str, float]]]
    ) -> bool:
        """Save text analysis topic vectors to the database and return success status (bool)."""
        try:
            topic_data = {
                "doc_topic_vectors": doc_topic_vectors,
                "topic_term_vectors": topic_term_vectors
            }
            
            query = """
                UPDATE Results
                SET topic_vector = %s
                WHERE result_id = %s;
            """
            
            self.db.execute_update(
                query,
                (json.dumps(topic_data), uuid.UUID(result_id))
            )
            
            print(f"Saved text analysis for result_id: {result_id}")
            return True
            
        except Exception as e:
            print(f"Error saving text analysis: {e}")
            return False

    def save_resume_points(self, result_id: str, points: List[str]) -> bool:
        """Save generated resume points to the database and return success status (bool)."""
        try:
            query = """
                UPDATE Results
                SET resume_points = %s
                WHERE result_id = %s;
            """
            self.db.execute_update(query, (json.dumps(points), uuid.UUID(result_id)))
            print(f"Saved resume points for result_id: {result_id}")
            return True
        except Exception as e:
            print(f"Error saving resume points: {e}")
            return False

    def save_package_analysis(self, result_id: str, insights: Dict[str, Any]) -> bool:
        """Save package analysis insights to the database and return success status (bool)."""
        try:
            query = """
                UPDATE Results
                SET package_insights = %s
                WHERE result_id = %s;
            """
            self.db.execute_update(query, (json.dumps(insights), uuid.UUID(result_id)))
            print(f"Saved package insights for result_id: {result_id}")
            return True
        except Exception as e:
            print(f"Error saving package insights: {e}")
            return False
    
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
            
            self.db.execute_update(
                query,
                (json.dumps(project_insights), uuid.UUID(result_id))
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
        bow_cache: Optional[List[List[str]]] = None,
        project_data: Optional[Dict[str, Any]] = None,
        package_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Save raw data to Tracked_Data table and return success status (bool)."""
        try:
            query = """
                INSERT INTO Tracked_Data (result_id, metadata_stats, bow_cache, project_data, package_data)
                VALUES (%s, %s, %s, %s, %s);
            """
            
            self.db.execute_update(
                query,
                (
                    uuid.UUID(result_id),
                    json.dumps(metadata_results),
                    json.dumps(bow_cache) if bow_cache else None,
                    json.dumps(project_data) if project_data else None,
                    json.dumps(package_data) if package_data else None
                )
            )
            
            print(f"Saved tracked data for result_id: {result_id}")
            return True
            
        except Exception as e:
            print(f"Error saving tracked data: {e}")
            return False
    
    def close(self):
        """Close the database connection (no-op as connections auto-close)."""
        # DB_connector uses context managers, so connections auto-close
        pass