import math


def prod(it):
    p = 1
    for v in it:
        p *= v
    return p


def is_ascending(it):
    last = None
    for v in it:
        if last is not None and v <= last:
            return False
        last = v
    return True


def argmin(iter) -> int:
    minV = None
    minI = -1
    for i, v in enumerate(iter):
        if minV is None or v < minV:
            minI = i
            minV = v
    return minI


def dist(xy1, xy2):
    (x1, y1) = xy1
    (x2, y2) = xy2
    return math.sqrt((x2 - x1)**2 + (y2-y1)**2)
