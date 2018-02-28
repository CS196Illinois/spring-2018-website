from collections import deque
from datetime import datetime
from enum import Enum
import itertools

class Privilege(Enum):
    STUDENT    = 1
    STAFF      = 2


class Message():
    def __init__(self, text, sender=None, time=datetime.now(), privilege=Privilege.STUDENT):
        self.text = text
        self.time = time
        self.privilege = privilege
        self.sender = sender

    def parse(self):
        priv_val = 1 if self.privilege == Privilege.STUDENT else 2
        return {"text": self.text,
                "time": self.time,
                "privilege": priv_val}


class FeedManager():
    def __init__(self, feed_size):
        self.feed_size = feed_size
        self.feed = deque([], maxlen=feed_size)

    def post(self, text, sender=None time=datetime.now(), privilege=Privilege.STUDENT):
        #TODO: filter content
        message = Message(text, time, privilege)
        self.feed.append(message)

    def get_feed(self, size=None):
        if size is None:
            size = len(self.feed)
        else:
            size = min(size, len(self.feed))

        return [self.feed[idx].parse() for idx in range(size)]

if __name__ == "__main__":
    feed = FeedManager(3)
    for i in range(50):
        feed.post("message #{}".format(i))
    print(feed.get_feed())
