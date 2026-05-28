import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
#Load environment variable from .env file
load_dotenv()
project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT")
model=os.getenv("MODEL_DEPLOYMENT")
project_client=AIProjectClient(credential=DefaultAzureCredential(),endpoint=project_endpoint)
#create openai compartible client from foundry project client
openai_client=project_client.get_openai_client()
response=openai_client.chat.completions.create(
    model=model,
    messages=[
        {"role":"system","content":"You are a helpful assistant."},
        {"role":"user","content":"What is Azure AI?"}
    ]
)
print(response.choices[0].message.content)