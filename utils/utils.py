
from enum import Enum


class CustomEmotes(Enum):
    Conduit = ":Conduit:865262930610094100"
    SixHeart = ":sixheart:744708453951602710"
    Spotlight = ":Spotlight:1009268522414772284"
    Backstage = ":Backstage:13342787605847122"
    Snell = ":snell:823597034485317682"
    Upgrade = ":Upgrade:124250265317147035"
    StJude = ":stjude:739880520703541268"
    ThumbsUp = "👍"
    Error = "🚫"


def progressBar(raised: float, goal: float):
    progress_full: str = "🟩"
    progress_empty: str = "⬜"
    bar_length: int = 15
    progress_percent: float = raised/goal

    green_squares: int = int(bar_length*progress_percent)
    progress: str = progress_full*green_squares
    if progress_percent >= 1:
        if int(raised) >= 1000000:
            return "🎊🎉🟥🟧🟨🟩🟦🟪🥇🟪🟦🟩🟨🟧🟥🎉🎊"
        else:
            return "🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨🟨"
    else:
        return f"{progress}{progress_empty*(bar_length-green_squares)}"
