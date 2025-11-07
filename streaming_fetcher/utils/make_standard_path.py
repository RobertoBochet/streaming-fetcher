from pathlib import Path
from typing import Callable


def make_standard_path(
    name: str,
    /,
    omit_season_folder: bool = False,
    year: str | int = None,
    suffix: str = "",
    episode_padding: int = 2,
    extension: str = "mp4",
    base_path: Path = None,
) -> Callable[[int, int | tuple[int, ...]], Path]:
    def get_path(s: int, e: int | tuple[int, ...]) -> Path:
        path = Path(name if year is None else f"{name} ({year})")

        if not omit_season_folder:
            path /= f"Season {s:02d}"

        episode_numbers = (e,) if type(e) is int else e
        episode_number_string = "-".join(map(lambda a: f"E{a:0{episode_padding}d}", episode_numbers))

        path /= f"{name} S{s:02d}{episode_number_string}{suffix}.{extension}"

        if base_path is not None:
            path = base_path / path

        return path

    return get_path
