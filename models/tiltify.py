from dataclasses import dataclass
from datetime import date, datetime


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
