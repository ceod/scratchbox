import datetime
import pickle
from typing import Optional, List, Dict

RESULT = {
    'objects': 0,
    'bytes': 0
}


class Tag(object):
    GEEK = 1
    VIP = 2


class User(object):

    oid: int
    name: str
    authid: str
    email: str
    birthday: datetime.date
    is_friendly: bool
    tags: Optional[List[str]]
    ratings: Dict[str, float] = {}
    friends: List[int] = []
    referred_by: int = None


def test():
    global RESULT

    user = User()
    user.oid = 23
    user.name = 'Homer Simpson'
    user.authid = 'homer'
    user.email = 'homer.simpson@example.com'

    user.birthday = datetime.date(1950, 12, 24)
    user.is_friendly = True
    user.tags = [Tag.GEEK, Tag.VIP]

    data = pickle.dumps(user, protocol=4)

    RESULT['objects'] += 1
    RESULT['bytes'] += len(data)


import timeit

N = 1000
M = 1000000

for i in range(N):
    secs = timeit.timeit(test, number=M)
    ops = round(float(M) / secs, 1)
    print('{} objects/sec'.format(ops))
    print(RESULT)
