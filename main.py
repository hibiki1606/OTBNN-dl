import asyncio
import argparse
import logging
import sys
from urllib import parse

import httpx
from clients.client_base import ClientBase

# Supported sites
from clients.sites.otbnn import BnnClient
from clients.sites.eron import EronClient

client_list = [BnnClient, EronClient]


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
    clients = {}
    for client in client_list:
        c: ClientBase = client(output_dir=output_dir, http_client=http)
        clients[c.get_base_url()] = c  # "example.com": *client*

    hostname = parse.urlparse(otbnn_url).hostname
    if hostname not in clients:
        logging.error("No client matched!")
        return

    await clients[hostname].download(otbnn_url)

    # Quit
    logging.info("Operation finished!")


if __name__ == "__main__":
    asyncio.run(main())
