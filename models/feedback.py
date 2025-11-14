from enum import Enum
from http.cookies import SimpleCookie

import aiohttp
from bs4 import BeautifulSoup
from bs4.element import Tag
from discord import Member, User

from utils.utils import CustomEmotes


class PerShowValues(Enum):
    Backstage = "Backstage"
    Spotlight = "Spotlight"
    AskUpgrade = "Ask Upgrade"
    SnellTalk = "Snell Talk"
    # TODO: Make sure this one has a way to be differenciated by show
    FollowUp = "Follow Up"


class DiscordFeedback:
    author: User | Member
    anon: bool

    def __init__(self, author: User | Member, anonymous: bool = False) -> None:
        self.author = author
        self.anon = anonymous


class Question(DiscordFeedback):
    question: str

    def __init__(self, question: str, author: User | Member, anonymous: bool = False) -> None:
        super().__init__(author, anonymous)
        self.question = question

    def __str__(self) -> str:
        return self.question


class PerShow:
    per_show_value: PerShowValues
    emote: CustomEmotes


class BackstageQuestion(Question, PerShow):
    def __init__(self, question: str, author: User | Member, anonymous: bool = False) -> None:
        super().__init__(question, author, anonymous)
        self.per_show_value = PerShowValues.Backstage
        self.emote = CustomEmotes.Backstage

    def __str__(self) -> str:
        return f"{self.emote.value} {super().__str__()}"


class SpotlightQuestion(Question, PerShow):
    def __init__(self, question: str, author: User | Member, anonymous: bool = False) -> None:
        super().__init__(question, author, anonymous)
        self.per_show_value = PerShowValues.Spotlight
        self.emote = CustomEmotes.Spotlight

    def __str__(self) -> str:
        return f"{self.emote.value} {super().__str__()}"


class SnellTalk(Question, PerShow):
    def __init__(self, question: str, author: User | Member, anonymous: bool = False) -> None:
        super().__init__(question, author, anonymous)
        self.per_show_value = PerShowValues.SnellTalk
        self.emote = CustomEmotes.Snell

    def __str__(self) -> str:
        return f"{self.emote.value} {super().__str__()}"


class AskUpgrade(Question, PerShow):
    def __init__(self, question: str, author: User | Member, anonymous: bool = False) -> None:
        super().__init__(question, author, anonymous)
        self.per_show_value = PerShowValues.AskUpgrade
        self.emote = CustomEmotes.Upgrade

    def __str__(self) -> str:
        return f"{self.emote.value} {super().__str__()}"


class ConnectionCheck(DiscordFeedback):
    of_the_show: str
    previous_connection: str
    next_connection: str
    status: str

    def __init__(self, previous_connection: str, status: str, next_connection: str, of_the_show: str | None, author: User | Member, anon=True):
        super().__init__(author, anon)
        self.next_connection = next_connection
        self.previous_connection = previous_connection
        self.status = status
        if of_the_show is not None:
            self.of_the_show = of_the_show

    def __str__(self) -> str:
        return f"{CustomEmotes.Conduit.value} Connection Check: {self.status} {self.previous_connection}\n\nNew Connection: {self.next_connection}"


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
    per_show_tag: str | None = None

    def update(self, feedback: DiscordFeedback) -> None:
        self.name = feedback.author.name
        self.text = str(feedback)
        self.anonymous = "1" if feedback.anon else "0"
        if isinstance(feedback, PerShow):
            self.per_show_tag = feedback.per_show_value.value

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
        if self.per_show_tag is not None:
            payload.update(
                {f"{broadcastStr}[per_show_tag]": self.per_show_tag})
        payload.update({f"{self.gibberish}": ""})
        payload.update({"spinner": self.spinner})
        payload.update({"commit": self.commit})
        return payload


class WebForm:
    _info: BeautifulSoup
    _cookies: SimpleCookie
    _form: FeedbackForm
    _url: str
    _discordFeedback: DiscordFeedback
    _cookieVal: dict[str, str] = {"_neon_cms_session": ''}

    def __init__(self, url: str, discordFeedback: DiscordFeedback) -> None:
        self._url = url
        self._discordFeedback = discordFeedback

    async def submit_form(self, url: str) -> bool:
        await self._update_bs_cookies()
        self._generate_feedback_form()
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=self._form.to_dict(), headers=self._generate_headers(), cookies=self._cookieVal) as r:
                return r.ok

    async def _update_bs_cookies(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self._url) as r:
                self._cookies = r.cookies
                self._info = BeautifulSoup(await r.text(), features="html.parser")

    def _generate_feedback_form(self):
        self._form = FeedbackForm()
        form = self._info.find('form', id="edit_broadcast")
        if form is not None and isinstance(form, Tag):
            inputs = form.find_all("input")
            for input in inputs:
                if isinstance(input, Tag) and isinstance(input.attrs.get("id"), str) \
                        and str(input.attrs.get("id")).startswith("broadcast_feedbacks_attribute"):
                    (num, field) = str(input.attrs.get("id")).removeprefix(
                        "broadcast_feedbacks_attributes_").split("_")
                    self._form.x = int(num)
                    self._form.__setattr__(field, str(
                        input.attrs.get("value") or ""))
                if isinstance(input, Tag) and isinstance(input.attrs.get("tabindex"), str) \
                        and str(input.attrs.get("tabindex")) == "-1":
                    self._form.gibberish = str(input.attrs.get("id"))
                if isinstance(input, Tag) and isinstance(input.attrs.get("name"), str) \
                        and str(input.attrs.get("name")) == "spinner" and isinstance(input.attrs.get("value"), str):
                    self._form.spinner = str(input.attrs.get("value"))

        self._form.update(self._discordFeedback)

    def _generate_headers(self) -> dict[str, str]:
        tempmorsel = self._cookies.get("_neon_cms_session")
        if tempmorsel is not None:
            self._cookieVal.update({"_neon_cms_session": tempmorsel.value})
        header: dict = {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        "accept-encoding": "gzip, deflate, br, zstd",
                        "accept-language": "en-us,en;q=0.5",
                        "content-type": "application/x-www-form-urlencoded",
                        "host": "www.relay.fm",
                        "te": "trailers",
                        "priority": "u=0, i",
                        "referer": "https://www.relay.fm/conduit/feedback",
                        "origin": "https://www.relay.fm",
                        "sec-fetch-dest": "document",
                        "sec-fetch-mode": "navigate",
                        "sec-fetch-site": "same-origin",
                        "sec-fetch-user": "?1",
                        "Upgrade-Insecure-Requests": "1",
                        "Cookie": f"_neon_cms_session={self._cookieVal}"}

        return header
