import os
from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential,get_bearer_token_provider
load_dotenv()
endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
model=os.getenv("MODEL_DEPLOYMENT")
token=get_bearer_token_provider(DefaultAzureCredential(),"https://ai.azure.com/.default")
client=OpenAI(base_url=endpoint,api_key=token)
# First turn in the conversation
response1 = client.responses.create(
    model="gpt-4.1",
    instructions="You are a helpful AI assistant that explains technology concepts clearly.",
    input="What is machine learning?"
)

print("Assistant:", response1.output_text)

# Continue the conversation
response2 = client.responses.create(
    model="gpt-4.1",
    instructions="You are a helpful AI assistant that explains technology concepts clearly.",
    input="Can you give me an example?",
    previous_response_id=response1.id
)

print("Assistant:", response2.output_text)
