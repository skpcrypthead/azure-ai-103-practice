"""
Azure AI Foundry Agent Interaction Script.
This program dynamically provisions a fresh agent version using a specified model 
deployment, initializes an OpenAI-compatible client, and maintains a multi-turn chat
using safe server-side response ID chaining.
"""

import os
import sys
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition


def handle_chat_session(openai_client: object, agent_name: str, agent_version: str, model_deployment_name: str) -> None:
    """
    Handles the interactive, stateful chat loop via server-side response history tracking.
    """
    print("\n" + "=" * 50)
    print(f"Agent session started with '{agent_name}' (v{agent_version}). Ready for input.")
    print("Type 'quit' or 'exit' at any time to close the session.")
    print("=" * 50)

    # Track conversation history implicitly using the server-side response ID chain
    last_response_id = None

    while True:
        try:
            input_text = input('\nEnter a prompt: ').strip()
            
            if input_text.lower() in ("quit", "exit"):
                print("\nExiting agent session. Goodbye!")
                break
                
            if not input_text:
                print("Please enter a valid, non-empty prompt.")
                continue

            # 1. Base parameters for the payload
            api_kwargs = {
                "model": model_deployment_name,
                "input": input_text,
                "extra_body": {
                    "agent_reference": {
                        "name": agent_name, 
                        "version": agent_version, 
                        "type": "agent_reference"
                    }
                }
            }

            # 2. Crucial Step: Only add previous_response_id if it is NOT None.
            # This completely avoids passing a 'null' object to Azure's strict validator.
            if last_response_id:
                api_kwargs["previous_response_id"] = last_response_id

            # Explicit routing via kwargs unpacking
            response = openai_client.responses.create(**api_kwargs)
            
            # Extract and print response
            agent_reply = response.output_text
            print(f"\nAgent: {agent_reply}")
            
            # Save the new response ID to automatically link the context for the next turn
            last_response_id = response.id

        except Exception as ex:
            print(f"\n[Error during request]: {ex}")


def main() -> None:
    """
    Main execution pipeline: loads environment, provisions a fresh agent, and triggers chat.
    """
    # Load environment variables from .env file (if present)
    load_dotenv()
    
    # Hardcoded endpoint from your environment configuration
    endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")

    # Read deployment name from environment configuration
    model_deployment_name = os.getenv("MODEL_DEPLOYMENT")
    fresh_agent_name = "Dynamic-GPT4-Agent1"

    if not model_deployment_name:
        print("Error: MODEL_DEPLOYMENT environment variable is missing from your .env file.", file=sys.stderr)
        sys.exit(1)

    print("Initializing Azure AI Project Client...")
    try:
        # Initialize identity and project client
        credential = DefaultAzureCredential()
        project_client = AIProjectClient(endpoint=endpoint, credential=credential)
        
        # 1. Dynamically provision/register a fresh agent version
        print(f"Creating fresh agent version for '{fresh_agent_name}' using deployment '{model_deployment_name}'...")
        agent_definition = PromptAgentDefinition(
            model=model_deployment_name,
            instructions="You are a helpful, precise, and sophisticated AI assistant."
        )
        
        fresh_agent = project_client.agents.create_version(
            agent_name=fresh_agent_name,
            definition=agent_definition
        )
        
        # Capture the true underlying string identifiers returned directly by the orchestrator
        my_agent = fresh_agent.name
        my_version = fresh_agent.version
        print(f"Fresh Agent successfully provisioned! (System Name: {my_agent}, Version: {my_version})")

        # 2. Get the global project level OpenAI client configuration
        openai_client = project_client.get_openai_client()
        
    except Exception as e:
        print(f"\nFailed to initialize Azure AI resources: {e}", file=sys.stderr)
        sys.exit(1)

    # 3. Start the interactive conversation loop with explicit tracking references
    handle_chat_session(openai_client, my_agent, my_version, model_deployment_name)


if __name__ == "__main__":
    main()