param responseTimeThreshold int = 3
param workspaceName string
param applicationInsightsName string
param location string

var responseAlertName = 'ResponseTime-${toLower(applicationInsightsName)}'

resource workspace 'Microsoft.OperationalInsights/workspaces@2020-10-01' existing = {
  name: workspaceName
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02-preview' = {
  name: applicationInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: workspace.id
  }
}

resource metricAlert 'Microsoft.Insights/metricAlerts@2018-03-01' = {
  name: responseAlertName
  location: 'global'
  properties: {
    description: 'Response time alert'
    severity: 0
    enabled: true
    scopes: [
      applicationInsights.id
    ]
    evaluationFrequency: 'PT1M'
    windowSize: 'PT5M'
    criteria: {
      'odata.type': 'Microsoft.Azure.Monitor.SingleResourceMultipleMetricCriteria'
      allOf: [
        {
          name: '1st criterion'
          metricName: 'requests/duration'
          operator: 'GreaterThan'
          threshold: responseTimeThreshold
          timeAggregation: 'Average'
          criterionType: 'StaticThresholdCriterion'
        }
      ]
    }
    actions: [
      {
        actionGroupId: emailActionGroup.id
      }
    ]
  }
}

resource emailActionGroup 'microsoft.insights/actionGroups@2019-06-01' = {
  name: 'emailActionGroup'
  location: 'global'
  properties: {
    groupShortName: 'string'
    enabled: true
    emailReceivers: [
      {
        name: 'Example'
        emailAddress: 'example@test.com'
        useCommonAlertSchema: true
      }
    ]
  }
}

output aiId string = applicationInsights.id
output aiName string = applicationInsights.name
output name string = applicationInsights.name
output connectionString string = applicationInsights.properties.ConnectionString
output instrumentationKey string = applicationInsights.properties.InstrumentationKey
