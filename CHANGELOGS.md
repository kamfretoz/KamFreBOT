# CHANGELOG

## v0.1.9

* Added `uvloop`
* Fixed formatting error in `anime` score section
* Fixed discrepancy in the synopsis section of the `anime` command
* Removed type conversion in weather temperature
* Auto adjust embed color to temperature in `weather` command and added more detailed wind condition
* Added safety mechanism in case the folder for `qrcodes` related command are not available
* Added some new commands
* Removed some useless commands

## v0.1.8

* `snipe` command is now working!
* Fixed Regression in `myanimelist` command
* Updated `README`
* Removed potentially offensive lines from The Truth database
* Switched from `Bot` client to `AutoShardedBot` client
* Few Bugfixes for `MyAnimeList` command
* Bug fixed and new addition
* Attempt a fix in `topic`,`truth`,`dare` commands
* Prettified the output of `myanimelist` and `weather` commands
* Added more information to `weather` commands

## v0.1.7

* Added New `F1` Submodule and commands!
* Added `anime` command along with a few subcommands!
* Added more information to `weather` command
* Added more checks to `sub` command
* Decreased the pingstorm limit from 200 to 100.
* Fixed `morse` command only accepting the first character
* The `stats` command now shows Kernel version as well
* Restructured the data files
* Bug fixes on the `ship` command

## v0.1.6

* Added love meter to ship command
* Added Many new commands like `weather` command!
* Make sure to close session when the request was completed
* Moved from `requests` to `aiohttp`
* The `slowmode` command now uses the same time formatting as `mute` command
* Renamed `SubredditFetcher` module to `Subreddit`
* Many bugfixes

Changes since v0.1.5:

## v0.1.5

Changes since v0.1.4:

* Added more restriction to pingstorm command
* Added paginator to `bans` command and fixed text cut-offs on some of them
* Added more questions to the `topic` command!
* Made the user role viewer colorful!
* Added `discriminator` command
* Fixes the `poll` command where it conflict with the prefix
* Removed `Pokedex` module

## v0.1.4

Changes since v0.1.3:

* Fixed a typo in `README.md`
* Added more commands
* Added aliases to converter commands
* Added more checks to the exception handler
* Start using Libneko's converters for lookup
* Added safety measures to `pingstorm` commands
* Integrated the list of timezones into the time command
* Adjusted the `random.seed()` function
* Adjusted the formatting of `servlist` command
* Removed some unused commands

## v0.1.3

Changes since v0.1.2:

* Added Spongebob's Timecards command
* Added Paginator to commands that require a large amount of output to be displayed
* Added more permission information to `roleinfo` command
* Fixed not found error on `prune` command
* Fixed message not awaited error on `countdown` command
* Fixed `hackban` command not being able to find the requested member
* Small cleanup of moderator embed formatting
* Updated `Emoji` cog with f-strings
* Increased error message log removal delay
* Rearranged the argument order of `prune` command

## v0.1.2

Changes since v0.1.1:

* Added full avatar link to `avatar`, `servericon`, `banner`, and `splash` command
* Added more aliases to the `currentgame` and `whosplaying` command
* Added cool gif to `hack` command
* Added more error messages text
* Cat-ified the error handler messages.
* Unhide the `curse` command
* Formatting adjustments for `stats` command
* Fixed a typo in the streaming status
* Fixed emote not found error in `slowmode` command

## v0.1.1

Changes since v0.1.0:

* Initial Update with new `CHANGELOGS.md` file
* Formatting correction `info` module
* Add configuration of GitHub link for `about` command
* Small fix for `Hackban` command not returning the correct message
* Makes exception delete itself
* More verbose error logs
* You can now configure the playing status
* Auto remove spaces from the `location` arguments of `clock` command
* Added some new commands
* Added shebang for ease of use
  