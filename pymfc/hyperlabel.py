import itertools
from pymfc import wnd, gdi, util, syscolor

# todo: use rich text instead? May be Windowless Richedit?

class _HyperLabelBlock(object):
    def __init__(self, item, col, width, height):
        self.item = item
        self.col = col
        self.width = width
        self.height = height

#        print ">>>>>>>>>>>>>", height, item._text[col[0]:col[1]]

    def draw(self, dc, rc, wnd):
        self.item.draw(dc, rc, self.col, wnd)

class LinkItem(object):
    ICON_GAP = 5
    MARGIN = 5

    def __init__(self, text, icon, clicked=None, rclicked=None):
        self._text = text
        self._icon = icon
        self._clicked = clicked
        self._rclicked = rclicked

    def _splitText(self, dc, f, width):
        # todo: word wrap
        ret = f
        retwidth = retheight = self.MARGIN
        for c in self._text[f:]:
            w, h = dc.getTextExtent(c)
            h += self.MARGIN
            if retwidth + w > width:
                break
            retheight = max(retheight, h)
            ret += 1
            retwidth += w

        return ret, retwidth, retheight

    def split(self, dc, width_first, width):
        ret = []

        if self._icon:
            iconsize = self._icon.getBitmap().getSize()
        else:
            iconsize = (0,0)
        
        if width_first < (iconsize[0]*2):
            ret.append(None)
            width_first = width
        
        t, w, h = self._splitText(dc, 0, width_first-iconsize[0]-self.ICON_GAP)
#        print "111111", t, w, h, self._text[0:t]
        block = _HyperLabelBlock(self, (0,t), w+iconsize[0]+self.ICON_GAP, max(h, iconsize[1]+self.MARGIN))
        ret.append(block)

        while t < len(self._text):
            f = t
            t, w, h = self._splitText(dc, f, width)
            h = max(iconsize[1], h)+self.MARGIN
            
#            print ">>>>>>>>>>", t, w, h, self._text[f:t]
            block = _HyperLabelBlock(self, (f,t), w, h)
            ret.append(block)

        return ret

    def draw(self, dc, rc, col, wnd):
        l, t, r, b = rc

        if col[0] == 0:
            if self._icon:
                iconsize = self._icon.getBitmap().getSize()
                icontop = b-iconsize[1]-self.MARGIN
                dc.drawIcon((l, icontop), self._icon, iconsize, normal=True)
                l += iconsize[0]+self.ICON_GAP

        s = self._text[col[0]:col[1]]
        w, h = dc.getTextExtent(s)
        dc.textOut(s, (l,b-h-self.MARGIN))
#        print "============", s, rc, (l,b-h-self.MARGIN)
        end = l + w
        
        if wnd.isPressing(self):
            l, t, r, b = rc
            b -= self.MARGIN//2
            dc.drawEdge((l, t, end, b),
                sunkenouter=False, sunkeninner=True, 
                left=True, top=True, right=True, bottom=True)
        elif wnd.isHighlighting(self):
            l, t, r, b = rc
            b -= self.MARGIN//2
            dc.drawEdge((l, t, end, b), raisedinner=True, raisedouter=True, bottom=True)

    def clicked(self):
        if self._clicked:
            self._clicked(self)

    def rclicked(self):
        if self._rclicked:
            self._rclicked(self)

    def getText(self):
        return self._text
        
class _HyperLabelRow(object):
    def __init__(self, width):
        self.height = 0
        self.width = width
        self._blocks = []
        self.remains = width

    def addBlock(self, block):
        self._blocks.append(block)
        self.remains -= block.width
        self.height = max(self.height, block.height)

    def getBlocks(self):
        return self._blocks

    def draw(self, dc, rc, wnd):
        l, t, r, b = rc
        for block in self._blocks:
            r = l+block.width
            b = t+self.height
            block.draw(dc, (l, t, r, b), wnd)
            l = r

class HyperLabel(wnd.Wnd):
    WNDCLASS_CURSOR = gdi.Cursor(arrow=True)
    FONT = gdi.StockFont(default_gui=True) 
    def _prepare(self, kwargs):
        super(HyperLabel, self)._prepare(kwargs)
        self._bgColor = kwargs.get('bgcolor', syscolor.window)

        self._items = []
        self._rows = []
        self._pressingLeft = None
        self._pressingRight = None
        self._highlighting = None
        self._topPos = 0
        
        self.msglistener.SIZE = self._onSize
        self.msgproc.SETCURSOR = self._onSetCursor
        self.msgproc.PAINT = self._onPaint
        self.msglistener.MOUSEMOVE = self._onMouseMove
        self.msglistener.MOUSELEAVE = self._onMouseLeave
        self.msglistener.LBUTTONDOWN = self._onLBtnDown
        self.msglistener.LBUTTONUP = self._onLBtnUp
        self.msglistener.RBUTTONDOWN = self._onRBtnDown
        self.msglistener.RBUTTONUP = self._onRBtnUp
        self.msglistener.CANCELMODE = self._onCancelMode
        self.msglistener.CHAR = self._onChar
        self.msglistener.VSCROLL = self._onVScroll

    def wndReleased(self):
        super(HyperLabel, self).wndReleased()
        self._items = []
        self._rows = []
        self._pressingLeft = None
        self._pressingRight = None
        self._highlighting = None
        
    def appendItem(self, item, redraw=False):
        self._items.append(item)
        if redraw:
            self.layout()
            self.invalidateRect(None, erase=False)
            
    def setItems(self, items, redraw=False):
        self._items = items
        if redraw:
            self.layout()
            self.invalidateRect(None, erase=False)

    def getItems(self):
        return self._items
        
    def clearItems(self, redraw=False):
        self._items = []
        if redraw:
            self.layout()
            self.invalidateRect(None, erase=False)
            
    def isPressing(self, item):
        return self._pressingLeft is item
        
    def isHighlighting(self, item):
        return self._highlighting is item
        
    def _onSize(self, msg):
        self.layout()

    def _onPaint(self, msg):
        dc = gdi.PaintDC(self)

        try:
            wndrc = self.getClientRect()
            rc = dc.rc

            paintdc = dc.createCompatibleDC()
            bmp = dc.createCompatibleBitmap(wndrc[2]-wndrc[0], wndrc[3] - wndrc[1])
            orgbmp = paintdc.selectObject(bmp)

            self._draw(paintdc, wndrc)
            dc.bitBlt(rc, paintdc, (rc[0], rc[1]), srccopy=True)
            
            paintdc.selectObject(orgbmp)

        finally:
            dc.endPaint()

    def _onSetCursor(self, msg):
        pos= self.getCursorPos()
        item = self._getItemAt(pos)
        if item:
            cursor = gdi.Cursor(hand=True)
            cursor.setCursor()
            return True
        else:
            return self.defWndProc(msg)

    def _onMouseMove(self, msg):
        pos= self.getCursorPos()
        item = self._getItemAt(pos)
        if self._highlighting is not item:
            self._highlighting = item
            self.invalidateRect(None, erase=False)

            if self._highlighting:
                self.trackMouseEvent(leave=True)

    def _onMouseLeave(self, msg):
        if self._highlighting:
            self._highlighting = None
            self.invalidateRect(None, erase=False)
        
    def _onLBtnDown(self, msg):
#        self.setFocus()
        if self._pressingRight:
            return
            
        pos= self.getCursorPos()
        item = self._getItemAt(pos)
        if item:
            self._pressingLeft = item
            self.setCapture()
            self.invalidateRect(None, erase=False)
            
    def _onLBtnUp(self, msg):
        if self._pressingLeft:
            self.releaseCapture()
            self.invalidateRect(None, erase=False)

            curpressing = self._pressingLeft
            self._pressingLeft = None

            pos= self.getCursorPos()
            item = self._getItemAt(pos)
            if item is curpressing:
                item.clicked()

                
    def _onRBtnDown(self, msg):
#        self.setFocus()

        if self._pressingLeft:
            return
            
        pos= self.getCursorPos()
        item = self._getItemAt(pos)
        if item:
            self._pressingRight = item
            self.setCapture()
            self.invalidateRect(None, erase=False)

    def _onRBtnUp(self, msg):
        if self._pressingRight:
            self.releaseCapture()
            self.invalidateRect(None, erase=False)

            curpressing = self._pressingRight
            self._pressingRight = None

            pos= self.getCursorPos()
            item = self._getItemAt(pos)
            if item is curpressing:
                item.rclicked()

            
    def _onCancelMode(self, msg):
        self._pressingLeft = self._pressingRight = None
        self.releaseCapture()
        self.invalidateRect(None, erase=False)

    def _onChar(self, msg):
        if self._pressingRight or self._pressingLeft:
            if ord(msg.char) == wnd.KEY.ESC:
                self._pressingLeft = self._pressingRight = None
                self.releaseCapture()
                self.invalidateRect(None, erase=False)
        
    def _onVScroll(self, msg):
        l, t, r, b = self.getClientRect()
        height = b-t
        if msg.linedown:
            self._lineDown()
        elif msg.pagedown:
            self._pageDown()
        elif msg.lineup:
            self._lineUp()
        elif msg.pageup:
            self._pageUp()

    def _setTopPos(self, pos):
        l, t, r, b = self.getClientRect()
        height = b-t

        totalheight = sum(row.height for row in self._rows)
        maxpos = totalheight-height
        self._topPos = max(0, min(maxpos, pos))
        self._updateScrollBar()
        self.invalidateRect(None)
    

    def _iterVisibleRows(self):
        clientrc = self.getClientRect()
        l, t, r, b = 0, -self._topPos, clientrc[2], 0

        for n, row in enumerate(self._rows):
            h = row.height
            b = t+h
            if b > 0:
                yield n, (l, t, r, b), row
            if b > clientrc[3]:
                break
            t = b
        

    def _getBotRow(self):
        ret = None
        l, t, r, b = self.getClientRect()
        for n, rc, row in self._iterVisibleRows():
            if rc[3] > b:
                if not ret:
                    ret = n, rc, row
                break
            ret = n, rc, row
        return ret

    def _lineDown(self):
        if not self._rows:
            return

        n, rc, row = self._iterVisibleRows().next() # get top row
        newpos = self._topPos+rc[3]-rc[1]
        self._setTopPos(newpos)
        
    def _pageDown(self):
        if not self._rows:
            return
            
        n, rc, row = self._getBotRow()
        l, t, r, b = self.getClientRect()
        height = rc[1]
        if not height:
            height = rc[3]
        newpos = self._topPos+height
        self._setTopPos(newpos)

    def _lineUp(self):
        if not self._rows:
            return

        n, rc, row = self._iterVisibleRows().next() # get top row
        if rc[1] != 0:
            newpos = self._topPos+rc[1]
            self._setTopPos(newpos)
        else:
            if n == 0:
                return

            row = self._rows[n-1]
            newpos = self._topPos-row.height
            self._setTopPos(newpos)

    def _pageUp(self):
        if not self._rows:
            return

        n, rc, row = self._iterVisibleRows().next() # get top row
        if rc[1] != 0:
            newpos = self._topPos+rc[1]
            self._setTopPos(newpos)
        else:
            if n == 0:
                return

            clientrc = self.getClientRect()
            clientheight = clientrc[3]-clientrc[1]

            scrollheight = clientheight - row.height
            dy = 0
            
            for idx in xrange(n-1, -1, -1):
                row = self._rows[idx]
                if row.height + dy > scrollheight:
                    break
                dy += row.height

            if dy == 0:
                prevrow = self._rows[n-1]
                dy = prevrow.height
                
            newpos = self._topPos-dy
            newpos = max(0, newpos)
            self._setTopPos(newpos)

    def _draw(self, dc, rc):
        if self._bgColor is not None:
            dc.fillSolidRect(rc, self._bgColor)

        org = dc.selectObject(self.FONT)

        for n, rc, row in self._iterVisibleRows():
            row.draw(dc, rc, self)

        dc.selectObject(org)

    def setBgColor(self, color):
        if self._bgColor != color:
            self._bgColor = color
            self.invalidateRect(None, erase=False)
            
    def layout(self):
        dc = gdi.ClientDC(self)
        org = dc.selectObject(self.FONT)
        rc = self.getClientRect()

        width = rc[2]-rc[0]
        width = max(50, width)
        
        self._splitItems(dc, width)
        dc.selectObject(org)

        l, t, r, b = self.getClientRect()
        totalheight = sum(row.height for row in self._rows)
        maxpos = max(0, totalheight-(b-t))
        self._topPos = min(maxpos, self._topPos)

        self._updateScrollBar()

    def _splitItems(self, dc, width):
        rows = [_HyperLabelRow(width)]

        for item in self._items:
            blocks = item.split(dc, rows[-1].remains, width)
            if blocks[0]:
                rows[-1].addBlock(blocks[0])

            for block in blocks[1:]:
                row = _HyperLabelRow(width)
                row.addBlock(block)
                rows.append(row)

        self._rows = rows

    def _getBlockAt(self, pos):
        for n, rowrc, row in self._iterVisibleRows():
            if util.ptInRect(pos, rowrc):
                l = r = 0
                for block in row.getBlocks():
                    r = l+block.width
                    if l <= pos[0] < r:
                        return block
                    l = r
                break

    def _getItemAt(self, pos):
        block = self._getBlockAt(pos)

        if block:
            return block.item

    def _updateScrollBar(self):
        totalheight = sum(row.height for row in self._rows)
        
        l, t, r, b = self.getClientRect()

        height = b-t
        if height >= totalheight:
            self.showScrollBar(vert=True, horz=True, show=False)
        else:
            self.showScrollBar(vert=True, horz=False, show=True)
            maxpos = max(0, totalheight-height)
            self.setScrollInfo(vert=True, min=0, max=maxpos, pos=self._topPos, redraw=True)

