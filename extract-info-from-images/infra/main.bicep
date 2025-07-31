@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string = 'francecentral'

@description('Location for AI Foundry resources.')
param aiFoundryLocation string = 'westus' //'westus' 'switzerlandnorth' swedencentral

@description('Name of the resource group to deploy to.')
param rootname string = 'extimage'

// tags that should be applied to all resources.
var tags = {
  // Tag all resources with the environment name.
  'azd-env-name': environmentName
}

module aiFoundry 'modules/ai-foundry.bicep' = {
  name: 'aiFoundryModel'
  params: {
    name: 'foundry-${rootname}-${aiFoundryLocation}-${environmentName}'
    location: aiFoundryLocation
    modelDeploymentsParameters: [
      {
        name: '${rootname}-gpt-4.1-mini'
        model: 'gpt-4.1-mini'
        capacity: 1000
        deployment: 'GlobalStandard'
        version: '2025-04-14'
        format: 'OpenAI'
      }
    ]
  }
}

module aiFoundryProject 'modules/ai-foundry-project.bicep' = {
  name: 'aiFoundryProject'
  params: {
    location: aiFoundryLocation
    aiFoundryName: aiFoundry.outputs.aiFoundryName
    aiProjectName: 'prj-${rootname}-${aiFoundryLocation}-${environmentName}'
    aiProjectFriendlyName: 'Setlistfy Project ${environmentName}'
    aiProjectDescription: 'Agents to help to manage setlist and music events.'

    applicationInsightsName: applicationInsights.outputs.name
    bingSearchServiceName: bingSearch.outputs.bingSearchServiceName
    storageAccountName: storage.name
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: '${environmentName}st${uniqueString(resourceGroup().id)}'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      bypass: 'AzureServices'
      defaultAction: 'Allow'
      virtualNetworkRules: []
    }
    allowSharedKeyAccess: false
  }
}

module bingSearch 'modules/bing-search.bicep' = {
  name: 'bing-search'
  params: {
    bingSearchServiceName: 'bing-${rootname}-${environmentName}'
  }
}

module logAnalyticsWorkspace 'modules/log-analytics-workspace.bicep' = {
  name: 'log-analytics-workspace'
  params: {
    location: location
    logAnalyticsName: '${rootname}-log-analytics'
  }
}

module applicationInsights 'modules/app-insights.bicep' = {
  name: 'application-insights'
  params: {
    location: location
    workspaceName: logAnalyticsWorkspace.outputs.name
    applicationInsightsName: '${rootname}-app-insights'
  }
}

module storageAccountRoleAssignments 'modules/storage-account-role-assignments.bicep' = {
  name: 'storage-account-role-${aiFoundryProject.name}'
  //scope: resourceGroup(aiSearchServiceSubscriptionId, aiSearchServiceResourceGroupName)
  params: {
    storageAccountName: storage.name
    principalId: aiFoundryProject.outputs.projectIdentityPrincipalId
    resourceId: aiFoundryProject.outputs.projectId
  }
}
