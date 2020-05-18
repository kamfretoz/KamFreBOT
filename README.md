# KamFreBOT Discord Bot

## A simple Discord bot made by me for some of my private Discord servers

This is Frankenstein abomination of a bot i have made few years ago. The result of accumulation of me copying some codes from another GitHub repo (only some, not the entire repo)
Feel free to explore it by yourself

![Bootup Screen](/screenshot/bootup.png)

## Installation

* Clone this Repo `$ git clone https://github.com/kamfretoz/KamFreBOT`
* Navigate to the desired directory
* Install the required dependencies with `python3 -m pip install -r requirements.txt`
* Fill in the Token and The YT API Key
* Run the bot with `./run.sh` or `./run.bat` according to your prerferred operating sytem.
* Enjoy the abomination 😂

## Customization

For configuration, see `config.py` file.

* This Bot has a custom boot/loading screen, Feel free to use it for whatever you like (I recommend to use it as an MOTD or something.)
* The bot also has a customizeable Error message quotes
* There also a meme command. You can put your own memes on `/memes/` folder and use the meme command to send it randomly.

* To customize the bootup logo, edit the `bootup_logo.txt` to your liking.
* Go to `quotes.py` to customize the error message quotes.

## Token, Key and Stuff

You will need to provide your own Token.
Put the token on `coin.js` file
And your YouTube API v3 Key on `/cogs/core/config.py`

## Libraries used

* Discord.py
* Libneko

## Credit

I've tried to put the credit as much as i can on the code. If i'm missing anyone, let me know!

* Discord.py [https://github.com/Rapptz/discord.py]
* Libneko    [https://gitlab.com/koyagami/libneko/tree/master/]

[![Built with libneko](https://img.shields.io/badge/built%20with-libneko-ff69b4.svg)](https://gitlab.com/koyagami/libneko)
