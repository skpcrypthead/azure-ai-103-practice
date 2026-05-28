import os
from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential,get_bearer_token_provider
load_dotenv()
endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
model="Phi-4-mini-reasoning"
token=get_bearer_token_provider(DefaultAzureCredential(),"https://ai.azure.com/.default")
client=OpenAI(base_url=endpoint,api_key=token)
response=client.responses.create(
    model=model,
    instructions="You are a helpful AI assistant that answers questions clearly and concisely.",
    input="What are the benefits of small language models?" 
)

print(response.output_text)