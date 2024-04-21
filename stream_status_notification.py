import os
from dotenv import load_dotenv
import asyncio

from periodic import Periodic
import aiohttp
from discord import Webhook
from twitchAPI.twitch import Twitch


async def check_live():
    twitch = await Twitch(os.getenv('TWITCHCLIENTID'), os.getenv('TWITCHCLIENTSECRET'))
    results = twitch.get_streams(user_id='TWITCHUSERID')
    streams = [stream async for stream in results]

    check_live.is_live = True if len(streams) == 1 else False

    if not hasattr(check_live, 'previous_is_live'):
        check_live.previous_is_live = check_live.is_live
        return

    if check_live.previous_is_live != check_live.is_live:
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url('WEBHOOKURL', session=session)
            if check_live.is_live:
                print('Stream has gone live.')

                webhook.send('Stream has gone live.')
            else:
                print('Stream has gone offline.')

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
