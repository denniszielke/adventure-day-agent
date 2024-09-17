import os
import json
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
#import redis
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import (
    VectorizedQuery
)
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SimpleField,
    SearchFieldDataType,
    SearchableField,
    SearchField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch,
    SearchIndex

)
# Load environment variables
if load_dotenv():
    print("Found Azure OpenAI API Base Endpoint: " + os.getenv("AZURE_OPENAI_ENDPOINT"))
else: 
    print("Azure OpenAI API Base Endpoint not found. Have you configured the .env file?")
    
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = os.getenv("OPENAI_API_VERSION")
RESOURCE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

credential = AzureKeyCredential(os.environ["AZURE_AI_SEARCH_KEY"]) if len(os.environ["AZURE_AI_SEARCH_KEY"]) > 0 else DefaultAzureCredential()

index_name = "question-semantic-index"

index_client = SearchIndexClient(
    endpoint=os.environ["AZURE_AI_SEARCH_ENDPOINT"], 
    credential=credential
)

# Create a search index with the fields and a vector field which we will fill with a vector based on the overview field
fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True),
    SearchableField(name="question", type=SearchFieldDataType.String),
    SearchableField(name="answer", type=SearchFieldDataType.String),
    SearchField(name="vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
]

# Configure the vector search configuration  
vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(
            name="myHnsw"
        )
    ],
    profiles=[
        VectorSearchProfile(
            name="myHnswProfile",
            algorithm_configuration_name="myHnsw",
        )
    ]
)

# Configure the semantic search configuration 
semantic_config = SemanticConfiguration(
    name="question-semantic-config",
    prioritized_fields=SemanticPrioritizedFields(
        title_field=SemanticField(field_name="question"),
        keywords_fields=[SemanticField(field_name="answer")],
        content_fields=[SemanticField(field_name="question")]
    )
)

# Create the semantic settings with the configuration
semantic_search = SemanticSearch(configurations=[semantic_config])

# Create the search index with the semantic settings
index = SearchIndex(name=index_name, fields=fields,
                    vector_search=vector_search, semantic_search=semantic_search)
result = index_client.create_or_update_index(index)







app = FastAPI()

load_dotenv()

class QuestionType(str, Enum):
    multiple_choice = "multiple_choice"
    true_or_false = "true_or_false"
    popular_choice = "popular_choice"
    estimation = "estimation"

class Ask(BaseModel):
    question: str | None = None
    type: QuestionType
    correlationToken: str | None = None

class Answer(BaseModel):
    answer: str
    correlationToken: str | None = None
    promptTokensUsed: int | None = None
    completionTokensUsed: int | None = None

client: AzureOpenAI

if "AZURE_OPENAI_API_KEY" in os.environ:
    client = AzureOpenAI(
        api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
        api_version = os.getenv("AZURE_OPENAI_VERSION"),
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    )
else:
    token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")
    client = AzureOpenAI(
        azure_ad_token_provider=token_provider,
        api_version = os.getenv("AZURE_OPENAI_VERSION"),
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
    )

deployment_name = os.getenv("AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME")
index_name = "movies-semantic-index"
service_endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
model_name = os.getenv("AZURE_OPENAI_COMPLETION_MODEL")

# Redis connection details
#redis_host = os.getenv('REDIS_HOST')
#redis_port = os.getenv('REDIS_PORT')
#redis_password = os.getenv('REDIS_PASSWORD')
 
# Connect to the Redis server
#conn = redis.Redis(host=redis_host, port=redis_port, password=redis_password, encoding='utf-8', decode_responses=True)
 
#if conn.ping():
#    print("Connected to Redis")

@app.get("/")
async def root():
    return {"message": "Hello Smorgs"}

# use an embeddingsmodel to create embeddings
def get_embedding(text, model=os.getenv("AZURE_OPENAI_EMBEDDING_MODEL")):
    return client.embeddings.create(input = [text], model=model).data[0].embedding


@app.post("/ask", summary="Ask a question", operation_id="ask") 
async def ask_question(ask: Ask):
    """
    Ask a question
    """   
    print (ask.question)
    index_name = "question-semantic-index"

    # create a vectorized query based on the question
    vector = VectorizedQuery(vector=get_embedding(ask.question), k_nearest_neighbors=5, fields="vector")


    # create new searchclient using our new index for the questions
    search_client = SearchClient(
        endpoint=os.environ["AZURE_AI_SEARCH_ENDPOINT"], 
        index_name=index_name,
        credential=credential
    )

    # check if the question &  answer is in the cache already
    # create search client to retrieve movies from the vector store
    found_questions = list(search_client.search(
        search_text=None,
        query_type="semantic",
        semantic_configuration_name="question-semantic-config",
        vector_queries=[vector],
        select=["question", "answer"],
        top=5
    ))
    questionMatchCount = len(found_questions)
    docIdCount = search_client.get_document_count() + 1 

    if questionMatchCount > 0 :
    # if found_questions[0]['@search.score'] > 0.90:
        search_client.upload_documents([{'Question': found_questions[0]['question'], 
                                         'Answer': found_questions[0]['answer'],
                                         'id': str(docIdCount)}])
        return found_questions[0]['answer'] 
    else:
         #   reach out to the llm to get the answer. 
        print('Sending a request to LLM')
        start_phrase = ask.question
        messages=  [{"role" : "assistant", "content" : start_phrase},
                     { "role" : "system", "content" : "Answer this question with a very short answer. Don't answer with a full sentence, and do not format the answer."}]
        
        response = client.chat.completions.create(
             model = deployment_name,
             messages =messages,
        )
        answer = Answer(answer=response.choices[0].message.content)
        search_client.upload_documents([{'Question': ask.question, 
                                         'Answer': response.choices[0].message.content,
                                         'id': str(docIdCount)}])
        
        print ("Added a new answer and question to the cache: " + answer.answer + "in position" + str(docIdCount))
        return answer
