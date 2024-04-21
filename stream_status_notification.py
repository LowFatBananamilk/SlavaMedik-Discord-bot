import os
from dotenv import load_dotenv
import yaml
import asyncio

from periodic import Periodic
import aiohttp
from discord import Webhook
from twitchAPI.twitch import Twitch

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
        async with aiohttp.ClientSession() as session:
            webhooks = [Webhook.from_url(discord_webhook_URL, session=session) for discord_webhook_URL in config['discord_webhook_URLs']]
            if check_live.is_live:
                print('Stream has gone live.')

                for webhook in webhooks:
                    webhook.send('Stream has gone live.')
            else:
                print('Stream has gone offline.')

                for webhook in webhooks:
                    webhook.send('Stream has gone offline.')
    else:
        if check_live.is_live:
            print('Stream is live.')
        else:
            print('Stream is offline.')


async def main():
    load_dotenv()
    p = Periodic(3, check_live)
    await p.start()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
