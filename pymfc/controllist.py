#import itertools
#from pymfc import gdi, wnd
#
#
#class RowWnd(wnd.Wnd):
#    def _prepare(self, kwargs):
#        super(RowWnd, self)._prepare(kwargs)
#        self._idx = None
#        self._rowInfo = None
#        
#        self.msgproc.PAINT = self._onPaint
#        
#    def wndReleased(self):
#        super(RowWnd, self).wndReleased()
#        self._rowInfo = None
#        
#    def setRowInfo(self, idx, info):
#        self._idx = idx
#        self._rowInfo = info
#    
#    def getRowInfo(self):
#        return self._idx, self._rowInfo
#        
#    def _onPaint(self, msg):
#        dc = gdi.PaintDC(msg.wnd)
#        try:
#            if self._rowInfo:
#                self._rowInfo.onPaint(dc, dc.rc, self)
#        finally:
#            dc.endPaint()
#
#class RowInfo(object):
#    def __init__(self):
#        self._idx = None
#        self._height = None
#        
#    def setIdx(self, idx):
#        self._idx = idx
#
#    def setRowWnd(self, rowwnd):
#        self._rowwnd = rowwnd
#
#    def getRowWndClass(self):
#        raise NotImplementedError
#        
#    def getHeight(self):
#        return self._height
#
#    def updateHeight(self, dc, width):
#        self._height = self.calcHeight(dc, width)
#        
#    def calcHeight(self, dc, width):
#        raise NotImplementedError
#
#    def onPaint(self, dc, rc, wnd):
#        pass
#
#
#class _RowWndCache(object):
#    def __init__(self):
#        self._cache = {}
#    
#    def get(self, cls):
#        objs = self._cache.get(cls)
#        if objs:
#            ret = objs.pop()
#            return ret
#        return
#
#    def rel(self, obj):
#        obj.setWindowPos(show=False)
#        cls = obj.__class__
#        self._cache.setdefault(cls, []).append(obj)
#
#
#class RowList(wnd.Wnd):
#    def _prepare(self, kwargs):
#        super(RowList, self)._prepare(kwargs)
#        self._rows = []
#        self._rowWnds = []
#        self._rowWndCache = _RowWndCache()
#        self._topPos = 0
#        self._totalHeight = 0
#        
#        self.msglistener.CREATE = self._onCreate
#        self.msglistener.SIZE = self._onSize
#        self.msglistener.VSCROLL = self._onVScroll
#
#    def wndReleased(self):
#        super(RowList, self).wndReleased()
#        self._rows = None
#        self._rowWnds = None
#        self._rowWndCache = None
#    
#        
#    def appendRows(self, rows):
#        self._callUpdateHeight(rows)
#        self._rows.extend(rows)
#        self._updateRowHeights()
#        self._updateScrollBar()
#        self._setRowWnds()
#        
#    def _iterRows(self, start):
#        return iter(self._rows[start:])
#
#    def _iterVisibleRows(self):
#        if not self._rows:
#            return
#
#        top = 0
#        for idx, row in enumerate(self._rows):
#            height = row.getHeight()
#            if height + top > self._topPos:
#                break
#            top += height
#        
#        l, t, r, b = self.getClientRect()
#        top -= self._topPos
#        for n in xrange(idx, len(self._rows)):
#            row = self._rows[n]
#            height = row.getHeight()
#            bottom = top+height
##            print ">>>>>", row._data, n, (l, top, r, bottom)
#            yield n, (l, top, r, bottom), row
#            top = bottom
#            if bottom >= b:
#                break
#        
#    def _getRowWnd(self, row):
#        cls = row.getRowWndClass()
#        obj = self._rowWndCache.get(cls)
#        if not obj:
#            obj = cls(parent=self)
#            obj.create()
#        return obj
#        
#    def releaseRowWnds(self, wnds):
#        for wnd in wnds:
#            idx, row = wnd.getRowInfo()
#            if row:
#                row.setRowWnd(None)
#            self._rowWndCache.rel(wnd)
#
#    def _callUpdateHeight(self, rows):
#        l, t, r, b = self.getClientRect()
#        width = r-l
#        dc = gdi.ClientDC(self)
#        try:
#            for row in rows:
#                row.updateHeight(dc, width)
#        finally:
#            dc.release()
#
#    def _updateTotalHeight(self):
#        height = 0
#        for row in self._rows:
#            height += row.getHeight()
#        self._totalHeight = height
#        
#    def _updateRowHeights(self):
#        self._callUpdateHeight(self._rows)
#        self._updateTotalHeight()
#
#    def _setTopPos(self, pos):
#        l, t, r, b = self.getClientRect()
#        height = b-t
#        maxpos = max(0, self._totalHeight-height)
#        self._topPos = min(maxpos, pos)
#        self._setRowWnds()
#        
#    def _updateScrollBar(self):
#        l, t, r, b = self.getClientRect()
#        height = b-t
#        if height >= self._totalHeight:
#            self.showScrollBar(vert=False, horz=False, show=True)
#        else:
#            self.showScrollBar(vert=True, horz=False, show=True)
#            maxpos = max(0, self._totalHeight-height)
#            self.setScrollInfo(vert=True, min=0, max=maxpos, pos=self._topPos, redraw=True)
#
#
#    def _setRowWnds(self):
#        n = max(len(self._rowWnds)*2, 40)
#        defer = self.beginDeferWindowPos(n)
#
#        wndidx = 0
#        for idx, rc, row in self._iterVisibleRows():
#            if wndidx >= len(self._rowWnds):
#                wnd = self._getRowWnd(row)
#                self._rowWnds.append(wnd)
#            else:
#                wnd = self._rowWnds[wndidx]
#                if not isinstance(wnd, row.getRowWndClass()):
#                    self.releaseRowWnds(wnd)
#                    wnd = self._getRowWnd(row)
#                    self._rowWnds[wndidx] = wnd
#
#            wnd.setRowInfo(idx, row)
#            defer = wnd.deferWindowPos(defer, rect=rc, show=True)
#            wnd.invalidateRect(None)
#            wndidx += 1
#        
#        self.endDeferWindowPos(defer)
#
#        rels = self._rowWnds[wndidx:]
#        del self._rowWnds[wndidx:]
#        
#        self.releaseRowWnds(rels)
#        self._updateScrollBar()
#
#    def _onCreate(self, msg):
#        pass
#
#    def _onSize(self, msg):
#        self._updateRowHeights()
#        self._updateScrollBar()
#        self._setRowWnds()
#
#    def _lineDown(self):
#        l, t, r, b = self.getClientRect()
#        height = b-t
#        amount = height//5+1
#        newpos = self._topPos+amount
#        self._setTopPos(newpos)
#
#    def _pageDown(self):
#        l, t, r, b = self.getClientRect()
#        height = b-t
#        newpos = self._topPos+height
#        self._setTopPos(newpos)
#
#    def _lineUp(self):
#        l, t, r, b = self.getClientRect()
#        height = b-t
#        amount = height//5+1
#        newpos = self._topPos-amount
#        newpos = max(0, newpos)
#        self._setTopPos(newpos)
#
#    def _pageUp(self):
#        l, t, r, b = self.getClientRect()
#        height = b-t
#        newpos = self._topPos-height
#        newpos = max(0, newpos)
#        self._setTopPos(newpos)
#
#    def _onVScroll(self, msg):
#        l, t, r, b = self.getClientRect()
#        height = b-t
#        if msg.linedown:
#            self._lineDown()
#        elif msg.pagedown:
#            self._pageDown()
#        elif msg.lineup:
#            self._lineUp()
#        elif msg.pageup:
#            self._pageUp()
