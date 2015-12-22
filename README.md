slack-pixiv-new-works-bot
==========================

## Requirements

- Python >= 3.4
- pixivpy (pip)
- slacker (pip)

## Usage

- Post new works to slack channel `#general` per 60s.

```bash
$ export PIXIV_BOT_SLACK_API_TOKEN=<slack api token here>
$ export PIXIV_BOT_USERNAME=<pixiv username here>
$ export PIXIV_BOT_PASSWORD=<base64 encoded pixiv password here>
$ python bot.py general 60
```