import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# Single unified endpoint connects to your entire project environment
project_client = AIProjectClient(
    endpoint="https://sitakanta-projects-resource.services.ai.azure.com/api/projects/sitakanta-projects",
    credential=DefaultAzureCredential()
)

# 1. You can list infrastructure connections or execute evaluation rules natively
connections = project_client.connections.list()

# 2. Extract an authenticated OpenAI-compatible client to run Responses or Agent tools
openai_client = project_client.get_openai_client()

response = openai_client.responses.create(
    model="gpt-4.1", # Can even route to non-OpenAI models deployed in your hub
    input="What is quantum computing?",
    max_output_tokens=500
)
print(response.output_text[:200])
print('\n')
# 1. Fetch all connections configured in your AI Foundry Project

print("\n=== Configured Project Connections ===")
for conn in connections:
    # Print the clean attributes from each connection object
    print(f"Name:        {conn.name}")
    print(f"Type:        {conn.type}")
    print(f"Endpoint/ID: {conn.endpoint_url if hasattr(conn, 'endpoint_url') else 'N/A'}")
    print("-" * 40)