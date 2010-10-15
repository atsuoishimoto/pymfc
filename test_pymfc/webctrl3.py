# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import time, cStringIO, re
from pymfc import wnd, app, menu, gdi, webprotocol


url1 = u"aa:abcdef.com"
url2 = u"aa://abcdef.com.2/aaa.gif"


html = """<html> <body> <img src='%s'> <A href='#today'>link</A> aag<br> aag<br> aag<br> aag<br> aag<br> 
aag<br> aag<br> aag<br> aag<br> aag<br> aag<br> aag<br> aag<br> aag<br> 
aag<br> aag<br> aag<br> aag<br> aag<br> aag<br> aag<br> aag<br> aag<br> 
aag<br> aag<br> aag<br> aag<br> aag<br> aag<br> aag<br> aag<br> aag<br> 
aag<br> aag<br> <A NAME='today'><H2>===============================================</H2>""" % (url2.encode("ascii"),)


def callback(url):
    print "@@@@@@@@@@@@@@@@@@@@@@@", url
    if url == url1:
        return {
            'src':html,
            'mimetype':u'text/html'
        }
#    if url == url2:
#        print 2222222222222222222222222222222222222
#        return {
#            'src':open("c:\\src\\infopile\\src\\a.gif", "rb").read(),
#            'mimetype':u'image/gif'
#        }
#

def run():
    for i in range(1):
        f = wnd.FrameWnd()
        f.create()
        
        global web

        web = wnd.WebCtrl(parent=f, anchor=wnd.Anchor(occupy=True))
        web.create()
        
        web.navigate(url1)
    app.run()

if __name__ == '__main__':
    webprotocol.registerCustomProtocol("aa")
    webprotocol.setCustomProtocolCallback(url1, callback)
    webprotocol.setCustomProtocolCallback(url2, callback)
    run()
