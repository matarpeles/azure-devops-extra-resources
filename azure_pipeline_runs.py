    import requests
    import json
    import base64

    # Replace 'YOUR INFO HERE' with your actual Port and Azure DevOps credentials
    PORT_CLIENT_ID = "<PORT CLIENT ID>"
    PORT_CLIENT_SECRET = "<PORT CLIENT SECRET"
    AZURE_DEVOPS_ORG_URL = "<Azure DevOps Org URL (https://dev.azure.com/<ORG NAME>)>"
    AZURE_DEVOPS_PAT = "<Azure DevOps Personal Access token>"
    API_URL = "https://api.getport.io/v1"

    # Bundle Port credentials for future use
    credentials = {'clientId': PORT_CLIENT_ID, 'clientSecret': PORT_CLIENT_SECRET}

    # Generate an API token for Port
    token_response = requests.post(
        f'{API_URL}/auth/access_token',
        json=credentials
    )

    access_token = token_response.json()['accessToken']

    # Create Port headers
    port_headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Define the Port blueprint ID to use for the Azure DevOps pipeline runs
    blueprint_id = 'azure_devops_pipeline_run'

    encoded_pat = base64.b64encode(f":{AZURE_DEVOPS_PAT}".encode()).decode()

    # Create Azure DevOps headers with Basic Auth using PAT
    azure_devops_headers = {
        'Authorization': f'Basic {encoded_pat}'
    }

    def get_projects():
        """
        Fetches all projects in the Azure DevOps organization.
        """
        url = f'{AZURE_DEVOPS_ORG_URL}/_apis/projects?api-version=6.0'
        response = requests.get(url, headers=azure_devops_headers)
        
        # Check if the response is successful
        if response.status_code != 200:
            print(f"Failed to fetch projects. Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
            response.raise_for_status()  # This will raise an HTTPError if the status is not 200

        # Attempt to parse JSON response
        try:
            return response.json()['value']
        except json.JSONDecodeError as e:
            print("Error decoding JSON response:", e)
            print("Response content:", response.text)
            raise

    def get_pipelines(project):
        """
        Fetches all pipeline definitions from Azure DevOps for a given project.
        """
        url = f'{AZURE_DEVOPS_ORG_URL}/{project}/_apis/pipelines?api-version=7.1'
        response = requests.get(url, headers=azure_devops_headers)
        response.raise_for_status()
        return response.json()['value']

    def get_pipeline_runs(project, pipeline_id):
        """
        Fetches all pipeline runs for a given pipeline ID and project from Azure DevOps.
        """
        url = f'{AZURE_DEVOPS_ORG_URL}/{project}/_apis/pipelines/{pipeline_id}/runs?api-version=6.0-preview.1'
        response = requests.get(url, headers=azure_devops_headers)
        response.raise_for_status()
        return response.json()['value']

    # Get all projects
    projects = get_projects()
    for project in projects:
        project_name = project['name']
        pipelines = get_pipelines(project_name)

        for pipeline in pipelines:
            # For each pipeline in the project, fetch its runs
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
                        "finished": run["finishedDate"]
                    },
                    "relations": {
                        "pipeline": str(pipeline['id'])
                        }
                    }
                
                
                # Push each pipeline run to Port
                response = requests.post(
                    f'{API_URL}/blueprints/{blueprint_id}/entities?upsert=true',
                    json=entity,
                    headers=port_headers
                )
                
                if response.status_code == 200:
                    print(f"Successfully ingested pipeline run {run['id']} from project {project_name} into Port with relation to pipeline {pipeline['id']}.")
                else:
                    print(f"Failed to ingest pipeline run {run['id']} from project {project_name} into Port. Status Code: {response.status_code}, Response: {response.text}")