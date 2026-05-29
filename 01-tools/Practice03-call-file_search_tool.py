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
    #create a vector store and upload a file to it then use file_seqarch tool to query the file
    vector_store = openai_client.vector_stores.create(name="policy-docs")
    openai_client.vector_stores.files.upload_and_poll(
        vector_store_id=vector_store.id,
        file=open("expenses_policy.pdf", "rb")
    )
    response=openai_client.responses.create(
        model=model_deployment,
        instructions="You are an AI assistant that provides information from HR policy documents.",
        input="What's the maximum amount I can claim so it requires approval?",
        tools=[{
            "type": "file_search",
            "vector_store_ids": [vector_store.id]
        }],
        include=["file_search_call.results"]
    )
    print("\n--- Response ---")
    print(response.output_text)   

if __name__ == '__main__':
    main()
    