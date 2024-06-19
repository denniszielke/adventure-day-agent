# adventure-day-agent
This repository host the adventure day agent

Regions that this deployment can be executed:
- uksouth
- swedencentral
- canadaeast
- australiaeast

## Quickstart

```
echo "log in with the provided credentials"
az login --use-device-code

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
PHASE1_URL="https://phase1..swedencentral.azurecontainerapps.io"

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

## Test API for Phase 1

Go to directory src-agents/phase1

Start up the agent api
```
pip install -r requirements.txt

uvicorn main:app --reload
```

Test the api with:
```
URL='http://localhost:8000'
URL='https://phase1..uksouth.azurecontainerapps.io'

curl -X 'POST' \
  "$URL/ask" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "question": "Who is the actor behind iron man?  1. Bill Gates, 2. Robert Downey Jr, 3. Jeff Bezos",
  "type": "multiple_choice",
  "correlationToken": "1234567890"
}'

curl -X 'POST' \
  "$URL/ask" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "question": "Which of the options below is a correct genre for the movie The Smoorgh Crusade? Action, Drama, Comedy, Adventure",
  "type": "multiple_choice",
  "correlationToken": "1234567890"
}'

curl -X 'POST' \
  "$URL/ask" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "question": "Does The Lost City have any sequels planned? True or False",
  "type": "true_or_false",
  "correlationToken": "1234567890"
}'

curl -X 'POST' \
  "$URL/ask" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "question": "Which country does The Lost Planet take place in?",
  "type": "multiple_choice",
  "correlationToken": "1234567890"
}'

```

## Deploy resources for Phase 1

Run the following script

```
azd env get-values | grep AZURE_ENV_NAME
source <(azd env get-values | grep AZURE_ENV_NAME)
bash ./azd-hooks/deploy.sh phase3 $AZURE_ENV_NAME
```

All the other phases work the same.

## Connect to Azure AI Search

The deployment will automatically inject the following environment variables into each running container:

```
AZURE_AI_SEARCH_NAME=
AZURE_AI_SEARCH_ENDPOINT=
AZURE_AI_SEARCH_KEY=
```

Here is some sample code that you can use to interact with the deployed Azure AI Search instance.

```
from azure.core.credentials import AzureKeyCredential
credential = AzureKeyCredential(os.environ["AZURE_AI_SEARCH_KEY"]) if len(os.environ["AZURE_AI_SEARCH_KEY"]) > 0 else DefaultAzureCredential()

from azure.search.documents import SearchClient

index_name = "movies-semantic-index"

search_client = SearchClient(
    os.environ["AZURE_AI_SEARCH_ENDPOINT"],
    azure_ai_search_index_name,
    AzureKeyCredential(azure_ai_search_api_key)
)

query = "What are the best movies about superheroes?"

results = list(search_client.search(
    search_text=query,
    query_type="simple",
    include_total_count=True,
    top=5
))
    
```