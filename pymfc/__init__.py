# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.
import time

f = time.clock()
import _pymfclib
#print "pymfc loaded:", time.clock() - f

#from _pymfclib import PyMFCException, Win32Exception
#from _pymfclib import DropEffect, StgMedium, FormatEtc, OleDropTarget, OleDataSource

from _pymfclib import *

class _KeyMap(object):
    def __init__(self, keydict=_pymfclib._keydict):
        self._keydict = keydict

    def __getattr__(self, name):
        return self._keydict[name]

KEY=_KeyMap()

class _MainWindows:
    def __init__(self):
        self._wnds = set()
    
    def add(self, w):
        assert w not in self._wnds
        def closed(msg):
            self._wnds.remove(w)
            if app.AUTOQUIT and not self._wnds:
                app.quit(0)

        w.msglistener.NCDESTROY = closed
        self._wnds.add(w)

    def contains(self, w):
        return w in self._wnds
        
class App(_pymfclib.App):
    _mainwnds = _MainWindows()
    AUTOQUIT = True

    @classmethod
    def addMainWindow(cls, w):
        cls._mainwnds.add(w)

    @classmethod
    def isMainWindow(cls, w):
        return cls._mainwnds.contains(w)
        
    @classmethod
    def iterWnds(cls):
        wnds = [w for w in cls._mainwnds._wnds]
        for w in wnds:
            yield w
    
    
app = App()
metric = _pymfclib.SystemMetrics()
syscolor = _pymfclib.SysColor()

