# KamFreBOT Discord Bot

## A simple Discord bot made by me for some of my private Discord servers

This Frankenstein abomination of a bot is something i have made few years ago.
Feel free to explore it by yourself
**Warning: TERRIBLE CODE AHEAD**
You have been warned.

![Bootup Screen](/screenshot/splash_bootup.gif)

## Installation

* Clone this Repo `$ git clone https://github.com/kamfretoz/KamFreBOT`
* Navigate to the desired directory
* Install the required dependencies with `python3 -m pip install -r requirements.txt`
* Fill in the Token and The YT API Key
* Run the bot with `./run.sh` or `./run.bat` according to your prerferred operating system.
* Enjoy the abomination 😂

## Customization

> All configuration files has been moved to `/data` folder
> For configuration, see `config.py` file.

* This Bot has a custom boot/loading screen
Feel free to use it for whatever you like (I recommend to use it as an MOTD or something.)
To customize the bootup logo, edit the `bootup_logo.txt` to your liking.
  
* The bot also has a customizeable Error message quotes
Go to `quotes.py` to customize the error message quotes.

* You can customize the Error Logging channel
Open up `config.py` and put your desired channel ID on `home` variable

## Token, Key and Stuff

You will need to provide your own Token.
Put the token on `coin.json` file
And your YouTube API v3 Key on `/cogs/core/config.py`
Also add your own OpenWeather API v3 Key to `/cogs/data/weather_api_key.json`

## Credit

Feel free to take any code you like! i don't mind :D
I've tried to put the credit as much as i can on the code. If i'm missing anyone, let me know!

* [Pycord](https://github.com/Pycord-Development/pycord)
* [Libneko](https://gitlab.com/Tmpod/libneko)
Many thanks to Discord Coding Academy (<https://discord.gg/dca>) server for helping with errors and troubleshooting!
  
## APIs used

* [KSoft.si](https://ksoft.si/)
* [TheCatAPI](https://www.thecatapi.com/)
* [TheDogAPI](https://thedogapi.com/)
* [Cat Facts](https://cat-fact.herokuapp.com/)
* [Random Fox](https://randomfox.ca/)
* [Shibe.online](https://shibe.online/)
* [Advices Slip](https://adviceslip.com/)
* [Programming Quotes](https://programming-quotes-api.herokuapp.com/)
* [QuoteGarden](https://pprathameshmore.github.io/QuoteGarden/)
* [icanhazdadjoke](https://icanhazdadjoke.com/)
* [Chuck Norris API](https://api.chucknorris.io/)
* [Kanye REST](https://kanye.rest/)
* [XKCD](https://xkcd.com/)
* [Jikan (MyAnimeList)](https://jikan.docs.apiary.io/#introduction/information)
* [Ergast F1 API](https://ergast.com/mrd/)
* [ipapi](https://ipapi.co/)
* [OpenWeatherMap](https://openweathermap.org/api)
* [Nationalize.io](https://nationalize.io/)
* [Rule34 API](https://github.com/kurozenzen/r34-json-api)
* [Neko's Life API](https://nekos.life/)

## Modules used

* [Vaporwavely](https://github.com/Owanesh/vaporwavely)
* [Owoify](https://github.com/crinny/owoify)

[![Built with libneko](https://img.shields.io/badge/built%20with-libneko-ff69b4.svg)](https://gitlab.com/koyagami/libneko)
