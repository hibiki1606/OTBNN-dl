import logging
import mutagen
from pathlib import Path
import re
import emoji


def sanitise_filename(filename: str) -> str:
    """
    Remove invalid characters / emotes in filenames
    """
    
    return emoji.replace_emoji(re.sub(r'[\\/:*?"<>|]+', "", filename))


def save_mp3_media(
    output_path: Path,
    mp3_bytes: bytes,
    mp3_artist_name: str = None,
    mp3_title: str = None,
    mp3_website: str = None,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not output_path.suffix == ".mp3":
        logging.warning("The file will be saved without a valid extension!")

    output_path.write_bytes(mp3_bytes)

    meta = mutagen.File(output_path, easy=True)
    meta["artist"] = mp3_artist_name
    meta["title"] = mp3_title
    meta["website"] = mp3_website

    meta.save()

    logging.info(f"mp3 saved, to: {output_path} !")
    return
