from models.feedback import Feedback, ConnectionCheck, StJudeCall
from utils.utils import progressBar
from discord import Intents, app_commands, Client, Interaction, InteractionMessage, Permissions, Embed, ForumChannel, CategoryChannel
from discord.app_commands import CommandTree
from dotenv import load_dotenv
import os
import json
import requests
from requests import Response

load_dotenv()
intents: Intents = Intents.default()
intents.message_content = True

client: Client = Client(intents=intents)
tree: CommandTree[Client] = app_commands.CommandTree(client)

test: str = ":brook:1237150453691711590"
thumbs_up: str = '👍'
st_jude_emote: str = "stjude:739880520703541268"
admin_mods_perms = Permissions()
admin_mods_perms.administrator = True
admin_mods_perms.moderate_members = True


@tree.command(name="connection_check", description="Log a connection check for the conduit podcast")
async def connection_check(interaction: Interaction, previous_connection: str, status: str, next_connection: str, of_the_show_name: str | None):
    connection: ConnectionCheck = ConnectionCheck(
        previous_connection, status, next_connection, of_the_show_name, interaction.user)
    response = await interaction.response.send_message(str(connection))
    if isinstance(response.resource, InteractionMessage):
        await response.resource.add_reaction(thumbs_up)
        await response.resource.add_reaction(test)
    # TODO Add to form


@tree.command(name="ask_backstage", description="Ask a question for the beards")
async def backstage(interaction: Interaction, question: str):
    response = await interaction.response.send_message(question)
    if isinstance(response.resource, InteractionMessage):
        await response.resource.add_reaction(thumbs_up)
        await response.resource.add_reaction(test)
    # TODO Add to form

st_jude_slug: str = 'relay-for-st-jude-2024'


@tree.command(name="set_st_jude_slug", description="Sets the st-jude event slug")
@app_commands.default_permissions(admin_mods_perms)
async def set_slug(interaction: Interaction, slug: str):
    global st_jude_slug
    st_jude_slug = slug
    await interaction.response.send_message(f"This year's st-jude event slug has been set to {slug}")


@tree.command(name="donate", description="Donate to St-Jude")
@app_commands.default_permissions(admin_mods_perms)
async def donate(interaction: Interaction):
    # await interaction.response.defer()
    headers = {"content-type": "application/json", "accept": "*/*"}
    call = StJudeCall(st_jude_slug)
    r: Response = requests.post("https://api.tiltify.com",
                                json=call.toDict(), headers=headers)
    info = r.json()
    raised: float = float(info["data"]["teamEvent"]
                          ["totalAmountRaised"]["value"])
    goal: float = float(info["data"]["teamEvent"]["goal"]["value"])
    embed = Embed(
        title="Donate to St. Jude!",
        url="https://www.stjude.org/relay",
        description="St. Jude Children's Research Hospital treats the toughest childhood cancers and deserves your money! https://www.stjude.org/relay",
        color=0xffcc33
    )
    embed.set_thumbnail(
        url="https://s3.amazonaws.com/relayfm/assets/Square-Campaign-URL-2024.png")
    embed.add_field(name="Currently Raised:",
                    value=f"${raised:,.2f}", inline=False)
    embed.add_field(name="Fundraising Target:",
                    value=f"${goal:,.2f}", inline=False)
    embed.add_field(name="Progress:",
                    value=f"{round(raised/goal*100, 2)}%", inline=False)
    embed.set_footer(text=progressBar(raised, goal))
    mess = await interaction.response.send_message(embed=embed)
    await interaction.followup.send("<https://www.stjude.org/relay>")
    if isinstance(mess.resource, InteractionMessage):
        # mess = await interaction.channel.send("<https://www.stjude.org/relay>")
        await mess.resource.add_reaction(test)


@client.event
async def on_ready():
    await tree.sync()
    a = 0


token = os.getenv("token")
if token is not None:
    client.run(token)
