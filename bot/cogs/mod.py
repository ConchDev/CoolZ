import asyncio
import discord
from discord.ext import commands
import shortuuid as uuid
import aiosqlite
from discord import Webhook, AsyncWebhookAdapter
import aiohttp


class Mod(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def new_modmail(self, user, message):
        db = await aiosqlite.connect("./bot/db/main.db")
        cursor = await db.cursor()

        guild = self.client.get_guild(843610787867525120)

        id = uuid.uuid()

        name = user.name.replace(" ", '-')
        category = discord.utils.get(guild.categories, id=848983634861621288)
        channel = await guild.create_text_channel(f'Modmail-{name}', category=category)

        hook = await channel.create_webhook(name=user.name)

        await cursor.execute(f"INSERT INTO modmail(user_id, channel_id, hook) VALUES ({user.id}, {channel.id}, '{hook.url}')")

        embed = discord.Embed(title="Incoming Modmail", color=discord.Color.random())
        embed.set_author(name=user, icon_url=user.avatar_url)
        embed.add_field(name="Content:", value=message)
        embed.set_footer(text=f"Modmail ID: {id} | Type anything after this message to respond.")

        await db.commit()
        await cursor.close()
        await db.close()

        await channel.send(self.client.get_role(853297538161573928).mention)
        await channel.send(embed=embed)

    async def check_modmail_session(self, user_id):
        db = await aiosqlite.connect("./bot/db/main.db")
        cursor = await db.cursor()

        await cursor.execute(f"SELECT user_id FROM modmail WHERE user_id = {user_id}")
        result = await cursor.fetchone()

        await cursor.close()
        await db.close()

        if result is not None:
            return True
        
        return False

    async def end_modmail_session(self, id):
        db = await aiosqlite.connect("./bot/db/main.db")
        cursor = await db.cursor()

        await cursor.execute(f"DELETE FROM modmail WHERE channel_id = {id}")

        await db.commit()
        await cursor.close()
        await db.close()

        return True

    async def reply_modmail(self, author, message, channel):
        db = await aiosqlite.connect("./bot/db/main.db")
        cursor = await db.cursor()

        await cursor.execute(f"SELECT user_id FROM modmail WHERE channel_id = {channel}")
        result = await cursor.fetchone()

        user = self.client.get_user(int(result[0]))

        await user.send(f"**{author.name}:** {message}")

    async def user_reply_modmail(self, user, message):
        db = await aiosqlite.connect("./bot/db/main.db")
        cursor = await db.cursor()
        
        await cursor.execute(f"SELECT channel_id FROM modmail WHERE user_id = {user.id}")
        result = await cursor.fetchone()

        await cursor.execute(f"SELECT hook FROM modmail WHERE user_id = {user.id}")
        hook = await cursor.fetchone()

        channel = self.client.get_channel(int(result[0]))

        embed = discord.Embed(title="Incoming Modmail", color=discord.Color.random())
        embed.set_author(name=user, icon_url=user.avatar_url)
        embed.add_field(name="Content:", value=message)
        embed.set_footer(text=f"Type anything after this message to respond.")

        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(hook[0], adapter=AsyncWebhookAdapter(session))
            await webhook.send(message, avatar_url=user.avatar_url)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        check = await self.check_modmail_session(message.author.id)
        if check is True:
            if message.channel.type is not discord.ChannelType.private:
                return
            return await self.user_reply_modmail(message.author, message.content)

        if message.channel.type is not discord.ChannelType.private:
            try:
                if message.channel.name.startswith("modmail"):
                    return await self.reply_modmail(message.author, message.content, message.channel.id)
                else:
                    return
            except Exception as e:
                print(e)
                return

        await self.client.process_commands(message)

        embed = discord.Embed(title="It seems you have slid into my DMs.", color=discord.Color.gold(), description="This is the modmail for The Cool Zone. If you would like to "
        "continue, please react with ✅. Else, react with ❌.")
        embed.set_footer(text="After reacting with ✅, your first message will be sent to the moderators of The Cool Zone.")
        msg = await message.author.send(embed=embed)
        
        await msg.add_reaction('✅')
        await msg.add_reaction('❌')
        
        def check(reaction, user):
            return str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌' and user == message.author

        conf = await self.client.wait_for('reaction_add', check=check, timeout=30)
        if str(conf[0].emoji) == '❌':
            embed=discord.Embed(title="Cancelling your modmail request...")
            await self.end_modmail_session(message.author.id)
            return await message.channel.send(embed=embed)
        elif str(conf[0].emoji) == '✅':
            pass
        else:
            await message.channel.send(conf)
            return await message.channel.send("Something has went terribly wrong.")

        await message.channel.send(embed=discord.Embed(title="Thank you for your query! Our moderators will get back to you shortly."))

        await self.new_modmail(message.author, message.content)    

    @commands.group(invoke_without_command=True)
    async def modmail(self, ctx):
        pass

    @commands.command()
    async def end(self, ctx):
        try:
            if not ctx.channel.name.startswith('modmail'):
                return await ctx.send("Only ticket handlers can close modmail tickets.")
        except:
            return await ctx.send("Only ticket handlers can close modmail tickets.")
            
        await self.end_modmail_session(ctx.channel.id) 

        await ctx.send("Successfully closed the modmail session. The channel will be deleted in ten seconds.")
        await asyncio.sleep(10)

        await ctx.channel.delete()


    
def setup(client):
    client.add_cog(Mod(client))
