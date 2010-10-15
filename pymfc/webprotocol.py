# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import _pymfclib
class _WebProtocol:
    # not thread safe
    
    _webprotocol = None
    
    
    def __init__(self):
        self._urlmap = {}
        
    def registerPassThru(self, protocol, http=0, https=0):
        if not self._webprotocol:
            self._webprotocol = _pymfclib.WebProtocol()
            self._webprotocol.customprotocolfunc(self._urlmapcallback)
        self._webprotocol.register(protocol, http=http, https=https)

    def setPassThruFilter(self, f):
        if not self._webprotocol:
            self._webprotocol = _pymfclib.WebProtocol()
            self._webprotocol.customprotocolfunc(self._urlmapcallback)
        self._webprotocol.filter = f

    def registerCustomProtocol(self, protocol):
        if not self._webprotocol:
            self._webprotocol = _pymfclib.WebProtocol()
            self._webprotocol.customprotocolfunc(self._urlmapcallback)
        self._webprotocol.registerCustomProtocol(protocol)
        
    def setUrlMap(self, url, f):
        if not f:
            del self._urlmap[url]
        else:
            self._urlmap[url] = f

    def _urlmapcallback(self, url):
        if url in self._urlmap:
            return self._urlmap[url](url)
            
_webprotocol = _WebProtocol()

def registerPassThru(protocol, http=False, https=False):
    _webprotocol.registerPassThru(protocol, http=http, https=https)

def setPassThruFilter(f):
    _webprotocol.setPassThruFilter(f)

def registerCustomProtocol(protocol):
    _webprotocol.registerCustomProtocol(protocol)

def setCustomProtocolCallback(url, f):
    _webprotocol.setUrlMap(url, f)

