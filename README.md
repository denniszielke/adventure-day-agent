# adventure-day-agent
This repository host the adventure day agent

Regions that this deployment can be executed:
- uksouth
- swedencentral
- canadaeast
- australiaeast

## Quickstart

```
# Log in to azd. Only required once per-install.
azd auth login

# Provision and deploy to Azure
azd up
```


## Configure the local env config for testing

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

## Test API for Challenge 1

Go to directory src-agents/challenge1

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

## Deploy resources for Challenge X

Run the following script

```
bash ./azd-hooks/deploy.sh challenge1 $ENVIRONMENT_NAME
```
