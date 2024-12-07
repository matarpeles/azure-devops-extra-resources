import requests
import json
import base64
import os
import re   
import fnmatch

# Load sensitive credentials and configuration from environment variables
PORT_CLIENT_ID = os.getenv("PORT_CLIENT_ID")
PORT_CLIENT_SECRET = os.getenv("PORT_CLIENT_SECRET")
AZURE_DEVOPS_ORG_URL = os.getenv("AZURE_DEVOPS_ORG_URL")
AZURE_DEVOPS_PAT = os.getenv("AZURE_DEVOPS_PAT")
API_URL = os.getenv("PORT_API_URL", "https://api.getport.io/v1")
API_SPEC_BLUEPRINT_ID = os.getenv("API_SPEC_BLUEPRINT_ID", "api_spec")

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

def sanitize_identifier(input_string):
    """
    Sanitizes an identifier by replacing invalid characters with underscores.
    """
    return re.sub(r"[^A-Za-z0-9@_.+:\\\/=-]", "_", input_string)

def fetch_files_in_repo(project_name, repo_name, path_pattern):
    """
    Fetch files matching the given path pattern in a repository.
    """
    url = f'{AZURE_DEVOPS_ORG_URL}/{project_name}/_apis/git/repositories/{repo_name}/items?recursionLevel=Full&api-version=6.0'
    response = requests.get(url, headers=azure_devops_headers)
    response.raise_for_status()

    # Filter files matching the path pattern
    all_files = response.json().get('value', [])
    return [
        {"path": file['path'], "id": file['objectId']}
        for file in all_files
        if fnmatch.fnmatch(file['path'], path_pattern)
    ]

def fetch_file_content(project_name, repo_name, file_path):
    """
    Fetches the content of a specific file in a repository.
    """
    url = f'{AZURE_DEVOPS_ORG_URL}/{project_name}/_apis/git/repositories/{repo_name}/items?path={file_path}&api-version=6.0'
    response = requests.get(url, headers=azure_devops_headers)
    response.raise_for_status()
    return response.text

def push_to_port_blueprint(blueprint_id, file_id, title, swagger_content, service_id):
    """
    Pushes an API spec to the `api_spec` blueprint in Port.
    """
    print(f"Pushing file with ID {file_id} to Port...")
    entity = {
        "identifier": file_id,
        "title": title,
        "properties": {
            "swagger_ui": swagger_content
        },
        "relations": {
            "service": service_id
        }
    }

    response = requests.post(
        f'{API_URL}/blueprints/{blueprint_id}/entities?upsert=true',
        json=entity,
        headers=port_headers
    )
    if 200 <= response.status_code < 300:
        print(f"Successfully pushed API spec {file_id} to Port.")
    else:
        print(f"Failed to push API spec {file_id} to Port. Response: {response.text}")

def main():
    # Configuration
    repos = json.loads(os.getenv("REPOS", '[{"project_name": "Matar Project", "repo_name": "Matar Project"}]'))
    swagger_path_pattern = os.getenv("SWAGGER_PATH_PATTERN", "**/swagger*.yaml")

    for repo_config in repos:
        project_name = repo_config['project_name']
        repo_name = repo_config['repo_name']
        repo_id = f"{project_name}/{repo_name}"
        service_id = re.sub(r"[ ();]", "", repo_id.lower())

        print(f"Fetching Swagger files from {project_name}/{repo_name}...")
        swagger_files = fetch_files_in_repo(project_name, repo_name, swagger_path_pattern)

        for file in swagger_files:
            file_path = file['path']
            file_name = f"{repo_name}-{os.path.basename(file['path'])}"
            swagger_content = fetch_file_content(project_name, repo_name, file_path)

            push_to_port_blueprint(
                API_SPEC_BLUEPRINT_ID,
                file_id=sanitize_identifier(file_name),
                title=file_name,
                swagger_content=swagger_content,
                service_id=service_id
            )

if __name__ == "__main__":
    main()
