import discord
from discord.ext import commands
import datetime
import random
import aiohttp

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = commands.Bot(command_prefix='-', intents=intents)

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


@client.event
async def on_ready():
    clock = datetime.datetime.now()
    current_time = clock.strftime("%H:%M")
    print(f"Bot connected as {client.user}")
    print(f"Bot online at {current_time}")


@client.command()
async def ping(ctx):
    latency = client.latency * 1000
    await ctx.message.reply(f':ping_pong: Pong! **{latency:.2f}ms**')


@client.command()
async def clock(ctx):
    clock = datetime.datetime.now()
    current_time = clock.strftime("%H:%M")
    await ctx.message.reply(f"It is **{current_time}** o clock :)")


@client.command()
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
    await ctx.message.reply(embed=embed)


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


@client.event
async def on_member_join(member):
    channel = member.guild.system_channel or discord.utils.get(member.guild.text_channels, permissions__send_messages=True)
    if channel:
        await welcome_message(member, channel)

#Test command (fake member join)
@client.command()
async def fakejoin(ctx):
    await welcome_message(ctx.author, ctx.channel)


    



client.run()