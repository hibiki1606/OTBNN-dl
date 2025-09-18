from enum import Enum
import subprocess
from urllib import parse
from bs4 import BeautifulSoup
import re
from dataclasses import dataclass
from datetime import datetime
import httpx
from typing import Union, Optional
from pathlib import Path
import logging

from .client_base import ClientBase


@dataclass
class EronPost:
    title: str
    post_id: str
    user_id: str
    user_name: str
    created_at: datetime
    original_url: str

    def __eq__(self, other):
        self.original_url == other.original_url


class EronUrlKind(Enum):
    USER = 1
    POST = 2


@dataclass
class EronKind:
    id_kind: Optional[EronUrlKind]
    id: Optional[str]


class EronClient(ClientBase):
    def __init__(self, output_dir: Union[str, Path], http_client=httpx.AsyncClient()):
        super().__init__(base_url="erovoice-ch.com", output_dir=output_dir, http_client=http_client)

    async def download(self, url: str):
        eron_kind = self.parse_eron_url(url)

        match eron_kind.id_kind:
            case EronUrlKind.USER:
                posts = await self.get_posts_by_user(eron_kind.id)
                for post in posts:
                    self.save_post(post)
            case EronUrlKind.POST:
                post = await self.get_post_by_id(eron_kind.id)
                self.save_post(post)
            case _:
                logging.error(f'"{url}" is not a valid URL for this client!')
                return

    @staticmethod
    def parse_eron_url(url: str) -> Optional[EronKind]:
        parsed_url = parse.urlparse(url)
        path = parsed_url.path
        url_patterns = [
            r"^/?(?:ero-voice|ero-asmr|moe-asmr)/(\d+)\.html$",  # e.g. /ero-voice/{post_id}.html
            r"^/?([\w-]+)$",  # e.g. /{user_name}
        ]
        kinds = [EronUrlKind.POST, EronUrlKind.USER]

        for pattern, kind in zip(url_patterns, kinds):
            id: re.Match = re.match(pattern, path)
            if id:
                return EronKind(kind, id.group(1))

    async def get_posts_by_user(self, user_id: str) -> list[EronPost]:
        response = await self.get_http(f"https://{self.base_url}/{user_id}")
        soup = BeautifulSoup(response.text, "html.parser")

        raw_posts = soup.select("ul.voiceList.cf > li")
        author_name = soup.select_one(".authorUser").text[:-2]

        posts: list[EronPost] = []

        for raw_post in raw_posts:
            a_tag = raw_post.find("a")

            post_original_url: str = a_tag.get("href")
            post_kind: EronKind = self.parse_eron_url(post_original_url)
            post_title = a_tag.get("title")
            post_datetime = datetime.strptime(a_tag.select_one("li.postTime").text, "%y/%m/%d")

            instance = EronPost(
                title=post_title,
                post_id=post_kind.id,
                user_id=user_id,
                user_name=author_name,
                created_at=post_datetime,
                original_url=post_original_url,
            )
            posts.append(instance)

        return posts

    async def get_post_by_id(self, post_id: str):
        original_url = f"https://{self.base_url}/moe-asmr/{post_id}.html"
        response = await self.get_http(original_url)
        soup = BeautifulSoup(response.text, "html.parser")
        
        voiceinfo = soup.select_one("#voiceInfos")

        post_title = voiceinfo.find("h1").text
        post_time = voiceinfo.select_one("li.postTime").text
        
        author_url = voiceinfo.select_one(".authorUser").find("a").get("href")
        author_name = voiceinfo.select_one(".authorUser").find("a").text[:-2]
        author_id = parse.urlparse(author_url).path.replace("/", "")

        return EronPost(
            title=post_title,
            post_id=post_id,
            user_id=author_id,
            user_name=author_name,
            created_at=datetime.strptime(post_time, "%Y/%m/%d"),
            original_url=original_url,
        )

    def save_post(self, post: EronPost):
        logging.info(f"We're going to download the post {post.title} ...")

        output_path = Path(f"{self.output_dir}/{post.user_id} - {post.title}.m4a")
        output_path.parent.mkdir(exist_ok=True)

        if output_path.exists():
            logging.info(f"The downloaded file {output_path} already exists, we're skipping this post!")
            return

        arguments = [
            "ffmpeg",
            "-nostdin",
            # On some website, The extension of the downloaded files may have another extension rather than m3u8, Which can cause an error during download.
            # To avoid that kind of errors, -allowed_extensions and -extension_picky are required:
            "-allowed_extensions",
            "ALL",
            "-extension_picky",
            "0",
            "-protocol_whitelist",
            "file,https,tls,tcp,crypto",
            "-i",
            f"https://erovoice-ch.com/wp-content/themes/erovoice-ch/libs/getm3u8file.php?id={post.post_id}",
            "-c:a",
            "copy",  # Copy the audio stream without re-encording
            output_path,
        ]

        try:
            subprocess.run(arguments, check=True)
        except FileNotFoundError:
            logging.error(
                "Ffmpeg is not found in the system! Please install it and add it to the path before you can download this post."
            )
