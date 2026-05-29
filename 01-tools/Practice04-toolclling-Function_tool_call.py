import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
# Function to get the current time
def get_time():
    return f"The time is {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
#main function
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
    function_tools = [
        {
            "type": "function",
            "name": "get_time",
            "description": "Get the current time"
        }
    ]
    # Initialize messages with a system prompt
    messages = [
        {"role": "developer", "content": "You are an AI assistant that provides information."},
    ]
    # Loop until the user types 'quit'
    while True:
        prompt = input("\nEnter a prompt (or type 'quit' to exit)\n")
        if prompt.lower() == "quit":
            break

        # Append the user prompt to the messages
        messages.append({"role": "user", "content": prompt})

        # Get initial response
        response = openai_client.responses.create(
            model=model_deployment,
            input=messages,
            tools=function_tools
        )

        # Append model output to the messages
        messages += response.output

        # Was there a function call?
        for item in response.output:
            if item.type == "function_call" and item.name == "get_time":
                current_time = get_time()
                messages.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": current_time
                })

                # Get a follow up response using the tool output
                response = openai_client.responses.create(
                    model=model_deployment,
                    instructions="Answer only with the tool output.",
                    input=messages,
                    tools=function_tools
                )

        print(response.output_text)


# Run the main function when the script starts
if __name__ == '__main__':
    main()
    