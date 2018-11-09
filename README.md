# MuseBot
A bot for the MuseScore Developers Telegram chat: https://t.me/musescoreeditorchat

## Features
Responds to any message with a number in the format `#xxxxxx`.
If an issue is found with that number, it will be linked, if not then the relevant PR, if any, will be linked.
Force the bot to link a PR by referencing a PR number as `pr#xxxx`.

### Commands

**mute** - this command will stop the bot from responding to messages from the user
that invokes it.

**unmute** - this command will allow the bot to respond to messages from the user
that invokes it, if it had been previously muted.

**delete** - if the last message was from the bot, it will be deleted

**integrate** - integrate PR and push notification messages into a chat

**unintegrate** - remove an integration in this chat
