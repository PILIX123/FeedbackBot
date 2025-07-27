
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
