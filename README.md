slack-pixiv-bot
==================
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

A Slack bot to post new works by following users.

## Requirements

- Python >= 3.4
- requests == 2.11.1 (pip)
- PixivPy == 3.1.0 (pip)

## Install

```bash
$ pip install -r requirements.txt
```

## Usage example
Post new works to slack per 60s.

```bash
$ export PIXIV_BOT_SLACK_INCOMING_HOOK_URL=<slack incoming webhook url here>
$ export PIXIV_BOT_USERNAME=<pixiv username here>
$ export PIXIV_BOT_PASSWORD=<base64 encoded pixiv password here>
$ python bot.py 60
```
