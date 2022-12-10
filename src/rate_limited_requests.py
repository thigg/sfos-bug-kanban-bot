import datetime
import time
from threading import Lock
from typing import Optional

import requests
from requests import Response

wait_until: datetime.datetime = datetime.datetime.now()
wait_until_write_lock: Lock = Lock()
request_session = requests.Session()


def do_rate_limited_request(url, agent: str = 'github.com/thigg/sfos-bug-kanban-bot'):
    """
    totally cool feature that limits the amount of requests when the server complains about the rate limit
    if this is annoying, simply remove the multiprocessing part and you can use requests.get (maybe with a session)
    :param url:url to load
    :return: the http response
    """
    global wait_until_lock, wait_until
    response: Optional[Response] = None
    for i in range(10):
        now = datetime.datetime.now()
        if wait_until > now: #if any thread saw a 429, wait without trying
            seconds: float = (wait_until - now).total_seconds()
            if seconds > 0:
                print(f"sleeping {seconds} +1 seconds until {wait_until} due to rate limiting (now: {datetime.datetime.now()})" , url)
                time.sleep(seconds + 1)
                if wait_until > datetime.datetime.now():
                    print("wait_until moved, retrying... ", url)
                    continue # retry if wait until moved
        response = request_session.get(url, headers={
            'User-agent': agent})
        if response.status_code == 429:  # handle rate limiting naivly, as no really cool solutions are available
            retry_after = int(response.headers['Retry-After'])
            our_wait_until = datetime.datetime.now() + datetime.timedelta(seconds=retry_after)
            with wait_until_write_lock:
                if wait_until < our_wait_until:
                    wait_until = our_wait_until
            print(f"need to slow down (try-counter {i}), server is complaining with status 429. waiting until: {wait_until} seconds (ours: {our_wait_until})")
            continue
        elif response.status_code != 200:
            print("got unexpected status code: ", response)
        else:
            break
    if not response:
        raise ValueError("Could not get item " + url)
    return response
