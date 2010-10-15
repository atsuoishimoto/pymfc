from pymfc.editor.buffer import Buffer
import pymfc.editor.bufre as bufre
from pymfc.editor.bufre import *

def _toBuffer(s):
    if not isinstance(s, unicode):
        s = unicode(s, "iso-8859-1")
    buf = Buffer()
    buf.ins(0, s)
    return buf
    
def match(pattern, string, flags=0):
    pattern = unicode(pattern)
    string = _toBuffer(string)
    return bufre.match(pattern, string, flags)

def search(pattern, string, flags=0):
    pattern = unicode(pattern)
    string = _toBuffer(string)
    return bufre.search(pattern, string, flags)

def sub(pattern, repl, string, count=0):
    pattern = unicode(pattern)
    repl = unicode(repl)
    string = _toBuffer(string)
    return bufre.sub(pattern, repl, string, count)

def subn(pattern, repl, string, count=0):
    pattern = unicode(pattern)
    repl = unicode(repl)
    string = _toBuffer(string)
    return bufre.subn(pattern, repl, string, count)

def split(pattern, string, maxsplit=0):
    pattern = unicode(pattern)
    string = _toBuffer(string)
    return bufre.split(pattern, string, flags)

def findall(pattern, string, flags=0):
    pattern = unicode(pattern)
    string = _toBuffer(string)
    return bufre.findall(pattern, string, flags)

def finditer(pattern, string, flags=0):
    pattern = unicode(pattern)
    string = _toBuffer(string)
    return bufre.finditer(pattern, string, flags)

class DmyPattern:
    def __init__(self, obj):
        self._obj = obj
    
    def findall(self, string, *args, **kwargs):
        string = _toBuffer(string)
        return self._obj.findall(string, *args, **kwargs)

    def match(self, string, *args, **kwargs):
        string = _toBuffer(string)
        return self._obj.match(string, *args, **kwargs)

    def search(self, string, *args, **kwargs):
        string = _toBuffer(string)
        return self._obj.search(string, *args, **kwargs)

    def scanner(self, s, *args, **kwargs):
        s = _toBuffer(s)
        return self._obj.scanner(s, *args, **kwargs)
        
def compile(pattern, flags=0):
    pattern = unicode(pattern)
    return DmyPattern(bufre.compile(pattern, flags))

def purge():
    "Clear the regular expression cache"
    _cache.clear()
    _cache_repl.clear()

def template(pattern, flags=0):
    "Compile a template pattern, returning a pattern object"
    pattern = unicode(pattern)
    return bufre.template(pattern, flags|T)

def escape(pattern):
    "Escape all non-alphanumeric characters in pattern."
    if not isinstance(pattern, unicode):
        pattern = unicode(pattern, "iso-8859-1")
    return bufre.escape(pattern)

