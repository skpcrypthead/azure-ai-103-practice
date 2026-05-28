import os
from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential,get_bearer_token_provider
load_dotenv()
endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
model=os.getenv("MODEL_DEPLOYMENT")
token=get_bearer_token_provider(DefaultAzureCredential(),"https://ai.azure.com/.default")
client=OpenAI(base_url=endpoint,api_key=token)
try:
    # Start with initial message
    conversation_history = [
        {
            "type": "message",
            "role": "user",
            "content": "What is machine learning?"
        }
    ]
    # First response
    response1 = client.responses.create(
        model="gpt-4.1",
        input=conversation_history
    )
    print("Assistant:", response1.output_text)
    print(response1.id)
    # Add assistant response to history
    conversation_history += response1.output
    # Add new user message
    conversation_history.append({
        "type": "message",
        "role": "user", 
        "content": "Can you give me an example?"
    })
     # Second response with full history
    response2 = client.responses.create(
        model="gpt-4.1",
        input=conversation_history
    )
    print("Assistant:", response2.output_text)
    
    print("conversation history:", conversation_history)
    
    # Retrieve a previous response
    response_id = "resp_06fd96309858634e006a17fb3110b88190b8fcb0cedea0cc9d"  # Example ID
    previous_response = client.responses.retrieve(response_id)

    print(f"Previous response: {previous_response.output_text}")
   



except Exception as ex:
    print(f"Error: {ex}")

except Exception as ex:
    print(f"Error: {ex}")
