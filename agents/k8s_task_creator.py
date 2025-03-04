import asyncio
import os

from autogen_core.models import UserMessage
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))


az_model_client = AzureOpenAIChatCompletionClient(
    azure_deployment=os.getenv("AZURE_DEPLOYMENT"),
    model=os.getenv("MODE_NAME"),
    api_version=os.getenv("API_VERSION"),
    azure_endpoint=os.getenv("AZURE_ENDPOINT"),
    api_key=os.getenv("API_KEY"),
)


async def main():
    result = await az_model_client.create(
        [UserMessage(content="What is the capital of France?", source="user")]
    )
    print(result)


asyncio.run(main())
