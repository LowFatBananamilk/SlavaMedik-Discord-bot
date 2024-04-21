import os
from dotenv import load_dotenv
import logging
import discord

intents = discord.Intents.default()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

load_dotenv()
client.run(os.getenv('DISCORDBOTTOKEN'))
