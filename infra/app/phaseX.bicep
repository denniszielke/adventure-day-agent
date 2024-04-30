param name string
param location string = resourceGroup().location
param exists bool = true
param containerAppsEnvironmentName string
param containerRegistryName string
param applicationInsightsName string
param identityName string
param openaiName string
param imageName string

var tags = { 'azd-env-name': containerAppsEnvironmentName }
var completionDeploymentModelName = 'gpt-35-turbo'
param openaiApiVersion string = '2024-02-01'

resource apiIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: identityName
}

resource account 'Microsoft.CognitiveServices/accounts@2022-10-01' existing = {
  name: openaiName  
}

var openaiEndpoint = account.properties.endpoint
// var openaiApiKey = listKeys(account.id, '2022-10-01').key1

module app '../core/host/container-app-upsert.bicep' = {
  name: '${name}-container-app'
  params: {
    name: name
    location: location
    tags: union(tags, { 'azd-service-name': name })
    identityName: identityName
    imageName: imageName
    exists: exists
    openaiName: openaiName
    containerAppsEnvironmentName: containerAppsEnvironmentName
    containerRegistryName: containerRegistryName
    env: [
      {
        name: 'AZURE_CLIENT_ID'
        value: apiIdentity.properties.clientId
      }
      {
        name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
        value: applicationInsights.properties.ConnectionString
      }
      // {
      //   name: 'AZURE_OPENAI_API_KEY'
      //   value: openaiApiKey
      // }
      {
        name: 'AZURE_OPENAI_ENDPOINT'
        value: openaiEndpoint
      }
      {
        name: 'AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME'
        value: completionDeploymentModelName
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
    targetPort: 8080
  }
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: applicationInsightsName
}

output SERVICE_API_IDENTITY_PRINCIPAL_ID string = apiIdentity.properties.principalId
output SERVICE_API_NAME string = app.outputs.name
output SERVICE_API_URI string = app.outputs.uri
output SERVICE_API_IMAGE_NAME string = app.outputs.imageName
