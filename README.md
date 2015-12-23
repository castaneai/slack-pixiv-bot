slack-pixiv-bot
==================
A Slack bot to post new works by following users.

## Requirements

- Python >= 3.4
- PixivPy == 3.1.0 (pip)
- slacker == 0.8.6 (pip)

## Install

```bash
$ pip install -r requirements.txt
```

## Usage

- Post new works to slack channel `#general` per 60s.

```bash
$ export PIXIV_BOT_SLACK_API_TOKEN=<slack api token here>
$ export PIXIV_BOT_USERNAME=<pixiv username here>
$ export PIXIV_BOT_PASSWORD=<base64 encoded pixiv password here>
$ python bot.py general 60
```