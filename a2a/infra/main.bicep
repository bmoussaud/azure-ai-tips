@description('Name of the AI Foundry project')
param projectName string = 'a2a-foundry-project'

@description('Location for the resources')
param location string = resourceGroup().location

@description('Name for the GPT-4o deployment')
param deploymentName string = 'gpt-4o-deployment'
