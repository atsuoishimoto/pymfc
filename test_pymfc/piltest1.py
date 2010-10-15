# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import app, wnd, gdi, shellapi
import cStringIO
from PIL import ImageWin, Image, BmpImagePlugin

# bug in PIL?
BmpImagePlugin.BIT2MODE[16] = ("RGB", "BGR;15")


imglist = shellapi.getSysImageList(isSmall=False)
sysidx = shellapi.shGetFileInfo(u"test.doc", usefileattributes=True, largeicon=True, sysiconindex=True)
icon = imglist.getIcon(sysidx)
icons = [
    icon,
    gdi.Icon(filename=u"pymfc\\test_pymfc\\icon_32_32_4.ico"),
    gdi.Icon(filename=u"pymfc\\test_pymfc\\icon_32_32_8.ico"),
    gdi.Icon(filename=u"pymfc\\test_pymfc\\icon_32_32_24.ico")
]


class TestImageWindow(ImageWin.Window):

    def __init__(self, image, title="PIL"):
        if not isinstance(image, ImageWin.Dib):
            image = ImageWin.Dib(image)
        self.image = image
        width, height = image.size
        ImageWin.Window.__init__(self, title, width=width*8, height=height*8)

    def ui_handle_repair(self, dc, x0, y0, x1, y1):
        self.image.draw(dc, (x0, y0, x1, y1))

for n, i in enumerate(icons):
    bmp = i.getBitmap()
    dib = bmp.createDIB()
    src = cStringIO.StringIO(dib.header+dib.bits)
    image = BmpImagePlugin.DibImageFile(src)

    if image.mode == "RGBA":
        pass
    else:
        bmp = i.getMaskBitmap()
        dib = bmp.createDIB()

        # http://www.djangosnippets.org/snippets/1287/
        stride = ((dib.width + 31) >> 5) << 2
        maskimage = Image.fromstring('1', image.size, dib.bits, 'raw',
                                        ('1;I', stride, -1))

        image = image.convert('RGBA')
        image.putalpha(maskimage)

    w = TestImageWindow(image)
    image.save("c:\\%d.png"%n)


#    image.save("c:\\a.bmp")
    
  


w.mainloop()


