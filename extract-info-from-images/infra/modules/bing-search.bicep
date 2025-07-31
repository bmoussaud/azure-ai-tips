param bingSearchServiceName string

//https://github.com/microsoft/semantic-kernel/blob/main/python/samples/concepts/agents/azure_ai_agent/azure_ai_agent_bing_grounding.py
resource bingSearchService 'Microsoft.Bing/accounts@2025-05-01-preview' = {
  name: bingSearchServiceName
  location: 'global'
  sku: {
    name: 'G2'
  }
  kind: 'Bing.GroundingCustomSearch'
}

//
resource bingCustomSearchConfiguration 'Microsoft.Bing/accounts/customSearchConfigurations@2025-05-01-preview' = {
  parent: bingSearchService
  name: 'defaultConfiguration'
  properties: {
    blockedDomains: [
      {
        domain: 'www.youtube.com'
      }
    ]
  }
}

output bingSearchServiceId string = bingSearchService.id
output bingCustomSearchConfigurationId string = bingCustomSearchConfiguration.id
output bingSearchServiceName string = bingSearchService.name
