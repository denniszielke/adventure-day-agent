# adventure-day-agent
This repository host the adventure day agent

Regions that this deployment can be executed:
- uksouth
- swedencentral
- canadaeast
- australiaeast

## Quickstart

```
echo "log into azure dev cli - only once"
azd auth login

echo "provisioning all the resources with the azure dev cli"
azd up

echo "get and set the value for AZURE_ENV_NAME"
azd env get-values | grep AZURE_ENV_NAME
source <(azd env get-values)

echo "building and deploying the agent for phase 1"
bash ./azd-hooks/deploy.sh phase1 $AZURE_ENV_NAME

```

### Test the deployed resource

```
PHASE1_URL="https://phase1.calmbush-f12187c5.swedencentral.azurecontainerapps.io"

curl -X 'POST' \
  "$PHASE1_URL/ask" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "question": "Who is the actor behind iron man?  1. Bill Gates, 2. Robert Downey Jr, 3. Jeff Bezos",
  "type": "multiple_choice",
  "correlationToken": "fgsdfgsd"
}'
```


## Manual creation of .env file
The .env file should be created automatically be the azd deployment script but if you want to create it manually these values have to be set:
Copy *template.env* and rename it to  *.env* config file with OpenAI, AI Search config details

```
OPENAI_API_TYPE = "azure"

AZURE_OPENAI_VERSION = "2024-02-01"
AZURE_OPENAI_API_KEY = ""
AZURE_OPENAI_ENDPOINT = "https://.openai.azure.com/"

AZURE_OPENAI_COMPLETION_MODEL = "gpt-35-turbo"
AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME = "gpt-35-turbo"

AZURE_OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = "text-embedding-3-small"
AZURE_OPENAI_EMBEDDING_VERSION = "2024-02-01"

```

## Test API for Phase 1

Go to directory src-agents/phase1

Start up the agent api
```
uvicorn main:app --reload
```

Test the api with:
```
curl -X 'POST' \
  'http://localhost:8000/ask' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "question": "Who is the actor behind iron man?  1. Bill Gates, 2. Robert Downey Jr, 3. Jeff Bezos",
  "type": "multiple_choice",
  "correlationToken": "fgsdfgsd"
}'

```

## Deploy resources for Phase X

Run the following script

```
azd env get-values | grep AZURE_ENV_NAME
bash ./azd-hooks/deploy.sh phase1 $AZURE_ENV_NAME
```
