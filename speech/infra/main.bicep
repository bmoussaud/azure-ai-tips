param location string = resourceGroup().location
param speechServiceName string = 'bmspeech${uniqueString(resourceGroup().id)}'

resource speech 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: speechServiceName
  location: location
  kind: 'SpeechServices'
  sku: {
    name: 'F0'
  }
  properties: {
    apiProperties: {}
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
}

output speechEndpoint string = speech.properties.endpoint
output KEY string = listKeys(speech.id, speech.apiVersion).key1
output REGION string = location
