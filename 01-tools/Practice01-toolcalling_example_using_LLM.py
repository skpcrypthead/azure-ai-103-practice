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
    
    print(f"Sending prompt to model '{model_deployment}' with code_interpreter tool...")
    try:
        # Get response using the code_interpreter tool
        response = openai_client.responses.create(
            model=model_deployment,  # FIXED: Removed curly braces {} so it passes as a clean string!
            instructions="You are an AI assistant that provides information. Use the python tool to run code for math problems.",
            input="What is the square root of 16?",
            tools=[{
                "type": "code_interpreter",
                "container": {"type": "auto"}
            }]
        )
        
        print("\n--- Response ---")
        print(response.output_text)   
        
    except Exception as ex:
        print(f"\n[Error during request]: {ex}")

if __name__ == '__main__':
    main()