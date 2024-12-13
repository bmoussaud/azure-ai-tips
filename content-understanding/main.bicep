@description('The name of the Document Intelligence resource.')
param aiServiceName string = 'ai-svc-${uniqueString(resourceGroup().id)}'

@description('Location for all resources.')
param location string = resourceGroup().location

@allowed(['S0', 'F0'])
param sku string = 'S0'

@description('Restore the service instead of creating a new instance. This is useful if you previously soft-deleted the service and want to restore it. If you are restoring a service, set this to true. Otherwise, leave this as false.')
param restore bool = false

@description('Creates an Azure OpenAI resource.')
resource aiServices 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: aiServiceName
  location: location
  kind: 'AIServices'
  sku: {
    name: sku
  }
  properties: {
    customSubDomainName: aiServiceName
    publicNetworkAccess: 'Enabled'
    restore: restore
  }
}

output cognitiveServicesAccountEndpoint string = aiServices.properties.endpoint
output cognitiveServicesAccountKey string = listKeys(aiServices.id, '2023-05-01').key1
