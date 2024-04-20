import os
from dotenv import load_dotenv
import logging
import discord
from discord.ext import tasks
from twitchAPI.twitch import Twitch


intents = discord.Intents.default()
client = discord.Client(intents=intents)


@tasks.loop(seconds=10)
async def check_live():
    twitch = await Twitch(os.getenv('TWITCHCLIENTID'), os.getenv('TWITCHCLIENTSECRET'))
    results = twitch.get_streams(user_id='user_id_here')
    streams = [stream async for stream in results]
    print('Stream offline' if len(streams) == 0 else 'Stream Online')
    return False if len(streams) == 0 else True


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    check_live.start()


load_dotenv()
client.run(os.getenv('DISCORDBOTTOKEN'))
