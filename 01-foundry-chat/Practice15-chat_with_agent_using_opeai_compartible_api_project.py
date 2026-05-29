"""
Azure AI Foundry Agent Interaction Script.
This program connects to a pre-configured agent in Azure AI Foundry 
using the OpenAI-compatible Responses API and maintains context across multi-turn chats.
"""

import os
import sys
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


def handle_chat_session(openai_client: object, agent_name: str, agent_version: str) -> None:
    """
    Handles the interactive, stateful chat loop with the Azure AI Foundry Agent.
    """
    print("\n" + "=" * 50)
    print("Agent session started. Ready for your input.")
    print("Type 'quit' or 'exit' at any time to close the session.")
    print("=" * 50)

    conversation_history = []

    while True:
        try:
            input_text = input('\nEnter a prompt: ').strip()
            
            if input_text.lower() in ("quit", "exit"):
                print("\nExiting agent session. Goodbye!")
                break
                
            if not input_text:
                print("Please enter a valid, non-empty prompt.")
                continue

            # Append user input to history to maintain context
            conversation_history.append({"role": "user", "content": input_text})

            # Call the OpenAI-compatible Responses API
            response = openai_client.responses.create(
                input=conversation_history,
                extra_body={
                    "agent_reference": {
                        "name": agent_name, 
                        "version": agent_version, 
                        "type": "agent_reference"
                    }
                },
            )
            
            # Extract and print response
            agent_reply = response.output_text
            print(f"\nAgent: {agent_reply}")
            
            # Append agent response to history for the next turn
            conversation_history.append({"role": "assistant", "content": agent_reply})

        except Exception as ex:
            print(f"\n[Error during request]: {ex}")
            # Safely remove the failed user prompt so history doesn't become corrupted
            if conversation_history and conversation_history[-1]["role"] == "user":
                conversation_history.pop()


def main() -> None:
    """
    Main execution pipeline: loads environment, initializes clients, and triggers chat.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    project_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    
    # Validation check to ensure environment variables are configured correctly
    if not project_endpoint:
        print("Error: FOUNDRY_PROJECT_ENDPOINT is missing from your environment setup / .env file.", file=sys.stderr)
        sys.exit(1)

    # Configuration for the existing agent
    my_agent = "Foundry-Syncronous-Agent1"
    my_version = "1"

    print("Initializing Azure AI Project Client...")
    try:
        # Initialize identity and core project client
        credential = DefaultAzureCredential()
        project_client = AIProjectClient(endpoint=project_endpoint, credential=credential)
        
        # Get the OpenAI-compatible client
        openai_client = project_client.get_openai_client()
        
    except Exception as e:
        print(f"Failed to initialize Azure AI clients: {e}", file=sys.stderr)
        sys.exit(1)

    # Start the interactive conversation
    handle_chat_session(openai_client, my_agent, my_version)


if __name__ == "__main__":
    main()