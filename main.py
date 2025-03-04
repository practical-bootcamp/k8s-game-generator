import asyncio
import os

from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.agents.web_surfer import MultimodalWebSurfer
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


# pip install -U autogen-agentchat autogen-ext[openai,web-surfer]
# playwright install


async def main() -> None:
    model_client = az_model_client
    assistant = AssistantAgent("assistant", model_client)
    web_surfer = MultimodalWebSurfer(
        name="web_surfer",
        model_client=model_client,
        start_page="https://www.google.com",
    )
    user_proxy = UserProxyAgent("user_proxy")
    termination = TextMentionTermination("exit")  # Type 'exit' to end the conversation.
    team = RoundRobinGroupChat(
        [web_surfer, assistant, user_proxy], termination_condition=termination
    )
    await Console(team.run_stream(task="Who is Cyrus Wong?"))


asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
