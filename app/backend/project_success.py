from typing import Dict, Any
from datetime import datetime

class ProjectSuccess:
    def __init__(self, project_data: Dict[str, Any]) -> None:
        self.project_data = project_data;

    def detect_deployment(self, project_data: Dict[str, Any]):
        """
        Detects if the project has deployment configuration using file ext
        """
        # CI/CD pipeline indicators
        cicd_files = {
            '.github/workflows/': 'GitHub Actions',
            '.gitlab-ci.yml': 'GitLab CI',
            '.travis.yml': 'Travis CI',
            'jenkinsfile': 'Jenkins',
            '.circleci/config.yml': 'CircleCI',
            'azure-pipelines.yml': 'Azure Pipelines',
            '.drone.yml': 'Drone CI'
        }
        
        # Containerization indicators
        container_files = {
            'dockerfile': 'Docker',
            'docker-compose.yml': 'Docker Compose',
            'docker-compose.yaml': 'Docker Compose',
            '.dockerignore': 'Docker'
        }
        
        # Cloud/hosting platform indicators
        platform_files = {
            'vercel.json': 'Vercel',
            'netlify.toml': 'Netlify',
            'render.yaml': 'Render',
            'railway.json': 'Railway',
            'railway.toml': 'Railway',
            'fly.toml': 'Fly.io',
            'heroku.yml': 'Heroku',
            'procfile': 'Heroku',
            'app.yaml': 'Google App Engine',
            'serverless.yml': 'Serverless Framework',
            'amplify.yml': 'AWS Amplify',
            '.platform.app.yaml': 'Platform.sh',
            'cloudbuild.yaml': 'Google Cloud Build'
        }

        detected_cicd = set()
        detected_containers = set()
        detected_platforms = set()

        all_files = project_data.get('all_files', set())

        for file in all_files:
            for pattern, platform in cicd_files.items():
                if pattern in file:
                    detected_cicd.add(platform)
            for pattern, platform in container_files.items():
                if pattern in file:
                    detected_containers.add(platform)
            for pattern, platform in platform_files.items():
                if pattern in file:
                    detected_platforms.add(platform)
        
        return {
            'has_cicd': len(detected_cicd) > 0,
            'cicd_tools': list(detected_cicd),
            'has_containerization': len(detected_containers) > 0,
            'containerization_tools': list(detected_containers),
            'has_hosting_platform': len(detected_platforms) > 0,
            'hosting_platforms': list(detected_platforms)
        }


    def version_control_success_indicators(self, project_data: Dict[str, Any]):
        """
        Analyzes version control activity such as commit consistency over project
        timeline, lines added/deleted per commit, total commits by lines added/deleted     
        """

        # Get all project info and dates
        repo_context = project_data.get('repository_context', {})
        total_commits = repo_context.get('total_commits_all_authors', 0)
        total_lines_added = repo_context.get('repo_total_lines_added', 0)
        total_lines_deleted = repo_context.get('repo_total_lines_deleted', 0)
        dates_info = project_data.get('dates', {})
        start_date_str = dates_info.get('start_date')
        end_date_str = dates_info.get('end_date')
        duration_days = dates_info.get('duration_days', 0)
        duration_seconds = dates_info.get('duration_seconds', 0)
        commit_dates = project_data.get('all_commits_dates', [])
        commit_date_range = project_data.get('repository_date_range', {})

        commit_dates.sort()

        # Calculate average lines modified per commit
        all_line_modifications = total_lines_added + total_lines_deleted
        lines_per_commit = all_line_modifications / total_commits if total_commits > 0 else 0


        return {
            avg_lines_per_commit': lines_per_commit,
        }



    def all_success_indicators(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combines all success indicators into a single dictionary
        """
        return {
            'deployment': {
                'cicd_tools': self.detect_deployment(project_data)
            }
        }