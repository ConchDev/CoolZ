import asyncio
import os
from itertools import cycle
import discord
from discord.ext import commands, tasks

class Client(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        allowed_mentions = discord.AllowedMentions(roles=False, everyone=False, users=True)
        super().__init__(command_prefix='>', intents=intents, allowed_mentions=allowed_mentions, case_insensitive=True)
    

    def load_cogs(self):
        self.remove_command('help')
        print("Loading All cogs...")
        print("------")
        for filename in os.listdir(f"./bot/cogs"):
            if filename.endswith(f".py"):
                self.load_extension(f"bot.cogs.{filename[:-3]}")
                print(f"Loaded `{filename[:20]}` Cog")
        print("------")
        self.load_extension('jishaku')
        print("Loaded `jishaku`")
        print("------")
            
    async def on_ready(self):
        print("------")
        print("CoolBot is online.")
    
    async def shutdown(self):
        print("------")
        print("Coolbot Closing connection to Discord...")
        print("------")

    async def close(self):
        print("------")
        print("Coolbot Closing on keyboard interrupt...\n")
        print("------")

    async def on_connect(self):
        print("------")
        print(f"Coolbot Connected to Discord (latency: {self.latency*1000:,.0f} ms).")

    async def on_resumed(self):
        print("------")
        print("Coolbot resumed.")

    async def on_disconnect(self):
        print("------")
        print("Coolbot disconnected.")

    def run(self):
        self.load_cogs()
        print("Running bot...")
        
        super().run("ODQzNjMyMDgxNTM1MTA3MDgz.YKGrmg.xLvbHEm4jY-hA6L2I0TH4x30Kqw", reconnect=True)
