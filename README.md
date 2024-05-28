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
  "correlationToken": "1234567890"
}'

```

## Deploy resources for Phase X

Run the following script

```
azd env get-values | grep AZURE_ENV_NAME
bash ./azd-hooks/deploy.sh phase1 $AZURE_ENV_NAME
```


## Connect to Qdrant

The deployment will automatically inject the following environment variables into each running container:

```
QDRANT_PORT=6333
QDRANT_HOST=qdrant
QDRANT_ENDPOINT=qdrant:6333
QDRANT_PASSWORD=
```

Here is some sample code that you can use to interact with the deployed Qdrant instance.

```
import os
import openai
from langchain.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_openai import AzureOpenAIEmbeddings

from langchain_openai import AzureOpenAIEmbeddings
# Create an Embeddings Instance of Azure OpenAI
embeddings = AzureOpenAIEmbeddings(
    azure_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
    openai_api_version = os.getenv("AZURE_OPENAI_VERSION"),
    model= os.getenv("AZURE_OPENAI_EMBEDDING_MODEL")
)

# load your data
data_dir = "data/movies"
documents = DirectoryLoader(path=data_dir, glob="*.md", show_progress=True, loader_cls=UnstructuredMarkdownLoader).load()

#create chunks
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
document_chunks = text_splitter.split_documents(documents)

from langchain.vectorstores import Qdrant

url = os.getenv('REDIS_PORT')
qdrant = Qdrant.from_documents(
    data,
    embeddings,
    url=url,
    prefer_grpc=False,
    collection_name="movies",
)

vectorstore = qdrant

query = "Can you suggest similar movies to The Matrix?"

query_results = qdrant.similarity_search(query)

for doc in query_results:
    print(doc.metadata['source'])
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
import openai

# Redis connection details
redis_host = os.getenv('REDIS_HOST')
redis_port = os.getenv('REDIS_PORT')
redis_password = os.getenv('REDIS_PASSWORD')
 
# Connect to the Redis server
conn = redis.Redis(host=redis_host, port=redis_port, password=redis_password, encoding='utf-8', decode_responses=True)
 
if conn.ping():
  print("Connected to Redis")

query = "Who is iron man?"

# Vectorize the query using OpenAI's text-embedding-ada-002 model
print("Vectorizing query...")
embedding = openai.Embedding.create(input=query, model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"))
query_vector = embedding["data"][0]["embedding"]

```