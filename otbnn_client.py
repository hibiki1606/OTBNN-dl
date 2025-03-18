import sys
from dataclasses import dataclass
from datetime import datetime

import httpx

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

class BnnClient:
    def __init__(self, BASE_URL: str):
        self.BASE_URL = BASE_URL
        self.BASE_API_URL = f'https://api.v2.{BASE_URL}/api'

        self.http = httpx.AsyncClient()

    async def get_http(self, api_url: str) -> httpx.Response:
        try:
            response = await self.http.get(api_url)
            response.raise_for_status()

            return response
        except httpx.HTTPStatusError as e:
            utils.global_logger.error(f'An error occurred! Here is the information:\n{e}\n\nTry another User ID or Post ID!')
            sys.exit(1)

    def parse_post_from_json(self, raw_post: dict) -> BnnPost:
        return BnnPost(
            title = raw_post['post']['title'],
            user_id = raw_post['post']['user']['username'],
            user_name = raw_post['post']['user']['name'],
            media_url = raw_post['audio_url'],
            original_id = raw_post['post']['id'],
            created_at = datetime.fromisoformat(raw_post['post']['created_at']),
            original_url = f'https://{self.BASE_URL}/cast/{raw_post['post']['id']}'
        )

    async def get_post(self, post_uuid: str) -> BnnPost | None:
        try:
            response = await self.get_http(f'{self.BASE_API_URL}/casts/{post_uuid}')
            data = response.json()

            return self.parse_post_from_json(data)
        except httpx.HTTPStatusError as e:
            utils.global_logger.error(e)
            return None

    async def get_posts_from_user(self, user_uuid: str) -> list[BnnPost]:
        page_url = f'{self.BASE_API_URL}/users/{user_uuid}/casts?is_adult=true'
        posts: list[BnnPost] = []
        
        post_count: int = 1

        while page_url:
            response = await self.get_http(page_url)
            data = response.json()
            
            utils.global_logger.info(f'page: {page_url}')

            for post in data['data']:
                instance = self.parse_post_from_json(post)

                utils.global_logger.info(f'{post_count}: {instance.title}')
                post_count += 1
                
                posts.append(instance)
            
            page_url = data.get('next_page_url', None)
            continue

        return posts

    async def get_user(self, user_uuid: str):
        response = await self.get_http(f'{self.BASE_API_URL}/users/{user_uuid}')
        data = response.json()

        return data