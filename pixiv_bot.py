# -*- coding: utf-8 -*-
from slacker import Slacker
from pixivpy3 import PixivAPI


def post_to_slack(channel, work_attachment):
    slack = Slacker("<token>")
    slack.chat.post_message(channel, "", as_user=True, attachments=[work_attachment])

if __name__ == "__main__":
    pixiv = PixivAPI()
    pixiv.login("<username>", "<password>")
    r = pixiv.me_following_works()
    for work in [w for w in r["response"] if w["age_limit"] != "r18"]:
        attachment = {
            "fallback": "pixiv new following works",
            "color": "good",
            "title": work["title"],
            "title_link": "http://www.pixiv.net/member_illust.php?mode=medium&illust_id={}".format(work["id"]),
            "image_url": work["image_urls"]["px_128x128"],
            "author_name": work["user"]["name"],
            "author_icon": work["user"]["profile_image_urls"]["px_50x50"],
            "text": work["caption"],
        }
        post_to_slack("#pixiv_test", attachment)
