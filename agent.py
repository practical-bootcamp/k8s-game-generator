# uv tool install mcp-server-fetch
# verify it in path by running uv tool update-shell
import asyncio
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools


async def main() -> None:
    # Setup server params for local filesystem access
    fetch_mcp_server = StdioServerParams(command="uvx", args=["mcp-server-fetch"])
    fetch_tools = await mcp_server_tools(fetch_mcp_server)

    file_mcp_server = StdioServerParams(
        command="npx",
        args=[
            "-y",
            "@modelcontextprotocol/server-filesystem",
            "/workspaces/k8s-game-generator/task/",
        ],
    )
    file_tools = await mcp_server_tools(file_mcp_server)

    tools = fetch_tools + file_tools

    # Create an agent that can use the fetch tool.
    model_client = AzureOpenAIChatCompletionClient(
        azure_deployment=os.getenv("AZURE_DEPLOYMENT"),
        model=os.getenv("MODE_NAME"),
        api_version=os.getenv("API_VERSION"),
        azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        api_key=os.getenv("API_KEY"),
    )
    agent1 = AssistantAgent(name="ai_assistant_1", model_client=model_client, tools=tools, reflect_on_tool_use=True)  # type: ignore
    agent2 = AssistantAgent(name="ai_assistant_2", model_client=model_client, tools=tools, reflect_on_tool_use=True)  # type: ignore

    text_termination = TextMentionTermination("successfully written")
    # Define a termination condition that stops the task after 5 messages.
    max_message_termination = MaxMessageTermination(10)
    # Combine the termination conditions using the `|`` operator so that the
    # task stops when either condition is met.
    termination = text_termination | max_message_termination
    team = RoundRobinGroupChat([agent1, agent2], termination_condition=termination)
    # The agent can now use any of the filesystem tools
    await Console(
        team.run_stream(
            task="""
            read https://www.vtc.edu.hk/admission/tc/programme/it114115-higher-diploma-in-cloud-and-data-centre-administration/basic-information/, 
            summerize it into markdown format.
            finally summerize result write_file to /workspaces/k8s-game-generator/task/summerize.md.""",
            cancellation_token=CancellationToken(),
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
