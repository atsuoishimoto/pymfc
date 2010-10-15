# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import app, wnd, gdi, shellapi

imglist = shellapi.getSysImageList(isSmall=False)
sysidx = shellapi.shGetFileInfo(u"test.doc", usefileattributes=True, largeicon=True, sysiconindex=True)
icon = imglist.getIcon(sysidx)

bmp = icon.getBitmap()
dib = bmp.createDIB()

icons = [
    gdi.Icon(filename=u"pymfc\\test_pymfc\\icon_32_32_4.ico"),
    gdi.Icon(filename=u"pymfc\\test_pymfc\\icon_32_32_8.ico"),
    gdi.Icon(filename=u"pymfc\\test_pymfc\\icon_32_32_24.ico")
]

dibs = [i.getBitmap().createDIB() for i in icons]
masks = [i.getMaskBitmap().createDIB() for i in icons]


def paint(msg):
    dc = gdi.PaintDC(msg.wnd)
    dc.drawIcon((0, 0), icon, size=(32, 32), normal=True)
    dc.drawDIB((0,64), dib, (32, 32), (0,0), (0, 32))

    for n, d in enumerate(dibs):
        dc.drawDIB((64, 32*n), d, (32, 32), (0,0), (0, 32))
        print d.compression, d.bitcount

    for n, d in enumerate(masks):
        dc.drawDIB((96, 32*n), d, (32, 32), (0,0), (0, 32))
        print d.compression, d.bitcount


    dc.endPaint()

def run():
    f = wnd.FrameWnd()
    f.WNDCLASS_BACKGROUNDCOLOR = 0xffffff
    f.msgproc.PAINT = paint
    f.create()

    app.run()

if __name__ == '__main__':
    run()


