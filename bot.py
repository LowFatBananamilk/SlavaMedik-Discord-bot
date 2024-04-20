import os
from dotenv import load_dotenv
import logging
import discord
from discord.ext import tasks
from twitchAPI.twitch import Twitch


intents = discord.Intents.default()
client = discord.Client(intents=intents)

# todo: use CRON like time instead of intervals
@tasks.loop(seconds=10)
async def check_live():
    twitch = await Twitch(os.getenv('TWITCHCLIENTID'), os.getenv('TWITCHCLIENTSECRET'))
    results = twitch.get_streams(user_id='user_id_here')
    streams = [stream async for stream in results]

    check_live.is_live = True if len(streams) == 1 else False
    
    if not hasattr(check_live, 'previous_is_live'):
        check_live.previous_is_live = check_live.is_live
        return

    if check_live.previous_is_live != check_live.is_live:
        if check_live.is_live:
            print('Stream has gone live.')
        else:
            print('Stream has gone offline.')
    else:
        if check_live.is_live:
            print('Stream is live.')
        else:
            print('Stream is offline.')


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    check_live.start()


load_dotenv()
client.run(os.getenv('DISCORDBOTTOKEN'))
