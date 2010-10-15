# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import pymfc
from pymfc import wnd, gdi, util
import _pymfclib
import traceback

class GridCol(object):
    __slots__ = ('_width', '_label')
    def __init__(self, width=0, label=u''):
        self._width = width
        self._label = label

    def setWidth(self, w):
        if w != self._width:
            self._width = w
            return True
    
    def getWidth(self):
        return self._width

    def getLabel(self):
        return self._label
        
class GridRow(object):
    __slots__ = ('_label', '_height')
    def __init__(self, height=0, label=u''):
        self._height = height
        self._label = label

    def setHeight(self, h):
        if h != self._height:
            self._height = h
            return True
    
    def getHeight(self):
        return self._height

    def getLabel(self):
        return self._label
        
class GridCell(object):
    def __init__(self, left=False, center=False, right=False, top=False, vcenter=False, bottom=False, 
                font=None, bgcolor=None, margin=5, indent=0, prop=None):

        self._rc = [0,0,0,0]

        if not (left or center or right):
            left = True
        if not (top or vcenter or bottom):
            top = True
        self._alignLeft = left
        self._alignCenter = center
        self._alignRight = right
        self._alignTop = top
        self._alignVcenter = vcenter
        self._alignBottom = bottom

        self._font = font
        self._bgcolor = bgcolor
        self._margin = margin
        self._indent = indent
        self._prop = prop
        
    def createCell(self, parent):
        pass

    def release(self):
        self._font = None
        self._prop = None

    def setFont(self, font):
        self._font = font

    def setBgColor(self, color):
        self._bgcolor = color

    def setRect(self, wnd, rc):
        rc = list(rc)
        if self._rc != rc:
            self._rc = rc
            self._rcUpdated(wnd)

    def getRect(self):
        return self._rc
        
    def getProp(self):
        return self._prop

    def setProp(self, prop):
        self._prop = prop

    def _rcUpdated(self, wnd):
        pass

    def _draw(self, wnd, dc):
        if self._bgcolor is not None:
            dc.fillSolidRect(self._rc, self._bgcolor)

class Grid(object):
    def __init__(self):
        self._cols = []
        self._rows = []
        self._cells = {}
        
    def clearAll(self):
        for cell in self._cells.itervalues():
            cell.release()
        self._cols = []
        self._rows = []
        self._cells = {}
            
    def appendCols(self, cols):
        self._cols.extend(cols)

    def removeCols(self, cols):
        for col in cols:
            self._cols.remove(col)
            for row in self._rows:
                cell = self._cells.get((row, col), None)
                if cell:
                    del self._cells[rc]
                    cell.release()

    def getCols(self):
        return self._cols
        
    def getCol(self, idx):
        return self._cols[idx]

    def appendRows(self, rows):
        self._rows.extend(rows)

    def removeRows(self, rows):
        for row in rows:
            self._rows.remove(row)
            for col in self._cols:
                cell = self._cells.get((row, col), None)
                if cell:
                    del self._cells[(row, col)]
                    cell.release()

    def clearRows(self):
        for cell in self._cells.itervalues():
            cell.release()
        self._rows = []
        self._cells = {}
        
    def getRows(self):
        return self._rows

    def getRow(self, idx):
        return self._rows[idx]

    def setCell(self, gridwnd, row, col, cell):
        assert row in self._rows
        assert col in self._cols

        key = (row, col)
        cur = self._cells.get(key)
        if cur:
            cur.release()
        self._cells[key] = cell
        
    def getCell(self, row, col, default=None):
        return self._cells.get((row, col), default)

    def getCells(self):
        return self._cells.itervalues()

    def getWidth(self):
        return sum((col.getWidth() for col in self._cols))
        
    def getHeight(self):
        return sum((row.getHeight() for row in self._rows))

class HeaderPane(wnd.Wnd):
    STYLE = wnd.Wnd.STYLE(clipchildren=True, clipsiblings=True)
    MINCOLWIDTH = 20
    MAXCOLWIDTH = 800
    def _prepare(self, kwargs):
        super(HeaderPane, self)._prepare(kwargs)
    
        self._dragging = None
        self._top = 0
        self._font = kwargs['font']
        self._textcolor = kwargs['textcolor']
        self._bgcolor = kwargs['bgcolor']
        self._bordercolor = kwargs['bordercolor']
        
        self.msgproc.PAINT = self._onPaint
        self.msgproc.LBUTTONDOWN = self._onLBtnDown
        self.msgproc.LBUTTONUP = self._onLBtnUp
        self.msgproc.MOUSEMOVE = self._onMouseMove
        self.msgproc.CANCELMODE = self._onCancelMode
        self.msgproc.SETCURSOR = self._onSetCursor

    def wndReleased(self):
        super(HeaderPane, self).wndReleased()
        self._dragging = None
    
    def _iterCols(self):
        left, top, right, bottom = self.getClientRect()
        left -= self._parent._hScrollPos
        for col in self._parent._grid.getCols():
            rc = (left, top, left+col.getWidth(), bottom)
            yield col, rc
            left += col.getWidth()

    def _iterVisibleCols(self):
        left, top, right, bottom = self.getClientRect()
        for col, rc in self._iterCols():
            if rc[2] >= 0:
                yield col, rc
            if rc[0] > right:
                return

    def _onPaint(self, msg):
        paintdc = pymfc.gdi.PaintDC(self)
        left, top, right, bottom = self.getClientRect()

        dc = paintdc.createCompatibleDC()
        bmp = paintdc.createCompatibleBitmap(right-left, bottom-top)

        pen = gdi.Pen(solid=True, width=0, color=self._bordercolor)
        org = dc.selectObject((bmp, self._font, pen))
        dc.setTextColor(self._textcolor)
        try:
            dc.fillSolidRect((left, top, right, bottom), self._bgcolor)

            for col, rc in self._iterVisibleCols():
                dc.moveTo((rc[2]-1, rc[1]))
                dc.lineTo((rc[2]-1, rc[3]-1))
                titlerc = rc[0]+3, rc[1], rc[2]-3, rc[3]-3
                if titlerc[0] < titlerc[2] and titlerc[1] < titlerc[3]:
                    dc.drawText(col.getLabel(), titlerc,
                        singleline=True, end_ellipsis=True, noprefix=True,
                        bottom=True, center=True)

            dc.moveTo((left, bottom-1))
            dc.lineTo((left, top))
            dc.lineTo((right-1, top))
            dc.lineTo((right-1, bottom-1))

            paintdc.bitBlt(paintdc.rc, dc, (paintdc.rc[0], paintdc.rc[1]), srccopy=True)

        finally:
            dc.selectObject(org)
            paintdc.endPaint()

    def _getColBorderAt(self, x):
        for col, rc in self._iterVisibleCols():
            if abs(rc[2]-x) <= 2:
                return col
        
    def _getColAt(self, x):
        for col, rc in self._iterVisibleCols():
            if x < rc[2]:
                return col
        
    def _onLBtnDown(self, msg):
        if self._dragging:
            return
        
        col = self._getColBorderAt(msg.x)
        if col:
            self._dragging = col
            self._dragStart = msg.x
            self._orgWidth = col.getWidth()
            self.setCapture()
                
    def _onMouseMove(self, msg):
        if not self._dragging:
            return
        x, y = msg.x, msg.y
        newwidth = self._orgWidth + (x - self._dragStart)
        if newwidth < self.MINCOLWIDTH:
            newwidth = self.MINCOLWIDTH
        if newwidth > self.MAXCOLWIDTH:
            newwidth = self.MAXCOLWIDTH
        if self._dragging.setWidth(newwidth):
            self.invalidateRect(None, erase=False)
            self._parent.cellResized()

    def _onLBtnUp(self, msg):
        if self._dragging:
            self._onCancelMode(msg)

    def _onCancelMode(self, msg):
        if not self._dragging:
            return
        self._dragging = None
        self.releaseCapture()

    def _onSetCursor(self, msg):
        x,y = self.getCursorPos()
        if self._getColBorderAt(x):
            cursor = gdi.Cursor(sizewe=True)
        else:
            cursor = gdi.Cursor(arrow=True)
        
        cursor.setCursor()
        return True


class RowHeaderPane(wnd.Wnd):
    STYLE = wnd.Wnd.STYLE(clipchildren=True, clipsiblings=True)
    MINROWHEIGHT = 10
    MAXROWHEIGHT = 600
    
    def _prepare(self, kwargs):
        super(RowHeaderPane, self)._prepare(kwargs)
    
        self._dragging = None

        self._font = kwargs['font']
        self._textcolor = kwargs['textcolor']
        self._bgcolor = kwargs['bgcolor']
        self._bordercolor = kwargs['bordercolor']

        self.msgproc.PAINT = self._onPaint
        self.msgproc.LBUTTONDOWN = self._onLBtnDown
        self.msgproc.LBUTTONUP = self._onLBtnUp
        self.msgproc.MOUSEMOVE = self._onMouseMove
        self.msgproc.CANCELMODE = self._onCancelMode
        self.msgproc.SETCURSOR = self._onSetCursor
    
    def wndReleased(self):
        super(RowHeaderPane, self).wndReleased()
        self._dragging = None
    
    def _iterRows(self):
        left, top, right, bottom = self.getClientRect()
        top -= self._parent._vScrollPos
        for row in self._parent._grid.getRows():
            bottom = top + row.getHeight()
            yield row, (left, top, right, bottom)
            top = bottom
        
    def _iterVisibleRows(self):
        left, top, right, bottom = self.getClientRect()
        for row, rc in self._iterRows():
            if rc[3] > 0:
                yield row, rc
            if rc[1] > bottom:
                return

    def _onPaint(self, msg):
        paintdc = pymfc.gdi.PaintDC(self)
        left, top, right, bottom = self.getClientRect()

        dc = paintdc.createCompatibleDC()
        bmp = paintdc.createCompatibleBitmap(right-left, bottom-top)

        pen = gdi.Pen(solid=True, width=0, color=self._bordercolor)
        org = dc.selectObject((bmp, self._font, pen))
        dc.setTextColor(self._textcolor)
        try:
            dc.fillSolidRect((left, top, right, bottom), self._bgcolor)

            for row, rc in self._iterVisibleRows():
                dc.moveTo((rc[0], rc[3]-1))
                dc.lineTo((rc[2]-1, rc[3]-1))
                titlerc = rc[0]+3, rc[1], rc[2]-3, rc[3]-3
                if titlerc[0] < titlerc[2] and titlerc[1] < titlerc[3]:
                    dc.drawText(row.getLabel(), titlerc, 
                        singleline=True, end_ellipsis=True, noprefix=True, 
                        bottom=True, center=True)
                
            dc.moveTo((right-1, top))
            dc.lineTo((left, top))
            dc.lineTo((left, bottom-1))
            dc.lineTo((right-1, bottom-1))

            paintdc.bitBlt(paintdc.rc, dc, (paintdc.rc[0], paintdc.rc[1]), srccopy=True)

        finally:
            dc.selectObject(org)
            paintdc.endPaint()

    def _getRowBorderAt(self, y):
        for row, rc in self._iterVisibleRows():
            if abs(rc[3]-y) <= 2:
                return row

    def _getRowAt(self, y):
        for row, rc in self._iterVisibleRows():
            if y < rc[3]:
                return row

    def _onLBtnDown(self, msg):
        if self._dragging:
            return
        
        row = self._getRowBorderAt(msg.y)
        if row:
            self._dragging = row
            self._dragStart = msg.y
            self._orgHeight = row.getHeight()
            self.setCapture()
                
    def _onMouseMove(self, msg):
        if not self._dragging:
            return
        x, y = msg.x, msg.y
        newheight = self._orgHeight + (y - self._dragStart)
        if newheight < self.MINROWHEIGHT:
            newheight = self.MINROWHEIGHT
        if newheight > self.MAXROWHEIGHT:
            newheight = self.MAXROWHEIGHT
        if self._dragging.setHeight(newheight):
            self.invalidateRect(None, erase=False)
            self._parent.cellResized()

    def _onLBtnUp(self, msg):
        if self._dragging:
            self._onCancelMode(msg)

    def _onCancelMode(self, msg):
        if not self._dragging:
            return
        self._dragging = None
        self.releaseCapture()

    def _onSetCursor(self, msg):
        x,y = self.getCursorPos()
        if self._getRowBorderAt(y):
            cursor = gdi.Cursor(sizens=True)
        else:
            cursor = gdi.Cursor(arrow=True)
        
        cursor.setCursor()
        return True

class GridPane(wnd.Wnd):
    STYLE = wnd.Wnd.STYLE(clipchildren=True, clipsiblings=True)
    def _prepare(self, kwargs):
        super(GridPane, self)._prepare(kwargs)

        self._bgcolor = kwargs['bgcolor']
        self._bordercolor = kwargs['bordercolor']
        self.msgproc.PAINT = self._onPaint
        
    def wndReleased(self):
        super(GridPane, self).wndReleased()

    def _getWndClass(self):
        return wnd.WndClassStyle().register(cursor=gdi.Cursor(arrow=True))

    def getRowAt(self, y):
        return self._parent._rowHeaderPane._getRowAt(y)
            
    def getColAt(self, x):
        return self._parent._headerPane._getColAt(x)
            
    def getCellAt(self, pos):
        col = self.getColAt(pos[0])
        if not col:
            return
        row = self.getRowAt(pos[1])
        if not row:
            return
        
        cell = self._parent.getCell(row, col)
        return cell
        
    def _onPaint(self, msg):
        paintdc = pymfc.gdi.PaintDC(self)

        try:
            wndrc = self.getClientRect()
            dc = paintdc.createCompatibleDC()
            bmp = paintdc.createCompatibleBitmap(wndrc[2]-wndrc[0], wndrc[3]-wndrc[1])
            orgbmp = dc.selectObject(bmp)

            rc = paintdc.rc
            try:
                dc.fillSolidRect(rc, self._bgcolor)
                
                if self._bordercolor is not None:
                    pen = gdi.Pen(solid=True, width=0, color=self._bordercolor)
                
                for row, rowrc in self._parent._rowHeaderPane._iterVisibleRows():
                    for col, colrc in self._parent._headerPane._iterVisibleCols():
                        cell = self._parent._grid.getCell(row, col)
                        if cell:
                            cell._draw(self, dc)
                            if self._bordercolor is not None:
                                l, t, r, b = cell.getRect()
                                org = dc.selectObject(pen)
                                try:
                                    dc.moveTo((r-1, t))
                                    dc.lineTo((r-1, b-1))
                                    dc.lineTo((l, b-1))
                                finally:
                                    dc.selectObject(org)

                if self._bordercolor is not None:
                    dc.frameRect(wndrc, gdi.Brush(color=self._bordercolor))

                paintdc.bitBlt(rc, dc, (rc[0], rc[1]), srccopy=True)

            finally:
                dc.selectObject(orgbmp)

        finally:
            paintdc.endPaint()

class GridWnd(wnd.Wnd):
    STYLE = wnd.Wnd.STYLE(clipchildren=True, clipsiblings=True)
    HEADERPANE = HeaderPane
    ROWHEADERPANE = RowHeaderPane
    GRIDPANE = GridPane
    FONT = gdi.StockFont(default_gui=True)
    BGCOLOR = 0xf0f8f8
    BORDERCOLOR = None
    HEADERBGCOLOR = 0xd0d8d8
    HEADERTEXTCOLOR = 0x000000
    HEADERBORDERCOLOR = 0x808080
    HEADERHEIGHT = 30
    ROWHEADERWIDTH = 100

    def _prepare(self, kwargs):
        super(GridWnd, self)._prepare(kwargs)
        
        self._bgcolor = kwargs.get('bgcolor', self.BGCOLOR)
        self._bordercolor = kwargs.get('bordercolor', self.BORDERCOLOR)
        self._headerbgcolor = kwargs.get('headerbgcolor', self.HEADERBGCOLOR)
        self._headertextcolor = kwargs.get('headertextcolor', self.HEADERTEXTCOLOR)
        self._headerbordercolor = kwargs.get('headerbordercolor', self.HEADERBORDERCOLOR)
        self._font = kwargs.get('font', self.FONT)
        self._oncellclicked = kwargs.get('oncellclicked', None)
        
        self._grid = Grid()
        self._gridPane = self.GRIDPANE(parent=self,
                bgcolor=self._bgcolor, bordercolor=self._bordercolor)
        self._headerPane = self.HEADERPANE(parent=self, font=self._font, textcolor=self._headertextcolor,
                bgcolor=self._headerbgcolor, bordercolor=self._headerbordercolor)
        self._rowHeaderPane = self.ROWHEADERPANE(parent=self, font=self._font, textcolor=self._headertextcolor,
                bgcolor=self._headerbgcolor, bordercolor=self._headerbordercolor)

        if kwargs.get('hideheader', False):
            self._headerHeight = 0
        else:
            self._headerHeight = kwargs.get('headerheight', self.HEADERHEIGHT)

        if kwargs.get('hiderowheader', False):
            self._rowHeaderWidth = 0
        else:
            self._rowHeaderWidth = kwargs.get('rowheaderwidth', self.ROWHEADERWIDTH)

        self._hScrollPos = 0
        self._vScrollPos = 0

        self.msgproc.PAINT = self._onPaint
        self.msglistener.CREATE = self._onCreate
        self.msglistener.SIZE = self._onSize
        
        self._gridPane.msgproc.MOUSEWHEEL = self._onMouseWheel
        self._gridPane.msglistener.HSCROLL = self._onHScroll
        self._gridPane.msglistener.VSCROLL = self._onVScroll
        self._gridPane.msglistener.LBUTTONDOWN = self._onLButtonDown
        self._gridPane.msglistener.KEYDOWN = self._onKeyDown

    def wndReleased(self):
        super(GridWnd, self).wndReleased()
        self._grid.clearAll()
        self._grid = None
        self._gridPane = None
        self._headerPane = None
        self._rowHeaderPane = None
        self._oncellclicked = None

    def getGridPane(self):
        return self._gridPane

    def clearAll(self):
        self._grid.clearAll()

    def setCols(self, cols):
        self._grid.setCols(cols)

    def appendCols(self, cols):
        self._grid.appendCols(cols)

    def removeCol(self, col):
        self._grid.removeCol(col)

    def getCols(self):
        return self._grid.getCols()

    def getCol(self, idx):
        return self._grid.getCol(idx)

    def setRows(self, rows):
        self._grid.setRows(rows)

    def getRows(self):
        return self._grid.getRows()

    def getRow(self, idx):
        return self._grid.getRow(idx)

    def appendRows(self, rows):
        self._grid.appendRows(rows)

    def appendRow(self, row):
        self._grid.appendRows((row,))
        
    def removeRows(self, rows):
        self._grid.removeRows(rows)
    
    def clearRows(self):
        self._grid.clearRows()
        
    def setCell(self, row, col, cell):
        self._grid.setCell(self, row, col, cell)
        if not cell._font:
            cell.setFont(self._font)

    def getCell(self, row, col):
        return self._grid.getCell(row, col)
        
    def iterCells(self):
        grid = self._grid
        for row in grid.getRows():
            for col in grid.getCols():
                cell = grid.getCell(row, col)
                if cell:
                    yield row, col, cell

    def redraw(self):
        self._headerPane.invalidateRect(None, erase=False)
        self._rowHeaderPane.invalidateRect(None, erase=False)
        self._gridPane.invalidateRect(None, erase=False)
        self.updateWindow()

    def _onCreate(self, msg):
        self._gridPane.create()
        self._headerPane.create()
        self._rowHeaderPane.create()

        for cell in self._grid.getCells():
            self.createCell(cell)

    def createCell(self, parent):
        pass

    def _onPaint(self, msg):
        dc = pymfc.gdi.PaintDC(self)
        try:
            if self._headerHeight or self._rowHeaderWidth:
                pen = gdi.Pen(solid=True, width=0, color=self._headerbordercolor)
                org = dc.selectObject(pen)
                try:
                    dc.fillSolidRect((0, 0, self._rowHeaderWidth, self._headerHeight), self._headerbgcolor)
                    dc.moveTo((self._rowHeaderWidth, 0))
                    dc.lineTo((0, 0))
                    dc.lineTo((0, self._headerHeight))
                finally:
                    dc.selectObject(org)
        finally:
            dc.endPaint()

    def _iterCellRect(self):
        for row, rowrc in self._rowHeaderPane._iterRows():
            t, b = rowrc[1], rowrc[3]
            for col, colrc in self._headerPane._iterCols():
                l, r = colrc[0], colrc[2]
                cell = self._grid.getCell(row, col)
                if cell:
                    yield row, col, cell, [l, t, r, b]
        

    def _updateCellRect(self):
        for row, col, cell, cellrc in self._iterCellRect():
            cell.setRect(self._gridPane, cellrc)

    def _layout(self):
        if not self._gridPane.getHwnd():
            return
        if not self._headerPane.getHwnd():
            return
        if not self._rowHeaderPane.getHwnd():
            return
            
        w = self._grid.getWidth()
        h = self._grid.getHeight()
        
        l, t, r, b = self.getClientRect()
            
        posRowHeader = (0, self._headerHeight)
        sizeRowHeader = (self._rowHeaderWidth, b-self._headerHeight)

        posHeader = (sizeRowHeader[0], 0)
        sizeHeader = (r-sizeRowHeader[0], self._headerHeight)

        panepos = sizeRowHeader[0], self._headerHeight
        panesize = r-sizeRowHeader[0], b-self._headerHeight

        # update size of panes
        self._gridPane.setWindowPos(pos=panepos, size=panesize)
        self._headerPane.setWindowPos(
            pos=posHeader, size=sizeHeader)

        self._rowHeaderPane.setWindowPos(pos=posRowHeader, size=sizeRowHeader)
            
        self._updateScrollBar()
        self._updateCellRect()
        self.redraw()

    def cellResized(self):
        self._updateScrollBar()
        self._updateCellRect()
        self.redraw()

    def _onSize(self, msg):
        self._layout()

    def _updateScrollBar(self):
        width = self._grid.getWidth()
        height = self._grid.getHeight()

        style = self._gridPane.getWindowStyle()
        rc = self._gridPane.getClientRect()
        outerwidth = rc[2] - rc[0]
        if style.vscroll:
            outerwidth += pymfc.metric.CXVSCROLL
        outerheight = rc[3] - rc[1]
        if style.hscroll:
            outerheight += pymfc.metric.CYHSCROLL
            
        innerwidth = outerwidth - pymfc.metric.CXVSCROLL
        innerheight = outerheight - pymfc.metric.CYHSCROLL

        if width <= outerwidth and height <= outerheight:
            self._gridPane.setScrollInfo(horz=True, min=0, max=0, pos=0, redraw=True)
            self._gridPane.setScrollInfo(vert=True, min=0, max=0, pos=0, redraw=True)
            self._gridPane.showScrollBar(horz=True, vert=True, show=False)
            self._hScrollPos = self._vScrollPos = 0

        elif width > innerwidth and height > innerheight:
            self._hScrollPos = max(0, min(self._hScrollPos, width-innerwidth))
            self._vScrollPos = max(0, min(self._vScrollPos, height-innerheight))
            self._gridPane.showScrollBar(horz=True, vert=True, show=True)
            self._gridPane.setScrollInfo(horz=True, min=0, max=width, pos=self._hScrollPos,
                                page=innerwidth+1, redraw=True)
            self._gridPane.setScrollInfo(vert=True, min=0, max=height, pos=self._vScrollPos,
                                page=innerheight+1, redraw=True)

        elif width > outerwidth:
            self._hScrollPos = max(0, min(self._hScrollPos, width-outerwidth))
            self._vScrollPos = 0
            self._gridPane.showScrollBar(horz=True, show=True)
            self._gridPane.setScrollInfo(horz=True, min=0, max=width, pos=self._hScrollPos,
                                page=outerwidth+1, redraw=True)
            self._gridPane.setScrollInfo(vert=True, min=0, max=0, pos=0, redraw=True)
            self._gridPane.showScrollBar(vert=True, show=False)
            
        elif height > outerheight:
            self._hScrollPos = 0
            self._vScrollPos = max(0, min(self._vScrollPos, height-outerheight))
            self._gridPane.showScrollBar(vert=True, show=True)
            self._gridPane.setScrollInfo(vert=True, min=0, max=height, pos=self._vScrollPos,
                                page=outerheight+1, redraw=True)
            self._gridPane.setScrollInfo(horz=True, min=0, max=0, pos=0, redraw=True)
            self._gridPane.showScrollBar(horz=True, show=False)

    def _onHScroll(self, msg):
        gridrc = self._gridPane.getClientRect()
        line_width = max(gridrc[2]/4, 10)
        maxWidth = self._grid.getWidth() - gridrc[2]
        
        if msg.left:
            newpos = 0

        elif msg.right:
            newpos = maxWidth

        elif msg.lineright:
            newpos = self._hScrollPos+line_width

        elif msg.pageright:
            newpos = self._hScrollPos+gridrc[2]

        elif msg.lineleft:
            newpos = self._hScrollPos-line_width

        elif msg.pageleft:
            newpos = self._hScrollPos-gridrc[2]

        elif msg.thumbtrack:
            info = self._gridPane.getScrollInfo(horz=True)
            newpos = info.trackpos
        else:
            return

        newpos = max(min(newpos, maxWidth), 0)
        if newpos != self._hScrollPos:
            self._hScrollPos = newpos
            self._updateScrollBar()
            self._updateCellRect()
            self.redraw()

    def _onVScroll(self, msg):
        if msg.thumbtrack:
            info = self._gridPane.getScrollInfo(vert=True)
            trackpos = info.trackpos
        else:
            trackpos = None

        self._vscroll(top=msg.top, bottom=msg.bottom, linedown=msg.linedown, lineup=msg.lineup,
                                        pagedown=msg.pagedown, pageup=msg.pageup, trackpos=trackpos)
        
    def _vscroll(self, top=False, bottom=False, linedown=False, lineup=False,
                                        pagedown=False, pageup=False, trackpos=None):
        gridrc = self._gridPane.getClientRect()
        line_height = max(gridrc[3]/4, 10)
        maxHeight = self._grid.getHeight() - gridrc[3]

        if top:
            newpos = 0

        elif bottom:
            newpos = maxHeight

        elif linedown:
            newpos = self._vScrollPos+line_height

        elif pagedown:
            newpos = self._vScrollPos+gridrc[3]

        elif lineup:
            newpos = self._vScrollPos-line_height

        elif pageup:
            newpos = self._vScrollPos-gridrc[3]

        elif trackpos is not None:
            newpos = trackpos
        else:
            return

        newpos = max(min(newpos, maxHeight), 0)
        if newpos != self._vScrollPos:
            self._vScrollPos = newpos
            self._updateScrollBar()
            self._updateCellRect()
            self.redraw()

    def _onMouseWheel(self, msg):
        gridrc = self._gridPane.getClientRect()
        line_height = max(gridrc[3]/4, 10)
        maxHeight = self._grid.getHeight() - gridrc[3]

        delta = msg.delta//120
        if delta < 0:
            delta = abs(delta)
        else:
            line_height = line_height*-1
        
        for d in range(delta):
            newpos = self._vScrollPos+line_height
            newpos = min(newpos, maxHeight)
            newpos = max(newpos, 0)
            self._vScrollPos = newpos
            self._updateScrollBar()
            self._updateCellRect()
            self.redraw()
            if self._vScrollPos >= maxHeight:
                break
            if self._vScrollPos == 0:
                break

        return 0

    def _onLButtonDown(self, msg):
        self._gridPane.setFocus()
        if self._oncellclicked:
            cell = self._getCellAt((msg.x, msg.y))
            if cell:
                self._oncellclicked(cell)

    def _getCellAt(self, (x, y)):
        for row, rowrc in self._rowHeaderPane._iterVisibleRows():
            for col, colrc in self._headerPane._iterVisibleCols():
                cell = self._grid.getCell(row, col)
                if cell:
                    l, t, r, b = cell.getRect()
                    if l <= x <= r and t <= y <= b:
                        return cell
        return None

    def _onKeyDown(self, msg):
        shift = wnd.getKeyState(wnd.KEY.SHIFT).down
        ctrl = wnd.getKeyState(wnd.KEY.CONTROL).down
        alt = wnd.getKeyState(wnd.KEY.MENU).down
        
        if msg.key == wnd.KEY.DOWN:
            self._vscroll(linedown=True)
        elif msg.key == wnd.KEY.UP:
            self._vscroll(lineup=True)
        elif msg.key == wnd.KEY.PGDN:
            self._vscroll(pagedown=True)
        elif msg.key == wnd.KEY.PGUP:
            self._vscroll(pageup=True)
        elif msg.key == wnd.KEY.HOME:
            self._vscroll(top=True)
        elif msg.key == wnd.KEY.END:
            self._vscroll(bottom=True)
        else:
            return

class TextCell(GridCell):
    def __init__(self, text, singleline=False,
                left=False, center=False, right=False, top=False, vcenter=False, bottom=False, 
                font=None, bgcolor=None, margin=5, indent=0, prop=None):

        super(TextCell, self).__init__(left, center, right, top, vcenter, bottom,
                                                    font, bgcolor, margin, indent, prop)
        self._text = text
        self._singleline = singleline
        
    def getText(self):
        return self._text

    def calcHeight(self, dc, width):
        if self._font:
            org = dc.selectObject(self._font)
        try:
            width = max(width - self._indent - self._margin*2, 1)
            ret = dc.drawText(self._text, (0,0,width,1), calcrect=True, editcontrol=True, wordbreak=not self._singleline,
                singleline=self._singleline, end_ellipsis=True, noprefix=True, 
                left=self._alignLeft, center=self._alignCenter, right=self._alignRight, 
                top=self._alignTop, vcenter=self._alignVcenter, bottom=self._alignBottom)

            return ret.rc[3]+self._margin*2

        finally:
            if self._font:
                dc.selectObject(org)

    def _draw(self, wnd, dc):
        super(TextCell, self)._draw(wnd, dc)

        orgmode = dc.setBkMode(transparent=True)
        if self._font:
            org = dc.selectObject(self._font)
        try:
            l, t, r, b = self._rc
            l += self._indent
            margin = self._margin
            rc = (l+margin, t+margin, r-margin, b-margin)

            if rc[0] >= rc[2] or rc[1] >= rc[3]:
                return

            dc.drawText(self._text, rc, editcontrol=True, wordbreak=not self._singleline,
                singleline=self._singleline, end_ellipsis=True, noprefix=True, 
                left=self._alignLeft, center=self._alignCenter, right=self._alignRight, 
                top=self._alignTop, vcenter=self._alignVcenter, bottom=self._alignBottom)
        finally:
            dc.setBkMode(orgmode)
            if self._font:
                dc.selectObject(org)

class ControlCell(GridCell):
    def __init__(self, ctrl, matchcell=False,
                left=False, center=False, right=False, top=False, vcenter=False, bottom=False,
                font=None, bgcolor=None, margin=5, indent=0, prop=None):
            
        super(ControlCell, self).__init__(left, center, right, top, vcenter, bottom,
                                                    font, bgcolor, margin, indent, prop)

        self._matchCell = matchcell
        self._ctrl = ctrl
        self._ctrlSize = None
        
    def createCell(self, parent):
        super(ControlCell, self).createCell(parent)

        self._ctrl.setParentObj(parent)
        self._ctrl.create()
        self._ctrlSize = self._ctrl._size
        if self._font:
            self._ctrl.setFont(self._font)
    
    def release(self):
        super(ControlCell, self).release()

        if self._ctrl and self._ctrl.getHwnd():
            self._ctrl.destroyWindow()
        self._ctrl = None
        self._ctrlSize = None

    def setFont(self, font):
        super(ControlCell, self).setFont(font)
        if font:
            ctrl = self.getControl()
            if ctrl:
                ctrl.setFont(font)

    def getControl(self):
        return self._ctrl

    def _getControlRect(self):
        rc = self._rc
        margin = self._margin
        l, t, r, b = rc[0]+margin+self._indent, rc[1]+margin, rc[2]-margin, rc[3]-margin
        
        width = r-l
        if self._ctrlSize[0] is not None:
            if self._matchCell:
                width = min(r-l, self._ctrlSize[0])
            else:
                width = self._ctrlSize[0]
        
        height = b-t
        
        if self._ctrlSize[1] is not None:
            if self._matchCell:
                height = min(b-t, self._ctrlSize[1])
            else:
                height = self._ctrlSize[1]

        if self._alignLeft:
            r = l+width
        elif self._alignCenter:
            l = l + ((r-l)-width)//2
            r = l + width
        elif self._alignRight:
            l = r - width
            
        if self._alignTop:
            b = t+height
        elif self._alignVcenter:
            t = t + ((b-t)-height)//2
            b = t + height
        elif self._alignBottom:
            t = b - height

        return l, t, r, b

    def _rcUpdated(self, wnd):
        l, t, r, b = self._getControlRect()
        wnd._deferCtrls = self._ctrl.deferWindowPos(wnd._deferCtrls, rect=(l, t, r, b))

class IconCell(GridCell):
    LABELMARGIN = 3

    def __init__(self, icon, label=None,
                left=False, center=False, right=False, top=False, vcenter=False, bottom=False, 
                font=None, bgcolor=None, margin=5, indent=0, prop=None):

        super(IconCell, self).__init__(left, center, right, top, vcenter, bottom,
                                                font, bgcolor, margin, indent, prop)
        self._label = label
        self.setIcon(icon)

    def calcHeight(self, dc, width):
        if self._label:
            if self._font:
                org = dc.selectObject(self._font)
            try:
                labelheight = dc.getTextExtent(self._label)[1]
            finally:
                if self._font:
                    dc.selectObject(org)
        else:
            labelheight = 0
        
        return max(self._iconsize[1], labelheight)+self._margin*2

    def setIcon(self, icon):
        self._icon = icon
        self._iconsize = icon.getBitmap().getSize()

    def _draw(self, wnd, dc):
        super(IconCell, self)._draw(wnd, dc)

        if self._font:
            org = dc.selectObject(self._font)
        try:
            l, t, r, b = self._rc
            l += self._indent
            margin = self._margin
            rc = (l+margin, t+margin, r-margin, b-margin)
            
            if rc[0] >= rc[2] or rc[1] >= rc[3]:
                return
                
            if self._label:
                labelsize = dc.getTextExtent(self._label)
            else:
                labelsize = (0, 0)

            if self._alignCenter:
                x = rc[0] + (rc[2] - rc[0] - (self._iconsize[0]+labelsize[0]+self.LABELMARGIN)) / 2
            elif self._alignRight:
                x = rc[2] - (self._iconsize[0]+labelsize[0]+self.LABELMARGIN)
            else:
                x = rc[0]
                
            if self._alignVcenter:
                y = rc[1] + (rc[3] - rc[1] - max(self._iconsize[1], labelsize[1])) / 2
            elif self._alignBottom:
                y = rc[3] - max(self._iconsize[1], labelsize[1])
            else:
                y = rc[1]
            
            rgn = gdi.RectRgn(rc)
            cur = dc.getClipRgn()
            orgmode = dc.setBkMode(transparent=True)
            try:
                dc.selectClipRgn(rgn)
                if self._iconsize[1] >= labelsize[1]:
                    icon_y = y
                else:
                    icon_y = y + (labelsize[1]-self._iconsize[1])/2
                dc.drawIcon((x, icon_y), self._icon, normal=True)

                if self._label:
                    label_x = x+self._iconsize[0]+self.LABELMARGIN
                    if self._iconsize[1] >= labelsize[1]:
                        label_y = y + (self._iconsize[1]-labelsize[1])/2
                    else:
                        label_y = y
                    dc.setBkMode
                    dc.textOut(self._label, (label_x, label_y))
            finally:
                dc.selectClipRgn(cur)
                dc.setBkMode(orgmode)
        finally:
            if self._font:
                dc.selectObject(org)
        
class ControlGridWnd(GridWnd):
    def _prepare(self, kwargs):
        super(ControlGridWnd, self)._prepare(kwargs)
        
    def wndReleased(self):
        super(ControlGridWnd, self).wndReleased()

    def _updateCellRect(self):
        for row, col, cell, cellrc in self._iterCellRect():
            cell.setRect(self._gridPane, cellrc)

    def _updateCellRect(self):
        self._gridPane._deferCtrls = self.beginDeferWindowPos(
                        len(self._grid.getCols())*len(self._grid.getRows()))
        try:
            super(ControlGridWnd, self)._updateCellRect()
        finally:
            self.endDeferWindowPos(self._gridPane._deferCtrls)
            self._gridPane._deferCtrls = None


    def createCell(self, cell):
        cell.createCell(self._gridPane)


