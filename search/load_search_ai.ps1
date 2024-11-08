$AZURE_REGION="France Central"

$prefix="contosobm"
$RG="ContosoHotel"
$INDEX=$(Get-Random -Minimum 100000 -Maximum 999999)
$STORAGE_ACCOUNT_NAME="sto$prefix$INDEX"
$SEARCH_SERVICE_NAME="srch$prefix$INDEX"
$AI_RESOURCE_NAME="openai$prefix$INDEX"
#$AI_RESOURCE_NAME="aqanqmyfutth2-openai" 
$PATH_TO_DOWNLOADS_FOLDER="C:\Users\bmoussaud\Workspaces\ContosoHotel\AssetRepo\TechExcel-Modernize-applications-to-be-AI-ready\Assets\PDFs"  
Write-Host "Azure Region: $AZURE_REGION"
Write-Host "Search Service Name: $SEARCH_SERVICE_NAME"
Write-Host "AI Resource Name: $AI_RESOURCE_NAME"
Write-Host "Storage Account Name: $STORAGE_ACCOUNT_NAME"
pause

#1. Configure the Azure OpenAI and Azure AI Search instances to use system-assigned managed identities.
Write-Host "Creating Azure Search Service, Azure OpenAI Service, and Azure Storage Account..."
Write-Host "Creating Azure OpenAI Service..."
az cognitiveservices account create -n $AI_RESOURCE_NAME -g $RG -l $AZURE_REGION --kind OpenAI --sku s0 --assign-identity --custom-domain $AI_RESOURCE_NAME 
pause 
Write-Host "Creating Azure Storage Account..."
az storage account create --name $STORAGE_ACCOUNT_NAME --resource-group $RG --location $AZURE_REGION --sku Standard_LRS
az storage container create --name brochures --account-name $STORAGE_ACCOUNT_NAME
Write-Host "Creating Azure Search Service..."
az search service create --name $SEARCH_SERVICE_NAME --resource-group $RG --sku Basic --location $AZURE_REGION  --auth-options aadOrApiKey --aad-auth-failure-mode http403 --identity-type SystemAssigned
pause 
# Deploy GPT-4o model
$DEPLOYMENT_NAME="gpt4o-deployment"
$MODEL_NAME="gpt-4o"

# deploy GPT 4.0 model using AZ CLI does not work 
# az cognitiveservices account deployment create --resource-group $RG --name $AI_RESOURCE_NAME --deployment-name $DEPLOYMENT_NAME --model-name $MODEL_NAME --model-version "4.0" --scale-settings-scale-type "Standard"

# 2. Configure a managed identity to allow the Azure AI Search and Azure OpenAI instances to access the Azure Blob Storage account.
Write-Host "Configure a managed identity to allow the Azure AI Search and Azure OpenAI instances to access the Azure Blob Storage account."
$SEARCH_SERVICE_IDENTITY=$(az search service show --name $SEARCH_SERVICE_NAME --resource-group $RG --query "identity.principalId" --output tsv)
$AI_RESOURCE_IDENTITY=$(az cognitiveservices account show --name $AI_RESOURCE_NAME --resource-group $RG --query "identity.principalId" --output tsv)
$STORAGE_SCOPE=$(az storage account show --name $STORAGE_ACCOUNT_NAME --resource-group $RG --query id -o tsv)
Write-Host "Search Service Identity: $SEARCH_SERVICE_IDENTITY"
Write-Host "AI Resource Identity: $AI_RESOURCE_IDENTITY"
Write-Host "Storage Scope: $STORAGE_SCOPE"

# Assign Storage Blob Data Contributor (could be Reader for e.g) role to the managed identities for the resource group
Write-Host "Assigning Storage Blob Data Contributor role to the managed identities for the resource group..."
az role assignment create --role "Storage Blob Data Contributor" --assignee $SEARCH_SERVICE_IDENTITY --scope $STORAGE_SCOPE
az role assignment create --role "Storage Blob Data Contributor" --assignee $AI_RESOURCE_IDENTITY --scope $STORAGE_SCOPE

#3. Configure a managed identity to allow Azure AI Search instance to access the Azure OpenAI Service instance.
Write-Host "Configure a managed identity to allow Azure AI Search instance to access the Azure OpenAI Service instance."
$AI_SCOPE=$(az cognitiveservices account show --name $AI_RESOURCE_NAME --resource-group $RG --query id -o tsv)
Write-Host "AI Scope: $AI_SCOPE"
az role assignment create --role "Cognitive Services OpenAI Contributor" --assignee $SEARCH_SERVICE_IDENTITY --scope $AI_SCOPE

#4. Configure a managed identity to allow Azure OpenAI Service instance to access the Azure AI Search instance.
Write-Host "Configure a managed identity to allow Azure OpenAI Service instance to access the Azure AI Search instance."
$SEARCH_SCOPE=$(az search service show --name $SEARCH_SERVICE_NAME --resource-group $RG --query id -o tsv)
Write-Host "Search Scope: $SEARCH_SCOPE"
az role assignment create --role "Search Index Data Contributor" --assignee $AI_RESOURCE_IDENTITY --scope $SEARCH_SCOPE
az role assignment create --role "Search Index Data Reader" --assignee $AI_RESOURCE_IDENTITY --scope $SEARCH_SCOPE
az role assignment create --role "Search Service Contributor" --assignee $AI_RESOURCE_IDENTITY --scope $SEARCH_SCOPE

#5. Upload the PDF files to the Azure Blob Storage account.
Write-Host "Uploading PDF files to the Azure Blob Storage account..."
az storage blob upload-batch --account-name $STORAGE_ACCOUNT_NAME --destination brochures --source "$PATH_TO_DOWNLOADS_FOLDER" --pattern "*.pdf" --overwrite
