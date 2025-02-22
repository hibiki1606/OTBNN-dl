import re

from pathlib import Path
from urllib import parse
from logging import getLogger, INFO, StreamHandler
from typing import Tuple

import mutagen

global_logger = getLogger(__name__)
global_logger.setLevel(INFO)

handler = StreamHandler()

global_logger.addHandler(handler)

def parse_otbnn_url(url: str) -> Tuple[str | None, str | None, str | None]:
    parsed_url = parse.urlparse(url)
    path = parsed_url.path
    base_url = parsed_url.hostname

    user_uuid = re.match(r'^/?(?:deep/|general/)?user/([\w-]+)(/cast)?$', path)
    if user_uuid:
        return (base_url, 'user', user_uuid.group(1))
    
    cast_uuid = re.match(r'^/?(?:deep/|general/)?cast/([\w-]+)$', path)
    if cast_uuid:
        return (base_url, 'post', cast_uuid.group(1))
    
    return None, None, None

def sanitise_filename(filename: str) -> str:
    """
    Remove invalid characters for windows-like systems in filenames. Such as backslash and asterisk etc
    """

    return re.sub(r'[\\/:*?"<>|]+', '', filename)

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
    output_dir.mkdir(exist_ok = True)

    file_path = output_dir / (output_filename + '.mp3')
    file_path.write_bytes(mp3_bytes)

    meta = mutagen.File(file_path, easy = True)
    meta['artist'] = mp3_artist_name
    meta['title'] = mp3_title
    meta['website'] = mp3_website
    
    meta.save()

    global_logger.info(f'mp3 saved, to: {file_path} !')
    return