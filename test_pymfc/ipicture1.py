# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd, app, gdi, shellapi, COM

def run():
    imglist = shellapi.getSysImageList(isSmall=False)
    sysidx = shellapi.shGetFileInfo(u"test.doc", usefileattributes=True, largeicon=True, sysiconindex=True)
    icon = imglist.getIcon(sysidx)


    stream = COM.IStream(buf='')
    stream.seek(0)
    pic = COM.IPicture(icon=icon)
    size = pic.saveAsFile(stream, savememcopy=True)
    
    stream.seek(0)
    f = open("c:\\a.ico", "wb").write(stream.read(size))
    
    f = wnd.FrameWnd()
    f.WNDCLASS_BACKGROUNDCOLOR = 0xffffff
    f.create()

    def paint(msg):
        dc = gdi.PaintDC(msg.wnd)

        dc.setMapMode(himetric=True)

#        pic = COM.IPicture(filename=u"c:\\aaa1.gif")
#        w, h = pic.width, pic.height
#        pic.render(dc, (0, -h, w, 0), (0, 0, w, -h))
#
#        for i in range(100):
#            icon = shellapi.shGetFileInfo(u"test.txt", largeicon=True, usefileattributes=True)
 

        pic = COM.IPicture(icon=icon)
        w2, h2 = pic.width, pic.height
        print w2, h2
        pic.render(dc, (0, -h2, w2, 0), (0, 0, w2, -h2))

        dc.setMapMode(text=True)
        dc.drawIcon((0, 32), icon, size=(32, 32), normal=True)

        dc.endPaint()

    f.msgproc.PAINT = paint
    app.run()

if __name__ == '__main__':
    run()


