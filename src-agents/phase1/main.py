import os
from dotenv import load_dotenv
from fastapi import FastAPI, Response, Request
from pydantic import BaseModel
from enum import Enum
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from starlette.background import BackgroundTask
from starlette.types import Message
import logging
logging.basicConfig(filename='info.log', level=logging.INFO)

app = FastAPI()

load_dotenv()

def log_info(req_body, res_body):
    logging.info(req_body)
    logging.info(res_body)


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

@app.middleware('http')
async def logging_middleware(request: Request, call_next):
    req_body = await request.body()
    response = await call_next(request)
    
    res_body = b''
    async for chunk in response.body_iterator:
        res_body += chunk
    
    task = BackgroundTask(log_info, req_body, res_body)
    return Response(content=res_body, status_code=response.status_code, 
        headers=dict(response.headers), media_type=response.media_type, background=task)

@app.get("/")
async def root():
    return {"message": "Hello Smorgs"}

@app.get("/healthz", summary="Health check", operation_id="healthz")
async def get_products(query: str = None):
    """
    Returns a status of the app
    """

@app.post("/ask", summary="Ask a question", operation_id="ask") 
async def ask_question(ask: Ask):
    """
    Ask a question
    """

    # Send a completion call to generate an answer
    print('Sending a request to openai')
    start_phrase = "Answer the following question. Do only provide the answer, no additional 'a)' or 'b)' or whatever. Question: " + ask.question
    response = client.chat.completions.create(
        model = deployment_name,
        messages = [{"role" : "assistant", "content" : start_phrase}],
    )

    print(response.choices[0].message.content)
    print(response)
    answer = Answer(answer=response.choices[0].message.content)
    answer.correlationToken = ask.correlationToken
    answer.promptTokensUsed = response.usage.prompt_tokens
    answer.completionTokensUsed = response.usage.completion_tokens

    return answer
