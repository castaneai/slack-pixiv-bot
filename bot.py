# -*- coding: utf-8 -*-
import os
import sys
import time
import base64
from slacker import Slacker
from pixiv import Pixiv


class LastGotWorkIdMemory:

    def __init__(self, slack: Slacker, channel_id: str):
        self._slack = slack
        self._channel_id = channel_id

    def read(self):
        for m in self._slack.channels.history(self._channel_id, count=10).body["messages"]:
            if len(m["attachments"]) > 0 and "fields" in m["attachments"][0] and len(m["attachments"][0]["fields"]) > 0:
                return int(m["attachments"][0]["fields"][0]["value"])
        return 0


class Bot:

    def __init__(self, slack_api_token: str, slack_channel_name: str, pixiv_username: str, pixiv_password: str):
        self._slack = Slacker(slack_api_token)
        self._slack.auth.test()
        self._slack_channel_id = self._get_channel_id(slack_channel_name.lstrip("#"))
        self._pixiv = Pixiv(username=pixiv_username, password=pixiv_password)
        self._last_got_work_id = LastGotWorkIdMemory(self._slack, self._slack_channel_id)

    def run(self):
        since_work_id = self._last_got_work_id.read()
        new_works = list(self._pixiv.following_works_since(since_work_id, limit=10))
        for work in reversed(new_works):
            print("[{}]{}: {} by {}".format(work["created_time"], work["id"], work["title"], work["user"]["name"]))
            self._post_pixiv_work(work)

    def _get_channel_id(self, channel_name: str):
        channels_dict = {c["name"]: c for c in self._slack.channels.list().body["channels"]}
        if channel_name in channels_dict:
            return channels_dict[channel_name]["id"]
        raise RuntimeError("Slack channel: #{} not found.".format(channel_name))

    def _post_pixiv_work(self, work):
        self._slack.chat.post_message(self._slack_channel_id, "", as_user=True,
                                      attachments=[self._pixiv_work_to_slack_attachment(work)])

    @staticmethod
    def _pixiv_work_to_slack_attachment(work):
        return {
            "fallback": "[pixiv]New following work: {}".format(work["title"]),
            "color": "#4385B7",
            "title": work["title"],
            "title_link": "http://www.pixiv.net/member_illust.php?mode=medium&illust_id={}".format(work["id"]),
            "image_url": work["image_urls"]["px_128x128"],
            "author_name": work["user"]["name"],
            "author_icon": work["user"]["profile_image_urls"]["px_50x50"],
            "text": work["caption"],
            "fields": [{"title": "work_id", "value": work["id"]}],
        }


def run(args):
    slack_api_token = os.environ["PIXIV_BOT_SLACK_API_TOKEN"]
    slack_channel_name = args[0]
    pixiv_username = os.environ["PIXIV_BOT_USERNAME"]
    pixiv_password = base64.b64decode(bytes(os.environ["PIXIV_BOT_PASSWORD"], encoding="utf8"))
    polling_interval_seconds = int(args[1])

    bot = Bot(slack_api_token, slack_channel_name, pixiv_username, pixiv_password)
    while True:
        bot.run()
        time.sleep(polling_interval_seconds)


if __name__ == "__main__":
    try:
        if len(sys.argv) != 3:
            print("Usage: bot.py <slack_channel_name> <polling_interval_seconds>")
            exit()
        run(sys.argv[1:])
    except KeyboardInterrupt:
        pass
    finally:
        print("shutdown...")
