# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from _pymfclib_gdi import Bitmap, Icon, Cursor, DC, ClientDC, WindowDC, DisplayDC, DesktopDC, PaintDC, CompatibleDC, IC, EnhMetaFileDC
from _pymfclib_gdi import Font, StockFont, Pen, HatchPen, Brush, HatchBrush, PatternBrush
from _pymfclib_gdi import EllipticRgn, RectRgn, RoundRectRgn
from _pymfclib_gdi import _text_metric as TextMetric
from _pymfclib_gdi import LogFont, Monitor, DevMode


class DCBlock(object):
    def __init__(self, dc, objs=(), onexit=None):
        self._dc = dc
        self._objs = objs[:]
        self._onexit = onexit
    
    def __enter__(self):
        self._orgObjs = [self._dc.selectObject(obj) for obj in self._objs]
        return self._dc
        
    def __exit__(self, type, value, traceback):
        for obj in self._orgObjs[::-1]:
            self._dc.selectObject(obj)
        if self._onexit:
            self._onexit()
        self._dc = self._objs = self._orgObjs = self._onexit = None
        