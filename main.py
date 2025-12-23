import os

from discord import (Activity, ActivityType, Client, Intents, Interaction,
                     InteractionMessage, Permissions, app_commands)
from discord.app_commands import (AppCommandError, CommandInvokeError,
                                  CommandTree)
from dotenv import load_dotenv

from models.feedback import (AskUpgrade, BackstageQuestion, ConnectionCheck,
                             SnellTalk, SpotlightQuestion, WebForm)
from models.tiltify import FullCampaign, generate_tiltify_campain
from utils.utils import CustomEmotes

load_dotenv()
intents: Intents = Intents.default()
intents.message_content = True

client: Client = Client(intents=intents)
tree: CommandTree[Client] = app_commands.CommandTree(client)

admin_mods_perms = Permissions()
admin_mods_perms.administrator = True
admin_mods_perms.moderate_members = True
embed_url: str = "https://s3.amazonaws.com/relayfm/assets/Square-Campaign-URL-2025.png"


@tree.command(name="connection_check", description="Log a connection check for the conduit podcast")
async def connection_check(interaction: Interaction, previous_connection: str, status: str, next_connection: str, of_the_show_name: str | None):
    await interaction.response.defer()

    connection: ConnectionCheck = ConnectionCheck(
        previous_connection, status, next_connection, of_the_show_name, interaction.user)

    form = WebForm("https://www.relay.fm/conduit/feedback", connection)
    success = await form.submit_form("https://www.relay.fm/shows/conduit/update?id=conduit")

    response = await interaction.edit_original_response(content=f"{str(connection)}")
    if not success:
        raise RuntimeError("Couldnt be sent to feedback form")
    if isinstance(response, InteractionMessage):
        await response.add_reaction(CustomEmotes.ThumbsUp.value)
        await response.add_reaction(CustomEmotes.Conduit.value)


@tree.command(name="ask_backstage", description="Ask a question for the beards")
async def ask_backstage(interaction: Interaction, question: str):
    await interaction.response.defer()

    feedback = BackstageQuestion(question, interaction.user)

    form = WebForm("https://www.relay.fm/membership/feedback", feedback)
    success = await form.submit_form(
        "https://www.relay.fm/shows/membership/update?id=membership")

    response = await interaction.edit_original_response(content=str(feedback))
    if not success:
        raise RuntimeError("Couldnt be sent to feedback form")
    if isinstance(response, InteractionMessage):
        await response.add_reaction(CustomEmotes.ThumbsUp.value)
        await response.add_reaction(CustomEmotes.Backstage.value)


@tree.command(name="ask_spotlight", description="Ask a question for the relay host/friend")
async def ask_spotlight(interaction: Interaction, question: str):
    await interaction.response.defer()

    feedback = SpotlightQuestion(question, interaction.user)

    form = WebForm("https://www.relay.fm/membership/feedback", feedback)
    success = await form.submit_form(
        "https://www.relay.fm/shows/membership/update?id=membership")

    response = await interaction.edit_original_response(content=str(feedback))
    if not success:
        raise RuntimeError("Couldnt be sent to feedback form")
    if isinstance(response, InteractionMessage):
        await response.add_reaction(CustomEmotes.ThumbsUp.value)
        await response.add_reaction(CustomEmotes.Spotlight.value)


# @tree.command(name="ask_upgrade", description="Submit a question for Jason and Myke to maybe answer on the podcast")
async def ask_upgrade(interaction: Interaction, question: str, anonymous: bool = False):
    await interaction.response.defer(ephemeral=anonymous)

    feedback = AskUpgrade(question, interaction.user, anonymous=anonymous)

    form = WebForm("https://www.relay.fm/upgrade/feedback", feedback)
    success = await form.submit_form(
        "https://www.relay.fm/shows/upgrade/update?id=upgrade")

    if anonymous and success:
        return await interaction.edit_original_response(content=f"You're question was sent to the feedback form anonymously")
    elif anonymous and not success:
        return await interaction.edit_original_response(content=f"There was an error submitting your question to the feedback try again later")
    if not success:
        raise RuntimeError("Couldnt be sent to feedback form")
    response = await interaction.edit_original_response(content=f"{str(feedback)}")
    if isinstance(response, InteractionMessage):
        await response.add_reaction(CustomEmotes.ThumbsUp.value)
        await response.add_reaction(CustomEmotes.Upgrade.value)


# @tree.command(name="snell_talk", description="Send in a question to open the show")
async def snell_talk(interaction: Interaction, question: str, anonymous: bool = False):
    await interaction.response.defer(ephemeral=anonymous)

    feedback = SnellTalk(question, interaction.user, anonymous=anonymous)

    form = WebForm("https://www.relay.fm/upgrade/feedback", feedback)
    success = await form.submit_form(
        "https://www.relay.fm/shows/upgrade/update?id=upgrade")

    if anonymous and success:
        return await interaction.edit_original_response(content=f"You're question was sent to the feedback form anonymously")
    elif anonymous and not success:
        return await interaction.edit_original_response(content=f"There was an error submitting your question to the feedback try again later")
    if not success:
        raise RuntimeError("Couldnt be sent to feedback form")
    response = await interaction.edit_original_response(content=f"{str(feedback)}")
    if isinstance(response, InteractionMessage):
        await response.add_reaction(CustomEmotes.ThumbsUp.value)
        await response.add_reaction(CustomEmotes.Snell.value)


@tree.error
async def on_error(interaction: Interaction, error: AppCommandError, /):
    if isinstance(error, CommandInvokeError):
        # TODO Add logger
        error.command.qualified_name
        error.original
        print(error.command.qualified_name)
        print(error.original)
    if interaction.response.is_done():
        mess = await interaction.original_response()
        await mess.add_reaction(CustomEmotes.Error.value)
    else:
        if interaction.command is not None:
            await interaction.response.send_message(f"There was an error executing the {interaction.command.qualified_name} command")
        else:
            await interaction.response.send_message("There was an error with the interaction")


async def set_embed_url(interaction: Interaction, image_url: str):
    # TODO: Make sure we save this into a mounted place so we can save the file path to a json
    global embed_url
    embed_url = image_url
    await interaction.response.send_message(f"This year's St. Jude embed image has been set to {image_url}")


@tree.command(name="donate", description="Donate to St-Jude")
@app_commands.default_permissions(admin_mods_perms)
async def donate(interaction: Interaction):
    await interaction.response.defer()

    campain: FullCampaign = await generate_tiltify_campain()
    embed = campain.generate_embed(embed_url)
    mess = await interaction.edit_original_response(content="<https://www.stjude.org/relay>", embed=embed)
    if isinstance(mess, InteractionMessage):
        await mess.add_reaction(CustomEmotes.StJude.value)


@client.event
async def on_ready():
    await tree.sync()
    await client.change_presence(activity=Activity(type=ActivityType.watching, name="for feedback"))


token = os.getenv("token")
if token is not None:
    client.run(token)
