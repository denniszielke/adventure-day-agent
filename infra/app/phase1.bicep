param name string
param location string = resourceGroup().location
param tags object = {}

@minLength(1)
@description('Openai API resource name for the API to use.')
param openaiName string

@minLength(1)
@description('Openai API Endpoint for the API to use.')
param openaiEndpoint string

@minLength(1)
@description('Name of the OpenAI Completion model deployment name.')
param completionDeploymentName string

param exists bool
param identityName string
param applicationInsightsName string
param containerAppsEnvironmentName string
param containerRegistryName string
param serviceName string = 'phase1'
param imageName string
param openaiApiVersion string
param searchName string
param searchEndpoint string

resource apiIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
}

module app '../core/host/container-app-upsert.bicep' = {
  name: '${serviceName}-container-app'
  params: {
    name: name
    location: location
    imageName: imageName
    tags: union(tags, { 'azd-service-name': serviceName })
    identityName: identityName
    exists: exists
    openaiName: openaiName
    containerAppsEnvironmentName: containerAppsEnvironmentName
    containerRegistryName: containerRegistryName
    searchName: searchName
    env: [
      {
        name: 'AZURE_CLIENT_ID'
        value: apiIdentity.properties.clientId
      }
      {
        name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
        value: applicationInsights.properties.ConnectionString
      }
      {
        name: 'AZURE_AI_SEARCH_NAME'
        value: searchName
      }
      {
        name: 'AZURE_AI_SEARCH_ENDPOINT'
        value: searchEndpoint
      }
      {
        name: 'AZURE_OPENAI_ENDPOINT'
        value: openaiEndpoint
      }
      {
        name: 'AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME'
        value: completionDeploymentName
      }
      {
        name: 'AZURE_OPENAI_VERSION'
        value: openaiApiVersion
      }
      {
        name: 'OPENAI_API_TYPE'
        value: 'azure'
      }
    ]
    targetPort: 80
  }
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: applicationInsightsName
}

output SERVICE_API_IDENTITY_PRINCIPAL_ID string = apiIdentity.properties.principalId
output SERVICE_API_NAME string = app.outputs.name
output SERVICE_API_URI string = app.outputs.uri
output SERVICE_API_IMAGE_NAME string = app.outputs.imageName
