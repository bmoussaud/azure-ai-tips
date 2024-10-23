@description('The name of the Document Intelligence resource.')
param docIntelligenceName string = 'docIntelligence-${uniqueString(resourceGroup().id)}'

@description('Location for all resources.')
param location string = resourceGroup().location

@allowed(['S0', 'F0'])
param sku string = 'F0'

resource docIntelligence 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: docIntelligenceName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: sku
  }
  kind: 'FormRecognizer'
  properties: {
    publicNetworkAccess: 'Enabled'
  }
}

// Create a storage account
resource storageAccount 'Microsoft.Storage/storageAccounts@2021-04-01' = {
  name: 'bmoussauddocint'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
}

// create a container in the storage account
resource storageContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-04-01' = {
  name: '${storageAccount.name}/default/${docIntelligenceName}'
  properties: {
    publicAccess: 'Container'
  }
}

output cognitiveServicesAccountId string = docIntelligence.id
output cognitiveServicesAccountEndpoint string = docIntelligence.properties.endpoint
output cognitiveServicesAccountKey string = listKeys(docIntelligence.id, '2023-05-01').key1
