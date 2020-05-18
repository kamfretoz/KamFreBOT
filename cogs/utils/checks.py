
# The permission system of the bot is based on a "just works" basis
# You have permissions and the bot has permissions. If you meet the permissions
# required to execute the command (and the bot does as well) then it goes through
# and you can execute the command.
# Certain permissions signify if the person is a moderator (Manage Server) or an
# admin (Administrator). Having these signify certain bypasses.
# Of course, the owner will always be able to execute commands.

import json
import time
import discord
from discord.ext import commands
import os
import aiohttp
from cogs.utils.dataIO import dataIO
from urllib.parse import quote as uriquote

try:
    from lxml import etree
except ImportError:
    from bs4 import BeautifulSoup
from urllib.parse import parse_qs, quote_plus

# from cogs.utils import common


# @common.deprecation_warn()
def load_config():
    with open("settings/config.json", "r") as f:
        return json.load(f)


# @common.deprecation_warn()
def load_optional_config():
    with open("settings/optional_config.json", "r") as f:
        return json.load(f)


# @common.deprecation_warn()
def load_moderation():
    with open("settings/moderation.json", "r") as f:
        return json.load(f)


# @common.deprecation_warn()
def load_notify_config():
    with open("settings/notify.json", "r") as f:
        return json.load(f)


# @common.deprecation_warn()
def load_log_config():
    with open("settings/log.json", "r") as f:
        return json.load(f)


def has_passed(oldtime):
    if time.time() - 20.0 < oldtime:
        return False
    return time.time()


def set_status(bot):
    if bot.default_status == "idle":
        return discord.Status.idle
    elif bot.default_status == "dnd":
        return discord.Status.dnd
    else:
        return discord.Status.invisible


def user_post(key_users, user):
    if time.time() - float(key_users[user][0]) < float(key_users[user][1]):
        return False, [time.time(), key_users[user][1]]
    else:
        log = dataIO.load_json("settings/log.json")
        now = time.time()
        log["keyusers"][user] = [now, key_users[user][1]]
        dataIO.save_json("settings/log.json", log)
        return True, [now, key_users[user][1]]


def gc_clear(gc_time):
    if time.time() - 3600.0 < gc_time:
        return False
    return time.time()


def game_time_check(oldtime, interval):
    if time.time() - float(interval) < oldtime:
        return False
    return time.time()


def avatar_time_check(oldtime, interval):
    if time.time() - float(interval) < oldtime:
        return False
    return time.time()


def cmd_prefix_len():
    config = load_config()
    return len(config["cmd_prefix"])


def embed_perms(message):
    try:
        check = message.author.permissions_in(message.channel).embed_links
    except:
        check = True

    return check


def get_user(message, user):
    try:
        member = message.mentions[0]
    except:
        member = message.guild.get_member_named(user)
    if not member:
        try:
            member = message.guild.get_member(int(user))
        except ValueError:
            pass
    if not member:
        return None
    return member


def find_channel(channel_list, text):
    if text.isdigit():
        found_channel = discord.utils.get(channel_list, id=int(text))
    elif text.startswith("<#") and text.endswith(">"):
        found_channel = discord.utils.get(
            channel_list, id=text.replace("<", "").replace(">", "").replace("#", "")
        )
    else:
        found_channel = discord.utils.get(channel_list, name=text)
    return found_channel


async def get_google_entries(query, session=None):
    if not session:
        session = aiohttp.ClientSession()
    url = "https://www.google.com/search?q={}".format(uriquote(query))
    params = {"safe": "off", "lr": "lang_en", "h1": "en"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64)"}
    entries = []
    async with session.get(url, params=params, headers=headers) as resp:
        if resp.status != 200:
            config = load_optional_config()
            async with session.get(
                "https://www.googleapis.com/customsearch/v1?q="
                + quote_plus(query)
                + "&start="
                + "1"
                + "&key="
                + config["google_api_key"]
                + "&cx="
                + config["custom_search_engine"]
            ) as resp:
                result = json.loads(await resp.text())
            return None, result["items"][0]["link"]

        try:
            root = etree.fromstring(await resp.text(), etree.HTMLParser())
            search_nodes = root.findall(".//div[@class='g']")
            for node in search_nodes:
                url_node = node.find(".//h3/a")
                if url_node is None:
                    continue
                url = url_node.attrib["href"]
                if not url.startswith("/url?"):
                    continue
                url = parse_qs(url[5:])["q"][0]
                entries.append(url)
        except NameError:
            root = BeautifulSoup(await resp.text(), "html.parser")
            for result in root.find_all("div", class_="g"):
                url_node = result.find("h3")
                if url_node:
                    for link in url_node.find_all("a", href=True):
                        url = link["href"]
                        if not url.startswith("/url?"):
                            continue
                        url = parse_qs(url[5:])["q"][0]
                        entries.append(url)
    return entries, root


def attach_perms(message):
    return message.author.permissions_in(message.channel).attach_files


def parse_prefix(bot, text):
    prefix = bot.cmd_prefix
    if type(prefix) is list:
        prefix = prefix[0]
    return text.replace("[c]", prefix).replace("[b]", bot.bot_prefix)


async def hastebin(content, session=None):
    if not session:
        session = aiohttp.ClientSession()
    async with session.post(
        "https://hastebin.com/documents", data=content.encode("utf-8")
    ) as resp:
        if resp.status == 200:
            result = await resp.json()
            return "https://hastebin.com/" + result["key"]
        else:
            return "Error with creating Hastebin. Status: %s" % resp.status

async def check_permissions(ctx, perms, *, check=all):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return check(getattr(resolved, name, None) == value for name, value in perms.items())

def has_permissions(*, check=all, **perms):
    async def pred(ctx):
        return await check_permissions(ctx, perms, check=check)
    return commands.check(pred)

async def check_guild_permissions(ctx, perms, *, check=all):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    if ctx.guild is None:
        return False

    resolved = ctx.author.guild_permissions
    return check(getattr(resolved, name, None) == value for name, value in perms.items())

def has_guild_permissions(*, check=all, **perms):
    async def pred(ctx):
        return await check_guild_permissions(ctx, perms, check=check)
    return commands.check(pred)

# These do not take channel overrides into account

def is_mod():
    async def pred(ctx):
        return await check_guild_permissions(ctx, {'manage_guild': True})
    return commands.check(pred)

def is_admin():
    async def pred(ctx):
        return await check_guild_permissions(ctx, {'administrator': True})
    return commands.check(pred)

def mod_or_permissions(**perms):
    perms['manage_guild'] = True
    async def predicate(ctx):
        return await check_guild_permissions(ctx, perms, check=any)
    return commands.check(predicate)

def admin_or_permissions(**perms):
    perms['administrator'] = True
    async def predicate(ctx):
        return await check_guild_permissions(ctx, perms, check=any)
    return commands.check(predicate)

def is_in_guilds(*guild_ids):
    def predicate(ctx):
        guild = ctx.guild
        if guild is None:
            return False
        return guild.id in guild_ids
    return commands.check(predicate)

def is_lounge_cpp():
    return is_in_guilds(145079846832308224)