import requests
import json
import base64
import os

# Load sensitive credentials and URLs from environment variables
PORT_CLIENT_ID = os.getenv("PORT_CLIENT_ID")
PORT_CLIENT_SECRET = os.getenv("PORT_CLIENT_SECRET")
AZURE_DEVOPS_ORG_URL = os.getenv("AZURE_DEVOPS_ORG_URL")
AZURE_DEVOPS_PAT = os.getenv("AZURE_DEVOPS_PAT")
API_URL = os.getenv("PORT_API_URL", "https://api.getport.io/v1")
BLUEPRINT_ID = os.getenv("PIPELINE_BLUEPRINT_ID", "azure_devops_pipeline_run")

# Ensure required environment variables are set
if not all([PORT_CLIENT_ID, PORT_CLIENT_SECRET, AZURE_DEVOPS_ORG_URL, AZURE_DEVOPS_PAT]):
    raise EnvironmentError("Missing required environment variables: PORT_CLIENT_ID, PORT_CLIENT_SECRET, AZURE_DEVOPS_ORG_URL, AZURE_DEVOPS_PAT")

# Port Headers
credentials = {'clientId': PORT_CLIENT_ID, 'clientSecret': PORT_CLIENT_SECRET}
token_response = requests.post(f'{API_URL}/auth/access_token', json=credentials)
token_response.raise_for_status()
access_token = token_response.json()['accessToken']
port_headers = {'Authorization': f'Bearer {access_token}'}

# Azure DevOps Headers
encoded_pat = base64.b64encode(f":{AZURE_DEVOPS_PAT}".encode()).decode()
azure_devops_headers = {'Authorization': f'Basic {encoded_pat}'}

def get_projects():
    """
    Fetches all projects in the Azure DevOps organization.
    """
    url = f'{AZURE_DEVOPS_ORG_URL}/_apis/projects?api-version=6.0'
    response = requests.get(url, headers=azure_devops_headers)
    if not 200 <= response.status_code < 300:
        raise requests.exceptions.RequestException(f"Failed to fetch projects: {response.text}")
    return response.json().get('value', [])

def get_pipelines(project):
    """
    Fetches all pipeline definitions from Azure DevOps for a given project.
    """
    url = f'{AZURE_DEVOPS_ORG_URL}/{project}/_apis/pipelines?api-version=7.1'
    response = requests.get(url, headers=azure_devops_headers)
    if not 200 <= response.status_code < 300:
        raise requests.exceptions.RequestException(f"Failed to fetch pipelines for project {project}: {response.text}")
    return response.json().get('value', [])

def get_pipeline_runs(project, pipeline_id):
    """
    Fetches all pipeline runs for a given pipeline ID and project from Azure DevOps.
    """
    url = f'{AZURE_DEVOPS_ORG_URL}/{project}/_apis/pipelines/{pipeline_id}/runs?api-version=6.0-preview.1'
    response = requests.get(url, headers=azure_devops_headers)
    if not 200 <= response.status_code < 300:
        raise requests.exceptions.RequestException(f"Failed to fetch runs for pipeline {pipeline_id} in project {project}: {response.text}")
    return response.json().get('value', [])

def push_to_port(entity):
    """
    Pushes an entity to Port's specified blueprint.
    """
    response = requests.post(
        f'{API_URL}/blueprints/{BLUEPRINT_ID}/entities?upsert=true',
        json=entity,
        headers=port_headers
    )
    if not 200 <= response.status_code < 300:
        print(f"Failed to push entity {entity['identifier']} to Port. Response: {response.text}")
    else:
        print(f"Successfully pushed entity {entity['identifier']} to Port.")

def main():
    # Fetch all projects
    projects = get_projects()
    for project in projects:
        project_name = project['name']
        pipelines = get_pipelines(project_name)

        for pipeline in pipelines:
            # Fetch all pipeline runs for the current pipeline
            pipeline_runs = get_pipeline_runs(project_name, pipeline['id'])

            for run in pipeline_runs:
                entity = {
                    "identifier": f"{run['id']}",
                    "title": f"Run {run['id']} for Pipeline {pipeline['name']}",
                    "properties": {
                        "pipeline_name": pipeline['name'],
                        "status": run['state'],
                        "result": run.get('result', 'N/A'),
                        "url": f"{AZURE_DEVOPS_ORG_URL}/{project_name}/_build/results?buildId={run['id']}",
                        "created_at": run["createdDate"],
                        "finished": run.get("finishedDate", None)  # Handle cases where 'finishedDate' is not present
                    },
                    "relations": {
                        "pipeline": str(pipeline['id'])
                    }
                }
                # Push pipeline run to Port
                push_to_port(entity)

if __name__ == "__main__":
    main()
