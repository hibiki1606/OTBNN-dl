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
class OtbnnKind:
    base_url: Optional[str]
    deep: Optional[bool]
    uuid_kind: Optional[BnnUrlKind]
    uuid: Optional[str]


def parse_otbnn_url(url: str) -> Optional[OtbnnKind]:
    parsed_url = parse.urlparse(url)
    path = parsed_url.path
    base_url = parsed_url.hostname
    uuid_patterns = [
        r"^/?(deep/|general/)?user/([\w-]+)(/cast)?$",
        r"^/?(deep/|general/)?cast/([\w-]+)$",
    ]
    kinds = [BnnUrlKind.USER, BnnUrlKind.CAST]

    for pattern, kind in zip(uuid_patterns, kinds):
        uuid: re.Match = re.match(pattern, path)
        if uuid:
            return OtbnnKind(base_url, (uuid.group(1) == "deep/"), kind, uuid.group(2))


def sanitise_filename(filename: str) -> str:
    """
    Remove invalid characters for windows-like systems in filenames. Such as backslash and asterisk etc
    """

    return re.sub(r'[\\/:*?"<>|]+', "", filename)


def save_mp3_media(
    output_path: Path,
    mp3_bytes: bytes,
    mp3_artist_name: str = None,
    mp3_title: str = None,
    mp3_website: str = None,
) -> None:
    output_path.parent.mkdir(exist_ok=True)

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
