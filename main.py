from keep_alive import keep_alive
import discord
import os
# load our local env so we dont have the token in public
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from discord import TextChannel
from youtube_dl import YoutubeDL

load_dotenv()
client = commands.Bot(command_prefix='!')  # prefix our commands with '.'

players = {}
List = []
Key = 0

@client.event  # check if bot is ready
async def on_ready():
    print('Bot online')


# command for bot to join the channel of the user, if the bot has already joined and is in a different channel, it will move to the channel the user is in
@client.command()
async def join(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()



# command to play sound from a youtube URL
@client.command()
async def play(ctx, url):
    global List
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()  


    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'true'}
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
      List.append(url)
      await ctx.send("Added video to queue")

    elif not voice.is_playing():
      List.append(url)
      with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(List[Key], download=False) 
      URL = info['url']              
      voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
      voice.is_playing()
      await ctx.send('Bot is playing...')
  

# command to skip song
@client.command()
async def skip(ctx):
  global List
  channel = ctx.message.author.voice.channel
  voice = get(client.voice_clients, guild=ctx.guild)
  if voice.is_playing():
      voice.stop()
      YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'false'}
      FFMPEG_OPTIONS = {
          'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
      voice = get(client.voice_clients, guild=ctx.guild)

      global Key
      Key += 1

      with YoutubeDL(YDL_OPTIONS) as ydl:
          info = ydl.extract_info(List[Key], download=False)
      URL = info['url']
      voice.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
      voice.is_playing()
      await ctx.send('Skipping to next video...')


# command to resume voice if it is paused
@client.command()
async def resume(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if not voice.is_playing():
        voice.resume()
        await ctx.send('Bot is resuming...')


# command to pause voice if it is playing
@client.command()
async def pause(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)

    if voice.is_playing():
        voice.pause()
        await ctx.send('Bot has been paused')


# command to stop voice
@client.command()
async def stop(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.stop()
        await ctx.send('Stopping....Playlist has been reset')

    global List
    List = []
    global Key
    Key = 0


# command to force disconnect bot
@client.command()
async def leave(ctx):
    voice = get(client.voice_clients, guild=ctx.guild)
    global List
    List = []
    global Key
    channel = ctx.voice_client.channel
    await ctx.voice_client.disconnect()
    await ctx.send("Disconnected from voice channel")
    await ctx.send("Clearing playlists...")
keep_alive()
client.run(os.getenv('TOKEN'))

