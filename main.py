import asyncio
import argparse
import logging
import sys
import utils

from otbnn_client import BnnClient, BnnPost

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
    otbnn_kind = utils.parse_otbnn_url(otbnn_url)
    if not otbnn_kind:
        logging.error("Incorrect URL!")
        return
    bnn_client = BnnClient(otbnn_kind.base_url, output_dir)
    posts: list[BnnPost] = []

    # Fetch Post(s)
    match otbnn_kind.uuid_kind:
        case utils.BnnUrlKind.USER:
            posts = await bnn_client.get_posts_from_user(otbnn_kind.uuid, otbnn_kind.deep)
            logging.info(f"We are going to download all {"R18" if otbnn_kind.deep else "Non-R18"} posts by {posts[0].user_name}...")

        case utils.BnnUrlKind.CAST:
            posts.append(await bnn_client.get_post(otbnn_kind.uuid))
            logging.info(f"We are going to download the post {posts[0].title} by {posts[0].user_name}...")

        case _:
            logging.error(f'"{otbnn_url}" is not a valid URL for this program!')
            return

    # Download Post(s)
    save_tasks = []

    for post in posts:
        save_tasks.append(bnn_client.save_post(post))

    await asyncio.gather(*save_tasks)

    # Quit
    logging.info("Download Complete!")


if __name__ == "__main__":
    asyncio.run(main())
