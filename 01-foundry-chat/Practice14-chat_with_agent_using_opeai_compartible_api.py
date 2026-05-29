#This program will interact with foundry created agent which i created by going throwug foundry portal
#then it will use openai compatible api to chat with the agent and get response from it
import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
# Load environment variables from .env file
load_dotenv()
project_endppoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT")
model_deployment=os.getenv("MODEL_DEPLOYMENT")
#inititlize project client
credential=DefaultAzureCredential()
project_client=AIProjectClient(endpoint=project_endppoint,credential=credential)
#define the existing agent configuration
my_agent = "Foundry-Syncronous-Agent1"
my_version = "1"
#Get the OpenAI-compatible client
openai_client=project_client.get_openai_client()
#chat with the agent
print("Agent session started. Ready for your input.")
print("-" * 50)
# 4. Maintain conversation history array
# Loop until the user wants to quit
conversation_history = []
while True:
    input_text=input('\nEnter a prompt (or type "quit" to exit): ')
    if input_text.lower()=="quit":
        break
    if len(input_text.strip())==0:
        print("Please enter a valid prompt")
        continue
    # Append user input to conversation history to maintain context
    conversation_history.append({"role": "user", "content": input_text})
    try:
        response=openai_client.responses.create(
            input=conversation_history,
            extra_body={
                "agent_reference": {
                    "name": my_agent, 
                    "version": my_version, 
                    "type": "agent_reference"
                }
            },
        )
        # Display the response text back to the user
        agent_reply=response.output_text
        print(f"\nAgent: {agent_reply}")
        #Append agent resaponse to conversation history to maintain context
        conversation_history.append({"role": "assistant", "content": agent_reply})
    except Exception as ex:
        print(ex)
        # Clean up the last user prompt from history since it failed to get a response
        conversation_history.pop()
    
    

