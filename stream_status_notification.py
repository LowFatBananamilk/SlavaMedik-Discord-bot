import os
from dotenv import load_dotenv
import yaml
import random
import asyncio

from periodic import Periodic
import aiohttp
from discord import Webhook, Embed
from twitchAPI.twitch import Twitch

# todo: remove
import json

with open('config.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


async def check_live():
    twitch = await Twitch(os.getenv('TWITCHCLIENTID'), os.getenv('TWITCHCLIENTSECRET'))
    results = twitch.get_streams(user_id=str(config['twitch_user_ID']))
    streams = [stream async for stream in results]

    check_live.is_live = True if len(streams) == 1 else False

    if not hasattr(check_live, 'previous_is_live'):
        check_live.previous_is_live = check_live.is_live
        return

    if check_live.previous_is_live != check_live.is_live:
        if check_live.is_live:
            print('Stream has gone live.')

            async with aiohttp.ClientSession() as session:
                webhooks = [Webhook.from_url(discord_webhook_URL, session=session) for discord_webhook_URL in config['discord_webhook_URLs']]

                get_users_result = twitch.get_users(user_ids=str(config['twitch_user_ID']))
                user = [user async for user in get_users_result][0]

                tag_string = ''
                for tag in streams[0].tags:
                    tag_string += f'`{tag}`, '
                tag_string = tag_string[:-2]

                stream = streams[0].to_dict()
                stream['stream_url'] = f"https://www.twitch.tv/{streams[0].user_id}"
                stream['user_pfp'] = user.profile_image_url
                stream['tags'] = tag_string

                embed = Embed(
                    title=format_config_string(config['embed']['title'], stream),
                    url=format_config_string(config['embed']['url'], stream),
                    description=format_config_string(config['embed']['description'], stream),
                    color=config['embed']['color']
                )
                embed.set_thumbnail(url=format_config_string(
                    config['embed']['thumbnail'], stream))
                embed.set_author(
                    name=format_config_string(config['embed']['author']['name'], stream),
                    url=format_config_string(config['embed']['author']['url'], stream),
                    icon_url=format_config_string(config['embed']['author']['icon_url'], stream)
                )
                embed.set_image(url=format_config_string(
                    config['embed']['image'], stream).format(width=1280, height=720))
                embed.set_footer(
                    text=format_config_string(config['embed']['footer']['text'], stream),
                    icon_url=format_config_string(config['embed']['footer']['icon_url'], stream)
                )

                for webhook in webhooks:
                    await webhook.send(embed=embed)
        else:
            print('Stream has gone offline.')
    else:
        if check_live.is_live:
            print('Stream is live.')
        else:
            print('Stream is offline.')


def format_config_string(string, format):
    if type(string) == list:
        if len(string) == 0 or string[0] == None:
            return None

        return random.choice(string).format(**format)

    if string == None or string == "":
        return None

    return string.format(**format)


async def main():
    load_dotenv()
    # p = Periodic(3, check_live)
    # await p.start()

# todo: remove
    twitch = await Twitch(os.getenv('TWITCHCLIENTID'), os.getenv('TWITCHCLIENTSECRET'))
    get_streams_result = twitch.get_streams(
        user_id=str(config['twitch_user_ID']))
    streams = [stream async for stream in get_streams_result]

    check_live.is_live = True if len(streams) == 1 else False
    if check_live.is_live:
        tag_string = ''
        for tag in streams[0].tags:
            tag_string += f'`{tag}`, '
        tag_string = tag_string[:-2]

        get_users_result = twitch.get_users(
            user_ids=str(config['twitch_user_ID']))
        user = [user async for user in get_users_result][0]

        async with aiohttp.ClientSession() as session:
            webhooks = [Webhook.from_url(discord_webhook_URL, session=session)
                        for discord_webhook_URL in config['discord_webhook_URLs']]
            if check_live.is_live:
                print('Stream has gone live.')

                stream = streams[0].to_dict()
                stream['stream_url'] = f"https://www.twitch.tv/{streams[0].user_id}"
                stream['user_pfp'] = user.profile_image_url
                stream['tags'] = tag_string

                embed = Embed(
                    title=format_config_string(
                        config['embed']['title'], stream),
                    url=format_config_string(config['embed']['url'], stream),
                    description=format_config_string(
                        config['embed']['description'], stream),
                    color=config['embed']['color']
                )
                embed.set_thumbnail(url=format_config_string(
                    config['embed']['thumbnail'], stream))
                embed.set_author(
                    name=format_config_string(
                        config['embed']['author']['name'], stream),
                    url=format_config_string(
                        config['embed']['author']['url'], stream),
                    icon_url=format_config_string(
                        config['embed']['author']['icon_url'], stream)
                )
                embed.set_image(url=format_config_string(
                    config['embed']['image'], stream).format(width=1280, height=720))
                embed.set_footer(
                    text=format_config_string(
                        config['embed']['footer']['text'], stream),
                    icon_url=format_config_string(
                        config['embed']['footer']['icon_url'], stream)
                )

                message = f'embed:\n```json\n{json.dumps(embed.to_dict(), indent=2)}\n```'

                for webhook in webhooks:
                    await webhook.send(message, embed=embed)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
