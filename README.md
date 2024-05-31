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

```

## Deploy resources for Phase 1

Run the following script

```
azd env get-values | grep AZURE_ENV_NAME
source <(azd env get-values | grep AZURE_ENV_NAME)
bash ./azd-hooks/deploy.sh phase1 $AZURE_ENV_NAME
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

## Connect to Redis

The deployment will automatically inject the following environment variables into each running container:

```
REDIS_PASSWORD=
REDIS_HOST=redis
REDIS_ENDPOINT=redis:6379
REDIS_PORT=6379
```

Here is some sample code that you can use to interact with the deployed redis instance.

```
import redis
import os

# Redis connection details
redis_host = os.getenv('REDIS_HOST')
redis_port = os.getenv('REDIS_PORT')
redis_password = os.getenv('REDIS_PASSWORD')
 
# Connect to the Redis server
conn = redis.Redis(host=redis_host, port=redis_port, password=redis_password, encoding='utf-8', decode_responses=True)
 
if conn.ping():
  print("Connected to Redis")

```