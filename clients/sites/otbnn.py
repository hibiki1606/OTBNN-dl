import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
import re
from typing import Union, Optional
from urllib import parse
import httpx
import logging
import utils

from clients.client_base import ClientBase


class BnnUserNotFoundError(Exception):
    def __init__(self, uuid=""):
        self.uuid = uuid

    def __str__(self):
        return f"The user that has a UUID {self.uuid} wasn't found!"


class BnnPostNotFoundError(Exception):
    def __init__(self, uuid=""):
        self.uuid = uuid

    def __str__(self):
        return f"The post that has a UUID {self.uuid} wasn't found!"


class BnnUrlKind(Enum):
    USER = 1
    CAST = 2


@dataclass
class OtbnnKind:
    base_url: Optional[str]
    deep: Optional[bool]
    uuid_kind: Optional[BnnUrlKind]
    uuid: Optional[str]


@dataclass
class BnnPost:
    title: str
    user_id: str
    user_name: str
    media_url: str
    original_id: str
    created_at: datetime
    original_url: str

    def __eq__(self, other):
        self.media_url == other.media_url


class BnnClient(ClientBase):
    def __init__(self, output_dir: Union[str, Path], http_client=httpx.AsyncClient()):
        super().__init__(base_url="otobanana.com", output_dir=output_dir, http_client=http_client)
        self.base_api_url = f"https://api.v2.{self.base_url}/api"

    @staticmethod
    def parse_otbnn_url(url: str) -> Optional[OtbnnKind]:
        parsed_url = parse.urlparse(url)
        path = parsed_url.path
        base_url = parsed_url.hostname
        url_patterns = [
            r"^/?(deep/|general/)?user/([\w-]+)(?:/cast)?$",  # e.g. /{deep/|general/}/user/{user_uuid}/cast
            r"^/?(deep/|general/)?cast/([\w-]+)$",  # e.g. /{deep/|general/}/cast/{post_uuid}
        ]
        kinds = [BnnUrlKind.USER, BnnUrlKind.CAST]

        for pattern, kind in zip(url_patterns, kinds):
            uuid: re.Match = re.match(pattern, path)
            if uuid:
                return OtbnnKind(base_url, (uuid.group(1) == "deep/"), kind, uuid.group(2))

    async def download(self, url: str):
        otbnn_kind = self.parse_otbnn_url(url)
        if not otbnn_kind:
            logging.error("Incorrect URL!")
            return
        posts: list[BnnPost]

        # Fetch Post(s)
        match otbnn_kind.uuid_kind:
            case BnnUrlKind.USER:
                posts = await self.get_posts_from_user(otbnn_kind.uuid, otbnn_kind.deep)
                logging.info(
                    f"We are going to download all {'R18' if otbnn_kind.deep else 'Non-R18'} posts by {posts[0].user_name}..."
                )

            case BnnUrlKind.CAST:
                posts = [await self.get_post(otbnn_kind.uuid)]
                logging.info(f"We are going to download the post {posts[0].title} by {posts[0].user_name}...")

            case _:
                logging.error(f'"{url}" is not a valid URL for this client!')
                return

        # Download Post(s)
        save_tasks = []

        for post in posts:
            save_tasks.append(self.save_post(post))

        await asyncio.gather(*save_tasks)

    async def get_post(self, post_uuid: str) -> Optional[BnnPost]:
        try:
            response = await self.get_http(f"{self.base_api_url}/casts/{post_uuid}")
            if not response:
                raise BnnPostNotFoundError(post_uuid)

            data = response.json()

            return self.parse_post_from_json(data)
        except httpx.HTTPStatusError as e:
            logging.error(e)
            return None

    async def get_posts_from_user(self, user_uuid: str, deep: bool) -> list[BnnPost]:
        page_url = f"{self.base_api_url}/users/{user_uuid}/casts?is_adult={str(deep).lower()}"
        posts: list[BnnPost] = []

        post_count = 1

        while page_url:
            response = await self.get_http(page_url)
            if not response:
                raise BnnUserNotFoundError(user_uuid)

            data = response.json()

            logging.info(f"page: {page_url}")

            for post in data["data"]:
                instance = self.parse_post_from_json(post)

                logging.info(f"{post_count}: {instance.title}")
                post_count += 1

                posts.append(instance)

            page_url = data.get("next_page_url", None)
            continue

        return posts

    async def get_user(self, user_uuid: str):
        response = await self.get_http(f"{self.base_api_url}/users/{user_uuid}")
        data = response.json()

        return data

    def parse_post_from_json(self, raw_post: dict) -> BnnPost:
        return BnnPost(
            title=raw_post["post"]["title"],
            user_id=raw_post["post"]["user"]["username"],
            user_name=raw_post["post"]["user"]["name"],
            media_url=raw_post["audio_url"],
            original_id=raw_post["post"]["id"],
            created_at=datetime.fromisoformat(raw_post["post"]["created_at"]),
            original_url=f"https://{self.base_url}/cast/{raw_post['post']['id']}",
        )

    async def save_post(self, post: BnnPost):
        logging.info(f"Preparing to download: {post.original_url} ( {post.media_url} ) ...")

        filename = f"{post.user_name} - {post.title} [{post.created_at.strftime('%Y-%m-%d_%H%M')}].mp3"
        output_path = self.output_dir / filename

        if output_path.exists():
            logging.info(f"The downloaded file {output_path} already exists, we're skipping this post!")
            return

        result = await self.get_http(post.media_url)

        utils.save_mp3_media(
            output_path=output_path,
            mp3_bytes=result.content,
            mp3_artist_name=post.user_id,
            mp3_title=post.title,
            mp3_website=post.original_url,
        )
