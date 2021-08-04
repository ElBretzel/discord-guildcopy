# Guildcopy discord bot

This discord bot can create an exact replica of a guild.
It is very usefull if you want to create a backup guild.
The bot is not hosted. You need to selfhost the bot.

## :memo: Features
* 1.0
	* Clone every channels and their permissions.
  	* Clone every roles and their permissions
	* Clone every emojis.
	* Clone every bans.
	* Clone every messages and attachments.
	* Clone guild configuration.
	* Create a new fresh guild after the copy is done.
  	* Automaticly add the user who start the clonage owner of the backup guild.
  	* Automaticly sync roles and channels permissions when a member join.
  	* And much more...
	
## :mag_right: Installation

1. If you don't have Python installed, download the last version [here][1].
2. Download the [last release version][2] of the project.
3. Install all the dependencies with: pip install -r requirements.txt --upgrade
4. Create your discord application [here][3].
5. Make your application a bot.
6. Copy the bot token.
7. Go to the OAuth2 menu, then under the "OAuth2 URL Generator" select 'bot' and 'Administrator'.
8. Copy the generated URL and paste it in your internet navigator.
9. Choose your discord server.
10. Move the bot role to the top of all your roles
10 bis. You can edit as you wish the configurations in the file const.py (for instance, change the language or the timezone)
11. Launch 'main.py' in the console.
12. Paste your bot token in the console.
13. To clone your guild, enter §copy <YourGuildId> (without the <>)
13. Keep your computer fully awake during the whole copy process.
14. Don't close the bot if you wan't to automaticly set roles to newcomers.
14 bis. If you want to run the bot permanently, you need to purchase a VPS or never turn off your computer.

## :computer: Compatibility
Works on Windows 10 with Python 3.9.

  [1]: https://www.python.org/downloads/
  [2]: https://github.com/ElBretzel/discord-guildcopy/releases
  [3]: https://discord.com/developers/applications
