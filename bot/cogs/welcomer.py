import discord
from discord.ext import commands
import PIL.Image
from PIL import ImageDraw, ImageFont
from io import BytesIO
import requests


class Welcomer(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        general = self.client.get_channel(843611895260774410)

        imge = PIL.Image.open("bot/src/WELCOME.png")

        response = requests.get(str(member.avatar_url))

        img = PIL.Image.open(BytesIO(response.content))

        img = img.resize((418, 396))

        imge.paste(img, (111, 0))

        imge.save("Welcome.png")
        await general.send(f"**{member.mention} Welcome! Make sure to read {self.client.get_channel(845711784610627615).mention}**", file=discord.File('Welcome.png'))

    @commands.Cog.listener()
    async def on_member_leave(self, member):
        pass

def setup(client):
    client.add_cog(Welcomer(client))
