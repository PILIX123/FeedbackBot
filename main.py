from models.feedback import Feedback, ConnectionCheck
from utils.utils import progressBar
from discord import Intents, app_commands, Client, Interaction, InteractionMessage
from discord.app_commands import CommandTree
from dotenv import load_dotenv
import os

load_dotenv()
intents: Intents = Intents.default()
intents.message_content = True

client: Client = Client(intents=intents)
tree: CommandTree[Client] = app_commands.CommandTree(client)

test: str = ":brook:1237150453691711590"
thumbs_up: str = '👍'


@tree.command(name="connection_check", description="Log a connection check for the conduit podcast")
async def connection_check(interaction: Interaction, previous_connection: str, status: str, next_connection: str):
    connection: ConnectionCheck = ConnectionCheck(
        previous_connection, status, next_connection, None, interaction.user)
    response = await interaction.response.send_message(str(connection))
    if isinstance(response.resource, InteractionMessage):
        await response.resource.add_reaction(thumbs_up)
        await response.resource.add_reaction(test)


@client.event
async def on_ready():
    await tree.sync()


token = os.getenv("token")
if token is not None:
    client.run(token)
