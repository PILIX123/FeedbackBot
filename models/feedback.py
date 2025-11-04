import json
from datetime import datetime
from typing import Any, Union

from discord import Member, Message, User
from discord.channel import (DMChannel, GroupChannel, PartialMessageable,
                             StageChannel, TextChannel, VoiceChannel)
from discord.threads import Thread


class Feedback:
    author: User | Member
    author_name: str
    content: str
    date: datetime
    url: str
    channel: Union[TextChannel, VoiceChannel, StageChannel,
                   Thread, DMChannel, PartialMessageable, GroupChannel]
    blank: str = ""
    discord: str = "Discord"
    author_id: int

    def __init__(self, message: Message):
        self.author = message.author
        self.author_name = message.author.display_name
        self.content = message.content
        self.date = message.created_at
        self.url = message.jump_url
        self.channel = message.channel
        self.author_id = message.author.id


class ConnectionCheck:
    author: User | Member
    of_the_show: str
    previous_connection: str
    next_connection: str
    status: str

    def __init__(self, previous_connection: str, status: str, next_connection: str, of_the_show: str | None, author: User | Member):
        self.author = author
        self.next_connection = next_connection
        self.previous_connection = previous_connection
        self.status = status
        if of_the_show is not None:
            self.of_the_show = of_the_show

    def __str__(self) -> str:
        return f"Connection Check: {self.status} {self.previous_connection}\n\nNew Connection: {self.next_connection}"


class StJudeVariables:
    vanity = "+relay-for-st-jude"
    slug: str

    def __init__(self, slug: str):
        self.slug = slug


class StJudeCall:
    operationName: str = "get_team_event_by_vanity_and_slug"
    variables: StJudeVariables
    query: str = "query get_team_event_by_vanity_and_slug($vanity: String!, $slug: String!) {teamEvent(vanity: $vanity, slug: $slug) {totalAmountRaised {currency value} goal {currency value}}}"
    embed_image_url: str

    def __init__(self, slug: str):
        self.variables = StJudeVariables(slug)

    def toDict(self):
        return {'operationName': self.operationName, 'variables': {
            'vanity': self.variables.vanity, 'slug': self.variables.slug}, 'query': self.query}


class FeedbackForm:
    utf8: str = "✓"
    _method: str = "put"
    name: str
    pronouns: str | None
    email: str | None
    text: str
    anonymous: str
    archived: str | bool = False
    x: int
    gibberish: str
    spinner: str
    commit: str = "Submit"

    def update(self, connection: ConnectionCheck) -> None:
        self.name = connection.author.name
        self.text = str(connection)
        self.anonymous = "0"

    def to_dict(self) -> dict:
        payload: dict = dict()
        payload.update({"utf8": self.utf8})
        payload.update({"_method": self._method})
        broadcastStr: str = f"broadcast[feedbacks_attributes][{self.x}]"
        payload.update({f"{broadcastStr}[name]": self.name})
        payload.update({f"{broadcastStr}[pronouns]": self.pronouns})
        payload.update({f"{broadcastStr}[email]": self.email})
        payload.update({f"{broadcastStr}[text]": self.text})
        payload.update({f"{broadcastStr}[anonymous]": self.anonymous})
        payload.update({f"{broadcastStr}[archived]": self.archived})
        payload.update({f"{self.gibberish}": ""})
        payload.update({"spinner": self.spinner})
        payload.update({"commit": self.commit})
        return payload
