import aiohttp
import asyncio
from discord.ext import commands
import logging

##
# CREDIT TO: nekokatt/espy
##

class HttpCogBase(commands.Cog):
    def __init__(self, loop):
        self.loop = loop

    def __init_subclass__(cls, **kwargs):
        # 100 is aiohttps' default
        cls._pool_size = kwargs.get("pool_size", 100)

    def acquire_session(self):
        # will error if you run outside event loop:
        asyncio.get_running_loop()
        if not hasattr(self, "_session"):
            self._session = aiohttp.ClientSession(
                connector = aiohttp.TCPConnector(
                    limit = self._pool_size,
                )
            )
        return self._session

    async def _release_session(self):
        try:
            session = self._session
            del self._session
            await session.close()
        except AttributeError:
            pass

    def cog_unload(self):
        try:
            if asyncio.get_running_loop() is self.loop:
                self.loop.create_task(self._release_session())
            elif self.loop.is_running():
                self.loop.run_coroutine_threadsafe(self._release_session())
        except RuntimeError:
            logging.exception("Failed to shut down client session, did you unload the cog after the bot shut down?")