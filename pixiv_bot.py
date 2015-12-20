# -*- coding: utf-8 -*-
import os
import time
from slacker import Slacker
from pixivpy3 import PixivAPI

PIXIV_COLOR_HEX = "#4385B7"
LAST_GOT_WORK_ID_FILENAME = "last_got_work_id"


def pixiv_get_following_works(pixiv: PixivAPI):
    """
    pixivのお気に入りユーザー新着作品を1つずつ返すジェネレータ
    無限ジェネレータなのでfor, listなどで全要素取得をしないように!!
    :param pixiv:
    :return:
    """
    page = 1
    while True:
        result = pixiv.me_following_works(page=page)
        if "response" not in result:
            break
        page += 1
        yield from result["response"]


def pixiv_get_following_works_since(pixiv: PixivAPI, since_work_id: int =0, get_limit_count:int =60):
    for i, new_work in enumerate(pixiv_get_following_works(pixiv)):
        if new_work["id"] <= since_work_id or i + 1 > get_limit_count:
            break
        yield new_work


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


def get_last_got_work_id():
    if os.path.exists(LAST_GOT_WORK_ID_FILENAME):
        with open(LAST_GOT_WORK_ID_FILENAME, "r") as f:
            return int(f.read())
    else:
        return 0


def set_last_got_work_id(val: int):
    with open(LAST_GOT_WORK_ID_FILENAME, "w") as f:
        f.write(str(val))


def post_to_slack(slack, channel, work_attachment):
    slack.chat.post_message(channel, "", as_user=True, attachments=[work_attachment])

if __name__ == "__main__":
    try:
        pixiv = PixivAPI()
        pixiv.login(os.environ["PIXIV_BOT_USERNAME"], os.environ["PIXIV_BOT_PASSWORD"])
        print("pixin auth success")
        slack = Slacker(os.environ["PIXIV_BOT_SLACK_API_TOKEN"])
        slack.auth.test()
        print("slack auth success")

        while True:
            last = get_last_got_work_id()
            new_works = list(reversed(list(pixiv_get_following_works_since(pixiv, last))))
            if new_works is not None and len(new_works) > 0:
                set_last_got_work_id(new_works[-1]["id"])
                for i, work in enumerate(new_works):
                    print("[{}]{}: {} by {}".format(work["created_time"], work["id"], work["title"], work["user"]["name"]))
                    post_to_slack(slack, "#pixiv_test", pixiv_work_to_slack_attachment(work))
            time.sleep(60)
    except KeyboardInterrupt:
        pass
    finally:
        print("shutdown...")
