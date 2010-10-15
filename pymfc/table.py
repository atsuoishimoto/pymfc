# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import sys
from pymfc import wnd, gdi, util
from pymfc.wnd import *

class _Border(object):
    ALLOW_DRAG = True
    def __init__(self, start, end, pos, width):
        self._start = start
        self._end = end
        self._pos = pos
        self._width = width
        self._preserved = None

    def getPos(self):
        return self._pos
        
    def setPos(self, pos):
        self._pos = pos

    def getRect(self):
        pass
    
    def getEnds(self):
        return self._start, self._end
        
    def setEnds(self, start, end):
        self._start = start
        self._end = end
        
    def getEndsPos(self):
        s = 0
        if self._start:
            s = self._start.getPos()
        e = sys.maxint
        if self._end:
            e = self._end.getPos()
        return s, e
        
    def setPreserved(self, pos):
        self._preserved = pos

    def getPreserved(self):
        return self._preserved
        

    def draw(self, wnd, dc, wndrc):
        rc = self.getRect()
        rc = util.rectIntersection(rc, wndrc)
#        print ">>", self, self._end, self.getRect(), rc
        if rc:
            dc.fillSolidRect(rc, wnd.BORDER_COLOR);
        
class _HorzBorder(_Border):
    def getRect(self):
        s, e = self.getEndsPos()
        return s, self._pos, e, self._pos+self._width

    def getDragCursor(self):
        return gdi.Cursor(sizens=True)

class _VertBorder(_Border):
    def getRect(self):
        s, e = self.getEndsPos()
        return self._pos, s, self._pos+self._width, e

    def getDragCursor(self):
        return gdi.Cursor(sizewe=True)

class Cell(object):
    def __init__(self, left, top, right, bottom):
        self._reservedWidth = None
        self.setBorders(left, top, right, bottom)
        
    def getBorders(self):
        return (self._left, self._top, self._right, self._bottom)

    def setBorders(self, left, top, right, bottom):
        self._left = left
        self._top = top
        self._right = right
        self._bottom = bottom
    
    def getRect(self):
        left=top=0
        right = bottom = sys.maxint
        
        if self._left:
            left = self._left.getPos()
        if self._top:
            top = self._top.getPos()
        if self._right:
            right = self._right.getPos()
        if self._bottom:
            bottom = self._bottom.getPos()
        
        return left, top, right, bottom

    def getClientRect(self):
        l, t, r, b = self.getRect()
        if self._left:
            l += self._left._width
        if self._top:
            t += self._top._width
        return l, t, r, b

    def resized(self, table, wndrc):
        pass
        
    def _removed(self, table):
        pass
    
    def _splitted(self, table, newcell):
        pass

class WndCell(Cell):
    def __init__(self, left, top, right, bottom):
        super(WndCell, self).__init__(left, top, right, bottom)
        self._wnd = None

    def setWnd(self, wnd):
        self._wnd = wnd
        wndrc = wnd._parent.getClientRect()
        
        rc = util.rectIntersection(wndrc, self.getClientRect())
        if not rc:
            rc = (0,0,0,0)
        self._wnd.setWindowPos(pos=rc[0:2], size=(rc[2]-rc[0], rc[3]-rc[1]))

    def getWnd(self):
        return self._wnd

    def resized(self, table, wndrc):
        if self._wnd:
            l, t, r, b = self.getClientRect()
            rc = util.rectIntersection(wndrc, (l, t, r, b))
            if not rc:
                l, t, r, b = (0,0,0,0)
            else:
                if not self._right: # if rightmost pane
                    r = rc[2]
                
                if not self._bottom: # if bottommost pane
                    b = rc[3]
            
            self._wnd.setWindowPos(pos=(l, t), size=(r-l, b-t))
        
    def _removed(self, table):
        if self._wnd:
            w = self._wnd
            self._wnd = None
            w.destroy()
            
#class Table(Wnd):
class Table(object):

#    CHILDID=0xe900
#    STYLE = WndStyle(visible=1, child=1, clientedge=0)

    DRAG_MARGIN = 5
    BORDER_WIDTH = 5
    MERGE_BORDER = False
    BORDER_COLOR = 0xc0c0c0
    
    def __init__(self, parent, cell=Cell):
        self._cellCls = cell
        self._wnd = parent
        self._dragging = None
        self._cells = []
        self._addCell(self._cellCls(None, None, None, None))
        
        self.msglistener = wnd.Listeners({'CELLDRAGGED': 'celldragged'})

        parent.msgproc.PAINT = self.__onPaint
        parent.msgproc.SETCURSOR = self.__onSetCursor
        parent.msgproc.LBUTTONDOWN = self.__onLBtnDown
        parent.msgproc.LBUTTONUP = self.__onLBtnUp
        parent.msgproc.MOUSEMOVE = self.__onMouseMove
        parent.msgproc.CANCELMODE = self.__onCancelMode
        parent.msglistener.SIZE = self.__onSize
        parent.msglistener.DESTROY = self.__onDestroy
        

    def _invertBorder(self, dc, rc):
        wndrc = self._wnd.getClientRect()
        rc = util.rectIntersection(rc, wndrc)
        
        pattern = '\x55\x00\xaa\x00'*4
        bmp = gdi.Bitmap(cx=8, cy=8, panes=1, bitsperpel=1, bits=pattern)
        _brush = gdi.PatternBrush(bmp)

        orgbrush = dc.selectObject(_brush)
        try:
            dc.patBlt(rc, invert=True)
        finally:
            dc.selectObject(orgbrush)
        
    def _addCell(self, cell):
        self._cells.append(cell)
        
    def _delCell(self, cell):
        cell._removed(self)
        self._cells.remove(cell)

    def _getDragRange(self, border):
        if isinstance(border, _HorzBorder):
            top = bottom = None
            for cell in self._cells:
                l, t, r, b = cell.getBorders()
                if t is border:
                    if not bottom or (b and (b.getPos() < bottom.getPos())):
                        bottom = b
                elif b is border:
                    if not top or (t and (top.getPos() < t.getPos())):
                        top = t
            return top, bottom
        else:
            left = right = None
            for cell in self._cells:
                l, t, r, b = cell.getBorders()
                if l is border:
                    if not right or (r and (r.getPos() < right.getPos())):
                        right = r
                elif r is border:
                    if not left or (l and (left.getPos() < l.getPos())):
                        left = l
            return left, right
            
    def _getBorders(self):
        ret = {}
        for cell in self._cells:
            for b in cell.getBorders():
                if b:
                    ret[b] = None
        return ret.keys()
        
    def resized(self):
        if self._wnd.getHwnd():
            wndrc = self._wnd.getClientRect()
            for cell in self._cells:
                cell.resized(self, wndrc)

    def clearCells(self):
        self._cells = []
        self._dragging = None
        self._dragRange = None
        
    def getBorderAt(self, pos):
        for border in self._getBorders():
            if util.ptInRect(pos, border.getRect()):
                return border
                
    def getCellAt(self, pos):
        for cell in self._cells:
            rc = cell.getRect()
            if util.ptInRect(pos, rc):
                return cell

    def splitCellHorz(self, cell, y, celltype=None):
        if not celltype:
            celltype = self._cellCls
            
        left, top, right, bottom = cell.getBorders()
        if bottom:
            assert y < bottom.getPos()

        newBorder = _HorzBorder(left, right, y, self.BORDER_WIDTH)
        cell.setBorders(left, top, right, newBorder)
        newCell = celltype(left, newBorder, right, bottom)
        cell._splitted(self, newCell)
        self._addCell(newCell)
        self.resized()
        return newCell
        
    def splitCellVert(self, cell, x, celltype=None):
        if not celltype:
            celltype = self._cellCls

        left, top, right, bottom = cell.getBorders()
        newBorder = _VertBorder(top, bottom, x, self.BORDER_WIDTH)
        
        cell.setBorders(left, top, newBorder, bottom)
        newCell = celltype(newBorder, top, right, bottom)
        cell._splitted(self, newCell)
        self._addCell(newCell)
        self.resized()
        return newCell
        
    def addHorzBorder(self, pos):
        cell = self.getCellAt(pos)
        return self.splitCellHorz(cell, pos[1])

    def addVertBorder(self, pos):
        cell = self.getCellAt(pos)
        return self.splitCellVert(cell, pos[0])

    def setBorderPos(self, border, pos):
        border.setPos(pos)
        self.resized()

    def getCells(self):
        return self._cells[:]

    def beginSplit(self, pos, horz):
        if self._dragging:
            return
        cell = self.getCellAt(pos)
        if not cell:
            return
        l, t, r, b = cell.getBorders()
        if horz:
            self._dragRange = (t, b)
            self._dragging = _HorzBorder(l, r, pos[1], self.BORDER_WIDTH)
        else:
            self._dragRange = (l, r)
            self._dragging = _VertBorder(t, b, pos[0], self.BORDER_WIDTH)
        
        self._splitNew = True
        self._wnd.setCapture()
        self._inverted = self._dragging.getRect()
        dc = gdi.ClientDC(self._wnd)
        try:
            self._invertBorder(dc, self._inverted)
        finally:
            dc.release()

        
    def __onPaint(self, msg):
        dc = gdi.PaintDC(msg.wnd)
        rc = self._wnd.getClientRect()
        try:
#            dc.fillSolidRect(rc, 0xffffff)
            for border in self._getBorders():
                border.draw(self, dc, rc)
        finally:
            dc.endPaint()

    def __onSetCursor(self, msg):
        border = self.getBorderAt(self._wnd.getCursorPos())
        if border and border.ALLOW_DRAG:
            cursor = border.getDragCursor()
        else:
            cursor = gdi.Cursor(arrow=True)
        
        cursor.setCursor()
        return True

    def __onLBtnDown(self, msg):
        if self._dragging:
            return
        border = self.getBorderAt((msg.x, msg.y))
        if border:
            if not border.ALLOW_DRAG:
                return

            self._dragging = border
            self._dragRange = self._getDragRange(self._dragging)
            
            self._splitNew = False
            self._wnd.setCapture()
            self._inverted = self._dragging.getRect()
            dc = gdi.ClientDC(self._wnd)
            try:
                self._invertBorder(dc, self._inverted)
            finally:
                dc.release()
        
    def __onMouseMove(self, msg):
        if not self._dragging:
            return
        wndrc = self._wnd.getClientRect()
        x, y = msg.x, msg.y
        left, top, right, bottom = self._dragging.getRect()
        if isinstance(self._dragging, _HorzBorder):
            if self._dragRange[0]:
                ymin = self._dragRange[0].getPos()
            else:
                ymin = 0
            
            if self._dragRange[1]:
                ymax = self._dragRange[1].getPos()
            else:
                ymax = wndrc[3]
            
            ymin += self.DRAG_MARGIN + self.BORDER_WIDTH
            ymax -= self.DRAG_MARGIN + self.BORDER_WIDTH
            
            if y < ymin:
                y = ymin
            elif y > ymax:
                y = ymax
            rc = left, y, right, y+self.BORDER_WIDTH
        else:
            if self._dragRange[0]:
                xmin = self._dragRange[0].getPos()
            else:
                xmin = 0
            
            if self._dragRange[1]:
                xmax = self._dragRange[1].getPos()
            else:
                xmax = wndrc[2]

            xmin += self.DRAG_MARGIN + self.BORDER_WIDTH
            xmax -= self.DRAG_MARGIN + self.BORDER_WIDTH

            if x < xmin:
                x = xmin
            elif x > xmax:
                x = xmax
            rc = x, top, x+self.BORDER_WIDTH, bottom

        dc = gdi.ClientDC(self._wnd)
        try:
            self._invertBorder(dc, self._inverted)
            self._invertBorder(dc, rc)
            self._inverted = rc
        finally:
            dc.release()
        

    # todo: unify these mergeToXXX()'s
    def mergeToUpper(self, mergeFrom, mergeTo):
        removeCells = []
        updateCells = []
        for cell in self._cells:
            l, t, r, b = cell.getBorders()
            if b is mergeFrom:
                if t is mergeTo:
                    removeCells.append(cell)
                else:
                    break
            if t is mergeFrom:
                updateCells.append(cell)
        else:
            for cell in removeCells:
                self._delCell(cell)
            
            for cell in updateCells:
                l, t, r, b = cell.getBorders()
                if l:
                    s, e = l.getEnds()
                    if s is mergeFrom:
                        l.setEnds(mergeTo, e)
                if r:
                    s, e = r.getEnds()
                    if s is mergeFrom:
                        r.setEnds(mergeTo, e)
                cell.setBorders(l, mergeTo, r, b)
            return True
        

    def mergeToLower(self, mergeFrom, mergeTo):
        removeCells = []
        updateCells = []
        for cell in self._cells:
            l, t, r, b = cell.getBorders()
            if t is mergeFrom:
                if b is mergeTo:
                    removeCells.append(cell)
                else:
                    break
            if b is mergeFrom:
                updateCells.append(cell)
        else:
            for cell in removeCells:
                self._delCell(cell)

            for cell in updateCells:
                l, t, r, b = cell.getBorders()
                if l:
                    s, e = l.getEnds()
                    if e is mergeFrom:
                        l.setEnds(s, mergeTo)
                if r:
                    s, e = r.getEnds()
                    if e is mergeFrom:
                        r.setEnds(s, mergeTo)
                cell.setBorders(l, t, r, mergeTo)

            return True
        
    def mergeToLeft(self, mergeFrom, mergeTo):
        removeCells = []
        updateCells = []
        for cell in self._cells:
            l, t, r, b = cell.getBorders()
            if r is mergeFrom:
                if l is mergeTo:
                    removeCells.append(cell)
                else:
                    break
            if l is mergeFrom:
                updateCells.append(cell)
        else:
            for cell in removeCells:
                self._delCell(cell)
            
            for cell in updateCells:
                l, t, r, b = cell.getBorders()
                if t:
                    s, e = t.getEnds()
                    if s is mergeFrom:
                        t.setEnds(mergeTo, e)
                if b:
                    s, e = b.getEnds()
                    if s is mergeFrom:
                        b.setEnds(mergeTo, e)
                cell.setBorders(mergeTo, t, r, b)

            return True
        
    def mergeToRight(self, mergeFrom, mergeTo):
        removeCells = []
        updateCells = []
        for cell in self._cells:
            l, t, r, b = cell.getBorders()
            if l is mergeFrom:
                if r is mergeTo:
                    removeCells.append(cell)
                else:
                    break
            if r is mergeFrom:
                updateCells.append(cell)
        else:
            for cell in removeCells:
                self._delCell(cell)
            
            for cell in updateCells:
                l, t, r, b = cell.getBorders()
                if t:
                    s, e = t.getEnds()
                    if e is mergeFrom:
                        t.setEnds(s, mergeTo)
                if b:
                    s, e = b.getEnds()
                    if e is mergeFrom:
                        b.setEnds(s, mergeTo)
                cell.setBorders(l, t, mergeTo, b)
        
            return True

    def _moveBorder(self, merge):
        wndrc = self._wnd.getClientRect()
        if isinstance(self._dragging, _HorzBorder):
            p = self._inverted[1]
            top, bottom = self._dragRange

            if top: 
                toppos = top.getPos()
            else:   
                toppos = wndrc[1]
            
            if p-toppos <= self.DRAG_MARGIN + self.BORDER_WIDTH:
                # merge to upper border
                if merge:
                    self.mergeToUpper(self._dragging, top)
                    return
                else:
                    p = toppos+self.DRAG_MARGIN + self.BORDER_WIDTH
            else:
                if bottom:
                    botpos = bottom.getPos()
                else:
                    botpos = wndrc[3]
                if botpos - p <= self.DRAG_MARGIN + self.BORDER_WIDTH:
                    # merge to lower border
                    if merge:
                        self.mergeToLower(self._dragging, bottom)
                        return
                    else:
                        p = botpos - (self.DRAG_MARGIN + self.BORDER_WIDTH)
                
            # not merged
            self._dragging.setPos(p)

            if self._dragging.getPreserved():
                self._dragging.setPreserved(wndrc[3]-p)

        else:
            # vert
            p = self._inverted[0]
            left, right = self._dragRange

            if left: 
                leftpos = left.getPos()
            else:   
                leftpos = wndrc[0]
            if p-leftpos <= self.DRAG_MARGIN + self.BORDER_WIDTH:
                # merge to left border
                if merge:
                    self.mergeToLeft(self._dragging, left)
                    return
                else:
                    p = leftpos + self.DRAG_MARGIN + self.BORDER_WIDTH
            else:
                if right: 
                    rightpos = right.getPos()
                else:   
                    rightpos = wndrc[2]
                if rightpos - p <= self.DRAG_MARGIN + self.BORDER_WIDTH:
                    # merge to right border
                    if merge:
                        self.mergeToRight(self._dragging, right)
                        return
                    else:
                        p = rightpos - (self.DRAG_MARGIN + self.BORDER_WIDTH)

            # not merged
            self._dragging.setPos(p)

            if self._dragging.getPreserved():
                self._dragging.setPreserved(wndrc[2]-p)
            
    def __onLBtnUp(self, msg):
        if self._dragging:
            if self._splitNew:
                if isinstance(self._dragging, _HorzBorder):
                    self.addHorzBorder(self._inverted[0:2])
                else:
                    self.addVertBorder(self._inverted[0:2])
            else:
                self._moveBorder(self.MERGE_BORDER)
                
            self.__onCancelMode(msg)
            self.resized()
            self.msglistener.run("celldragged", self)
            
    def __onCancelMode(self, msg):
        if not self._dragging:
            return
        self._dragging = None
        self._wnd.invalidateRect(None)
        self._wnd.releaseCapture()
    

    def adjustPreservedCell(self):

        MIN_MARGIN = self.DRAG_MARGIN + self.BORDER_WIDTH

        borders = self._getBorders()
        horzs = []
        verts = []
        for border in borders:
            if isinstance(border, _HorzBorder):
                horzs.append((border.getPos(), border))
            else:
                verts.append((border.getPos(), border))

        wndrc = self._wnd.getClientRect()

        verts.sort()
        if verts:
            rightmost = verts[-1][1]
            preserve = rightmost.getPreserved()
            if preserve:
                newpos = max(MIN_MARGIN, wndrc[2]-preserve)
            
                if len(verts) >= 2:
                    next = verts[-2][1]
                    newpos = max(next.getPos()+MIN_MARGIN, newpos)
                    
                rightmost.setPos(newpos)
            
        horzs.sort()
        if horzs:
            bottommost = horzs[-1][1]
            preserve = bottommost.getPreserved()
            if preserve:
                newpos = max(MIN_MARGIN, wndrc[3]-preserve)
            
                if len(horzs) >= 2:
                    next = horzs[-2][1]
                    newpos = max(next.getPos()+MIN_MARGIN, newpos)
                    
                bottommost.setPos(newpos)


    def __onSize(self, msg):
        self.adjustPreservedCell()
        self.resized()

    def __onDestroy(self, msg):
        self.clearCells()
        self.msglistener.clear()
        self.msglistener = None
        self._wnd = None

