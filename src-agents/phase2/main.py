import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.models import (
    VectorizedQuery
)

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
        azure_ad_token_provider = token_provider,
        api_version = os.getenv("AZURE_OPENAI_VERSION"),
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
    )

deployment_name = os.getenv("AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME")
index_name = "movies-semantic-index"
service_endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT")
embedding_model = os.getenv("AZURE_OPENAI_EMBEDDING_MODEL")

# use an embeddingsmodel to create embeddings
def get_embedding(text, model=embedding_model):
    return client.embeddings.create(input = [text], model=model).data[0].embedding

credential = None
if "AZURE_AI_SEARCH_KEY" in os.environ:
    credential = AzureKeyCredential(os.environ["AZURE_AI_SEARCH_KEY"])
else:
    credential = DefaultAzureCredential()

search_client = SearchClient(
    service_endpoint, 
    index_name, 
    credential
)

@app.get("/")
async def root():
    return {"message": "Hello Smorgs"}

@app.post("/ask", summary="Ask a question", operation_id="ask") 
async def ask_question(ask: Ask):
    """
    Ask a question
    """

    start_phrase =  ask.question
    response: openai.types.chat.chat_completion.ChatCompletion = None

    #####\n",
    client = AzureOpenAI(
            api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version = os.getenv("AZURE_OPENAI_VERSION"),
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        )

    deployment_name = os.getenv("AZURE_OPENAI_COMPLETION_DEPLOYMENT_NAME")
    model_name = os.getenv("AZURE_OPENAI_COMPLETION_MODEL")

    index_client = SearchClient(
        endpoint=os.environ["AZURE_AI_SEARCH_ENDPOINT"], 
        index_name=index_name,
        credential=credential
    )

    question = ask.question
    type = ask.type

    # create a vectorized query based on the question
    vector = VectorizedQuery(vector=get_embedding(question), k_nearest_neighbors=5, fields="vector")


    # create search client to retrieve movies from the vector store
    found_docs = list(search_client.search(
        search_text=None,
        query_type="semantic",
        semantic_configuration_name="movies-semantic-config",
        vector_queries=[vector],
        select=["title", "genre", "plot", "year"],
        top=5
    ))

    found_docs_as_text = " "
    # print the found documents and the field that were selected
    for doc in found_docs:
        print("Movie: {}".format(doc["title"]))
        print("Genre: {}".format(doc["genre"]))
        print("Year: {}".format(doc["year"]))
        print("----------")
        found_docs_as_text += " "+ "Movie Title: {}".format(doc["title"]) +" "+ "Release Year: {}".format(doc["year"]) + " "+ "Movie Plot: {}".format(doc["plot"])
        
    # augment the question with the found documents and ask the LLM to generate a response
    system_prompt = "Here is what you need to do:"

    parameters = [system_prompt, ' Context:', found_docs_as_text , ' Question:', question]
    joined_parameters = ''.join(parameters)

    response = client.chat.completions.create(
            model = deployment_name,
            messages = [{"role" : "assistant", "content" : joined_parameters}],
        )

    print (response.choices[0].message.content)
    ######\n",

    answer = Answer(answer=response.choices[0].message.content)
    answer.correlationToken = ask.correlationToken
    answer.promptTokensUsed = response.usage.prompt_tokens
    answer.completionTokensUsed = response.usage.completion_tokens

    return answer