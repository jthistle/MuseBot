# MuseBot
A bot for the MuseScore Developers Telegram chat: https://t.me/musescoreeditorchat

## Features
Responds to any message with a number in the format `#xxxxxx`.
If it is low enough, the relevant pull request will be linked, if it is higher
then the relevant musescore.org node will be linked.

### Commands

**mute** - this command will stop the bot from responding to messages from the user
that invokes it.

**unmute** - this command will allow the bot to respond to messages from the user
that invokes it, if it had been previously muted.
