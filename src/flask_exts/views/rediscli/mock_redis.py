import random
import re
from collections import defaultdict


class MockRedis:
    """Imitate a Redis object so tests can run without needing a real Redis server.
    This is not a complete implementation of Redis commands.
    https://pypi.org/project/fakeredis/ could be used instead, but it seems overkill for our simple needs.
    """

    # The 'Redis' store
    redis = defaultdict(dict)
    # The pipeline
    pipe = None

    def __init__(self):
        """Initialize the object."""
        pass

    def type(self, key):
        _type = type(self.redis[key])
        if _type == dict:
            return "hash"
        elif _type == str:
            return "string"
        elif _type == set:
            return "set"
        elif _type == list:
            return "list"
        return None

    def ping(self):
        """Emulate ping."""
        return True

    def set(self, key, value):
        """Emulate set."""

        self.redis[key] = value
        return True

    def get(self, key):
        """Emulate get."""

        result = "" if key not in self.redis else self.redis[key]
        return result

    def keys(self, pattern):
        """Emulate keys."""

        # Make a regex out of pattern. The only special matching character we look for is '*'
        regex = "^" + pattern.replace("*", ".*") + "$"

        # Find every key that matches the pattern
        result = [key for key in self.redis.keys() if re.match(regex, key)]

        return result

    def delete(self, key):
        """Emulate delete."""

        if key in self.redis:
            del self.redis[key]

    def exists(self, key):
        """Emulate exists."""

        return key in self.redis

    def hget(self, hashkey, attribute):
        """Emulate hget."""

        # Return '' if the attribute does not exist
        result = (
            self.redis[hashkey][attribute] if attribute in self.redis[hashkey] else ""
        )
        return result

    def hgetall(self, hashkey):
        """Emulate hgetall."""

        return self.redis[hashkey]

    def hlen(self, hashkey):
        """Emulate hlen."""

        return len(self.redis[hashkey])

    def hmset(self, hashkey, value):
        """Emulate hmset."""

        # Iterate over every key:value in the value argument.
        for attributekey, attributevalue in value.items():
            self.redis[hashkey][attributekey] = attributevalue

    def hset(self, hashkey, attribute, value):
        """Emulate hset."""

        self.redis[hashkey][attribute] = value

    def lrange(self, key, start, stop):
        """Emulate lrange."""

        # Does the set at this key already exist?
        if key in self.redis:
            # Yes, add this to the list
            return self.redis[key][start : stop + 1]
        else:
            # No, override the defaultdict's default and create the list
            self.redis[key] = list([])

    def rpush(self, key, *args):
        """Emulate rpush."""

        # Does the set at this key already exist?
        if not key in self.redis:
            self.redis[key] = list([])
        for arg in args:
            self.redis[key].append(arg)

    def sadd(self, key, value):
        """Emulate sadd."""

        # Does the set at this key already exist?
        if key in self.redis:
            # Yes, add this to the set
            self.redis[key].add(value)
        else:
            # No, override the defaultdict's default and create the set
            self.redis[key] = set([value])

    def srem(self, key, member):
        """Emulate a srem."""

        self.redis[key].discard(member)
        return self

    def srandmember(self, key):
        """Emulate a srandmember."""
        length = len(self.redis[key])
        rand_index = random.randint(0, length - 1)

        i = 0
        for set_item in self.redis[key]:
            if i == rand_index:
                return set_item

    def smembers(self, key):
        """Emulate smembers."""

        return self.redis[key]

    def flushdb(self):
        self.redis.clear()
