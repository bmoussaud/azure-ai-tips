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

output cognitiveServicesAccountId string = docIntelligence.id
output cognitiveServicesAccountEndpoint string = docIntelligence.properties.endpoint
output cognitiveServicesAccountKey string = listKeys(docIntelligence.id, '2023-05-01').key1
