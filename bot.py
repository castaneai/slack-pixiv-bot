# -*- coding: utf-8 -*-
import os
import sys
import time
import base64
from slacker import Slacker
from pixiv import Pixiv


class LastGotWorkIdMemory:
    FILENAME = "last_got_work_id"

    def read(self):
        if os.path.exists(self.FILENAME):
            with open(self.FILENAME, "r") as f:
                return int(f.read())
        else:
            return 0

    def write(self, last_got_work_id):
        with open(self.FILENAME, "w") as f:
            f.write(str(last_got_work_id))


def pixiv_work_to_slack_attachment(work):
    return {
        "fallback": "[pixiv]New following work: {}".format(work["title"]),
        "color": "#4385B7",
        "title": work["title"],
        "title_link": "http://www.pixiv.net/member_illust.php?mode=medium&illust_id={}".format(work["id"]),
        "image_url": work["image_urls"]["px_128x128"],
        "author_name": work["user"]["name"],
        "author_icon": work["user"]["profile_image_urls"]["px_50x50"],
        "text": work["caption"],
    }


def post_to_slack(slack, channel, pixiv_work):
    slack.chat.post_message(channel, "", as_user=True, attachments=[pixiv_work_to_slack_attachment(pixiv_work)])


def run(slack_channel, polling_interval):
    username = bytes(os.environ["PIXIV_BOT_USERNAME"], encoding="utf8")
    password = base64.b64decode(bytes(os.environ["PIXIV_BOT_PASSWORD"], encoding="utf8"))
    pixiv = Pixiv(username=username, password=password)
    slack = Slacker(os.environ["PIXIV_BOT_SLACK_API_TOKEN"])
    slack.auth.test()
    last_got_work_id = LastGotWorkIdMemory()
    while True:
        new_works = list(pixiv.following_works_since(last_got_work_id.read(), limit=5))
        for work in reversed(new_works):
            print("[{}]{}: {} by {}".format(work["created_time"], work["id"], work["title"], work["user"]["name"]))
            post_to_slack(slack, slack_channel, work)
            last_got_work_id.write(work["id"])
        time.sleep(polling_interval)


if __name__ == "__main__":
    try:
        if len(sys.argv) != 3:
            print("Usage: bot.py <slack_channel_name> <polling_interval_seconds>")
            exit()
        slack_channel_name = "#" + sys.argv[1]
        polling_interval_seconds = int(sys.argv[2])
        run(slack_channel_name, polling_interval_seconds)
    except KeyboardInterrupt:
        pass
    finally:
        print("shutdown...")
