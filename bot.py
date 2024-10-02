# bot.py
import os

import discord
from discord import app_commands
from dotenv import load_dotenv

import doc_config
import googleHandler
import quarterHandler

from googleapiclient.errors import HttpError

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
    name="test-command",
    description="test bot response",
    guild=discord.Object(id=doc_config.guild_id),
)
async def doc_clone_command(interaction: discord.Interaction):
    """
    Test Command
    """
    await interaction.response.send_message("Command Recieved!")


@tree.command(
    name="doc-update",
    description="Creates transparency doc or updates transparency report if it exists",
    guild=discord.Object(id=doc_config.guild_id),
)
async def doc_update(interaction: discord.Interaction):
    """
    Creates transparency document or updates it
    """
    initial_embed = discord.Embed(
        title="Transparency Report Request",
        description="Command recieved! Processing updates...",
        color=discord.Color.yellow(),
    )
    await interaction.response.send_message(embed=initial_embed)
    original_message = await interaction.original_response()

    try:

        sdm_count = await get_role_member_count(
            doc_config.guild_id, doc_config.sdm_role_name
        )
        dm_count = await get_role_member_count(
            doc_config.guild_id, doc_config.dm_role_name
        )
        await googleHandler.run_doc_update(dm_count, sdm_count)
        name = quarterHandler.make_file_name()
        link = googleHandler.get_file_link(name, doc_config.folder_id)

        updated_embed = discord.Embed(
            title="Transparency Report Request",
            description=(f"{name}: {link}"),
            color=discord.Color.green(),
        )
    except Exception:
        updated_embed = discord.Embed(
            title="Transparency Report Request",
            description=("Exception occured. Check Error Stack."),
            color=discord.Color.red(),
        )

    await original_message.edit(embed=updated_embed)


@tree.command(
    name="announcement-set",
    description="Lists out previous transparency reports",
    guild=discord.Object(id=doc_config.guild_id),
)
async def announcement_set(
    interaction: discord.Interaction, title: str = "", text: str = ""
):
    """
    Sets the announcement in the current document
    """
    initial_embed = discord.Embed(
        title="Announcement Set",
        description="Command recieved! Processing updates...",
        color=discord.Color.yellow(),
    )
    await interaction.response.send_message(embed=initial_embed)
    original_message = await interaction.original_response()
    print("Recieved announcement set")
    cur_file = quarterHandler.make_file_name()

    try:
        file_id = googleHandler.get_file_id_by_name(cur_file, doc_config.folder_id)

        if file_id is not None:

            googleHandler.make_announcement(file_id, title, text)

            print(f"Updated: {cur_file}")

            updated_embed = discord.Embed(
                title=f"Announcement Set: {cur_file}",
                description=(f"{title}: {text}"),
                color=discord.Color.green(),
            )
            await original_message.edit(embed=updated_embed)
    except HttpError:
        setting_embed = discord.Embed(
            title="Publishing Document",
            description="HTTP Error; No action taken",
            color=discord.Color.red(),
        )
        await original_message.edit(embed=setting_embed)


@tree.command(
    name="previous-reports",
    description="Lists out previous transparency reports",
    guild=discord.Object(id=doc_config.guild_id),
)
async def list_docs(interaction: discord.Interaction):
    """
    Lists previous documents that are found in public and private folders
    """
    print("List command called!")
    initial_embed = discord.Embed(
        title="Transparency Report List",
        description="Command recieved! Searching for documents...",
        color=discord.Color.yellow(),
    )
    await interaction.response.send_message(embed=initial_embed)
    original_message = await interaction.original_response()

    try:
        previous_private = googleHandler.find_previous_docs(doc_config.folder_id)
        previous_public = googleHandler.find_previous_docs(doc_config.share_folder_id)

        if previous_private is None:
            previous = previous_public
        elif previous_public is None:
            previous = previous_private
        else:
            previous = previous_private.copy()
            previous.update(previous_public)

        final_embed = discord.Embed(
            title="Transparency Report List",
            color=discord.Color.green(),
        )

        for name in previous.keys():
            folder_id = googleHandler.get_folder_from_docname(name)
            doc_id = googleHandler.get_file_id_by_name(name, folder_id)

            if googleHandler.check_string_in_doc(doc_id, "Unpublished"):
                pubStr = "Unpublished"
            elif googleHandler.check_string_in_doc(doc_id, "Published"):
                pubStr = "Published"
            else:
                pubStr = "Unknown"

            final_embed.add_field(
                name=f"{name}: {pubStr}", value=(f"{previous[name]}"), inline=False
            )

        await original_message.edit(embed=final_embed)
        print("Responded to list command!")
    except HttpError:
        setting_embed = discord.Embed(
            title="Transparency Report List",
            description="HTTP Error",
            color=discord.Color.red(),
        )
        await original_message.edit(embed=setting_embed)


@tree.command(
    name="publish-quarter",
    description="Sets to public. Announcements must be manually added after publishing",
    guild=discord.Object(id=doc_config.guild_id),
)
async def publishDoc(interaction: discord.Interaction):
    """
    Tasks:
    - Clean up holder text
    - Move document to new folder
    - Return link in response
    """
    print("Publish command called!")
    initial_embed = discord.Embed(
        title="Publishing Document",
        description="Command recieved! Cleaning up placeholders...",
        color=discord.Color.yellow(),
    )
    await interaction.response.send_message(embed=initial_embed)
    original_message = await interaction.original_response()

    cur_name = quarterHandler.make_file_name()

    try:
        id = googleHandler.get_file_id_by_name(cur_name, doc_config.folder_id)

        for holder in doc_config.holder_list:
            googleHandler.replace_text(id, holder, "N/A")

        googleHandler.replace_text(id, "Unpublished", "Published")

        setting_embed = discord.Embed(
            title="Publishing Document",
            description="Command recieved! Transferring folder...",
            color=discord.Color.yellow(),
        )
        await original_message.edit(embed=setting_embed)

        googleHandler.move_file(
            cur_name, doc_config.folder_id, doc_config.share_folder_id
        )

        link = googleHandler.get_file_link(cur_name, doc_config.share_folder_id)

        setting_embed = discord.Embed(
            title="Publishing Document",
            description=f"Document has been published at: {link}",
            color=discord.Color.green(),
        )
        await original_message.edit(embed=setting_embed)

    except HttpError:
        setting_embed = discord.Embed(
            title="Publishing Document",
            description="HTTP Error: File not moved",
            color=discord.Color.red(),
        )
        await original_message.edit(embed=setting_embed)


@tree.command(
    name="toggle-visibility",
    description="Toggles visibility of the document to the public",
    guild=discord.Object(id=doc_config.guild_id),
)
async def toggle_location(interaction: discord.Interaction, file_name: str):
    """
    Handles moving files from public to private and vice versa
    """
    print("Toggle command called!")
    initial_embed = discord.Embed(
        title="Toggle Document Location",
        description="Command recieved! Verifying publish status...",
        color=discord.Color.yellow(),
    )
    await interaction.response.send_message(embed=initial_embed)
    original_message = await interaction.original_response()

    folder_id = googleHandler.get_folder_from_docname(file_name)

    if folder_id is not None:
        doc_id = googleHandler.get_file_id_by_name(file_name, folder_id)

        if folder_id == doc_config.folder_id:
            if googleHandler.check_string_in_doc(doc_id, "Unpublished"):
                notif_embed = discord.Embed(
                    title="Toggle Document Location",
                    description="Document is unpublished, run /publish-quarter to publish.",
                    color=discord.Color.red(),
                )
                await original_message.edit(embed=notif_embed)
            else:
                googleHandler.move_file(
                    file_name, doc_config.folder_id, doc_config.share_folder_id
                )
                notif_embed = discord.Embed(
                    title="Toggle Document Location",
                    description="Document location is toggled.",
                    color=discord.Color.green(),
                )
                await original_message.edit(embed=notif_embed)
        elif folder_id == doc_config.share_folder_id:
            googleHandler.move_file(
                file_name, doc_config.share_folder_id, doc_config.folder_id
            )
            notif_embed = discord.Embed(
                title="Toggle Document Location",
                description="Document location is toggled.",
                color=discord.Color.green(),
            )
            await original_message.edit(embed=notif_embed)
        else:
            notif_embed = discord.Embed(
                title="Toggle Document Location",
                description="Error: Document not found. This error should not happen.",
                color=discord.Color.red(),
            )
            await original_message.edit(embed=notif_embed)

    else:
        notif_embed = discord.Embed(
            title="Toggle Document Location",
            description="Error: Document not found. No Files Changed.",
            color=discord.Color.red(),
        )
        await original_message.edit(embed=notif_embed)


@client.event
async def on_message(message: discord.Message):
    """
    Test Message detector 2
    """
    if message.author == client.user:
        return
    if message.content == "bing chilling":
        print(f"Message Recieved from {message.author}: {message.content}, Responding!")
        response = (
            "早上好中国 现在我有冰淇淋 我很喜欢冰淇淋 但是 速度与激情9 比冰淇淋 "
            "速度与激情 速度与激情9 我最喜欢 所以…现在是音乐时间 准备 1 2 3 "
            "两个礼拜以后 速度与激情9 x3 不要忘记 不要错过 记得去电影院看速度与激情9"
            " 因为非常好电影 动作非常好 差不多一样冰淇淋 再见"
        )

        await message.channel.send(response)


async def get_role_member_count(guild_id, role_name):
    """
    Gets the number of people with the given role name in a given server ID

    Args:
        guild_id: int
        role_name: String

    Returns:
        tuple[0]: int member count
        tuple[1]: Error if there is any
    """
    guild = client.get_guild(guild_id)
    if not guild:
        return None, "Guild not found"
    role = discord.utils.get(guild.roles, name=role_name)
    if not role:
        return None, f"Role '{role_name}' not found"
    return len(role.members), None


# Run bot
client.run(TOKEN)
