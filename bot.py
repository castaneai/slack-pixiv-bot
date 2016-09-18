# -*- coding: utf-8 -*-
import os
import sys
import time
import base64
import itertools
import requests
import pixivpy3


class Bot:

    def __init__(self, slack_incoming_hook_url, pixiv_username, pixiv_password, polling_seconds):
        self._slack_incoming_hook_url = slack_incoming_hook_url
        self._pixiv_api = pixivpy3.PixivAPI()
        self._pixiv_api.login(pixiv_username, pixiv_password)
        self._polling_seconds = polling_seconds
        self._last_fetched_post_id = 0

    def run_forever(self):
        self._last_fetched_post_id = self.fetch_least_post_id()
        while True:
            new_posts = self.fetch_new_posts()
            self.notify_posts_to_slack(new_posts)
            time.sleep(self._polling_seconds)

    def fetch_least_post_id(self):
        """
        最新の投稿のIDを取得
        このIDより新しいものを次の取得時の新着投稿とする
        """
        api_result = self._pixiv_api.me_following_works(page=1, per_page=1, include_stats=False, include_sanity_level=False)
        if api_result["status"] != "success":
            raise RuntimeError("[pixiv API]me_following_works failed. {0}".format(api_result))
        if len(api_result["response"]) < 1:
            raise RuntimeError("[pixiv API]me_following_works result count 0...")
        return int(api_result["response"][0]["id"])

    def fetch_new_posts(self):
        """
        pixivからフォローしたユーザーの新着投稿一覧を返す
        """
        new_posts = list(itertools.takewhile(self.is_new_post, self.fetch_posts()))
        if len(new_posts) > 0:
            self._last_fetched_post_id = int(new_posts[0]["id"])
        return reversed(new_posts)

    def is_new_post(self, post):
        """
        投稿が新しいものかどうか返す
        """
        return post is not None and post["id"] > 0 and post["id"] != self._last_fetched_post_id

    def fetch_posts(self):
        """
        pixivからフォロー新着の投稿一覧を取得
        """
        api_result = self._pixiv_api.me_following_works(include_stats=False, include_sanity_level=False)
        if api_result["status"] != "success":
            raise RuntimeError("[pixiv API]me_following_works failed. {0}".format(api_result))
        return api_result["response"]

    def notify_posts_to_slack(self, posts):
        """
        pixivの投稿リストをslackに通知する
        """
        for post in posts:
            requests.post(self._slack_incoming_hook_url, json=self.pixiv_post_to_slack_message(post))

    @staticmethod
    def pixiv_post_to_slack_message(post):
        """
        pixivの投稿をSlackのメッセージに変換
        """
        attachment = {
            "fallback": "[pixiv]{}".format(post["title"]),
            "color": "#4385B7",  # pixivカラーの青
            "title": post["title"],
            "title_link": "http://www.pixiv.net/member_illust.php?mode=medium&illust_id={}".format(post["id"]),
            "image_url": post["image_urls"]["px_128x128"],
            "text": "",
        }
        return {
            "username": post["user"]["name"],
            "icon_url": "http://winapp.jp/wp/wp-content/uploads/2012/11/pixiv-icon.png",
            "text": "",
            "attachments": [attachment],
        }


def run(args):
    slack_incoming_hook_url = os.environ["PIXIV_BOT_SLACK_INCOMING_HOOK_URL"]
    pixiv_username = os.environ["PIXIV_BOT_USERNAME"]
    pixiv_password = base64.b64decode(bytes(os.environ["PIXIV_BOT_PASSWORD"], encoding="utf8"))
    polling_seconds = int(args[0])
    bot = Bot(slack_incoming_hook_url, pixiv_username, pixiv_password, polling_seconds)
    bot.run_forever()

if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            print("Usage: bot.py <polling_interval_seconds>")
            exit()
        run(sys.argv[1:])
    except KeyboardInterrupt:
        pass
    finally:
        print("shutdown...")
