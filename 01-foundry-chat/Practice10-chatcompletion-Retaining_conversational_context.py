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
# Initial messages
conversation_messages=[
    {
        "role": "system",
        "content": "You are a helpful AI assistant that answers questions and provides information."
    }
]

# Add the first user message
conversation_messages.append(
    {"role": "user",
    "content": "When was Microsoft founded?"}
)

# Get a completion
completion = openai_client.chat.completions.create(
    model="gpt-4.1",
    messages=conversation_messages
)
assistant_message = completion.choices[0].message.content
print("Assistant:", assistant_message)

# Append the response to the conversation
conversation_messages.append(
    {"role": "assistant", "content": assistant_message}
)

# Add the next user message
conversation_messages.append(
    {"role": "user",
    "content": "Who founded it?"}
)

# Get a completion
completion = openai_client.chat.completions.create(
    model="gpt-4.1",
    messages=conversation_messages
)
assistant_message = completion.choices[0].message.content
print("Assistant:", assistant_message)

# and so on...