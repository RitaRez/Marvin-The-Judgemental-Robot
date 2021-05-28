import discord
from discord.ext import commands,tasks
import os
from dotenv import load_dotenv
from dialogue import help_text, voice_channel_message
import youtube_dl
import requests

load_dotenv()

# Get the API token from the .env file.
DISCORD_TOKEN = os.getenv("discord_token")
API = os.getenv("api")
MASTER = os.getenv("master")

client = discord.Client()
bot = commands.Bot(command_prefix='?')

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}


ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename

async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect(reconnect=False)
    return channel
    
@bot.command()
async def play(ctx, url):
    
    if ctx.author.voice is None:
        await ctx.send(voice_channel_message)
        return 

    try :
        voice_channel = await join(ctx)

        # async with ctx.typing():
        #     filename = await YTDLSource.from_url(url, loop=bot.loop)
        #     voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
        # await ctx.send('**Now playing:** {}'.format(filename))
    except:
        await ctx.send("Oh no I'm malfunctioning! (I hope i short circuit myself to be completely honest)")


@bot.command()
async def help_me(ctx):
    await ctx.send(help_text)

@bot.command()
async def insult(ctx, victim):
    response = requests.get(API)
    victim_id = victim.replace('<', '').replace('>','').replace('@','').replace('!','')

    if victim_id == MASTER: answer = "I would never offend my beautiful master! Fuck you  <@!" + str(ctx.message.author.id) + ">!"
    else : answer = victim + " " + response.json()["insult"]
    
    await ctx.send(answer)  


if __name__ == "__main__" :
    bot.run(DISCORD_TOKEN)