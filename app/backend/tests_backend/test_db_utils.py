import pytest
from psycopg.types.json import Json
from db_utils import *


### Declaration of various types of Test JSON Objects
# These help ensure that JSON Objects of various complexities are handled
# IT DOES NOT REPRESENT VALID OUTPUTS OF OUR DATABASE AND IS INSTEAD PULLED FROM STACKOVERFLOW !!
# 1. Simple flat object
simple_json = {
    "name": "John Doe",
    "age": 30,
    "email": "john@example.com",
    "active": True
}

nested_json = {
    "user": {
        "id": 12345,
        "profile": {
            "firstName": "Jane",
            "lastName": "Smith",
            "contact": {
                "email": "jane@example.com",
                "phone": "+1-555-0123",
                "address": {
                    "street": "123 Main St",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10001"
                }
            }
        }
    },
    "metadata": {
        "created": "2024-01-15T10:30:00Z",
        "lastModified": "2024-11-18T14:22:00Z"
    }
}

array_json = {
    "user_id": 789,
    "tags": ["premium", "verified", "early-adopter"],
    "roles": ["admin", "moderator"],
    "recent_logins": [
        {"timestamp": "2024-11-18T09:00:00Z", "ip": "192.168.1.1"},
        {"timestamp": "2024-11-17T15:30:00Z", "ip": "192.168.1.2"},
        {"timestamp": "2024-11-16T08:45:00Z", "ip": "192.168.1.1"}
    ],
    "permissions": [
        {"resource": "users", "actions": ["read", "write", "delete"]},
        {"resource": "posts", "actions": ["read", "write"]},
        {"resource": "comments", "actions": ["read", "moderate"]}
    ]
}

mixed_types_json = {
    "string": "Hello World",
    "integer": 42,
    "float": 3.14159,
    "boolean_true": True,
    "boolean_false": False,
    "null_value": None,
    "empty_string": "",
    "empty_array": [],
    "empty_object": {},
    "large_number": 9999999999999999,
    "negative_number": -273.15,
    "scientific_notation": 1.23e-4
}

# 5. Edge cases and special characters
edge_cases_json = {
    "unicode": "Hello 世界 🌍",
    "special_chars": "Quote: \" Backslash: \\ Newline: \n Tab: \t",
    "html": "<div class='test'>HTML Content</div>",
    "sql": "SELECT * FROM users WHERE id = 1; DROP TABLE users;",
    "url": "https://example.com/path?param=value&other=123",
    "email": "test+tag@example.co.uk",
    "multiline": "Line 1\nLine 2\nLine 3",
    "spaces": "   leading and trailing spaces   "
}

db = None
@pytest.fixture
def set_db_Connector():
    global db 
    db = DB_connector('test_db')

def test_getting_connection():
    global db
    with pytest.raises(Exception) as e_info:
        db = DB_connector("postgresql://user:password@localhost:5432/user") #Check for Exception on invalid Arg
    
    db = DB_connector('test')  #Should not raise Exception, default valuse uses env variables for string
    assert db is not None
    assert type(db) is DB_connector
    assert db.test_connection() is not None



def test_inserts(set_db_Connector):
    global db
    
    #create Analysis first to satisfy Foreign Key constraint
    analysis_res = db.execute_update(
        "INSERT INTO Analyses DEFAULT VALUES RETURNING analysis_id",
        returning=True
    )
    analysis_id = analysis_res['analysis_id']

    #Testing Invalid Column Name Inserts
    with pytest.raises(Exception):
        uuid = db.execute_update(
        "INSERT INTO Results (analysis_id, topic_vector,resume_points,projeccct_insights,package_insights,metadata_insights) VALUES (%s, %s, %s, %s, %s, %s) RETURNING result_id",
        (analysis_id, "Sample String",Json(nested_json),Json(array_json),Json(mixed_types_json),Json(edge_cases_json)),
        returning=True
    )
    
    #Testing Valid Inserts
    #Note the database is not responsible for ensuring JSON files are in valid format accepted by our app.
    uuid = db.execute_update(
        "INSERT INTO Results (analysis_id, topic_vector,resume_points,project_insights,package_insights,metadata_insights) VALUES (%s, %s, %s, %s, %s, %s) RETURNING result_id",
        (analysis_id, Json("Sample String"),Json(nested_json),Json(array_json),Json(mixed_types_json),Json(edge_cases_json)),
        returning=True
    )
    print(f"Inserted Row with ID: {uuid}")
    return None

def test_query(set_db_Connector):
    global db
    
    #Test Invalid Query
    with pytest.raises(Exception):
        result = db.execute_query("SELECT * FROM Resilts") 
    
    #Test Valid Query
    result = db.execute_query("SELECT * FROM Results")
    print(result)
    return None
