# bot.py
import os

import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# print(f"running token: {TOKEN}")

testing_guild = 996319065679331348

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
    await tree.sync(guild=discord.Object(id=testing_guild))
    print(f"{client.user} has connected to Discord!")


@tree.command(
    name="doc-clone",
    description="clones template doc",
    guild=discord.Object(id=testing_guild),
)
async def doc_clone_command(interaction):
    await interaction.response.send_message("Command Recieved!")


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


client.run(TOKEN)
