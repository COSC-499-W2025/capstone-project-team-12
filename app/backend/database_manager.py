import json
import uuid
from typing import Dict, Any, List, Optional, Tuple, BinaryIO
from datetime import datetime
from db_utils import DB_connector

# new commit qebfkjebkjfe
# REMEMBER TO REPLACE THE FUNCT NAMES IN REPO

class DatabaseManager:
    def __init__(self):
        """Initialize database connection."""
        self.db = DB_connector()
    

    # old funct name: create_new_result(self) -> str:

    def create_analyses(self) -> str:
        """Create a new result entry and return its result_id UUID (str)."""
        try:
            #central record
            query = """
                INSERT INTO Analyses DEFAULT VALUES
                RETURNING analysis_id;
            """
            res_analysis = self.db.execute_update(query, returning=True)
            
            if not res_analysis:
                raise Exception("Failed to generate analysis_id")

            analysis_id = str(res_analysis['analysis_id'])
            
            a_uuid = uuid.UUID(analysis_id) #convert to UUID object for foreign key

            #start associated records: results, tracked_data, resumes, portfolio, 
            
            #results
            query_res = "INSERT INTO Results (analysis_id) VALUES (%s);"
            r_row = self.db.execute_update(query_res, (a_uuid))

            #tracked_data
            query_td = "INSERT INTO Tracked_Data (analysis_id) VALUES (%s);"
            td_row = self.db.execute_update(query_td, (a_uuid))

            #resumes
            query_resume = "INSERT INTO Resumes (analysis_id) VALUES (%s);"
            resume_row = self.db.execute_update(query_resume, (a_uuid))

            #proftfolio
            query_pfo = "INSERT INTO Results (analysis_id) VALUES (%s);"
            pfo_row = self.db.execute_update(query_pfo, (a_uuid))
        except Exception as e:
            print(f"Error creating new analyses: {e}")
            raise


    #now starting this
    #need to update 
    #updated
    def save_metadata_analysis(
        self, 
        analysis_id: str, 
        metadata_insights: Dict[str, Any]
    ) -> bool:
        """Save metadata analysis results to the database and return success status (bool)."""
        try:
            query = """
                UPDATE Results
                SET metadata_insights = %s
                WHERE analysis_id = %s;
            """
            
            self.db.execute_update(
                query, 
                (json.dumps(metadata_insights, default=str), uuid.UUID(analysis_id))
            )
            
            #good till now
            print(f"Saved metadata analysis for analysis_id: {analysis_id}")
            return True
            
        except Exception as e:
            print(f"Error saving metadata analysis: {e}")
            return False


    #updated
    def save_text_analysis(
        self,
        analysis_id: str,
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
                WHERE analysis_id = %s;
            """
            
            self.db.execute_update(
                query,
                (json.dumps(topic_data), uuid.UUID(analysis_id))
            )
            
            print(f"Saved text analysis for analysis_id: {analysis_id}")
            return True
            
        except Exception as e:
            print(f"Error saving text analysis: {e}")
            return False
    #done
    #will probably have to modify the output for the llm results
    def save_resume_points(self, analysis_id: str, points: List[str]) -> bool:
        """Save generated resume points to the database and return success status (bool)."""
        try:
            query = """
                UPDATE Results
                SET resume_points = %s
                WHERE analysis_id = %s;
            """
            self.db.execute_update(query, (json.dumps(points), uuid.UUID(analysis_id)))
            print(f"Saved resume points for analysis_id: {analysis_id}")
            return True
        except Exception as e:
            print(f"Error saving resume points: {e}")
            return False

    #done
    def save_package_analysis(self, analysis_id: str, insights: Dict[str, Any]) -> bool:
        """Save package analysis insights to the database and return success status (bool)."""
        try:
            query = """
                UPDATE Results
                SET package_insights = %s
                WHERE analysis_id = %s;
            """
            self.db.execute_update(query, (json.dumps(insights), uuid.UUID(analysis_id)))
            print(f"Saved package insights for analysis_id: {analysis_id}")
            return True
        except Exception as e:
            print(f"Error saving package insights: {e}")
            return False
    #updated
    def save_repository_analysis(
        self,
        analysis_id: str,
        project_analysis_data: Dict[str, Any]
    ) -> bool:
        """Save repository analysis results to the database and return success status (bool).
        Includes the processed repositories, analyzed insights, and the timeline with the relevant 
        project data.
        Thus project_analysis_data: Dict contaning:
            - analyzed_insights: Detailed project insights generated for ALL projects
            - timeline: Basic project information sorted in chronological order for timeline output
        
        """
        try:
            query = """
                UPDATE Results
                SET project_insights = %s
                WHERE analysis_id = %s;
            """
            
            self.db.execute_update(
                query,
                (json.dumps(project_analysis_data, default=str), uuid.UUID(analysis_id))
            )
            
            print(f"Saved repository analysis for analysis_id: {analysis_id}")
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
                    json.dumps(bow_cache) if bow_cache is not None else None,
                    json.dumps(project_data, default=str) if project_data is not None else None,
                    json.dumps(package_data) if package_data is not None else None
                )
            )
            
            print(f"Saved tracked data for result_id: {result_id}")
            return True
            
        except Exception as e:
            print(f"Error saving tracked data: {e}")
            return False

    def get_result_by_id(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a complete result and its tracked data by its ID."""
        try:
            query = """
                SELECT 
                    r.result_id,
                    r.topic_vector,
                    r.resume_points,
                    r.project_insights,
                    r.package_insights,
                    r.metadata_insights,
                    t.bow_cache,
                    t.project_data,
                    t.package_data,
                    t.metadata_stats
                FROM Results r
                LEFT JOIN Tracked_Data t ON r.result_id = t.result_id
                WHERE r.result_id = %s;
            """
            results = self.db.execute_query(query, (uuid.UUID(result_id),))
            
            if not results:
                return None

            #main result data
            row = results[0]
            result_data = {
                "result_id": str(row['result_id']),
                "topic_vector": row['topic_vector'],
                "resume_points": row['resume_points'],
                "project_insights": row['project_insights'],
                "package_insights": row['package_insights'],
                "metadata_insights": row['metadata_insights'],
                "tracked_data": {
                    "bow_cache": row['bow_cache'],
                    "project_data": row['project_data'],
                    "package_data": row['package_data'],
                    "metadata_stats": row['metadata_stats']
                }
            }
            return result_data
            
        except Exception as e:
            print(f"Error retrieving result by ID: {e}")
            return None

    def get_all_results_summary(self) -> List[Dict[str, Any]]:
        """Retrieve a summary of all results from the database."""
        try:
            query = "SELECT result_id, metadata_insights FROM Results ORDER BY result_id;"
            results = self.db.execute_query(query)
            #convert UUID to string for JSON compatibility if needed later
            for result in results:
                result['result_id'] = str(result['result_id'])
            return results
        except Exception as e:
            print(f"Error retrieving all results: {e}")
            return []

    def delete_result(self, result_id: str) -> bool:
        """Delete a result and its associated tracked data from the database."""
        try:
            #delete from Tracked_Data due to the foreign key constraint
            delete_tracked_query = "DELETE FROM Tracked_Data WHERE result_id = %s;"
            self.db.execute_update(delete_tracked_query, (uuid.UUID(result_id),))
            
            #then delete from Results
            delete_result_query = "DELETE FROM Results WHERE result_id = %s;"
            self.db.execute_update(delete_result_query, (uuid.UUID(result_id),))
            
            print(f"Successfully deleted result and associated data for result_id: {result_id}")
            return True
        except Exception as e:
            print(f"Error deleting result: {e}")
            return False

    def wipe_all_data(self) -> bool:
        """Delete all records from both Results and Tracked_Data tables."""
        try:
            # TRUNCATE is faster and resets any auto-incrementing counters.
            # CASCADE handles the foreign key relationship automatically.
            query = "TRUNCATE TABLE Results, Tracked_Data RESTART IDENTITY CASCADE;"
            self.db.execute_update(query)
            print("Successfully wiped all data from Results and Tracked_Data tables.")
            return True
        except Exception as e:
            print(f"Error wiping database tables: {e}")
            return False
    
    def save_result_thumbnail(self,result_id:str,data:BinaryIO):
        """Insert the binary data of provided image binary into DB for a particular result"""
        
        try:
            #Sepera
            query = "UPDATE Results SET thumbnail_image= %s WHERE result_id = %s;"
            self.db.execute_update(query,(data,result_id)) #tuple of bin data as string and result_id
            
            print(f"Successfully added thumbnail image to result with result_id:{result_id}")
            return True
        except Exception as e:
            print(f"Error Inserting image to result:{e}")
            return False
            
    def close(self):
        """Close the database connection."""
        #DB_connector uses context managers, so connections auto-close
        pass