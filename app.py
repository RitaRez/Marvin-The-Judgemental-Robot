import os, re, requests, urllib.parse, urllib.request, discord, music_player, random
from discord.ext import commands,tasks
from dialogue import help_text, voice_channel_message, bad_taste_messages, good_taste_messages
from dotenv import load_dotenv
from bs4 import BeautifulSoup
 

load_dotenv()

MASTER = os.getenv("master")
client = discord.Client()
bot = commands.Bot(command_prefix='?')


async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect(reconnect=False)
    return channel


async def find_best_url(music_name):
    query_string = urllib.parse.urlencode({"search_query": music_name})
    formatUrl = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
    search_results = re.findall(r"watch\?v=(\S{11})", formatUrl.read().decode())

    return "https://www.youtube.com/watch?v=" + "{}".format(search_results[0])


async def play_song(ctx, url):
    if ctx.author.voice is None:
        await ctx.send(voice_channel_message)
        return 
    await join(ctx)

    voice_channel = ctx.voice_client
    async with ctx.typing():
        filename, title = await music_player.YTDLSource.from_url(url, loop=bot.loop)
        voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename))
    await ctx.send('**Now playing:** {}'.format(title))
    print(ctx.author.id, MASTER)
    
    if str(ctx.author.id) == MASTER: await ctx.send(good_taste_messages[random.randint(0,6)])
    else: await ctx.send(bad_taste_messages[random.randint(0,6)])
        

@bot.command()
async def search_song(ctx, *, music_name):
    try:
        url = await find_best_url(music_name)
        print(url)
        await play_song(ctx, url)
    except:
        await ctx.send("Oh no I'm malfunctioning! (I hope i short circuit myself to be completely honest)")

@bot.command()
async def play(ctx, url):
    try :
        await play_song(ctx, url)
    except:
        await ctx.send("Oh no I'm malfunctioning! (I hope i short circuit myself to be completely honest)")

@bot.command()
async def help_me(ctx):
    await ctx.send(help_text)

@bot.command()
async def insult(ctx, victim):
    response = requests.get(os.getenv("api"))
    victim_id = victim.replace('<', '').replace('>','').replace('@','').replace('!','')

    if victim_id == MASTER: answer = "I would never offend my beautiful master! Fuck you  <@!" + str(ctx.message.author.id) + ">!"
    else : answer = victim + " " + response.json()["insult"]
    
    await ctx.send(answer)  


if __name__ == "__main__" :
    bot.run(os.getenv("discord_token"))