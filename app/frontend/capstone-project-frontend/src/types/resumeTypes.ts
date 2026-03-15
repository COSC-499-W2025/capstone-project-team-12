// These types mirror the structure of the resume data that we expect to receive from the backend.
// The output comes from _build_resume() in resume_builder.py, which is a dictionary with the following structure:

export interface Project {
    name: string;
    date_range: string;
    collaboration_insight: string;   // user_role.blurb from infer_user_role()
    frameworks: string[];   // top 5 imports from _get_top_frameworks()
}
// TODO: For Milestone 3, we will likely need to add more fields to the Project interface to capture additional information 
// that we want to display in the resume, such as contribution percentage, number of commits, etc to satisfy evidence of success req.

export interface Language {
    name: string;
    file_count: number;
}

export interface Resume {
    analysis_id: string;
    summary: string;
    projects: Project[];
    skills: string[];   // This is for the flat list of skills from extract_metadata_skills()
    languages: Language[];

    // TODO: (for backend) we collect GitHub username and email in run_repo_analysis(), but we don't currently return it in the resume data. 
    // We should add these fields here and return them from the backend, since they are important pieces of information to display in the resume.
    github_username?: string;
    user_email?: string;
}



