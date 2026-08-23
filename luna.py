import discord
from discord.ext import commands
import random
import asyncio
from datetime import datetime, timedelta
import os
import re
import aiohttp
from flask import Flask
from threading import Thread

# Flask web server
app = Flask('')
@app.route('/')
def home():
    return "✅ Luna Bot is alive!"
def run():
    app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ========== CONFIGURATION ==========
# REPLACE THIS WITH YOUR ACTUAL DISCORD USER ID
# Right-click on your name in Discord -> Copy User ID
OWNER_USER_ID = 1232243863423418432  # <- CHANGE THIS NUMBER!

# ========== BANNED PHRASES (auto-delete for members only) ==========
# Messages containing any of these (case‑insensitive) will be deleted
# ONLY for non-owner members
BANNED_PHRASES = [
    "banned",
    "ban",
    "Blocklist",
    "id ban",
    "id get banned",
    "id banned"
]

# ========== VIDEO LINKS DATABASE (UP TO 50 VIDEOS) ==========
# MAKE SURE EACH VIDEO NUMBER HAS ONLY ONE LINK!
VIDEO_LINKS = {
    # Video 1-10
    1: "https://youtu.be/tUQ2s7U0hng?si=8S5xTUp6FogA0CKN",
    2: "https://youtu.be/D-WOcICCoM4?si=ZXeO9lG13oy29Xw0",
    3: "https://youtu.be/0CHQG-9L8CE?si=Ag3XHy5unNt_9IF-",
    4: "https://youtu.be/GoOQpNFofR0?si=inPGFJfmsPPcUrHX",
    5: "https://youtu.be/8RqrMgY_njc?si=q_kKuk72ZrjGwUlA",
    6: "https://youtu.be/itlOUx0NNJo?si=2PDg6ha2DgMC5Ucv",
    7: "https://youtu.be/o0bg7z6-rUQ?si=tXGiets0v6P4I0vv",
    8: "https://youtu.be/NafVL3Sihxw?si=6Q9pB4jC6M434v39",
    9: "https://youtu.be/MK5wVpqlj5Y?si=uudFAuj02ksz8xBc",
    10: "https://youtu.be/vG1wNpylgM8?si=FvfEkfadKZqMaCKY",
    
    # Video 11-20
    11: None,
    12: None,
    13: None,
    14: None,
    15: None,
    16: None,
    17: None,
    18: "https://youtu.be/jOn7pFw66fI?si=8PLvGRzEJXN80BMS",
    19: "https://youtu.be/QB1Ylu7a624?si=295yanCw9U1X7xCI",
    20: "https://youtu.be/isQ6S2302AU?si=nK32HNp2Mz3giGUR",
    
    # Video 21-30
    21: "https://youtu.be/cEciZxV6nVs?si=POAx-j_ny3tTJvP6",
    22: "https://youtu.be/biI06dOe_QM?si=DDKxG1ikNxyAmw3_",
    23: "https://youtu.be/nxEsHv57J0U?si=25J0Z7Toq0QdgGX5",
    24: "https://youtu.be/BfPLVpEV0Z8?si=vhV8ZwR8_dxqL-rO",
    25: "https://youtu.be/TOt42jVaROQ?si=gYefmwGnFiqjjomV",
    26: None,
    27: None,
    28: None,
    29: None,
    30: None,
    
    # Video 31-40
    31: None,
    32: None,
    33: None,
    34: None,
    35: None,
    36: None,
    37: None,
    38: None,
    39: None,
    40: None,
    
    # Video 41-50
    41: None,
    42: None,
    43: None,
    44: None,
    45: None,
    46: None,
    47: None,
    48: None,
    49: None,
    50: None,
}

def is_owner():
    """Check if user is the bot owner by user ID"""
    async def predicate(ctx):
        if ctx.author.id != OWNER_USER_ID:
            await ctx.send(f"❌ You don't have permission! Only the server owner can use this command.")
            return False
        return True
    return commands.check(predicate)

# ========== YOUTUBE FUNCTIONS ==========
async def process_youtube_channel(url):
    channel_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/@([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/channel/([a-zA-Z0-9_-]+)',
        r'(?:https?://)?(?:www\.)?youtube\.com/c/([a-zA-Z0-9_-]+)'
    ]
    for pattern in channel_patterns:
        match = re.search(pattern, url)
        if match:
            channel_identifier = match.group(1)
            return {
                'type': 'channel',
                'handle': f"@{channel_identifier}",
                'url': f"https://youtube.com/@{channel_identifier}",
                'clean_url': f"https://youtube.com/@{channel_identifier}"
            }
    return None

async def send_subscribe_embed(channel, channel_handle="@FIXCORPORATION"):
    embed = discord.Embed(
        title="🎯 Don't Forget to Subscribe!",
        description=f"Check out **{channel_handle}** on YouTube!",
        color=discord.Color.gold()
    )
    embed.add_field(name="📺 Channel Link", value=f"https://youtube.com/{channel_handle}", inline=False)
    embed.add_field(name="🎁 What You Get", value="• Free Aimbot panel\n• 100% Safe\n• Trusted Panel Seller", inline=False)
    embed.add_field(name="📊 Current Stats", value="405 subscribers • 19 videos", inline=True)
    embed.set_footer(text="Subscribe, like, and stay tuned for more!")
    await channel.send(embed=embed)

# ========== VIDEO COMMANDS (OWNER ONLY) ==========
@bot.command(name='video')
@is_owner()
async def get_video(ctx, video_number: int):
    """Get a specific video by number (1-50). Usage: !video 18"""
    if video_number < 1 or video_number > 50:
        await ctx.send(f"❌ Please enter a video number between 1 and 50. You requested: {video_number}")
        return
    
    video_link = VIDEO_LINKS.get(video_number)
    
    if not video_link or video_link is None:
        await ctx.send(f"❌ Video #{video_number} link has not been added yet. Use `!addvideo {video_number} <link>` to add it!")
        return
    
    # Single embed - NO DUPLICATES
    embed = discord.Embed(
        title=f"🎬 Video #{video_number}",
        description=f"Here's your video!",
        color=discord.Color.blue()
    )
    embed.add_field(name="📹 Video Link", value=video_link, inline=False)
    embed.set_footer(text="Subscribe The channel")
    await ctx.send(embed=embed)

@bot.command(name='videos')
@is_owner()
async def list_videos(ctx):
    """List all available video numbers"""
    available_videos = [num for num, link in VIDEO_LINKS.items() 
                       if link and link is not None]
    
    if not available_videos:
        await ctx.send("❌ No videos have been added yet! Use `!addvideo <number> <link>` to add videos.")
        return
    
    # Create chunks of 10 videos for better display
    chunks = [available_videos[i:i+10] for i in range(0, len(available_videos), 10)]
    
    embed = discord.Embed(
        title="📋 Available Videos",
        description=f"Total videos available: {len(available_videos)}/50",
        color=discord.Color.green()
    )
    
    for i, chunk in enumerate(chunks, 1):
        embed.add_field(
            name=f"Videos {chunk[0]}-{chunk[-1]}",
            value=", ".join(map(str, chunk)),
            inline=True
        )
    
    embed.add_field(name="💡 How to use", value="Use `!video <number>` to get a video link!\nExample: `!video 18`", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='addvideo')
@is_owner()
async def add_video(ctx, video_number: int, *, video_link: str):
    """Add a new video link (Owner only). Usage: !addvideo 21 https://youtu.be/xxxxx"""
    if video_number < 1 or video_number > 50:
        await ctx.send(f"❌ Video number must be between 1 and 50!")
        return
    
    # Basic YouTube URL validation
    if not ('youtu.be/' in video_link or 'youtube.com/' in video_link):
        await ctx.send(f"❌ Please provide a valid YouTube link!")
        return
    
    # Check if video already exists
    if VIDEO_LINKS.get(video_number) is not None:
        await ctx.send(f"⚠️ Video #{video_number} already has a link: {VIDEO_LINKS[video_number]}\nUse `!updatevideo {video_number} <new_link>` to update it, or `!removevideo {video_number}` to remove it first.")
        return
    
    VIDEO_LINKS[video_number] = video_link
    await ctx.send(f"✅ Video #{video_number} has been added!\nLink: {video_link}")

@bot.command(name='updatevideo')
@is_owner()
async def update_video(ctx, video_number: int, *, video_link: str):
    """Update a video link (Owner only). Usage: !updatevideo 18 https://youtu.be/xxxxx"""
    if video_number < 1 or video_number > 50:
        await ctx.send(f"❌ Video number must be between 1 and 50!")
        return
    
    # Basic YouTube URL validation
    if not ('youtu.be/' in video_link or 'youtube.com/' in video_link):
        await ctx.send(f"❌ Please provide a valid YouTube link!")
        return
    
    old_link = VIDEO_LINKS.get(video_number)
    VIDEO_LINKS[video_number] = video_link
    
    if old_link is None:
        await ctx.send(f"✅ Video #{video_number} has been added!\nNew link: {video_link}")
    else:
        await ctx.send(f"✅ Video #{video_number} has been updated!\nOld link: {old_link}\nNew link: {video_link}")

@bot.command(name='removevideo')
@is_owner()
async def remove_video(ctx, video_number: int):
    """Remove a video link (Owner only). Usage: !removevideo 19"""
    if video_number < 1 or video_number > 50:
        await ctx.send(f"❌ Video number must be between 1 and 50!")
        return
    
    old_link = VIDEO_LINKS.get(video_number)
    
    if old_link is None:
        await ctx.send(f"❌ Video #{video_number} does not have a link to remove!")
        return
    
    VIDEO_LINKS[video_number] = None
    await ctx.send(f"✅ Video #{video_number} has been removed!\nRemoved link: {old_link}")

@bot.command(name='showvideo')
@is_owner()
async def show_video(ctx, video_number: int):
    """Show what link is stored for a video number (Owner only). Usage: !showvideo 19"""
    if video_number < 1 or video_number > 50:
        await ctx.send(f"❌ Video number must be between 1 and 50!")
        return
    
    video_link = VIDEO_LINKS.get(video_number)
    
    if video_link is None:
        await ctx.send(f"❌ Video #{video_number} has no link stored. Use `!addvideo {video_number} <link>` to add it!")
    else:
        await ctx.send(f"📹 Video #{video_number} current link: {video_link}")

# ========== MAIN ON_MESSAGE (FIXED) ==========
@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    is_owner = (message.author.id == OWNER_USER_ID)

    # ---- AUTO-DELETE for banned phrases (members only) ----
    # Owner is exempt from deletion
    if not is_owner:
        content_lower = message.content.lower()
        if any(phrase in content_lower for phrase in BANNED_PHRASES):
            try:
                await message.delete()
            except discord.Forbidden:
                pass
            return   # stop further processing for this message

    # ---- 'luna' keyword triggers subscribe embed (for everyone, including owner) ----
    if 'luna' in message.content.lower():
        await send_subscribe_embed(message.channel, "@FIXCORPORATION")
        return   # do not process commands after sending embed

    # ---- Process commands (for everyone) ----
    await bot.process_commands(message)

# ========== MODERATION COMMANDS ==========
@bot.command(name='timeout')
@is_owner()
async def timeout_member(ctx, member: discord.Member, duration: int = 60, *, reason: str = "No reason provided"):
    try:
        timeout_duration = timedelta(minutes=duration)
        await member.timeout(timeout_duration, reason=reason)
        
        embed = discord.Embed(
            title="⏰ Member Timed Out",
            description=f"{member.mention} has been timed out!",
            color=discord.Color.orange()
        )
        embed.add_field(name="Duration", value=f"{duration} minutes", inline=True)
        embed.add_field(name="Reason", value=reason, inline=True)
        await ctx.send(embed=embed)
        
        try:
            await member.send(f"⚠️ You have been timed out in **{ctx.guild.name}** for {duration} minutes.\nReason: {reason}")
        except:
            pass
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to timeout this member!")

@bot.command(name='untimeout')
@is_owner()
async def untimeout_member(ctx, member: discord.Member):
    try:
        await member.timeout(None)
        await ctx.send(f"✅ {member.mention} timeout has been removed!")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to remove timeout!")

@bot.command(name='kick')
@is_owner()
async def kick_member(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    if member == ctx.author:
        await ctx.send("❌ You cannot kick yourself!")
        return
    try:
        await member.kick(reason=reason)
        await ctx.send(f"✅ {member.mention} has been kicked!\nReason: {reason}")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to kick this member!")

@bot.command(name='ban')
@is_owner()
async def ban_member(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    if member == ctx.author:
        await ctx.send("❌ You cannot ban yourself!")
        return
    try:
        await member.ban(reason=reason)
        await ctx.send(f"✅ {member.mention} has been banned!\nReason: {reason}")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to ban this member!")

@bot.command(name='unban')
@is_owner()
async def unban_member(ctx, *, member_name):
    try:
        banned_users = [entry async for entry in ctx.guild.bans()]
        member_name_split = member_name.split('#')
        for ban_entry in banned_users:
            user = ban_entry.user
            if user.name == member_name_split[0]:
                await ctx.guild.unban(user)
                await ctx.send(f"✅ Unbanned {user.mention}")
                return
        await ctx.send(f"❌ Could not find banned user: {member_name}")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='clear')
@is_owner()
async def clear(ctx, amount=5):
    if amount > 100:
        amount = 100
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'✅ Deleted {amount} messages!', delete_after=3)

# ========== REGULAR COMMANDS ==========
@bot.command(name='subscribe')
async def subscribe_reminder(ctx):
    await send_subscribe_embed(ctx.channel, "@FIXCORPORATION")

@bot.command(name='ping')
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f'🏓 Pong! Latency: {latency}ms')

@bot.command(name='commands')
async def show_commands(ctx):
    embed = discord.Embed(title="📋 Available Commands", color=discord.Color.green())
    embed.add_field(name="!ping", value="Check bot latency", inline=False)
    embed.add_field(name="!subscribe", value="Get FIX CORPORATION YouTube link", inline=False)
    embed.add_field(name="🔒 OWNER ONLY COMMANDS:", value="━━━━━━━━━━━━━━━━━━", inline=False)
    embed.add_field(name="!video <number>", value="Get a specific video (1-50)", inline=False)
    embed.add_field(name="!videos", value="List all available video numbers", inline=False)
    embed.add_field(name="!addvideo <number> <link>", value="Add a new video link", inline=False)
    embed.add_field(name="!updatevideo <number> <link>", value="Update an existing video link", inline=False)
    embed.add_field(name="!removevideo <number>", value="Remove a video link", inline=False)
    embed.add_field(name="!showvideo <number>", value="Show what link is stored", inline=False)
    embed.add_field(name="!timeout @user [min] [reason]", value="Timeout a member", inline=False)
    embed.add_field(name="!untimeout @user", value="Remove timeout", inline=False)
    embed.add_field(name="!kick @user [reason]", value="Kick a member", inline=False)
    embed.add_field(name="!ban @user [reason]", value="Ban a member", inline=False)
    embed.add_field(name="!clear [amount]", value="Delete messages", inline=False)
    embed.add_field(name="🎬 Auto Features", value="• Type 'Luna' anywhere to get subscribe link!\n• Banned words auto-deleted (members only)", inline=False)
    embed.set_footer(text="Made for FIX CORPORATION | 🔒 = Owner only")
    await ctx.send(embed=embed)

# ========== ERROR HANDLING ==========
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument! Example: `!{ctx.command.name} @user`")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Member not found! Please mention a valid user.")
    elif isinstance(error, commands.BadArgument):
        if ctx.command.name == 'video':
            await ctx.send("❌ Please provide a valid video number! Example: `!video 18`")

# ========== BOT STARTUP ==========
@bot.event
async def on_ready():
    print(f'✅ {bot.user} is online!')
    print(f'📊 Bot is in {len(bot.guilds)} guilds')
    available = len([l for l in VIDEO_LINKS.values() if l is not None])
    print(f'🎬 Loaded {available}/50 video links')
    await bot.change_presence(activity=discord.Game(name="WELCOME TO FIXCORPORATION"))

# ========== RUN BOT ==========
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ Error: DISCORD_TOKEN environment variable not found!")
    else:
        keep_alive()
        print("🚀 Starting bot...")
        bot.run(TOKEN)
