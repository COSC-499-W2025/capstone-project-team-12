from typing import Dict, Any
import os

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


    def all_success_indicators(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combines all success indicators into a single dictionary
        """
        return {
            'deployment': {
                'cicd_tools': self.detect_deployment(project_data)
            }
        }