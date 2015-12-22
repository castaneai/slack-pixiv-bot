import itertools
import pixivpy3

DEFAULT_GET_LIMIT = 50


def _take_until(generator, predicate):
    for val in generator:
        if predicate(val):
            break
        yield val


def _take_limit(generator, limit):
    count = 0
    for val in generator:
        if count >= limit:
            break
        count += 1
        yield val


class Pixiv:
    def __init__(self, username=None, password=None):
        self._api = pixivpy3.PixivAPI()
        self._api.login(username, password)

    def following_works(self):
        for page in itertools.count(start=1):
            result = self._api.me_following_works(page=page)
            if result["status"] != "success":
                raise RuntimeError("API: me_following_works failed.")
            yield from result["response"]

    def following_works_since(self, since_work_id, limit=DEFAULT_GET_LIMIT):
        yield from _take_limit(
            _take_until(self.following_works(), lambda w: w["id"] <= since_work_id),
            limit)


if __name__ == "__main__":
    assert [0, 1, 2, 3] == list(_take_until(range(10), lambda i: i > 3))
    assert [0, 1, 2, 3] == list(_take_limit(range(10), 4))
    assert [0, 1] == list(_take_limit(range(2), 4))
