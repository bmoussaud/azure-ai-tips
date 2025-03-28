@description('The location where the resources will be deployed.')
param location string = 'eastus'

@description('The name of the Cognitive Services Translator resource.')
param cognitiveServiceName string = uniqueString(resourceGroup().id, 'bmotranslator')

@description('The name of the storage account.')
param storageAccountName string = uniqueString(resourceGroup().id, 'tstorage')

@description('The SKU for the Cognitive Services Translator resource.')
param cognitiveServiceSku string = 'S1'

@description('The SKU for the storage account.')
param storageAccountSku string = 'Standard_LRS'

// Cognitive Services Translator resource
resource cognitiveService 'Microsoft.CognitiveServices/accounts@2022-12-01' = {
  name: cognitiveServiceName
  location: location
  kind: 'TextTranslation'
  sku: {
    name: cognitiveServiceSku
  }
  properties: {
    customSubDomainName: cognitiveServiceName
  }
  identity: {
    type: 'SystemAssigned'
  }
}

// Storage account
resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: storageAccountSku
  }
  kind: 'StorageV2'
  properties: {
    allowSharedKeyAccess: false
  }
  resource blobServices 'blobServices' = {
    resource inputcontainer 'containers' = {
      name: 'input'
      properties: {
        publicAccess: 'None'
      }
    }
    resource outputcontainer 'containers' = {
      name: 'output'
      properties: {
        publicAccess: 'None'
      }
    }

    name: 'default'
  }
}

// Assign identity to Cognitive Services and grant Storage Blob Data Contributor role
resource cognitiveServiceIdentity 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(cognitiveService.id, 'StorageBlobDataContributor')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    ) // Storage Blob Data Contributor
    principalId: cognitiveService.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource currentUserStorageBlobDataContributor 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(
    resourceGroup().id,
    'Deployer',
    subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
  )
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    ) // Storage Blob Data Contributor
    principalId: az.deployer().objectId
  }
}

output AZURE_DOCUMENT_TRANSLATION_KEY string = listKeys(cognitiveService.id, '2022-12-01').key1
output AZURE_DOCUMENT_TRANSLATION_ENDPOINT_ALL object = cognitiveService.properties.endpoints
output AZURE_DOCUMENT_TRANSLATION_ENDPOINT string = cognitiveService.properties.endpoints['DocumentTranslation']
output AZURE_STORAGE_BLOB_ENDPOINT string = storageAccount.properties.primaryEndpoints.blob
