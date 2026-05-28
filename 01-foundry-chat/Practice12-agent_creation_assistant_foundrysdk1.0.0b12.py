# import required Libraries
#with azure azure-ai-projects==1.0.0b12 pip install azure-ai-projects==1.0.0b12
#the program will only work with the beta version of the SDK, which is 1.0.0b12 as of June 2024.
# Please ensure you have this version installed to avoid any compatibility issues.
# import required Libraries
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

def main():
    
    # 1. Loading environment variables and initializing variables
    load_dotenv()
    project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT")
    
    # 2. Initializing Foundry project client
    project_client = AIProjectClient(endpoint=project_endpoint, credential=DefaultAzureCredential())
    
    # 3. Creating agent using the Beta v1 method
    print("Creating agent...")
    agent = project_client.agents.create_agent(
        model=model_deployment,
        name="Foundry-Syncronous-Agent",
        instructions="You are a helpful assistant that provides concise and accurate answers to user queries.",
    )
    print(f"Agent created with ID: {agent.id}")
    
    # 4. Create thread
    print("Creating thread for conversation...")
    thread = project_client.agents.threads.create()
    print(f"Thread created with ID: {thread.id}")
    
    # 5. Post message
    print("Sending message to the agent...")
    project_client.agents.messages.create(
        thread_id=thread.id,
        role="user",
        content="what is azure openai projects?"
    )
    
    # 6. Execute run loop execution
    print("Processing the agent to get the response...")
    run = project_client.agents.runs.create_and_process(
        thread_id=thread.id,
        agent_id=agent.id
    )
    print(f"Run finished with status: {run.status}")
    
    # 7. Collect response payload pages
    messages = project_client.agents.messages.list(thread_id=thread.id)
    
    print("\n--- Response ---")
    # FIX: Iterate directly over the ItemPaged 'messages' object
    for message in messages:
        if message.role == "assistant":
            # Extract the raw string value out of the content object structure
            print(message.content[0].text.value)
            break

# Top-level execution wrapper
if __name__ == "__main__":
    main()
    
    
    