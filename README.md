
# Getting Started

This guide explains how to set up and run each script in the repository. Each section includes the required blueprints, environment variables, and instructions for running the script.

---

## Prerequisites 
- Install the [Port Azure DevOps integration](https://docs.getport.io/build-your-software-catalog/sync-data-to-catalog/git/azure-devops/installation)
- Retrieve your [Port credentials](https://docs.getport.io/build-your-software-catalog/sync-data-to-catalog/code-quality-security/wiz#port-credentials)
- Create a [Personal Access token](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=Windows) in Azure DevOps
- Retrieve your organization url in Azure DevOps

## Scripts Overview

### 1. `ingesting-monorepos/ado-monorepos.py`
- Ingests monorepos from Azure DevOps and maps them to the Service blueprint in Port.

### 2. `ingesting-pipeline-runs/azure_pipeline_runs.py`
- Ingests Azure DevOps pipeline runs and maps them to the `azure_devops_pipeline_run` blueprint.

### 3. `ingesting-repo-files/api-specs/api-specs.py`
- Ingests API specs from repository files and maps them to the `api_spec` blueprint.

---

## Script: `ingesting-monorepos/ado-monorepos.py`

### 1. Blueprints

#### Blueprint: `monorepo`
- **Identifier**: `monorepo`
- **Schema**:
  ```json
  {
    "identifier": "monorepo",
    "title": "Monorepo",
    "schema": {
      "properties": {
        "name": {
          "type": "string",
          "title": "Name"
        },
        "description": {
          "type": "string",
          "title": "Description"
        },
        "url": {
          "type": "string",
          "title": "Repository URL",
          "format": "url"
        }
      }
    }
  }
  ```

### 2. Setting Environment Variables

Run the following commands:

```bash
export PORT_CLIENT_ID="your-port-client-id"
export PORT_CLIENT_SECRET="your-port-client-secret"
export AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-org"
export AZURE_DEVOPS_PAT="your-azure-devops-pat"
export PORT_API_URL="https://api.getport.io/v1"
export REPOS='[{"project_name": "Your Project", "repo_name": "Your Repo"}]'
export TARGET_PATH="/services"
```

### 3. Running the Script

Run the script using:

```bash
python ingesting-monorepos/ado-monorepos.py
```

---

## Script: `ingesting-pipeline-runs/azure_pipeline_runs.py`

### 1. Blueprints

#### Blueprint: `azure_devops_pipeline_run`
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
      }
    }
  }
  ```

### 2. Setting Environment Variables

Run the following commands:

```bash
export PORT_CLIENT_ID="your-port-client-id"
export PORT_CLIENT_SECRET="your-port-client-secret"
export AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-org"
export AZURE_DEVOPS_PAT="your-azure-devops-pat"
export PORT_API_URL="https://api.getport.io/v1"
export PIPELINE_BLUEPRINT_ID="azure_devops_pipeline_run"
```

### 3. Running the Script

Run the script using:

```bash
python ingesting-pipeline-runs/azure_pipeline_runs.py
```

---

## Script: `ingesting-repo-files/api-specs/api-specs.py`

### 1. Blueprints

#### Blueprint: `api_spec`
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

### 2. Setting Environment Variables

Run the following commands:

```bash
export PORT_CLIENT_ID="your-port-client-id"
export PORT_CLIENT_SECRET="your-port-client-secret"
export AZURE_DEVOPS_ORG_URL="https://dev.azure.com/your-org"
export AZURE_DEVOPS_PAT="your-azure-devops-pat"
export PORT_API_URL="https://api.getport.io/v1"
export API_SPEC_BLUEPRINT_ID="api_spec"
export SWAGGER_PATH_PATTERN="**/swagger*.yaml"
```

### 3. Running the Script

Run the script using:

```bash
python ingesting-repo-files/api-specs/api-specs.py
```

---

This guide ensures you can set up and execute each script securely and effectively.
