# IServ Exercise Notify Discord Bot  v.0.1.1

This is a discord bot, that posts exercises from IServ into a designated channel.
This was done with [this](https://github.com/RedstoneMedia/auto-iserv) library.

# Selling points
This bot can serve as a backup when IServ is down again but its main use is to notify you and others of the newest exercises.
This bot is recomended if you already have or plan to have a class discord server.

# Notice
This can only post the exercises of the user you provide when you create the credential.
This is due to technical limitations

# Contributing
You can make pull requests and I will look at them.

# Setup
1. Clone this repo
2. Run `pip3 install -r requirements.txt`
3. Create a credential file with `gen-iserv-credential`
4. Add the encryption password to the config.json (Don't accidently push this)
5. Add your IServ url to the config.json Something like this : `https://your-shoolname-here.de/iserv`
6. Add your discord bot token to to config.json (If you don't know how that works look at [this](https://www.writebots.com/discord-bot-token/))
7. Get the channel ID in which you want the notifications and where you want the old notifications
8. Add those IDs to bot.py


If you don't have geckodriver in path you will need to [download](https://github.com/mozilla/geckodriver/releases) it and add it to path or place it in this directory.

Then just run `python main.py` and your hopefully good.
