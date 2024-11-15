import discord
from discord.ext import commands
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import youtube_dl
import os

# Discord bot setup
TOKEN = 'YOUR_DISCORD_BOT_TOKEN'
bot = commands.Bot(command_prefix="!")

# Spotify API credentials
SPOTIFY_CLIENT_ID = 'YOUR_SPOTIFY_CLIENT_ID'
SPOTIFY_CLIENT_SECRET = 'YOUR_SPOTIFY_CLIENT_SECRET'

# Setup Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
))

# Join voice channel
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You need to be in a voice channel to use this command!")

# Leave voice channel
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("I'm not in a voice channel!")

# Play Spotify song
@bot.command()
async def play(ctx, *, url):
    # Get song details from Spotify
    try:
        track = sp.track(url)
        song_name = track['name']
        artist = track['artists'][0]['name']
        query = f"{song_name} {artist}"
        await ctx.send(f"Searching for: {query}")
    except:
        await ctx.send("Invalid Spotify URL!")
        return

    # Search for song on YouTube
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            url = info['url']
            title = info['title']
            await ctx.send(f"Now playing: {title}")
        except Exception as e:
            await ctx.send("Error finding song on YouTube.")
            return

    # Play audio in voice channel
    if ctx.voice_client:
        ctx.voice_client.stop()
        ctx.voice_client.play(discord.FFmpegPCMAudio(url), after=lambda e: print(f"Finished playing: {e}"))
    else:
        await ctx.send("I need to be in a voice channel to play music!")

# Run the bot
bot.run(TOKEN)
