from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import httpx
import logging
import sys

import utils


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


class BnnClient:
    def __init__(self, base_url: str, output_dir: str):
        self.base_url = base_url
        self.base_api_url = f"https://api.v2.{base_url}/api"
        self.output_dir = Path(output_dir)
        self.http = httpx.AsyncClient()

    async def get_http(self, api_url: str) -> httpx.Response:
        try:
            response = await self.http.get(api_url)
            response.raise_for_status()

            return response
        except httpx.HTTPStatusError as e:
            logging.error(f"An error occurred! Here is the information:\n{e}\n\nTry another User ID or Post ID!")
            sys.exit(1)

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

    async def get_post(self, post_uuid: str) -> BnnPost | None:
        try:
            response = await self.get_http(f"{self.base_api_url}/casts/{post_uuid}")
            data = response.json()

            return self.parse_post_from_json(data)
        except httpx.HTTPStatusError as e:
            logging.error(e)
            return None

    async def get_posts_from_user(self, user_uuid: str, deep: bool) -> list[BnnPost]:
        page_url = f"{self.base_api_url}/users/{user_uuid}/casts?is_adult={str(deep).lower()}"
        posts: list[BnnPost] = []

        post_count: int = 1

        while page_url:
            response = await self.get_http(page_url)
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

    async def save_post(self, post: BnnPost):
        logging.info(f"Downloading: {post.original_url} ( {post.media_url} ) ...")

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
