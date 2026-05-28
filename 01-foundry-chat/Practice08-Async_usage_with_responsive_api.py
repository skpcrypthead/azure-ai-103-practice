import os
from dotenv import load_dotenv
import asyncio
from openai import AsyncOpenAI
from azure.identity.aio import DefaultAzureCredential,get_bearer_token_provider
async def main():
    load_dotenv()
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    model=os.getenv("MODEL_DEPLOYMENT")
    token=get_bearer_token_provider(DefaultAzureCredential(),"https://ai.azure.com/.default")
    async_client=AsyncOpenAI(base_url=endpoint,api_key=token)

    response = await async_client.responses.create(
        model="gpt-4.1",
        input="Explain quantum computing briefly."
    )
    print(response.output_text)
if __name__ == '__main__': 
    asyncio.run(main())
