# bot.py
import os

import discord
from discord import app_commands
from dotenv import load_dotenv

import doc_config
import googleHandler

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# print(f"running token: {TOKEN}")

intents = discord.Intents.default()
intents.messages = True
intents.members = True
intents.message_content = True
intents.guilds = True


client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    """
    Initialization print
    """
    await tree.sync(guild=discord.Object(id=doc_config.guild_id))
    print(f"{client.user} has connected to Discord!")


@tree.command(
    name="doc-clone",
    description="clones template doc",
    guild=discord.Object(id=doc_config.guild_id),
)
async def doc_clone_command(interaction):
    await interaction.response.send_message("Command Recieved!")


@tree.command(
    name="doc-update",
    description="Creates transparency doc or updates transparency report if it exists",
    guild=discord.Object(id=doc_config.guild_id),
)
async def doc_update(interaction):
    await interaction.response.send_message("Update command recieved")
    sdm_count = await get_role_member_count(doc_config.guild_id, doc_config.sdm_role_name)
    dm_count = await get_role_member_count(doc_config.guild_id, doc_config.dm_role_name)
    await googleHandler.run_doc_update(dm_count, sdm_count)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == "bing chilling":
        print(f"Message Recieved: {message}, Responding!")
        response = "早上好中国 现在我有冰淇淋 我很喜欢冰淇淋 但是 速度与激情9 比冰淇淋 速度与激情 速度与激情9 我最喜欢 所以…现在是音乐时间 准备 1 2 3 两个礼拜以后 速度与激情9 x3 不要忘记 不要错过 记得去电影院看速度与激情9 因为非常好电影 动作非常好 差不多一样冰淇淋 再见"

        await message.channel.send(response)
    elif message.content == "Tiennamen Square":
        response = "-100 Social credits"
        await message.channel.send(response)


async def get_role_member_count(guild_id, role_name):
    guild = client.get_guild(guild_id)
    if not guild:
        return None, "Guild not found"
    role = discord.utils.get(guild.roles, name=role_name)
    if not role:
        return None, f"Role '{role_name}' not found"
    return len(role.members), None


client.run(TOKEN)
