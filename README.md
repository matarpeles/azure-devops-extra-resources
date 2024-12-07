
This guide explains how to set up and run each script. It includes instructions on setting environment variables, creating the required blueprints in Port, and running the scripts.

---

## Prerequisites

1. **Python**: Ensure you have Python 3.7+ installed.
2. **Dependencies**: Install required packages using:
   ```bash
   pip install requests
   ```
3. **Access**:
   - Azure DevOps account with appropriate permissions.
   - Port account with credentials for API access.
---

## 1. Setting Environment Variables

Before running any script, set the required environment variables. These credentials and configuration parameters are essential for interacting with Port and Azure DevOps APIs.

Run the following commands in your terminal to set up the environment:

```bash
export PORT_CLIENT_ID="your-port-client-id"
export PORT_CLIENT_SECRET="your-port-client-secret"
export AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-org"
export AZURE_DEVOPS_PAT="your-azure-devops-pat"
export PORT_API_URL="https://api.getport.io/v1"
export REPOS='[{"project_name": "Your Project", "repo_name": "Your Repo"}]'
export SWAGGER_PATH_PATTERN="**/swagger*.yaml"
export PIPELINE_BLUEPRINT_ID="azure_devops_pipeline_run"
export API_SPEC_BLUEPRINT_ID="api_spec"
export TARGET_PATH="/services"
```

Replace the placeholder values with your actual credentials and configuration.

---

## 2. Creating the Blueprints in Port

Each script interacts with specific blueprints in Port. Create the necessary blueprints in your Port account by following these steps:

### Blueprint: `azure_devops_pipeline_run`
- **Identifier**: `azure_devops_pipeline_run`
- **Schema**:
  ```json
  {
    "identifier": "azure_devops_pipeline_run",
    "title": "Azure DevOps Pipeline Run",
    "schema": {
      "properties": {
        "pipeline_name": {
          "type": "string",
          "title": "Pipeline Name"
        },
        "status": {
          "type": "string",
          "title": "Status"
        },
        "result": {
          "type": "string",
          "title": "Result"
        },
        "url": {
          "type": "string",
          "title": "URL",
          "format": "url"
        },
        "created_at": {
          "type": "string",
          "title": "Created At",
          "format": "date-time"
        },
        "finished": {
          "type": "string",
          "title": "Finished",
          "format": "date-time"
        }
      },
      "relations": {
        "pipeline": {
          "target": "pipeline",
          "title": "Pipeline",
          "required": false,
          "many": false
        }
      }
    }
  }
  ```

### Blueprint: `api_spec`
- **Identifier**: `api_spec`
- **Schema**:
  ```json
  {
    "identifier": "api_spec",
    "title": "API Spec",
    "schema": {
      "properties": {
        "swagger_ui": {
          "type": "string",
          "title": "Swagger UI",
          "format": "yaml",
          "spec": "open-api"
        }
      },
      "relations": {
        "service": {
          "target": "service",
          "title": "Service",
          "required": false,
          "many": false
        }
      }
    }
  }
  ```

---

## 3. Running the Script

1. Ensure the environment variables are set as shown above.
2. Run the script with Python:

   ```bash
   python <script_name>.py
   ```

Replace `<script_name>` with the name of the script you want to run.

---

## Example Workflow

1. **Set environment variables**:
   ```bash
   export PORT_CLIENT_ID="your-port-client-id"
   export PORT_CLIENT_SECRET="your-port-client-secret"
   ...
   ```
2. **Create blueprints**: Use the JSON schemas provided above in your Port account.
3. **Run the script**:
   ```bash
   python script_name.py
   ```

---

