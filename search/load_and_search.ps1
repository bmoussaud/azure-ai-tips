
$AZURE_REGION="France Central"
$RG="ContosoHotel"
$prefix="contoso"
$STORAGE_ACCOUNT_NAME="$prefix$(Get-Random -Minimum 100000 -Maximum 999999)"
$SEARCH_SERVICE_NAME="$prefix$(Get-Random -Minimum 100000 -Maximum 999999)"

az storage account create --name $STORAGE_ACCOUNT_NAME --resource-group $RG --location $AZURE_REGION --sku Standard_LRS
az storage container create --name brochures --account-name $STORAGE_ACCOUNT_NAME
az storage blob upload-batch --account-name $STORAGE_ACCOUNT_NAME --destination brochures --source "$PATH_TO_DOWNLOADS_FOLDER\AssetsRepo\Assets\PDFs" --pattern "*.pdf" --overwrite
az search service create --name $SEARCH_SERVICE_NAME --resource-group $RG --sku Basic --location $AZURE_REGION  --auth-options aadOrApiKey --aad-auth-failure-mode http403 --identity-type SystemAssigned

