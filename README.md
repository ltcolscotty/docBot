# docBot

This is a discord bot meant to work with the google docs and roblox API to produce a transparency report detailing moderation statistics over a set period of 3 months with a single command.

## Files
``bot.py`` - main bot code: handles discord side operations <br>
``doc_config.py`` - contstants such as doc IDs, guilds, roles, etc. to make changes easier <br>
``googlehandler.py`` - Handles all google API calls <br>
``quarterhandler.py`` - Handles automatic name creation and date formatting <br>
``robloxhandler.py`` - Handles gathering statistics from the Roblox Website <br>

## Hidden files
Standard files are hidden such as the .env folder containing the API key to the discord bot's functionality as well as keys/ which holds the API key to the google drive functionality. Pycache has also been hidden as it doesn't serve any functional purpose for deployment.

## Commands

``doc-update`` - Creates/Updates Document <br>
``announcement-set`` - Sets announcements <br>
``previous-reports`` - lists out previous documents <br>
``publish-quarter`` - Prepares document and transfers it to the public folder <br>
``toggle-visibility`` - moves specified document to public/private folder <br>

# Setup

Some technical knowledge is needed for the setup of the bot. The ``tests`` folder may be removed or modified if modification of the bot is desired.
[Modular] - Indicates that this can be duplicated or removed with additonal names. Additional modifications are detailed.

## python environment
run ``pip install -r requirements.txt`` in an environment to get the bot setup <br>

## File Structure
create a file called ``.env``, and a folder named ``keys`` <br>
``.env`` - should contain ``DISCORD_TOKEN='putyourbottokenhere'`` <br>
``keys/`` - should contain your google Oauth2 key json file. <br>

## doc_config.py

``file_id`` - Template file that the bot is modifying. This is a file ID. Ensure the service account has access to this file. <br>
``folder_id`` - Folder that the privated files are stored at. This is a folder ID. Ensure the service account has access to this file. <br>
``share_folder_id`` - Folder that public files are stored at. This is a folder ID. Ensure the service account has access to this file. <br>

``mod_group`` - roblox group ID of the group of interest

``guild_id`` - ID of the discord server where discord moderation roles are kept <br>
``sdm_role_name`` - Name of Role 1 of interest [Modular] <br>
``dm_role_name`` - Name of Role 2 of interest [Modular] <br>
(new roles of interest can be added, eg ``jdm_role_name``)

``holder_list`` - List of placeholders that need to be modified in the document. Treat these as variables in the actual document itself as these are to be altered by ``googleHandler.py`` [Modular]

## googleHandler.py
``SERVICE_ACCOUNT_FILE`` - "xina_service.json" should be modified to the key json file of your google service account stored in ``keys/`` that was created earlier <br>
``run_doc_update()`` - ``replace_text`` calls should be modified to match your desired placeholders. The function works by looking for all instances of placeholder text and replacing said placeholder text with desired text. Make sure to have all [Modular] calls updated here from doc_config.py so that every desired placeholder is replaced with desired values. <br>

## quarterHandler.py
``make_file_name()`` - update the return statement to return the proper file name format.

# Run the bot
Once everything is set up, ``python bot.py`` should all that nees to be run.

# Using the bot
1. Create a report using ``/doc-update`` to create a report. If everything is properly configured, minimal configuration should be needed.
2. If ``announcementTitleHolder`` and ``announcentHolder`` are in the google docs template and were not removed from doc_config.py, you can set an announcement using ``/announcement-set`` which takes two optional arguments. If no arguments are passed, both will be set to blanks.
3. Use ``/publish-quarter`` to send the file to the public folder, the link is ready for you to post!
4. ``/previous-reports`` will be available if you want to see previously generated reports with their respective links and publication status. 
5. ``/toggle-visibility`` is available should you want to set a file that is public to private, and vice versa
6. ``/test-command`` is a basic function available that only interacts with discord.py to help troubleshoot should issues come up.