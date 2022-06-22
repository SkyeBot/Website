import asyncio
import os
from typing import Optional
from quart import Quart
from discord.ext import ipc
import asyncpg

from quart_discord import DiscordOAuth2Session

class App(Quart):
    def __init__(self):
        self.ipc = ipc.Client(host="127.0.0.1", port=2300, secret_key="your_secret_key_here")

        self.db = asyncpg.create_pool(dsn="postgres://skye:GRwe2h2ATA5qrmpa@localhost:5432/skyetest")


        super().__init__(__name__)

        self.config["SECRET_KEY"] = "test123"
        self.config["DISCORD_CLIENT_ID"] = os.environ["DISCORD_CLIENT_ID"]
        self.config["DISCORD_CLIENT_SECRET"] = os.environ["DISCORD_CLIENT_SECRET"]
        self.config["DISCORD_REDIRECT_URI"] = "https://skyebot.dev/callback"

        
        self.discord = DiscordOAuth2Session(self)


    def start(self, *, port: Optional[int]=None, debug: Optional[bool]=None):
        port = port or 5000
        debug = debug or False


        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
        try:
            self.ipc = loop.run_until_complete(self.ipc.start(loop=loop))
            self.run(port=port,loop=loop, debug=debug)
        finally:
            loop.run_until_complete(self.ipc.close()) # Closes the session, doesn't close the loop
            loop.close()
