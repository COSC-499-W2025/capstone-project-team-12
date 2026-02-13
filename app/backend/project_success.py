from typing import Dict, Any
from datetime import datetime

class ProjectSuccess:
    def __init__(self, project_data: Dict[str, Any]) -> None:
        self.project_data = project_data

    def detect_deployment(self):
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

        all_files = self.project_data.get('all_files', set())

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


    def version_control_success_indicators(self):
        """
        Analyzes version control activity such as commit consistency over project
        timeline, lines added/deleted per commit, total commits by lines added/deleted     
        """

        # Get all project info and dates
        repo_context = self.project_data.get('repository_context', {})
        total_commits = repo_context.get('total_commits_all_authors', 0)
        total_lines_added = repo_context.get('repo_total_lines_added', 0)
        total_lines_deleted = repo_context.get('repo_total_lines_deleted', 0)
        
        commit_dates = repo_context.get('all_commits_dates', [])
        commit_date_range = repo_context.get('repository_date_range', {})     
        start_date_str = commit_date_range.get('start_date')
        end_date_str = commit_date_range.get('end_date')
        duration_days = commit_date_range.get('duration_days', 1)

        if start_date_str and end_date_str:
            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)
        else:
            return {
                'avg_lines_per_commit': 0,
                'commit_consistency': 'No date information available'
            }

        commit_dates.sort()

        # Count the commits in the last quarter of the project timeline
        last_quarter_start = start_date + (end_date - start_date) * 0.75
        last_quarter_commits = sum(1 for date in commit_dates if date >= last_quarter_start)
        
        # Find the percentage of commits made in the last 
        last_quarter_percentage = (last_quarter_commits / total_commits) * 100 if total_commits > 0 else 0
        
        # Map percentage to a blurb
        if last_quarter_percentage >= 75:
            activity_blurb = f"Commits were crammed at the end. {last_quarter_percentage:.1f}% of commits were made in the last quarter."
        elif last_quarter_percentage > 45:
            activity_blurb = f"Commits were end-heavy. {last_quarter_percentage:.1f}% of commits were made in the last quarter."
        else:
            activity_blurb = f"Commits were well-distributed. {last_quarter_percentage:.1f}% of commits were made in the last quarter."

        # Calculate average lines modified per commit
        all_line_modifications = total_lines_added + total_lines_deleted
        lines_per_commit = all_line_modifications / total_commits if total_commits > 0 else 0


        return {
            'avg_lines_per_commit': round(lines_per_commit, 2),
            'commit_consistency': activity_blurb,
        }



    def all_success_indicators(self) -> Dict[str, Any]:
        """
        Combines all success indicators into a single dictionary
        """
        return {
            'deployment': self.detect_deployment(),
            'version_control': self.version_control_success_indicators()
        }