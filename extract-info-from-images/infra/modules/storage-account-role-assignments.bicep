// Assigns the necessary roles to the Storage Account

@description('Name of the Storage Account resource')
param storageAccountName string

@description('Principal ID of the AI project')
param principalId string

@description('Resource ID of the AI project')
param resourceId string

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' existing = {
  name: storageAccountName
  scope: resourceGroup()
}

// Storage Blob Data Contributor role
resource storageBlobDataContributorRole 'Microsoft.Authorization/roleDefinitions@2022-04-01' existing = {
  name: 'ba92f5b4-2d11-453d-a403-e96b0029c9fe' // Storage Blob Data Contributor
  scope: resourceGroup()
}

resource storageBlobDataContributorAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: storageAccount
  name: guid(resourceId, storageBlobDataContributorRole.id, storageAccount.id)
  properties: {
    principalId: principalId
    roleDefinitionId: storageBlobDataContributorRole.id
    principalType: 'ServicePrincipal'
  }
}
