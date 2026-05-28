import os
import dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential,get_bearer_token_provider
#load environment variables from .env file

dotenv.load_dotenv()
openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
model=os.getenv("MODEL_DEPLOYMENT")
# Initialize the OpenAI client with Azure AD authentication
token_provider=get_bearer_token_provider(DefaultAzureCredential(),"https://ai.azure.com/.default")
client=OpenAI(base_url=openai_endpoint,api_key=token_provider)
response=client.responses.create(
    model=model,
    input="what is quantum computing?",
    instructions="You are a helpful AI assistant that answers questions clearly and concisely.",
    temperature=0.2,
    max_output_tokens=100,
    top_p=0.5
)
print(f"Response: {response.output_text}")
print(f"Response ID: {response.id}")
print(f"Tokens used: {response.usage.total_tokens}")
print(f"Status: {response.status}")