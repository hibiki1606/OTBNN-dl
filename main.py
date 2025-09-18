import asyncio
import argparse
import logging
import sys
import importlib
from urllib import parse
from pathlib import Path

import httpx
from clients.client_base import ClientBase

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
    format="%(message)s",
)


async def main():
    # Prepare Arguments
    parser = argparse.ArgumentParser(description="OTBNN Downloader")
    parser.add_argument("otbnn_url", help="An OTBNN url of an user or a cast.")
    parser.add_argument(
        "-o",
        "--output_dir",
        help="Path to the folder where downloaded files will be saved. "
        "If nothing is specified, the output folder will be created directly under the path where this source file is located.",
        default="dl",
    )

    args = parser.parse_args()

    # Prepare Variables
    otbnn_url = args.otbnn_url
    output_dir = args.output_dir
    http = httpx.AsyncClient()

    # Load Clients
    client_module_path = Path("./clients")
    clients: dict = {}
    for client_module_file in client_module_path.glob("*_client.py"):
        module_name = str(client_module_file).removesuffix(".py").replace("/", ".")
        try:
            module = importlib.import_module(module_name)
            for name, client in vars(module).items():
                if isinstance(client, type) and issubclass(client, ClientBase) and client is not ClientBase:
                    logging.info(f"Loading {name}...")
                    instance: ClientBase = client(output_dir=output_dir, http_client=http)
                    clients[instance.get_base_url()] = instance  # "example.com": *client*

        except ImportError as error:
            logging.error(f"Failed to import {module_name} due to the error {error} !")

    hostname = parse.urlparse(otbnn_url).hostname
    if hostname not in clients:
        logging.error("No client matched!")
        return

    await clients[hostname].download(otbnn_url)

    # Quit
    logging.info("Operation finished!")


if __name__ == "__main__":
    asyncio.run(main())
