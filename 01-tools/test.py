import os
from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

def main():
    # Load environment variables
    load_dotenv()
    
    model_deployment = os.getenv("MODEL_DEPLOYMENT")
    azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    
    if not model_deployment or not azure_openai_endpoint:
        print("Error: Missing environment variables. Please check your .env file.")
        return

    print("Initializing Azure OpenAI Client with Token Provider...")
    # Initialize authentication token provider
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), 
        "https://ai.azure.com/.default"
    )
    
    openai_client = OpenAI(
        base_url=azure_openai_endpoint,
        api_key=token_provider()
    )
    stores = openai_client.vector_stores.list()

    for store in stores.data:
        print(f"ID: {store.id}")
        print(f"Name: {store.name}")
        print(f"Status: {store.status}")
        print("-" * 50)
if __name__ == '__main__':
    main()