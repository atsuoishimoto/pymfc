# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import time, cStringIO, re
from pymfc import wnd, app, menu, gdi


html = u"""
<html>
<body>
<A href="#today" id=abcdefg><font>link</font></A><br/>
<p href="#aaa" id='abcdef'>Click here</a><br>
abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br>
abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br>abcdefg<br>
abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br>
 abcdefg<br> abcdefg<br> abcdefg<br>abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br>
abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br> abcdefg<br>
<A NAME="today"><H2>===============================================</H2>
</body></html>
"""

def onkeypress(msg):
    print "onkeypress"
    print msg.srcElement
    print msg.srcElement.tagName
    print msg.srcElement.getDocument().getBody().clientRect
    print msg.srcElement.getDocument().getBody().scrollRect

    from pymfc import olecmdid
    print "::::::::", web.execCommand(olecmdid.OLECMDID_SELECTALL)

    return True
    
def onclick(msg):
    print "onclick"
    print msg.srcElement
    print msg.srcElement.tagName, msg.srcElement.elemId
    print msg.srcElement.getDocument().getBody().clientRect
    print msg.srcElement.getDocument().getBody().scrollRect

    print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    p = msg.srcElement
    while p:
        print p.tagName, p.elemId
        p = p.getParent()
        print p
    return True
    
urlset = False

def documentcomplete(url):
    print "documentcomplete:", url
    global doc
    global urlset
    doc = web.getDocument()
    print "+++++++++++++++", doc.URL

    x = doc.getBody()
    print x.events
    doc.events.KeyPress = onkeypress
    doc.events.Click = onclick
    web.getDocument().setHTML(html)

def statuschange(s):
#    print s
    pass
    

def showcontextmenu(msg):
    from pymfc import olecmdid
    print "SHOWCONTEXTMENU", msg.getDict()

    print msg.cmdTarget.queryStatus(olecmdid.OLECMDID_PRINT)
#    print "::::::::", msg.cmdTarget.execCommand(olecmdid.OLECMDID_PRINT)
    return True

def run():
    f = wnd.FrameWnd()
    f.create()
    
    global web

    web = wnd.WebCtrl(parent=f, anchor=wnd.Anchor(occupy=True))
    web.events.DocumentComplete = documentcomplete
    web.events.StatusTextChange = statuschange
    web.events.ShowContextMenu = showcontextmenu
    web.create()
    web.navigate(u"http://www.google.jp")
    app.run()

if __name__ == '__main__':
    run()
del web