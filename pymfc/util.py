# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import sys, threading
from math import sqrt

class IdPool:
    def __init__(self, start, end):
        self.start = self.cur = start
        self.end = end
        self.pool = []

    def __del__(self):
        pass
        
    def get(self):
        if self.pool:
            return self.pool.pop()
        if self.cur == self.end:
            raise ValueError, "No more id available"
        ret = self.cur
        self.cur += 1
        return ret

    def release(self, v):
        assert v not in self.pool
        assert self.start <= v < self.cur
        self.pool.append(v)

def RGB(r,g,b):
    return b*256*256 + g*256 + r


def normalizeRect(rc):
    l, t, r, b = rc
    return (min(l, r), min(t, b), max(l, r), max(t, b))
    
def rectIntersection(rc1, rc2, normalized=False):
    # Normalize rect
    if not normalized:
        l, t, r, b = rc1
        rc1 = (min(l, r), min(t, b), max(l, r), max(t, b))
        
        l, t, r, b = rc2
        rc2 = (min(l, r), min(t, b), max(l, r), max(t, b))
    
    if ((rc1[0] < rc2[2]) and (rc2[0] < rc1[2]) 
        and (rc1[1] < rc2[3]) and (rc2[1] < rc1[3])):

        l = max(rc1[0], rc2[0])
        t = max(rc1[1], rc2[1])
        r = min(rc1[2], rc2[2])
        b = min(rc1[3], rc2[3])
        return l, t,r, b
    else:
        return ()

def rectUnion(rects):
    l = t = sys.maxint
    r = b = sys.maxint*-1
    for rc in rects:
        l = min(rc[0], l)
        t = min(rc[1], t)
        r = max(rc[2], r)
        b = max(rc[3], b)
    return (l, t, r, b)
    
def ptInRect(pt, rc):
    x, y = pt

    # Normalize rect
    l, t, r, b = rc
    l, t, r, b = (min(l, r), min(t, b), max(l, r), max(t, b))
    
    if (l <= x < r) and (t <= y < b):
        return True
    else:
        return False

def ptOnLine(pos, posFrom, posTo, width):
    if posFrom < posTo:
        f = posFrom
        t = posTo
    else:
        f = posTo
        t = posFrom

    if f[1] < t[1]:
        lo_y = f[1]
        hi_y = t[1]
    else:
        lo_y = t[1]
        hi_y = f[1]
    
    w = float(width) / 2

    if not (lo_y-w <= pos[1] < hi_y+w):
        return False

    if not (f[0]-w <= pos[0] < t[0]+w):
        return False

    dx = float(t[0] - f[0])
    dy = float(t[1] - f[1])

    if not dx:
        return (f[0] - w <= pos[0] < t[0] + w)

    d = dy/dx
    k = sqrt(1.0/(1.0+d**2))

    y = d*(pos[0] - f[0]) + f[1]
    p = k * (y - pos[1])
    
    return abs(p) < w

def isEmptyRect(rc):
    if rc[0] == rc[2]:
        return True
    if rc[1] == rc[3]:
        return True
    return False


# http://www.ibm.com/developerworks/java/library/j-j2d/

def _getComplement(colorVal):
     diff = -colorVal if colorVal >= 128 else 255 - colorVal
#     diff = int(diff / 2.0)
     return colorVal + diff
     
     
def RGBComplement(color):
    r = color & 0xff
    r = _getComplement(r)
    g = (color >> 8) & 0xff
    g = _getComplement(g)
    b = (color >> 16) & 0xff
    b = _getComplement(b)

    return ((b << 16) & 0xff0000) | ((g << 8) & 0xff00) | (r & 0xff)


def synchronized(func):
    def f(*args, **kwargs):
        func.__pymfc_decolators_synchronized.acquire(True)
        try:
            return func(*args, **kwargs)
        finally:
            func.__pymfc_decolators_synchronized.release()
    func.__pymfc_decolators_synchronized = threading.RLock()
    return f
