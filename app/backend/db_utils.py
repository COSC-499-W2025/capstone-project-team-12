import psycopg
from psycopg.rows import dict_row
from contextlib import contextmanager
from psycopg.types.json import Json
import os
import regex as re


class DB_connector:
    
    """Simple PostgreSQL connection handler using psycopg 3"""
    def __init__(self,database_name = os.environ['DBNAME']):
        """
        Initialize database connector
        
        Args:
         database_name: Has default value derived from user docker environment, provide custom value 'test' to use test database
        """
        
        #Validate passed value as valid postgresql dbname
        if not re.fullmatch(re.compile("^[A-Za-z][A-Za-z0-9_]*$"),database_name):
            raise ValueError('Not a valid sql db name!')
        else:
            self.database_name = database_name
        
    @contextmanager
    def get_connection(self):
        """
        Get a database connection with automatic close
        
       
        
        Usage:
            with connector.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM table")
                    results = cur.fetchall()
        """
        conn = None
        try:
            conn = psycopg.connect(
                host = os.environ['HOST'],
                user = os.environ['USER'],
                password = os.environ['PASS'],
                dbname= self.database_name,
                port = os.environ['PORT'],
                row_factory=dict_row,
                autocommit=False,
            )
            yield conn
        except Exception as e:
            print(f"Connection Error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def test_connection(self) -> bool:
        """Test if connection is working"""
        try:
            result = self.fetch_one("SELECT 1 as test")
            return result is not None and result.get('test') == 1
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def execute_query(self, query: str, params: tuple = None) -> list[dict]:
        """
        Execute a SELECT query and return results as list of dicts
        
        Args:
            query: SQL query string
            params: Query parameters (use %s placeholders)
            
        Returns:
            List of dictionaries with column names as keys
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    results = cursor.fetchall()
                    print(f"Query Successful: Result has {len(results)} rows")
                    return results
        except Exception as e:
            print(f"Query execution failed: {e}")
            raise
        
    def execute_update(self, query: str, params: tuple = None, returning: bool = False):
        """
        Execute INSERT/UPDATE/DELETE query
        
        Args:
            query: SQL query string (use RETURNING clause if returning=True)
            params: Query parameters
            returning: If True, return the fetched result instead of rowcount
            
        Returns:
            Number of affected rows, or returned data if returning=True
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    conn.commit()
                    
                    if returning:
                        return cur.fetchone()
                    else:
                        affected = cur.rowcount
                        print(f"Query affected {affected} rows")
                        return affected
        except Exception as e:
            print(f"Update execution failed: {e}")
            raise