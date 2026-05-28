#Use the ChatCompletions API to chat with the model
import os
from dotenv import load_dotenv

# import namespaces
#Import namespaces and add the following code to import the namespace you will need to use the OpenAI SDK:
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
load_dotenv()
azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
model_deployment = os.getenv("MODEL_DEPLOYMENT")

# Initialize the OpenAI client
token_provider = get_bearer_token_provider(DefaultAzureCredential(),"https://ai.azure.com/.default")
openai_client=OpenAI(base_url=azure_openai_endpoint,api_key=token_provider)
completion = openai_client.chat.completions.create(
    model="gpt-4.1",  # Your model deployment name
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "When was Microsoft founded?"}
    ]
)

print(completion.choices[0].message.content)