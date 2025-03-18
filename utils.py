from dataclasses import dataclass
from enum import Enum
import logging
import mutagen
from pathlib import Path
import re
from typing import Optional
from urllib import parse


class BnnUrlKind(Enum):
    USER = 1
    CAST = 2


@dataclass
class Otbnn:
    base_url: Optional[str]
    uuid_kind: Optional[BnnUrlKind]
    uuid: Optional[str]


def parse_otbnn_url(url: str) -> Optional[Otbnn]:
    parsed_url = parse.urlparse(url)
    path = parsed_url.path
    base_url = parsed_url.hostname
    uuid_patterns = [
        r"^/?(?:deep/|general/)?user/([\w-]+)(/cast)?$",
        r"^/?(?:deep/|general/)?cast/([\w-]+)$",
    ]
    kinds = [BnnUrlKind.USER, BnnUrlKind.CAST]

    for pattern, kind in zip(uuid_patterns, kinds):
        uuid: re.Match = re.match(pattern, path)
        if uuid:
            return Otbnn(base_url, kind, uuid.group(1))


def sanitise_filename(filename: str) -> str:
    """
    Remove invalid characters for windows-like systems in filenames. Such as backslash and asterisk etc
    """

    return re.sub(r'[\\/:*?"<>|]+', "", filename)


def save_mp3_media(
    output_dir_path: str,
    output_filename: str,
    mp3_bytes: bytes,
    mp3_artist_name: str = None,
    mp3_title: str = None,
    mp3_website: str = None,
) -> None:
    """
    Save mp3 from bytes and tags.

    Args:
        output_dir_path (str): The path of a directory where mp3 files will be saved.
            If the directory does not exist, it will be created automatically.
        output_filename (str): The filename of mp3
    """
    output_dir = Path(output_dir_path)
    output_dir.mkdir(exist_ok=True)

    file_path = output_dir / (output_filename + ".mp3")
    file_path.write_bytes(mp3_bytes)

    meta = mutagen.File(file_path, easy=True)
    meta["artist"] = mp3_artist_name
    meta["title"] = mp3_title
    meta["website"] = mp3_website

    meta.save()

    logging.info(f"mp3 saved, to: {file_path} !")
    return
