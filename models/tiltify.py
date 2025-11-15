import os
from dataclasses import dataclass
from datetime import date, datetime

import aiohttp
from discord import Embed

from utils.utils import progressBar


@dataclass
class MoneyHelper:
    currency: str
    value: float


@dataclass
class Avatar:
    alt: str
    height: int
    src: str
    width: int


@dataclass
class FullCampaign:
    avatar: Avatar
    can_publish_supporting_at: datetime
    cause_id: str
    currency_code: str
    description: str
    donate_url: str
    end_supporting_at: datetime
    ends_at: date
    goal: MoneyHelper
    id: str
    inserted_at: datetime
    legacy_id: int
    name: str
    published_at: datetime
    retired_at: datetime | None
    slug: str
    start_supporting_at: datetime
    starts_at: date
    status: str
    total_amount_raised: MoneyHelper
    updated_at: datetime
    url: str
    url: str
    url: str
    url: str
    url: str

    def __post_init__(self):
        self.avatar = Avatar(**self.avatar)
        self.goal = MoneyHelper(**self.goal)
        self.total_amount_raised = MoneyHelper(**self.total_amount_raised)

    def generate_embed(self, embed_url: str) -> Embed:
        raised: float = float(self.total_amount_raised.value)
        goal: float = float(self.goal.value)
        embed = Embed(
            title="Donate to St. Jude!",
            url="https://www.stjude.org/relay",
            description="St. Jude Children's Research Hospital treats the toughest childhood cancers and deserves your money! https://www.stjude.org/relay",
            color=0xFFCC33,
        )
        embed.set_thumbnail(url=embed_url)
        embed.add_field(name="Currently Raised:",
                        value=f"${raised:,.2f}", inline=False)
        embed.add_field(name="Fundraising Target:",
                        value=f"${goal:,.2f}", inline=False)
        embed.add_field(
            name="Progress:", value=f"{round(raised/goal*100, 2)}%", inline=False
        )
        embed.set_footer(text=progressBar(raised, goal))
        return embed


async def generate_tiltify_campain() -> FullCampaign:
    client_id: str | None = os.getenv("tildify_client_id")
    client_secret: str | None = os.getenv("tildify_client_secret")
    fundraising_id: str | None = os.getenv("fundraising_id")
    headers = {"Content-Type": "application/json"}
    campain: FullCampaign
    async with aiohttp.ClientSession() as session:
        data: dict = {
            "client_id": f"{client_id}",
            "client_secret": f"{client_secret}",
            "grant_type": "client_credentials",
            "scope": "public",
        }
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
    return campain
