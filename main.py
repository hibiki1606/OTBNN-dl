import asyncio
import argparse
import logging
import sys
import utils

from otbnn_client import BnnClient

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
    format="%(message)s",
)


async def main():
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

    otbnn_url = args.otbnn_url
    output_dir = args.output_dir
    otbnn = utils.parse_otbnn_url(otbnn_url)
    if not otbnn:
        logging.error("Incorrect URL!")
        return
    bnn_client = BnnClient(otbnn.base_url, output_dir)

    match otbnn.uuid_kind:
        case utils.BnnUrlKind.USER:
            posts = await bnn_client.get_posts_from_user(otbnn.uuid, otbnn.deep)
            save_tasks = []

            for post in posts:
                save_tasks.append(bnn_client.save_post(post))

            await asyncio.gather(*save_tasks)

        case utils.BnnUrlKind.CAST:
            post = await bnn_client.get_post(otbnn.uuid)
            await bnn_client.save_post(post)

        case _:
            logging.info(f'"{otbnn_url}" is not a valid URL for this program!')
            return

    logging.info("Download Complete!")


if __name__ == "__main__":
    asyncio.run(main())
