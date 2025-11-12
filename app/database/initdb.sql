CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

SELECT uuid_generate_v4();

CREATE TABLE IF NOT EXISTS 
Results(
    result_id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    topic_vector varchar(300),
    resume_points JSON,
    project_insights JSON,
    package_insights JSON,
    metadata_insights JSON
);

CREATE TABLE IF NOT EXISTS 
Tracked_Data(
    dataID uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    result_id uuid REFERENCES Results(result_id) NOT NULL,
    bow_cache JSON,
    project_data JSON,
    package_data JSON,
    metadata_stats JSON
);


