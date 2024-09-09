# docBot

This is a discord bot meant to work with the google docs and roblox API to produce a transparency report detailing moderation statistics over a set period of 3 months with a single command.

Currently a work in progress to get the base concept working with additional functionality coming later.

## Files
``bot.py`` - main bot code: handles discord side operations <br>
``doc_config.py`` - contstants such as doc IDs, guilds, roles, etc. to make changes easier <br>
``googlehandler.py`` - Handles all google API calls <br>
``quarterhandler.py`` - Handles automatic name creation and date formatting <br>
``robloxhandler.py`` - Handles gathering statistics from the Roblox Website <br>

## Hidden files
Standard files are hidden such as the .env folder containing the API key to the discord bot's functionality as well as keys/ which holds the API key to the google drive functionality. Pycache has also been hidden as it doesn't serve any functional purpose for deployment.
