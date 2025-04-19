import discord
from discord.ext import commands
import datetime
import random
import aiohttp
import sqlite3
import os

#Discord
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
client = commands.Bot(command_prefix='-', help_command=None, intents=intents)

#SQLite
conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), "xp_system.db"))


cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    xp INTEGER DEFAULT 0
)
''')

conn.commit()
conn.close()

async def get_gif_url(query):
    api_key = "jtyizMERY5ZSUDoGW8Usq7mHKkiORRXZ"
    url = f'https://api.giphy.com/v1/gifs/search?api_key={api_key}&q={query}&limit=10&rating=g'    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                gifs = data['data']
                if gifs:
                    gifs = random.choice(gifs)
                    return gifs['images']['original']['url']
    return None

#XP System
def add_xp(user_id, xp_to_add):
    conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), "xp_system.db"))
    cursor = conn.cursor()

    cursor.execute('SELECT xp FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    
    if result:
        new_xp = result[0] + xp_to_add
        cursor.execute('UPDATE users SET xp = ? WHERE user_id = ?', (new_xp, user_id))
    else:
        cursor.execute('INSERT INTO users (user_id, xp) VALUES(?, ?)', (user_id, xp_to_add))

    conn.commit()
    conn.close()

def get_xp(user_id):
    conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), "xp_system.db"))
    cursor = conn.cursor()

    cursor.execute('SELECT xp FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return 0





@client.event
async def on_ready():
    clock = datetime.datetime.now()
    current_time = clock.strftime("%H:%M")
    print(f"Bot connected as {client.user}")
    print(f"Bot online at {current_time}")


@client.command(help="tell you the bot latency!")
async def ping(ctx):
    latency = client.latency * 1000
    await ctx.message.reply(f':ping_pong: Pong! **{latency:.2f}ms**')


@client.command(help="tell you what time is it based on your computer clock!")
async def clock(ctx):
    clock = datetime.datetime.now()
    current_time = clock.strftime("%H:%M")
    await ctx.message.reply(f"It is **{current_time}** o clock :)")

@client.command(help="delete past messages")
async def clear(ctx, number: int = None):
    if not number or not isinstance(number, int) or number <= 0:
        await ctx.message.reply("ERROR: Number invalid")
        return
    elif number > 100:
        await ctx.message.reply("ERROR: Number bigger than 100 ")
        return
    await ctx.channel.purge(limit=number+ 1)
    await ctx.send(f"{number} messages cleared! {ctx.author.mention}", delete_after=20)


@client.command(help="Adds XP to a user!")
async def addxp(ctx,  value: int, member: discord.Member = None):
    member = member or ctx.author
    add_xp(member.id, value)
    await ctx.message.reply(f"**{value}** XP added to **{member.name}**.")

@client.command(help="show information about an user!")
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title="User Information:", color=discord.Color.random())
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="Name: ", value=member.name, inline=True)
    embed.add_field(name="User ID: ", value=member.id, inline=False)
    embed.add_field(name="Discord Member Since: ", value=member.created_at.strftime("%d/%m/%Y"), inline = True)
    embed.add_field(name="Joined Server At: ", value=member.joined_at.strftime("%d/%m/%Y"), inline = True)
    embed.add_field(name="Top Role: ", value=member.top_role.name, inline=False)
    embed.add_field(name="User XP", value=f"{get_xp(member.id)} XP", inline=True)
    await ctx.message.reply(embed=embed)

@client.command(help="show you all my commands!")
async def help(ctx):
    embed = discord.Embed(title=f"{client.user}'s COMMANDS", color=discord.Color.random())
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    embed.add_field(name='"INFO" COMMAND', value="Info about a certain command: '-info [command]'", inline=True )
    embed.add_field(name="General:", value="-ping; -clock; -userinfo; -serverinfo", inline=False)
    embed.add_field(name="Fun: ", value="-gif", inline=False)

    embed.add_field(name="Testing: ", value="-fakejoin", inline=False)

    await ctx.message.reply(embed=embed)



@client.command(help="tell you the command description")
async def info(ctx, command: str = None):
    if not command:
        await ctx.message.reply("Write the name of the command you want to know more about!")
        return
    
    command_obj = client.get_command(command)
    if command_obj:
        description = command_obj.help or "This command has no description yet. :("
        await ctx.message.reply(f"**{command_obj.name}**: {description}")
    else:
        await ctx.message.reply(":cross_mark: Command not found, sorry :(")

@client.command(help="tell information about the server")
async def serverinfo(ctx):
    online = len([m for m in ctx.guild.members if m.status in [discord.Status.online, discord.Status.do_not_disturb]])
    embed = discord.Embed(title=f'"{ctx.guild.name}" INFORMATION', color=discord.Color.random())
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    embed.add_field(name="Date Created:", value=f"{ctx.guild.created_at.strftime("%d/%m/%Y")}",inline=True)
    embed.add_field(name="Member Count:", value=f"{ctx.guild.member_count} members ({online} online)", inline=True)
    embed.add_field(name="Server Owner:", value=f"{ctx.guild.owner.name} ({ctx.guild.owner.status})", inline=False)
    await ctx.send(embed=embed)

@client.event
async def on_command(ctx, member: discord.member = None):
    commandName = ctx.command.name
    clock = datetime.datetime.now()
    current_time = clock.strftime("%H:%M:%S")
    print(f"Command Used: {commandName}\nMessage Author: {ctx.author}\nChannel used in: {ctx.channel.name}\nTime used at: {current_time}")
    print("___________________________________________________________________________")


async def welcome_message(member, channel):
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"----> {member} joined {member.guild.name} server at {current_time}")
    print("___________________________________________________________________________")
    await channel.send(f"**Welcome to the server, {member.mention}!** Make yourself comfortable and let's chill together. :coffee:")
    url = await get_gif_url("welcome")
    await channel.send(url)

@client.command(help="give you a GIF with given keyword")
async def gif(ctx, keyword: str = None):
    if not keyword:
        await ctx.message.reply("**ERROR: *GIF keyword missing.***")
        return
    url = await get_gif_url(keyword)
    await ctx.message.reply(f"{url}")


@client.event
async def on_member_join(member):
    channel = member.guild.system_channel or discord.utils.get(member.guild.text_channels, permissions__send_messages=True)
    if channel:
        await welcome_message(member, channel)

#Test command (fake member join)
@client.command(help="simulates a new member joining the server (for testing purposes)!")
async def fakejoin(ctx):
    await welcome_message(ctx.author, ctx.channel)


client.run("")