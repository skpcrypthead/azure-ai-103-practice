import os
from dotenv import load_dotenv

# import namespaces
from openai import OpenAI
from azure.identity import DefaultAzureCredential,get_bearer_token_provider

def main(): 
    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        # Get configuration settings 
        load_dotenv()
        azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        model_deployment = os.getenv("MODEL_DEPLOYMENT")

        # Initialize the OpenAI client
        token_provider=get_bearer_token_provider(DefaultAzureCredential(),"https://ai.azure.com/.default")
        azure_openai_client=OpenAI(base_url=azure_openai_endpoint,api_key=token_provider)

        
        # Loop until the user wants to quit
        #Unlike the Responses API, the ChatCompletions API doesn't provide a stateful response tracking feature. To retain conversational context, you must write code to manually track previous prompts and responses.
        conversation_messages=[
            {
                "role": "system",
                "content": "You are a helpful AI assistant that answers questions and provides information."
           }
       ]
        while True:
            input_text = input('\nEnter a prompt (or type "quit" to exit): ')
            if input_text.lower() == "quit":
                break
            if len(input_text) == 0:
                print("Please enter a prompt.")
                continue

            # Get a response
            # Add the user message to the conversation history
            conversation_messages.append(
                {"role": "user",
                "content": input_text}
           )
            # Get a completion response based on the conversation history
            completion=azure_openai_client.chat.completions.create(
                model=model_deployment,
                messages=conversation_messages
            )
            assistant_message =completion.choices[0].message.content
            print("\nAssistant:", assistant_message)
            # Append the response to the conversation history to maintain context for the next run
            conversation_messages.append(
                {"role": "assistant",
                "content": assistant_message}
            )

    except Exception as ex:
        print(ex)

if __name__ == '__main__': 
    main()
