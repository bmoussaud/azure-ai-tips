# Azure AI TIPS

This repository gathers a set of snippets of documentation or code about Azure AI Solutions

## Setup the environment

Fill the `.env` file with the following sensitive information

```
AZURE_SUBSCRIPTION_ID=your_subscription_id
YOUR_API_KEY=your_api_key
```

## Execution

There is a `Taskfile` that contains several atomic commands. If you have not already install it, please refer to [https://taskfile.dev/] web site

```
task: Available tasks for this project:
* azure_auth:                  Authenticate to Azure using Azure CLI
* clean_up:                    Clean up
* create_resource_group:       Create a resource group ${RG} in $LOCATION
* deploy_all:                  Deploy all
* deploy_dalle3:               Deploy DALLE-3
* deploy_gtp4o:                Deploy GPT4o
* deploy_open_ai:              Deploy Open AI
* list_deployments:            List deployments
```

![Title](logo.png "Title")
