import json
import os

import requests

import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description='')
parser.add_argument('filename', type=argparse.FileType('r'), nargs='?')
parser.add_argument('--numPages', type=int, nargs='?', default=1)
args = parser.parse_args()
if args.filename:
    topic_ids = [int(x) for x in args.filename.readlines()]
else:  # otherwise get latest page from forum
    topic_ids = [int(x['id']) for page in range(1,args.numPages+1) for x in
                 requests.get(f"https://forum.sailfishos.org/c/bug-reports/13.json?page={page}").json()['topic_list']['topics'] ]

print("got %d ids" % len(topic_ids))

summaries = []
base_temp_path = Path("/tmp/sfos-forum-bug-moderation-tool/")
base_temp_path.mkdir(parents=True, exist_ok=True)


def get_cached_closure(url_template, base_temp_path, filenamepattern):
    def inner(param):
        result = None
        topic_temp_path = Path(base_temp_path, filenamepattern % param)
        if os.path.exists(topic_temp_path):
            with open(topic_temp_path, 'r') as f:
                result = json.load(f)
        else:
            url = url_template % param
            print("Getting %s" % url)
            result = requests.get(url).json()
            with open(topic_temp_path, 'w') as f:
                json.dump(result, f)
        return result

    return inner


get_topic = get_cached_closure("https://forum.sailfishos.org/t/%d.json", base_temp_path, "%d.json")
get_likes_of_post = get_cached_closure(
    "https://forum.sailfishos.org/post_action_users.json?id=%d&post_action_type_id=2",
    base_temp_path, "%d-likes.json")

for topic_id in topic_ids:
    topic_temp_path = Path(base_temp_path, "%d.json" % topic_id)
    topic = get_topic(topic_id)
    first_post_id = int(topic['post_stream']["posts"][0]['id'])
    # first_post_likes = get_likes_of_post(first_post_id)
    # likes = [user["id"] for user in first_post_likes["post_action_users"]]
    likes = ["disabled"]

    summaries.append({"title": topic['title'],
                      "id": topic['id'],
                      "reply_count": topic['reply_count'],
                      "last_posted_at": topic['last_posted_at'],
                      "tags": topic['tags'],
                      "url": "https://forum.sailfishos.org/t/%d" % topic_id,
                      "created_at": topic['created_at'],
                      "closed": topic['closed'],
                      "likes": likes,
                      "description": topic['post_stream']['posts'][0]['cooked'][:5000]
                      })

summaries_ordered = sorted(summaries, key=lambda x: x['last_posted_at'])
with open("%s/summary.json" % base_temp_path, 'w') as f:
    json.dump(summaries_ordered, f)
