import logging
import mutagen
from pathlib import Path
import re
import emoji
from typing import Union


def sanitise_filename(filename: str) -> str:
    """
    Remove invalid characters / emotes in filenames
    """

    return emoji.replace_emoji(re.sub(r'[\\/:*?"<>|]+', "", filename))


def save_mp3_media(
    output_path: Union[Path, str],
    mp3_bytes: bytes,
    mp3_artist_name: str = None,
    mp3_title: str = None,
    mp3_website: str = None,
) -> None:
    out_file = Path(output_path).with_suffix(".mp3")
    out_file.parent.mkdir(parents=True, exist_ok=True)

    out_file.write_bytes(mp3_bytes)

    meta = mutagen.File(output_path, easy=True)
    meta["artist"] = mp3_artist_name
    meta["title"] = mp3_title
    meta["website"] = mp3_website

    meta.save()

    logging.info(f"mp3 saved, to: {output_path} !")
    return
