from pathlib import Path
from typing import Union, Optional

import logging
import httpx


class ClientBase:
    def __init__(self, base_url: str, output_dir: Union[str, Path], http_client = httpx.AsyncClient()):
        self.http = http_client
        self.output_dir = Path(output_dir)
        self.base_url = base_url

    def get_base_url(self) -> str:
        return self.base_url

    async def download(self, url: str) -> bool:
        raise NotImplementedError()

    async def get_http(self, api_url: str) -> Optional[httpx.Response]:
        try:
            response = await self.http.get(api_url, follow_redirects=True)
            response.raise_for_status()

            return response
        except httpx.HTTPStatusError as e:
            logging.error(f"An error occurred during an HTTP request! Here is the information:\n{e}")
            return None