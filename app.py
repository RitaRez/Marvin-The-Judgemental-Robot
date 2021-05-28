import discord
from discord.ext import commands,tasks
import os
from dotenv import load_dotenv
from dialogue import help_text
import youtube_dl
import requests

load_dotenv()

# Get the API token from the .env file.
DISCORD_TOKEN = os.getenv("discord_token")
API = os.getenv("api")
MASTER = os.getenv("master")

client = discord.Client()
bot = commands.Bot(command_prefix='?')



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