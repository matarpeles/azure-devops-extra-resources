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

def fetch_folders_in_path(project_name, repo_name, path):
    """
    Fetches the immediate folders in the specified path for a repository.
    """
    url = f'{AZURE_DEVOPS_ORG_URL}/{project_name}/_apis/git/repositories/{repo_name}/items?scopePath={path}&recursionLevel=OneLevel&api-version=6.0'
    response = requests.get(url, headers=azure_devops_headers)
    response.raise_for_status()

    # Filter results to include only folders
    all_items = response.json().get('value', [])
    folders = [
        item['path']
        for item in all_items
        if item['isFolder'] and item['path'].startswith(path) and item['path'] != path
    ]
    return folders

def fetch_readme_content(project_name, repo_name, folder_path):
    """
    Fetches the content of a README file from the specified folder path.
    """
    readme_files = ["README.md", "README.txt"]  # Add other possible README file names if needed
    for readme in readme_files:
        readme_path = f"{folder_path}/{readme}"
        url = f'{AZURE_DEVOPS_ORG_URL}/{project_name}/_apis/git/repositories/{repo_name}/items?path={readme_path}&api-version=6.0'
        response = requests.get(url, headers=azure_devops_headers)

    if response.status_code > 200 or response.status_code < 300:
            return response.text  # Return the content if the file is found

    # Return None if no README file is found
    return None

def push_service_to_port(identifier, title, url, readme):
    """
    Pushes a service entity to the Port `service` blueprint.
    """
    entity = {
        "identifier": identifier,
        "title": title,
        "properties": {
            "url": url,
            "readme": readme if readme else "No README found."
        }
    }
    response = requests.post(
        f'{API_URL}/blueprints/service/entities?upsert=true',
        json=entity,
        headers=port_headers
    )
    response.raise_for_status()
    print(f"Successfully pushed service {identifier} to Port.")

def main():
    # Load configuration from environment variables or defaults
    monorepos = json.loads(os.getenv("REPOS", '[{"project_name": "Matar Project", "repo_name": "Matar Project"}]'))
    target_path = os.getenv("TARGET_PATH", "/services")

    for repo_config in monorepos:
        project_name = repo_config['project_name']
        repo_name = repo_config['repo_name']

        print(f"Fetching folders in '{target_path}' from {project_name}/{repo_name}...")
        try:
            folders = fetch_folders_in_path(project_name, repo_name, target_path)

            for folder in folders:
                # Generate service identifier and title
                folder_name = folder.split("/")[-1]  # Extract folder name
                identifier = f"{repo_name}-{folder_name}".replace(" ", "_").lower()
                title = folder_name

                # Generate service URL
                url = f"{AZURE_DEVOPS_ORG_URL}/{project_name}/_git/{repo_name}?path={folder}"

                # Fetch README content
                readme = fetch_readme_content(project_name, repo_name, folder)

                # Push service to Port
                push_service_to_port(identifier, title, url, readme)

        except requests.exceptions.HTTPError as e:
            print(f"Failed to fetch folders for {repo_name}. Error: {e}")

if __name__ == "__main__":
    main()
