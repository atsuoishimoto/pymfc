import time
import itertools
from pymfc import gdi, wnd, util

def _timetime(f):
    def w(*args, **kargs):
        t = time.clock()
        ret = f(*args, **kargs)
        print "[%s] %f" % (f.func_name, time.clock()-t)
        return ret
    return f
    return w
    
class RowInfo(object):
    def __init__(self):
        self._height = None
        self._rect = (0,0,0,0)

    def getHeight(self):
        return self._height

    def updateHeight(self, dc, width, wnd, idx):
        self._height = self.calcHeight(dc, width, wnd, idx)
        
    def setRect(self, rc):
        self._rect = rc
        self._onSetRect()
    
    def _onSetRect(self):
        pass
        
    def getRect(self):
        return self._rect
        
    def detached(self):
        pass
        
    def onFocusChanged(self, focused, wnd, focusidx):
        pass

    def onLBtnDown(self, msg, idx):
        pass
        
    def onLBtnDblClk(self, msg, idx):
        pass
        
    def onMouseMove(self, msg, idx):
        pass
        
    def calcHeight(self, dc, width, wnd, idx):
        raise NotImplementedError

    def onPaint(self, dc, wnd, idx):
        pass

class RowList(wnd.Wnd):
    STYLE=wnd.Wnd.STYLE(border=True)
    def _prepare(self, kwargs):
        super(RowList, self)._prepare(kwargs)
        self._multisel = kwargs.get('multisel', False)
        self._rows = []
        self._changedRows = []
        self._visibleRows = [0,0]
        self._focusIdx = None
        self._selectedIdxes = set()
        self._rangeSel = None

        self.msgproc.PAINT = self._onPaint
        self.msgproc.SETCURSOR = self._onSetCursor
        self.msgproc.GETDLGCODE = self._onGetDlgCode

        self.msglistener.SIZE = self._onSize
        self.msglistener.VSCROLL = self._onVScroll
        self.msglistener.LBUTTONDOWN = self._onLBtnDown
        self.msglistener.LBUTTONDBLCLK = self._onLBtnDblClk
        self.msglistener.MOUSEMOVE = self._onMouseMove

        self.msglistener.KEYDOWN = self._onKeyDown

    def wndReleased(self):
        super(RowList, self).wndReleased()

        for row in self._rows:
            row.detached()
        self._rows = None
        self._changedRows = None
        self._visibleRows = None

    def _callUpdateHeight(self, rows, idx):
        l, t, r, b = self.getClientRect()
        width = r-l
        dc = gdi.ClientDC(self)
        try:
            for row in rows:
                row.updateHeight(dc, width, self, idx)
                idx += 1
        finally:
            dc.release()

    @_timetime
    def _updateVisibleRows(self):

        l, t, r, b = self.getClientRect()
        h = b - t
        
        pos = start = self._visibleRows[0]
        total = 0
        nRows = len(self._rows)

        while (total <= h) and (pos < nRows):
            row = self._rows[pos]
            height = row.getHeight()
            b = t + height
            rc = (l, t, r, b)
            row.setRect(rc)
            t=b
            total += height
            pos += 1
        
        for idx in range(pos, self._visibleRows[1]):
            if idx < nRows:
                self._rows[idx].setRect((0,0,0,0))
        
        self._visibleRows = [start, pos]

    def _getRowRect(self, idx):
        if self._visibleRows[0] <= idx < self._visibleRows[1]:
            return self._rows[idx].getRect()

    def getRowAt(self, pos):
        for idx in range(*self._visibleRows):
            rc = self._rows[idx].getRect()
            if util.ptInRect(pos, rc):
                return idx

    def _updateScrollBar(self):
        if not self._rows:
            self.showScrollBar(vert=True, horz=False, show=False)
            return

        top = self._getTopVisibleRow()
        last = self._getLastVisibleRow()

        if last-top+1 >= len(self._rows):
            self.showScrollBar(vert=True, horz=False, show=False)
        else:
            self.showScrollBar(vert=True, horz=False, show=True)
            maxpos = max(0, len(self._rows)-1)
            self.setScrollInfo(vert=True, min=0, max=maxpos, pos=self._getTopVisibleRow(), redraw=True)

    def _getTopVisibleRow(self):
        curtop, curend = self._visibleRows
        return curtop
        
    def _getLastVisibleRow(self):
        l, t, r, b = self.getClientRect()
        curtop, curend = self._visibleRows
        if curend-curtop <=1:
            ret = curtop+1
        else:
            ret = curend-1
            
            while ret > curtop:
                rc = self._getRowRect(ret)
                if rc and rc[3] <= b:
                    break
                ret -= 1
            if ret == curtop:
                ret += 1
        
        if ret >= len(self._rows):
            ret = len(self._rows)-1
        return ret
        
    def appendRows(self, rows):
        self._callUpdateHeight(rows, len(self._rows))
        self._rows.extend(rows)
        self._updateVisibleRows()
            
        self._updateScrollBar()
        
    def clearRows(self):
        for row in self._rows:
            row.detached()
            
        self._rows = []
        self._visibleRows = [0, 0]
        self._updateScrollBar()
        
    def removeRow(self, row):
        assert row in self._rows
        self._rows = [_row for _row in self._rows if _row is not row]
        self._updateVisibleRows()
        self._updateScrollBar()
        
    @_timetime
    def setFocusIdx(self, idx):
        assert idx is not None
        cur = self._focusIdx

        currow = self.getFocusRow()
        self._focusIdx = idx
        if currow:
            currow.onFocusChanged(False, self, cur)

        if self._focusIdx is not None:
            row = self.getFocusRow()
            if row:
                row.onFocusChanged(True, self, idx)
            

        if self._changedRows:
            self._updateVisibleRows()
            self._updateScrollBar()
            self._changedRows = []
            
        self.invalidateRect(None, erase=False)

    def getFocusRow(self):
        if self._focusIdx is not None:
            if self._focusIdx < len(self._rows):
                return self._rows[self._focusIdx]

    def isFocused(self, idx):
        return self._focusIdx == idx
        
    def isSelected(self, idx):
        return idx in self._selectedIdxes

    def rowHeightChanged(self, idx):
        row = self._rows[idx]
        curheight = row.getHeight()

        self._callUpdateHeight([row], idx)
        
        newheight = row.getHeight()
        
        self._changedRows.append((idx, row))
        
    def _locate(self, idx, top=False, mid=False, bot=False):
        if not self._rows:
            return
        
        wndrc = self.getClientRect()
        rowrc = [wndrc[0], 0, wndrc[1], self._rows[idx].getHeight()]
        if not top:
            if mid:
                adjust = (wndrc[3] - wndrc[1]) / 2
            elif bot:
                adjust = wndrc[3] - wndrc[1] - (rowrc[3]-rowrc[1])
            else:
                assert 0 # one of top, mid or bot should be specified.
            
            newtop = idx
            for n in range(idx-1, -1, -1):
                row = self._rows[n]
                height = row.getHeight()
                adjust -= height
                if adjust < 0:
                    break
                newtop = n
        else:
            newtop = idx
        
        visibles = set(range(*self._visibleRows))

        self._visibleRows = [newtop, newtop]
        self._updateVisibleRows()
        
        hiddens = visibles - set(range(*self._visibleRows))
        for hidden in hiddens:
            row = self._rows[hidden]
            row.setRect((0,0,0,0))

    def ensureVisible(self, idx, top=False, mid=False, bot=False):
        rowrect = self._getRowRect(idx)

        if rowrect:
            if rowrect[1] < 0:
                self._locate(idx, top, mid, bot)
            else:
                clientrc = self.getClientRect()
                if rowrect[3] > clientrc[3]:
                    self._locate(idx, top, mid, bot)
        else:
            self._locate(idx, top, mid, bot)

    @_timetime
    def caretDown(self):
        if self._focusIdx is not None:
            if self._focusIdx < len(self._rows)-1:
                self.setFocusIdx(self._focusIdx+1)
                self.ensureVisible(self._focusIdx, bot=True)
                self._updateScrollBar()
                
    @_timetime
    def caretUp(self):
        if self._focusIdx is not None:
            if self._focusIdx > 0:
                self.setFocusIdx(self._focusIdx-1)
                self.ensureVisible(self._focusIdx, top=True)
                self._updateScrollBar()

    def caretPageDown(self):
        if self._focusIdx is not None:
            self.ensureVisible(self._focusIdx, mid=True)
            
            newtop = self._getLastVisibleRow()
            
            self._locate(newtop, top=True)
            self.setFocusIdx(newtop)
            self.ensureVisible(newtop, top=True)

            self._updateScrollBar()

    def caretPageUp(self):
        if self._focusIdx is not None:
            newbot = self._visibleRows[0]
            self._locate(newbot, bot=True)
            self.setFocusIdx(self._visibleRows[0])

            self._updateScrollBar()

    def caretTop(self):
        if self._focusIdx is not None:
            self.ensureVisible(0, top=True)
            self.setFocusIdx(0)

            self._updateScrollBar()

    def caretBottom(self):
        if self._focusIdx is not None:
            idx = len(self._rows)-1
            self.ensureVisible(idx, top=True)
            self.setFocusIdx(idx)

            self._updateScrollBar()

    def _prepareDC(self, dc):
        pass
        
    def _onPaint(self, msg):
        dc = gdi.PaintDC(msg.wnd)
        self._prepareDC(dc)
        try:
            bot = 0
            for idx in range(*self._visibleRows):
                row = self._rows[idx]
                rc = row.getRect()
                row.onPaint(dc, self, idx)
                bot = rc[3]
            
            if self.WNDCLASS_BACKGROUNDCOLOR is not None:
                l, t, r, b = self.getClientRect()
                if bot <= b:
                    dc.fillSolidRect((l, bot, r, b), self.WNDCLASS_BACKGROUNDCOLOR)
        finally:
            dc.endPaint()

    def _onGetDlgCode(self, msg):
        return 4  # wantallkeys

    def _onSetCursor(self, msg):
        return msg.wnd.defWndProc(msg)
        
    def _lineDown(self):
        top = self._getTopVisibleRow()
        if top+1 < len(self._rows):
            self._locate(top+1, top=True)
            self.invalidateRect(None, erase=False)
            self._updateScrollBar()

    def _pageDown(self):
        newtop = self._getLastVisibleRow()
        
        self._locate(newtop, top=True)
        self.invalidateRect(None, erase=False)
        self._updateScrollBar()

    def _lineUp(self):
        top = self._getTopVisibleRow()
        if top:
            self._locate(top-1, top=True)
            self.invalidateRect(None, erase=False)
            self._updateScrollBar()

    def _pageUp(self):
        top = self._getTopVisibleRow()
        if top:
            self._locate(top, bot=True)
            self.invalidateRect(None, erase=False)
            self._updateScrollBar()

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
        elif msg.thumbtrack:
            info = self.getScrollInfo(vert=True)
            newpos = info.trackpos
            top = min(newpos, len(self._rows)-1)
            self._locate(top, top=True)
            self._updateScrollBar()
            self.invalidateRect(None, erase=False)
            
            
            
    def _rangeSelStart(self):
        if not self._multisel:
            return
        
        if self._rangeSel is not None:
            return

        if self._focusIdx is None:
            return

        self._rangeSel = (self._focusIdx, self._focusIdx)
        self._selectedIdxes.add(self._focusIdx)
        
        self.invalidateRect(None, erase=False)

    def _rangeSelUpdate(self, to):
        if not self._multisel:
            return

        if not self._rangeSel:
            return

        start = self._rangeSel[0]
        self._rangeSel = (start, to)

        if start == to:
            self._selectedIdxes = set([start])
            self.invalidateRect(None, erase=False)
            return

        selStart = min(start, to)
        selEnd = max(start, to)
        self._selectedIdxes = set(range(selStart, selEnd+1))
        
        self.invalidateRect(None, erase=False)

    def _rangeSelClear(self):
        self._selectedIdxes = set()
        if self._focusIdx is not None:
            self._selectedIdxes.add(self._focusIdx)

        self._rangeSel = None
        self.invalidateRect(None, erase=False)

    def _onSize(self, msg):
        self._callUpdateHeight(self._rows, 0)
        self._updateVisibleRows()
        self._updateScrollBar()
        
    def _onLBtnDown(self, msg):
        self.setFocus()
        pos = msg.x, msg.y
        idx = self.getRowAt(pos)

        shift = wnd.getKeyState(wnd.KEY.SHIFT).down
        ctrl = wnd.getKeyState(wnd.KEY.CONTROL).down
        alt = wnd.getKeyState(wnd.KEY.MENU).down

        select = toggle = False
        if self._multisel:
            if shift and not alt and not ctrl:
                select = True
            elif not shift and not alt and ctrl:
                toggle = True
            

        if idx is not None:
            if select:
                self._rangeSelStart()
                
            self.setFocusIdx(idx)
            self.ensureVisible(idx, mid=True)
                
            if select:
                self._rangeSelUpdate(idx)
            elif toggle:
                self._rangeSel = None
                if idx in self._selectedIdxes:
                    self._selectedIdxes.remove(idx)
                else:
                    self._selectedIdxes.add(idx)
            else:
                self._rangeSelClear()
        
            self._rows[idx].onLBtnDown(msg, idx)

    def _onLBtnDblClk(self, msg):
        pos = msg.wnd.getCursorPos()
        idx = self.getRowAt(pos)
        if idx is not None:
            self._rows[idx].onLBtnDblClk(msg, idx)
        
    def _onMouseMove(self, msg):
        pos = msg.wnd.getCursorPos()
        idx = self.getRowAt(pos)
        if idx is not None:
            self._rows[idx].onMouseMove(msg, idx)
        
    def _onKeyDown(self, msg):
        key = msg.key
        shift = wnd.getKeyState(wnd.KEY.SHIFT).down
        ctrl = wnd.getKeyState(wnd.KEY.CONTROL).down
        alt = wnd.getKeyState(wnd.KEY.MENU).down

        select = False
        if self._multisel:
            if shift and not alt and not ctrl:
                select = True

        if key == wnd.KEY.DOWN:
            if select:
                self._rangeSelStart()
            self.caretDown()

            if select:
                self._rangeSelUpdate(self._focusIdx)
            else:
                self._rangeSelClear()
                
        elif key == wnd.KEY.UP:
            if select:
                self._rangeSelStart()

            self.caretUp()

            if select:
                self._rangeSelUpdate(self._focusIdx)
            else:
                self._rangeSelClear()

        elif msg.key == wnd.KEY.PGDN:
            if select:
                self._rangeSelStart()

            self.caretPageDown()

            if select:
                self._rangeSelUpdate(self._focusIdx)
            else:
                self._rangeSelClear()

        elif msg.key == wnd.KEY.PGUP:
            if select:
                self._rangeSelStart()

            self.caretPageUp()

            if select:
                self._rangeSelUpdate(self._focusIdx)
            else:
                self._rangeSelClear()

        elif msg.key == wnd.KEY.HOME:
            if select:
                self._rangeSelStart()

            self.caretTop()

            if select:
                self._rangeSelUpdate(self._focusIdx)
            else:
                self._rangeSelClear()

        elif msg.key == wnd.KEY.END:
            if select:
                self._rangeSelStart()

            self.caretBottom()

            if select:
                self._rangeSelUpdate(self._focusIdx)
            else:
                self._rangeSelClear()


class BtnRowList(RowList):
    _activeBtn = None

    def _prepare(self, kwargs):
        super(BtnRowList, self)._prepare(kwargs)
        self.msglistener.MOUSELEAVE = self._onMouseLeave
        
    def wndReleased(self):
        super(BtnRowList, self).wndReleased()
        self._activeBtn = None
        
    def _onMouseMove(self, msg):
        ret = super(BtnRowList, self)._onMouseMove(msg)
        self.trackMouseEvent(leave=True)

        pos = msg.wnd.getCursorPos()
        idx = self.getRowAt(pos)
        if idx is None:
            self.btnUpdated(None)
        return ret

    def btnUpdated(self, btn):
        if self._activeBtn:
            self._activeBtn.updateBorder(self, self.getCursorPos())

        self._activeBtn = btn

    def _onMouseLeave(self, msg):
        self.btnUpdated(None)

class BtnRowInfo(RowInfo):
    def detached(self):
        for btn in self.getButtons():
            btn.destroy()

    def onMouseMove(self, msg, idx):
        pos = msg.wnd.getCursorPos()
        for btn in self.getButtons():
            if btn.onMouseMove(msg.wnd, pos):
                msg.wnd.btnUpdated(btn)

    def onMouseLeave(self, msg, idx):
        pos = msg.wnd.getCursorPos()
        for btn in self.getButtons():
            if btn.onMouseMove(msg.wnd, pos):
                msg.wnd.btnUpdated(btn)
        
    def onLBtnDown(self, msg, idx):
        for btn in self.getButtons():
            if btn.onLBtnDown(msg.wnd, msg.wnd.getCursorPos()):
                msg.wnd.btnUpdated(btn)
    
