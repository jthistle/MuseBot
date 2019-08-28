# MuseBot [![Build Status](https://travis-ci.com/jthistle/MuseBot.svg?branch=master)](https://travis-ci.com/jthistle/MuseBot)
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

**help** - get info on how to use MuseBot

## Setup

If you want to run MuseBot, you'll need to do a few things. For webhook config, see [the README](./hooks/README.md).

You'll probably need to change some values in `lib/config.py`. To do this, place any changes in `lib/production.py`. This will not be tracked in git, unlike `config.py`.

The values you'll need to specify in `production.py` are:

```python
# You probably won't have access to the original MuseBot if you're setting this up. Create a new bot on Telegram
# and set the username here.
USERNAME = "username_goes_here"

# This will need to be changed. Also make sure you update the value in the webhooks config.
WEBHOOKS_DIR = "/your/directory/name/here/"
```

You may also want to change some of the debug settings; see `config.py` to see what you can change.

Two other things that will need to be changed are `run.sh` and `daemon.sh`. The constant `SRC_LOCATION` should be updated in both files to look a bit like:

```bash
SRC_LOCATION="/your/directory/name/here/"
```

If you've set everything up correctly, you should be able to copy `daemon.sh` to `/etc/init.d/` and set it up:

```bash
sudo cp daemon.sh /etc/init.d/musebot
sudo chown root:root /etc/init.d/musebot
sudo update-rc.d musebot defaults
sudo update-rc.d musebot enable
```

Then, all you need is:

```bash
sudo service musebot start
```

and you're up and running!
