param name string
param location string = resourceGroup().location
param exists bool = true
param containerAppsEnvironmentName string
param containerRegistryName string
param applicationInsightsName string
param identityName string
param openaiName string
param imageName string
param searchName string

var tags = { 'azd-env-name': containerAppsEnvironmentName }
var completionDeploymentModelName = 'gpt-4o'
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
        value: 'https://${searchName}.search.windows.net'
      }
      {
        name: 'AZURE_OPENAI_ENDPOINT'
        value: openaiEndpoint
      }
      {
        name: 'AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME'
        value: completionDeploymentModelName
      }
      {
        name: 'AZURE_OPENAI_COMPLETION_MODEL'
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
      {
        name: 'AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME'
        value: 'text-embedding-ada-002'
      }
      {
        name: 'AZURE_OPENAI_EMBEDDING_MODEL'
        value: 'text-embedding-ada-002'
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
output uri string = app.outputs.uri
