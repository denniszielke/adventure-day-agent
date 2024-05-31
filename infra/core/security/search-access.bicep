param searchName string
param principalId string

// https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles
// Search Index Data Reader
var openAiUserRole = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '1407120a-92aa-4202-b7e9-c0e197c71c8f')

resource searchAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: search // Use when specifying a scope that is different than the deployment scope
  name: guid(subscription().id, resourceGroup().id, principalId, openAiUserRole)
  properties: {
    roleDefinitionId: openAiUserRole
    principalType: 'ServicePrincipal'
    principalId: principalId
  }
}

resource search 'Microsoft.Search/searchServices@2023-11-01' existing = {
  name: searchName
}
