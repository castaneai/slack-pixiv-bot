# -*- coding: utf-8 -*-
import os
from slacker import Slacker
from pixivpy3 import PixivAPI

PIXIV_COLOR_HEX = "#4385B7"


def pixiv_get_following_works(pixiv: PixivAPI, start_timestamp=None):
    page = 1
    while True:
        result = pixiv.me_following_works(page=page)
        if "response" not in result:
            break
        page += 1
        yield from result["response"]


def pixiv_work_filter(work):
    return work["age_limit"] != ["r18"]


def pixiv_work_to_slack_attachment(work):
    return {
        "fallback": "[pixiv]New following user works.",
        "color": PIXIV_COLOR_HEX,
        "title": work["title"],
        "title_link": "http://www.pixiv.net/member_illust.php?mode=medium&illust_id={}".format(work["id"]),
        "image_url": work["image_urls"]["px_128x128"],
        "author_name": work["user"]["name"],
        "author_icon": work["user"]["profile_image_urls"]["px_50x50"],
        "text": work["caption"],
    }


def post_to_slack(channel, work_attachment):
    slack = Slacker("<token>")
    slack.chat.post_message(channel, "", as_user=True, attachments=[work_attachment])

if __name__ == "__main__":
    # slack = Slacker(os.environ["PIXIV_BOT_SLACK_API_TOKEN"])
    pixiv = PixivAPI()
    pixiv.login(os.environ["PIXIV_BOT_USERNAME"], os.environ["PIXIV_BOT_PASSWORD"])

    w = next(pixiv_get_following_works(pixiv))
    print(w)
