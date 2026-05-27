import os
from dotenv import load_dotenv

# import namespaces for async
import asyncio
from openai import AsyncOpenAI
from azure.identity.aio import DefaultAzureCredential,get_bearer_token_provider

async def main(): 

    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        # Get configuration settings 
        load_dotenv()
        azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        model_deployment = os.getenv("MODEL_DEPLOYMENT")

        # Initialize an async OpenAI client
        credential=DefaultAzureCredential()
        token_provider=get_bearer_token_provider(credential,"https://ai.azure.com/.default")
        async_client=AsyncOpenAI(base_url=azure_openai_endpoint,api_key=token_provider)
        

        

        # Track responses
        last_response_id = None

        # Loop until the user wants to quit
        last_response_id=None
        while True:
            input_text = input('\nEnter a prompt (or type "quit" to exit): ')
            if input_text.lower() == "quit":
                break
            if len(input_text) == 0:
                print("Please enter a prompt.")
                continue

            # Await an asynchronous response
            stream_response=await async_client.responses.create(
                model=model_deployment,
                instructions="You are a helpful AI assistant that answers questions and provides information.",
                input=input_text,
                previous_response_id=last_response_id,
                stream=True
            )
            async for event in stream_response:
                
                if event.type == "response.output_text.delta":
                    print(event.delta, end="")
                elif event.type == "response.completed":
                    last_response_id = event.response.id
            print()

            

    except Exception as ex:
        print(ex)

    finally:
        await credential.close()



if __name__ == '__main__': 
    asyncio.run(main())
