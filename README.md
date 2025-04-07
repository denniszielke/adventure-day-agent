# Azure AI Adventure Day Player repository

This repository host the Azure AI Adventure Day player code

## What is Azure AI Adventure Day? ✨

![Azure AI Adventure Day](aaday.png)

Azure AI Adventure Day is an interactive team-based learning experience designed to enable attendees to test and learn new skills in a real-world, risk-free, challenging but also fun environment.

Participants will be working as a team to build an intelligent Agent to automatically respond to increasingly complex input questions using OpenAI. The Game Play itself will have a multi-phase narrative around deployment of resources, implementation of retrieval augmented generation, leveraging of function calling, ensuring security & content safety, tuning of cost, latency and efficiency. 

Attendees should have a basic understanding of Python. Azure experience is helpful. A highly recommended starting point is Azure AI Fundamentals and Introduction to OpenAI.

See https://aka.ms/azure-adventure-day

## AI Adventure Day concept 

The AI Adventure Day consists of two parts, an agent and a backend. The participants will work in teams with the Adventure Day agent repository, which is a collection of Azure Deployments, Jupyter Notebooks and Code samples. The backend will be provided by the Microsoft proctor team and is used for grading the solutions and providing the scores. 

### Adventure Day agent

The agent setup contains an Azure deployment which will setup the needed cloud resources for the challenges. This includes, among others, the needed Azure OpenAI models and an AI Search instance as well as a hosting environment to host the applications which the participants will be developing. Next to the cloud resources, the agents contain several Jupyter notebooks. These will guide through the different challenges and act as the local developer loop for a challenge. Once the team decides that their code base is sufficient enough to solve the challenge, they will deploy the local version to the cloud environment where it can be tested/graded by the backend. 

### Adventure Day backend

The backend will be provided by the Microsoft proctors and the teams will receive credentials to login to the backend portal. There they can see the current score and also register their applications. Once the application is registered with the backend, it will generate requests to check the correct implementation and efficiency of the solution. It will award points according to the error rate and efficiency of the code. 

## Quickstart & Infrastructure setup

### Azure Resources and Quotas 
|Azure Service  |SKU  |Annotations  |
|---------|---------|---------|
|Application Insights & Log Analytics workspace   |  Pay-as-you-go  | Will be used for monitoring and debugging. |
|Container Apps Environment     | Consumption Only | Will be used to host Container Apps with application code. |
|Container App     | Consumption Only | Initial deployment with redis container. More Container Apps are added later during the phase configuration.  |
|Container registry     |  Standard | Stores container images. |
|Azure OpenAI | Standard | Access to LLM models. The following models will be deployed: gpt-4o, text-embedding-ada-002 |
|Managed Identity     |  User assigned managed Identity | Contains permissions for Container Registry, Azure AI Search and AI Services  |
|Azure AI Search     |  Standard | Setup with 1 search unit. Well be used for RAG challenge. |

### Available Regions

Regions that this deployment can be executed:
- northcentralus
- swedencentral
- eastus2
- westus3

### Login to your Azure Environment 

**Important hint:**
Make sure you log into  a private browser session using the correct identity provided in the team portal and log into http://portal.azure.com there with this identity! Otherwise, you might end up using the wrong Azure subscription!
Make sure you are providing the device codes in this private browser session using the correct identity mentioned!

The following lines of code will connect your Codespace az cli and azd cli to the right Azure subscription:

```
# log in with the provided credentials - OPEN A PRIVATE BROWSER SESSION
az login --use-device-code

# "log into azure dev cli - only once" - OPEN A PRIVATE BROWSER SESSION
azd auth login --use-device-code

# press enter open up https://microsoft.com/devicelogin and enter the code

```

### Deploy/Connect the infrastructure components

Next, we need to setup the cloud infrastructure for the Adventure Day agent. If the infrastructure has not been deployed yet, follow the steps in the section ```Create new Azure Adventure Day Agent deployment```. If the infrastructure has already been setup (for example by your team colleague or the IT department), follow the instruction in the section ```Connect to an existing Azure Adventure Day Agent deployment```.

<details>
  <summary> <b>Create new Azure Adventure Day Agent deployment</b> </summary>

  ```
  # "Provisioning all the resources with the azure dev cli"
  azd up
  ```

</details>

---

<details>
  <summary> <b>Connect to an existing Azure Adventure Day Agent deployment </b> </summary>

  You can use the connect-environment script to detect existing Adventure Day agent deployments in your default AzureCLI Subscription. The script will then obtain the configuration and connect the azd deployment with your local instance.

  ```
  # "Use the connect-environment script to detect existing deploy"
  python ./azd-hooks/connect-environment.py
  ```
  > The script only obtains the correct AZD deployment name, location and subscriptionId and executes azd up with these settings. You can also run ```azd up -e <existing deployment name>``` on your own to get a similiar result. However, the goal behind this script is to avoid redeployments or permissions problems in regulated environments. 

</details>

### Prepare environment variables 

Get the values for some env variables which will be used by some scripts later. 
```
# "get and set the value for AZURE_ENV_NAME"
source <(azd env get-values | grep AZURE_ENV_NAME)
```

### Deploy the first dummy application

Last but not least: deploy a dummy container in Azure Container Apps. 
```
echo "building and deploying the agent for phase 1"
bash ./azd-hooks/deploy.sh phase1 $AZURE_ENV_NAME

```

### Work with the deployed resource

If the following request provides a useful answer, you are ready to go with Phase 1. Make sure to provide the correct URL.

> [!NOTE]  
  > During the Adventure Day you will work with local instances of the phases. Once you are ready to test your application, you will deployed it via the ```deploy.sh```. However, for now the dummy deployment is not working (on purpose), so do not be surprised if the first call will result in an error. This is happening on purpose and you will fix this later.

```
PHASE1_URL="https://phase1....westus3.azurecontainerapps.io"

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

## Inner Loop and local testing 

Go to directory src-agents/phase1 (for other phases, pick the correct folder) in bash.

Start up the agent api
```
pip install -r requirements.txt

uvicorn main:app --reload
```

This starts a local python webserver which hosts your main.py. Now you can work on localhost to test your application. If you get errors here, your stuff also won't run in the cloud.

### Phase 1 test

Test the api with eg:
```
URL='http://localhost:8000'
# URL='https://phase1..uksouth.azurecontainerapps.io'

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

### Phase 2 test

```
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
```

### Phase 3 test

```
curl -X 'POST' \
  "$URL/ask" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "question": "When was the release year of Ant-Man and the Quantum Invasion? 1) 2026 2) 2022 3) 2020 4) 2027",
  "type": "multiple_choice",
  "correlationToken": "1234567890"
}'

```

### Phase 4 test

```

curl -X 'POST' \
  "$URL/ask" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "question": "In the Marvel Cinematic Universe, who is the actor that brings Tony Stark to life? Robert Downey Jr., Chris Hemsworth, Chris Evans, Mark Ruffalo",
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
