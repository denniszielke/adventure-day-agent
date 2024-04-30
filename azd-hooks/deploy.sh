#!/bin/bash

set -e

PHASE="$1"

if [ "$PHASE" == "" ]; then
echo "No phase name provided - aborting"
exit 0;
fi

AZURE_ENV_NAME="$2"

if [ "$AZURE_ENV_NAME" == "" ]; then
echo "No environment name provided - aborting"
exit 0;
fi

if [[ $PHASE =~ ^[a-z0-9]{5,12}$ ]]; then
    echo "phase name $PHASE is valid"
else
    echo "phase name $PHASE is invalid - only numbers and lower case min 5 and max 12 characters allowed - aborting"
    exit 0;
fi

RESOURCE_GROUP="rg-$AZURE_ENV_NAME"

if [ $(az group exists --name $RESOURCE_GROUP) = false ]; then
    echo "resource group $RESOURCE_GROUP does not exist"
    error=1
else   
    echo "resource group $RESOURCE_GROUP already exists"
    LOCATION=$(az group show -n $RESOURCE_GROUP --query location -o tsv)
fi

APPINSIGHTS_NAME=$(az resource list -g $RESOURCE_GROUP --resource-type "Microsoft.Insights/components" --query "[0].name" -o tsv)
AZURE_CONTAINER_REGISTRY_NAME=$(az resource list -g $RESOURCE_GROUP --resource-type "Microsoft.ContainerRegistry/registries" --query "[0].name" -o tsv)
OPENAI_NAME=$(az resource list -g $RESOURCE_GROUP --resource-type "Microsoft.CognitiveServices/accounts" --query "[0].name" -o tsv)
ENVIRONMENT_NAME=$(az resource list -g $RESOURCE_GROUP --resource-type "Microsoft.App/managedEnvironments" --query "[0].name" -o tsv)
IDENTITY_NAME=$(az resource list -g $RESOURCE_GROUP --resource-type "Microsoft.ManagedIdentity/userAssignedIdentities" --query "[0].name" -o tsv)
SERVICE_NAME=$PHASE
AZURE_SUBSCRIPTION_ID=$(az account show --query id -o tsv)

echo "container registry name: $AZURE_CONTAINER_REGISTRY_NAME"
echo "application insights name: $APPINSIGHTS_NAME"
echo "openai name: $OPENAI_NAME"
echo "environment name: $ENVIRONMENT_NAME"
echo "identity name: $IDENTITY_NAME"
echo "service name: $SERVICE_NAME"

CONTAINER_APP_EXISTS=$(az resource list -g $RESOURCE_GROUP --resource-type "Microsoft.App/containerApps" --query "[?contains(name, '$SERVICE_NAME')].id" -o tsv)
EXISTS="false"

if [ "$CONTAINER_APP_EXISTS" == "" ]; then
    echo "container app $SERVICE_NAME does not exist"
else
    echo "container app $SERVICE_NAME already exists"
    EXISTS="true"
fi

az acr build --subscription ${AZURE_SUBSCRIPTION_ID} --registry ${AZURE_CONTAINER_REGISTRY_NAME} --image $SERVICE_NAME:latest ./src-agents/$SERVICE_NAME
IMAGE_NAME="${AZURE_CONTAINER_REGISTRY_NAME}.azurecr.io/$SERVICE_NAME:latest"

az deployment group create -g $RESOURCE_GROUP -f ./infra/app/phaseX.bicep \
          -p name=$SERVICE_NAME -p location=$LOCATION -p containerAppsEnvironmentName=$ENVIRONMENT_NAME \
          -p containerRegistryName=$AZURE_CONTAINER_REGISTRY_NAME -p applicationInsightsName=$APPINSIGHTS_NAME \
          -p openaiName=$OPENAI_NAME -p identityName=$IDENTITY_NAME -p imageName=$IMAGE_NAME -p exists=$EXISTS