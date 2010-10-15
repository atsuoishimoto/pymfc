# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import time, cStringIO, re
from pymfc import wnd, app, menu, gdi, webprotocol


def filter(url):
    print url
    if url == u"testtest://www.google.com/":
        return u"http://www.yahoo.com"
    if url == u"https://www.amazon.co.jp/":
        return url
    else:
        return True

def run():
    webprotocol.registerPassThru(u"http", http=True)
    webprotocol.registerPassThru(u"https", https=True)
    webprotocol.setPassThruFilter(filter)
    
    f = wnd.FrameWnd()
    f.create()
    
    global web

    web = wnd.WebCtrl(parent=f, anchor=wnd.Anchor(occupy=True))
    web.create()
#    web.navigate(u"testtest://www.google.com")
    web.navigate(u"https://www.amazon.co.jp")
    app.run()

if __name__ == '__main__':
    run()
