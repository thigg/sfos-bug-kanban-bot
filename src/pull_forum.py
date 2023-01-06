import argparse
import itertools
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Callable, Any, Iterator

import requests

from rate_limited_requests import do_rate_limited_request

class ForumPuller:

    get_topic: Callable[[str], Any]
    base_temp_path: Path
    rate_limited_until: int = 0

    def __init__(self) -> None:
        super().__init__()
        self.base_temp_path = Path("/tmp/sfos-forum-bug-moderation-tool/")
        self.base_temp_path.mkdir(parents=True, exist_ok=True)
        self.get_topic = self.get_cached_closure("https://forum.sailfishos.org/t/%d.json", self.base_temp_path, "%d.json")
        # self.get_likes_of_post = self.get_cached_closure(
        #     "https://forum.sailfishos.org/post_action_users.json?id=%d&post_action_type_id=2",
        #     base_temp_path, "%d-likes.json")

    def get_cached_closure(self, url_template: str, base_temp_path: Path, filenamepattern: str) -> Callable[[str], Any]:
        def inner(param: str):
            result: Any
            topic_temp_path = Path(base_temp_path, filenamepattern % param)
            if os.path.exists(topic_temp_path):
                with open(topic_temp_path, 'r') as f:
                    result = json.load(f)
            else:
                url = url_template % param
                print("Getting %s" % url)
                response = do_rate_limited_request(url)
                try:
                    result = response.json()
                except:
                    logging.exception(f"could not parse to json {url} got response {response}")
                    raise
                with open(topic_temp_path, 'w') as f:
                    json.dump(result, f)
            return result

        return inner





    def get_topic_summary(self, topic_id):
        topic = self.get_topic(topic_id)
        # not collecting likes
        # first_post_id = int(topic['post_stream']["posts"][0]['id'])
        # first_post_likes = get_likes_of_post(first_post_id)
        # likes = [user["id"] for user in first_post_likes["post_action_users"]]
        likes = ["disabled"]
        return {"title": topic['title'],
                          "id": topic['id'],
                          "reply_count": topic['reply_count'],
                          "last_posted_at": topic['last_posted_at'],
                          "tags": topic['tags'],
                          "url": "https://forum.sailfishos.org/t/%d" % topic_id,
                          "created_at": topic['created_at'],
                          "closed": topic['closed'],
                          "likes": likes,
                          "description": topic['post_stream']['posts'][0]['cooked'][:5000]
                          }

    def write_summary(self, topic_ids: List[int]):
        summaries: List[dict]

        # parallelize with threads. The GIL is no problem here, as we're mainly IO bound.
        with ThreadPoolExecutor() as executor:
            summaries = list(executor.map(self.get_topic_summary, topic_ids))

        summaries_ordered = sorted(summaries, key=lambda x: x['last_posted_at'])
        with open("%s/summary.json" % self.base_temp_path, 'w') as f:
            json.dump(summaries_ordered, f)

def get_topic_ids_from_category_page(page:int) -> List[int]:
    print(f"requesting page {page}")
    ids = [int(x['id']) for x in requests.get(f"https://forum.sailfishos.org/c/bug-reports/13.json?page={page}").json()[
        'topic_list']['topics']]
    print(f"found {len(ids)} on page {page}")
    return ids

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('filename', type=argparse.FileType('r'), nargs='?')
    parser.add_argument('--numPages', type=int, nargs='?', default=1)
    args = parser.parse_args()
    if args.filename:
        topic_ids = [int(x) for x in args.filename.readlines()]
    else:  # otherwise get the latest page from forum
        with ThreadPoolExecutor() as executor:
            topic_ids = list(itertools.chain(*executor.map(get_topic_ids_from_category_page,range(0, args.numPages))))

    print("got %d ids" % len(topic_ids))
    ForumPuller().write_summary(topic_ids)


