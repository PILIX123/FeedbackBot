import json
import os
import re
from types import SimpleNamespace
from typing import Any

import aiohttp
import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString, PageElement, Tag
from discord import (Activity, ActivityType, Client, Embed, Intents,
                     Interaction, InteractionMessage, Permissions,
                     app_commands)
from discord.app_commands import (AppCommandError, CommandInvokeError,
                                  CommandTree)
from dotenv import load_dotenv
from requests import Response

from models.feedback import ConnectionCheck, Feedback, FeedbackForm, StJudeCall
from models.tiltify import FullCampaign
from utils.utils import progressBar

load_dotenv()
intents: Intents = Intents.default()
intents.message_content = True

client: Client = Client(intents=intents)
tree: CommandTree[Client] = app_commands.CommandTree(client)

test: str = ":brook:1237150453691711590"
thumbs_up: str = '👍'
error_emote: str = "🚫"
st_jude_emote: str = "stjude:739880520703541268"
admin_mods_perms = Permissions()
admin_mods_perms.administrator = True
admin_mods_perms.moderate_members = True
st_jude_slug: str = 'relay-for-st-jude-2025'
embed_url: str = "https://s3.amazonaws.com/relayfm/assets/Square-Campaign-URL-2025.png"
client_id: str | None = os.getenv("tildify_client_id")
client_secret: str | None = os.getenv("tildify_client_secret")
fundraising_id: str | None = os.getenv("fundraising_id")

client.on_error


@tree.command(name="connection_check", description="Log a connection check for the conduit podcast")
async def connection_check(interaction: Interaction, previous_connection: str, status: str, next_connection: str, of_the_show_name: str | None):
    await interaction.response.defer()
    info: BeautifulSoup
    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.relay.fm/conduit/feedback") as r:
            info = BeautifulSoup(await r.text(), features="html.parser")

    feedbackFrom = FeedbackForm()
    form = info.find('form', id="edit_broadcast")
    if form is not None and isinstance(form, Tag):
        inputs = form.find_all("input")
        for input in inputs:
            if isinstance(input, Tag) and isinstance(input.attrs.get("id"), str) and str(input.attrs.get("id")).startswith("broadcast_feedbacks_attribute"):
                (num, field) = str(input.attrs.get("id")).removeprefix(
                    "broadcast_feedbacks_attributes_").split("_")
                feedbackFrom.x = int(num)
                feedbackFrom.__setattr__(field, str(
                    input.attrs.get("value") or ""))
            if isinstance(input, Tag) and isinstance(input.attrs.get("tabindex"), str) and str(input.attrs.get("tabindex")) == "-1":
                feedbackFrom.gibberish = str(input.attrs.get("id"))
            if isinstance(input, Tag) and isinstance(input.attrs.get("name"), str) and str(input.attrs.get("name")) == "spinner" and isinstance(input.attrs.get("value"), str):
                feedbackFrom.spinner = str(input.attrs.get("value"))

    header: dict = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Content-Type": "application/x-www-form-urlencoded"}
    connection: ConnectionCheck = ConnectionCheck(
        previous_connection, status, next_connection, of_the_show_name, interaction.user)
    feedbackFrom.update(connection)
    testFeedback = feedbackFrom.to_dict()
    sentRequest = requests.post("https://www.relay.fm/shows/conduit/update?id=conduit",
                                data=testFeedback, headers=header)
    response = await interaction.edit_original_response(content=f":conduit: {str(connection)}")
    if not sentRequest.ok:
        raise RuntimeError("Couldnt be sent to feedback form")
    if isinstance(response, InteractionMessage):
        await response.add_reaction(thumbs_up)
        await response.add_reaction(test)


@tree.command(name="ask_backstage", description="Ask a question for the beards")
async def backstage(interaction: Interaction, question: str):
    response = await interaction.response.send_message(question)
    if isinstance(response.resource, InteractionMessage):
        await response.resource.add_reaction(thumbs_up)
        await response.resource.add_reaction(test)
    # TODO Add to form


@tree.error
async def on_error(interaction: Interaction, error: AppCommandError, /):
    if isinstance(error, CommandInvokeError):
        # TODO Add logger
        error.command.qualified_name
        error.original
    if interaction.response.is_done():
        mess = await interaction.original_response()
        await mess.add_reaction(error_emote)
    else:
        if interaction.command is not None:
            await interaction.response.send_message(f"There was an error executing the {interaction.command.qualified_name} command")
        else:
            await interaction.response.send_message("There was an error with the interaction")


@tree.command(name="ask_upgrade", description="Submit a question for Jason and Myke to maybe answer on the podcast")
async def ask_upgrade(interaction: Interaction, question: str, anonymous: bool = False):
    raise Exception("hi")
    await interaction.response.send_message(content=f"Question", ephemeral=anonymous)


@tree.command(name="set_embed_image", description="Sets this years image for the st-jude campain embed")
@app_commands.default_permissions(admin_mods_perms)
async def set_embed_url(interaction: Interaction, image_url: str):
    global embed_url
    embed_url = image_url
    await interaction.response.send_message(f"This year's St. Jude embed image has been set to {image_url}")


@tree.command(name="set_st_jude_slug", description="Sets the st-jude event slug")
# @app_commands.default_permissions(admin_mods_perms)
async def set_slug(interaction: Interaction, slug: str):
    global st_jude_slug
    st_jude_slug = slug
    await interaction.response.send_message(f"This year's st-jude event slug has been set to {slug}")


@tree.command(name="donate", description="Donate to St-Jude")
# @app_commands.default_permissions(admin_mods_perms)
async def donate(interaction: Interaction):
    await interaction.response.defer()
    headers = {"Content-Type": "application/json",
               }
    call = StJudeCall(st_jude_slug)

    info: dict
    campain: FullCampaign
    async with aiohttp.ClientSession() as session:
        data: dict = {"client_id": f"{client_id}", "client_secret": f"{client_secret}",
                      "grant_type": "client_credentials", "scope": "public"}
        async with session.post(f"https://v5api.tiltify.com/oauth/token", json=data, headers=headers) as r:
            info = await r.json()
            headers.update(
                {"Authorization": f"Bearer {info.get("access_token")}"})
        async with session.get(f"https://v5api.tiltify.com/api/public/fundraising_events/{fundraising_id}",
                               headers=headers) as r:
            data = await r.json()
            if data.get("data") is not None:
                actual_data: dict[Any, Any] = data.get("data")  # type:ignore
                campain = FullCampaign(**actual_data)
            else:
                raise Exception("Campain info wasnt querried properly")

    raised: float = float(campain.total_amount_raised.value)
    goal: float = float(campain.goal.value)
    embed = Embed(
        title="Donate to St. Jude!",
        url="https://www.stjude.org/relay",
        description="St. Jude Children's Research Hospital treats the toughest childhood cancers and deserves your money! https://www.stjude.org/relay",
        color=0xffcc33
    )
    embed.set_thumbnail(
        url=embed_url)
    embed.add_field(name="Currently Raised:",
                    value=f"${raised:,.2f}", inline=False)
    embed.add_field(name="Fundraising Target:",
                    value=f"${goal:,.2f}", inline=False)
    embed.add_field(name="Progress:",
                    value=f"{round(raised/goal*100, 2)}%", inline=False)
    embed.set_footer(text=progressBar(raised, goal))
    mess = await interaction.edit_original_response(content="<https://www.stjude.org/relay>", embed=embed)
    if isinstance(mess, InteractionMessage):
        await mess.add_reaction(test)


@client.event
async def on_ready():
    await tree.sync()
    await client.change_presence(activity=Activity(type=ActivityType.watching, name="for feedback"))


token = os.getenv("token")
if token is not None:
    client.run(token)
