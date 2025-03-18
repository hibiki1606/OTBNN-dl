import asyncio
import argparse
import time

import utils

from otbnn_client import BnnClient

if __name__ == '__main__':
    async def main():
        parser = argparse.ArgumentParser(description = 'OTBNN Downloader')
        parser.add_argument('otbnn_url', help = 'An OTBNN url of an user or a cast.')
        parser.add_argument(
            '-o', '--output_dir', 
            help = 'Path to the folder where downloaded files will be saved. If nothing is specified, the output folder will be created directly under the path where this source file is located.', 
            default = 'dl'
        )

        args = parser.parse_args()
        
        otbnn_url = args.otbnn_url
        output_dir = args.output_dir

        base_url, uuid_kind, uuid = utils.parse_otbnn_url(otbnn_url)

        otbnn_client = BnnClient(base_url)
        
        if (uuid_kind == utils.UrlKind.USER):
            posts = await otbnn_client.get_posts_from_user(uuid)
            
            for post in posts:
                utils.global_logger.info(f'downloading: {post.original_url}({post.media_url}) ...')

                result = await otbnn_client.get_http(post.media_url)

                utils.save_mp3_media(
                    output_dir_path = output_dir,
                    output_filename = f'{post.user_name} - {post.title} [{post.created_at.strftime('%Y-%m-%d_%H%M')}]',
                    mp3_bytes = result.content,
                    mp3_artist_name = post.user_id,
                    mp3_title = post.title,
                    mp3_website = post.original_url
                )

                time.sleep(2)
        elif(uuid_kind == utils.UrlKind.CAST):
            post = await otbnn_client.get_post(uuid)
            utils.global_logger.info(f'downloading: {post.original_url}({post.media_url}) ...')

            result = await otbnn_client.get_http(post.media_url)

            utils.save_mp3_media(
                output_dir_path = output_dir,
                output_filename = f'{post.user_name} - {post.title} [{post.created_at.strftime('%Y-%m-%d_%H%M')}]',
                mp3_bytes = result.content,
                mp3_artist_name = post.user_id,
                mp3_title = post.title,
                mp3_website = post.original_url
            )
        else:
            utils.global_logger.info(f'"{otbnn_url}" is not a valid URL for this program!')
    asyncio.run(main())