import os
import re
import time
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 📝 PROMO DETECTION CONFIG
PROMO_KEYWORDS = [
    "join my discord ",  "join my server ",  "i give panel ",  "my id Ban",
    "check my channel ",  "subscribe to ",  "get Ban ",  "advertisement ",  "ad link ",
    "my discord server ",  "discord.gg ",  "invite me ",  "check this out ",
    "Ban my id ",  "guys my get Ban ",  "dm me for script ",  "watch my video ",
    "selling panel ",  "sell panel ",  "panel sale ",  "buy panel ",
    "come to join ",  "casino ",  "withdrawal ",  "suspend my id ",  "Not safe ",
    "Do not use panel ",  "panel not use ",  "It's not safe ",  "my id Ban ",  "Dm me "
]
URL_REGEX = re.compile(r'https?://\S+|discord.gg/\S+', re.IGNORECASE)
WARNING_COOLDOWN_SECONDS = 86400  # 24 hours
promo_warn_tracker = {}

# 🔧 CHANNEL CONFIGURATION
LOG_CHANNEL_ID = None
BYPASS_CHANNEL_IDS = []

def is_promo_message(content):
    if not content:
        return False
    if URL_REGEX.search(content):
        return True
    lower_content = content.lower()
    return any(keyword in lower_content for keyword in PROMO_KEYWORDS)

def is_protected_user(member):
    """Ignore Owner, Admins, and Moderators"""
    if member.id == member.guild.owner_id:
        return True
    perms = member.guild_permissions
    return perms.administrator or perms.manage_messages or perms.kick_members or perms.ban_members

async def setup_channels(guild):
    global LOG_CHANNEL_ID, BYPASS_CHANNEL_IDS
    # Auto-detect log channel
    for name in ['logging', 'log']:
        ch = discord.utils.get(guild.text_channels, name=name)
        if ch:
            LOG_CHANNEL_ID = ch.id
            break
    # Auto-detect bypass channels
    BYPASS_CHANNEL_IDS = []
    for name in ['uidbypass', 'mod', 'admin']:
        ch = discord.utils.get(guild.text_channels, name=name)
        if ch:
            BYPASS_CHANNEL_IDS.append(ch.id)

async def send_log(guild, title, description):
    if LOG_CHANNEL_ID:
        ch = guild.get_channel(LOG_CHANNEL_ID)
        if ch:
            try:
                await ch.send(f"📜 {title}\n{description}")
            except:
                pass

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online | Anti-Promo System Active")
    for guild in bot.guilds:
        await setup_channels(guild)
        print(f"📂 {guild.name}: Log Channel ID = {LOG_CHANNEL_ID}")

@bot.event
async def on_message(message):
    # 1. Ignore bots
    if message.author.bot:
        return

    # 2. Ignore Staff (Admins/Mods/Owner) - ONLY MEMBERS get punished
    if is_protected_user(message.author):
        return

    # 3. Ignore if in bypass channel
    if message.channel.id in BYPASS_CHANNEL_IDS:
        return

    # 4. CHECK FOR IMAGES - DELETE SILENTLY (No warning, no kick)
    if len(message.attachments) > 0:
        try:
            await message.delete()
        except discord.Forbidden:
            pass
        return  # STOP HERE - Don't process text logic

    # 5. Detect Text Promo Only
    if is_promo_message(message.content):
        user_id = message.author.id
        now = time.time()

        # CHECK IF ALREADY WARNED
        if user_id in promo_warn_tracker:
            warning_time = promo_warn_tracker[user_id]
            
            # If within 24 hours → SECOND OFFENSE: KICK
            if now - warning_time < WARNING_COOLDOWN_SECONDS:
                try:
                    await message.delete()
                    await message.author.kick(reason="Repeated promotional content after warning")
                    
                    await message.channel.send(f"🔨 {message.author.mention} has been **kicked** for repeated promotion.")
                    await send_log(message.guild, "MEMBER KICKED", 
                        f"👤 {message.author.mention} (`{message.author.id}`)\n"
                        f"📝 Reason: Second promotional offense within 24h\n"
                        f"⏰ Time: <t:{int(now)}:F>")
                except discord.Forbidden:
                    await message.channel.send("⚠️ Bot missing Kick permission.")
                except Exception as e:
                    print(f"Kick Error: {e}")
                finally:
                    promo_warn_tracker.pop(user_id, None)
                return
            else:
                # Warning expired → reset
                promo_warn_tracker.pop(user_id, None)

        # FIRST OFFENSE → WARNING
        promo_warn_tracker[user_id] = now
        await message.delete()
        
        # 📢 WARNING MESSAGE WITH MENTION
        await message.channel.send(
            f"⚠️ {message.author.mention} promote Message Do not Allowed It Fixcorporation rule next time send this message You Will be kicked from the server "
        )
        
        await send_log(message.guild, "WARNING ISSUED", 
            f"👤 {message.author.mention} (`{message.author.id}`)\n"
            f"📝 Reason: First promotional offense\n"
            f"⏰ Time: <t:{int(now)}:F>")

    await bot.process_commands(message)

bot.run(TOKEN)
