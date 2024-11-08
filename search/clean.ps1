$AZURE_REGION="France Central"
$prefix="contosobm"
$RG="ContosoHotel"
$INDEX="254502"
$STORAGE_ACCOUNT_NAME="sto$prefix$INDEX"
$SEARCH_SERVICE_NAME="srch$prefix$INDEX"
$AI_RESOURCE_NAME="openai$prefix$INDEX" 
$PATH_TO_DOWNLOADS_FOLDER="C:\Users\bmoussaud\Workspaces\ContosoHotel\AssetRepo\TechExcel-Modernize-applications-to-be-AI-ready\Assets\PDFs"  # Add this line
Write-Host "Search Service Name: $SEARCH_SERVICE_NAME"
Write-Host "AI Resource Name: $AI_RESOURCE_NAME"
Write-Host "Storage Account Name: $STORAGE_ACCOUNT_NAME"
pause

# delete the resources
Write-Host "Deleting Azure Search Service, Azure OpenAI Service, and Azure Storage Account..."
az cognitiveservices account delete --name $AI_RESOURCE_NAME --resource-group $RG 
az search service delete --name $SEARCH_SERVICE_NAME --resource-group $RG 
az storage account delete --name $STORAGE_ACCOUNT_NAME --resource-group $RG 
pause 
