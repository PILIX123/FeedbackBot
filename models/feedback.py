from discord import Message, User, Member
from datetime import datetime
from typing import Any


class Feedback:
    author: User | Member
    author_name: str
    content: str
    date: datetime
    url: str
    channel: Any
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
