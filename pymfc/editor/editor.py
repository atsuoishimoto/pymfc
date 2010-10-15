import time
import pymfc
from pymfc import wnd, gdi, util
from pymfc.editor import buffer, screen, mode

class _EditorWnd(wnd.Wnd):
    MARGIN_LEFT = 5
    def _prepare(self, kwargs):
        super(_EditorWnd, self)._prepare(kwargs)

        self._screen = None
        self._buf = None
        self._conf = None
        self._mode = None
        self._caret = None
        self._idle = None
        self._lineNoWidth = 0

        self._hasCaret = False
        self._hScrollPos = 0
        self._curRows = []
        self._mouseSelecting = False
        self._mouseBlockSelecting = False
        
        self._mouseCaptureTimer = None
        
        self.msgproc.PAINT = self._onPaint
        self.msgproc.GETDLGCODE = self._onGetDlgCode
        self.msgproc.SETCURSOR = self._onSetCursor
        self.msglistener.CREATE = self.__onCreate
        self.msglistener.SIZE = self._onSize
        self.msglistener.CHAR = self._onChar
        self.msgproc.IME_STARTCOMPOSITION = self._onImeStart
        self.msglistener.IME_ENDCOMPOSITION = self._onImeEnd
        self.msgproc.IME_COMPOSITION = self._onImeComposition
        self.msglistener.IME_NOTIFY = self._onImeNotify
        self.msglistener.SETFOCUS = self._onSetFocus
        self.msglistener.KILLFOCUS = self._onKillFocus
        self.msglistener.LBUTTONDOWN = self._onLButtonDown
        self.msglistener.LBUTTONUP = self._onLButtonUp
        self.msglistener.MOUSEMOVE = self._onMouseMove
        self.msglistener.CANCELMODE = self._onCancelMode
        self.msglistener.LBUTTONDBLCLK = self._onLButtonDblClk
        self.msgproc.MOUSEWHEEL = self._onMouseWheel

    def wndReleased(self):
        super(_EditorWnd, self).wndReleased()
        self._buf = None
        self._conf = None
        if self._mode:
            self._mode.detachWnd(self)
        self._mode = None
        self._screen = None
        self._caret = None
        self._idle = None
        self._mouseCaptureTimer = None
        
    def _setScreenSize(self):
        if self._screen is not None and self.getHwnd():
            rc = self.getClientRect()
            w, h = rc[2] - rc[0] - self.MARGIN_LEFT - self._lineNoWidth, rc[3] - rc[1]
            self._screen.setScreenSize(w, h)
            self.invalidateRect(None, erase=False)
            self._updateScrollBar()

    def setConf(self, conf):
        self._conf = conf

    def initEditor(self, conf=None, editmode=None):
        if conf:
            self._conf = conf
        
        if editmode is None:
            editmode = mode.Mode(buffer.Buffer())
        self.setMode(editmode)
        self._screen = screen.Screen(device=gdi.IC(u"Display"), buf=self._buf, conf=self._conf)
        self._caret = screen._caret(self, self._screen)
        self._setScreenSize()
        self._screen.locate(0)

    def getMode(self):
        return self._mode
        
    def setMode(self, mode):
        if self._mode:
            self._mode.detachWnd(self)

        self._mode = mode
        self._buf = mode.buf
        self._mode.attachWnd(self)
        
    def registerKeyMap(self, keys):
        self.keymap.clear()
        for key, name in keys.iteritems():
            def runCommand(msg, cmdname=name):
                self._mode.runKeyCommand(self, msg.keys, cmdname)
            self.keymap.addKey(runCommand, key)

    def getBuffer(self):
        return self._buf
    buf = property(getBuffer)

    def getCaret(self):
        return self._caret
    caret = property(getCaret)

    def getText(self):
        return self._buf[:]

    def setText(self, text):
#        self.initEditor()
        if not isinstance(text, unicode):
            text = unicode(text, "mbcs")
        text = u"\n".join(text.split(u"\r\n"))
#        buf = buffer.Buffer()
#        buf.ins(0, text)
#        editmode = mode.Mode(buf)
#        self.initEditor(editmode=editmode)
#        editmode.runHighlight()
        
        t = len(self._mode.buf)
        self._mode.replaceString(self, 0, t, text, moveCaret=False)
        self._mode.buf.undo.clear()
        self._caret.top()
        


    def calcCaretLoc(self, pos):
        # calc caret position
        rect = self._screen.getCharRect(pos)
        if not rect:
            return
        return self._toWinLoc(rect)

    def runCommand(self, cmdname):
        self._mode.runCommand(self, cmdname)

    def checkCommand(self, cmdname):
        return self._mode.checkCommand(self, cmdname)

    def cut(self):
        self.runCommand("edit.clipboard.cut")

    def copy(self):
        self.runCommand("edit.clipboard.copy")

    def paste(self):
        self.runCommand("edit.clipboard.paste")

    def undo(self):
        self.runCommand("edit.undo")

    def redo(self):
        self.runCommand("edit.redo")

    def beginSearch(self):
        self.runCommand("edit.search.begin")

    def beginReplace(self):
        self.runCommand("edit.replace.begin")

    def canCut(self):
        return self.checkCommand("edit.clipboard.cut")

    def canCopy(self):
        return self.checkCommand("edit.clipboard.copy")

    def canPaste(self):
        return self.checkCommand("edit.clipboard.paste")

    def canUndo(self):
        return self.checkCommand("edit.undo")

    def canRedo(self):
        return self.checkCommand("edit.redo")

    def isLastPage(self):
        botidx = self._screen.getBottomRowIdx()
        row = self._screen[botidx]
        return row.isLastRow()
            
    def _toWinLoc(self, loc):
        ''' convert text coordinates to client coordinates'''
        ret = list(loc)
        ret[0] += self.MARGIN_LEFT + self._lineNoWidth - self._hScrollPos
        
        if len(loc) == 4:
            ret[2] += self.MARGIN_LEFT + self._lineNoWidth - self._hScrollPos
        return ret
        
    def _fromWinLoc(self, loc):
        ''' convert client coordinates to text coordinate'''
        ret = list(loc)
        ret[0] -= self.MARGIN_LEFT - self._lineNoWidth - self._hScrollPos
        
        if len(loc) == 4:
            ret[2] -= self.MARGIN_LEFT - self._lineNoWidth - self._hScrollPos
        return ret

    def locToPos(self, loc):
        x, y = loc
        for i in range(len(self._screen)):
            l, t, r, b = self._screen.getRowRect(i)
            if y <= b:
                row = self._screen[i]
                break
        else:
            row = self._screen[-1]
        pos = row.locToPos(x)
        return pos


    def onBufModified(self, pos, inslen, dellen):
        if not len(self._screen):
            return

        row = self._screen[-1]
        if pos > self._screen[-1].end:
            return

        top = self._screen[0].top

        if inslen >= dellen:
            if pos < top:
                top += inslen - dellen
        else:
            deleted = dellen - inslen
            if pos < top:
                if pos + deleted > top:
                    top = pos
                else:
                    top -= deleted
        
        if top >= len(self._buf):
            top = len(self._buf)
        if self.caret.pos >= len(self._buf):
            self.caret._pos = len(self._buf)

        self._screen.locate(top)
        self.screenUpdated()
        self.caret.show()

    def screenUpdated(self):
        ''' Invalidate updated region'''
        
        screen = self._screen
        if not screen:
            return
        rc = self.getClientRect()
        left, top, right, bottom = rc
        bottom = top

        nrow = min(len(self._curRows), len(screen))
        for i in range(nrow):
            bottom = top + self._curRows[i].height
            if self._curRows[i].height != screen[i].height:
                # if row height changed, then redraw all rows below the line.
                break

            # check if row is updated
            if self._curRows[i].compare(screen[i]):
                self.invalidateRect((left, top, right, bottom), erase=False)
            top = bottom

        # invalidate below of rows
        if top < rc[3]:
            self.invalidateRect((left, top, right, rc[3]), erase=False)

        self._updateScrollBar()

    def onStyleUpdated(self, f, t):
        if f > self._screen[-1].end:
            return
        if t < self._screen[0].top:
            return
        self._screen.locate(self._screen[0].top)
        self.screenUpdated()
        self.caret.show()

    def isInsMode(self):
        return True


    def dispCaret(self):
        if not self._screen:
            return

        # hide caret before move to new position
        self.removeCaret()

        # Don't show caret if not focused
        if self.getFocus() != self:
            return
        
        loc = self.calcCaretLoc(self._caret.pos)
        if not loc:
            # caret is out of screen
            return
        
        l, t, r, b = loc
        if l < self.MARGIN_LEFT + self._lineNoWidth:
            return

        # show caret
        style = self.getStyleAt(self._caret.pos)
        if self.isInsMode():
            width = 2
        else:
            if self._caret.pos < len(self._buf):
                width = r - l
            else:
                device=gdi.IC(u"Display")
                device.selectObject(style.latinFont)
                width = device.getTextExtent(u" ")[0]

        height = b-t
        top = b-height
        imm = wnd.ImmContext(self)
        try:
            if imm.isOpen():
                height = max(3, int(height*2//3))
                top = b - height - int(height*1//3)
        finally:
            imm.release()
            
        self.createCaret(width=width, height=height)
        self.setCaretPos((l, top))
        self.showCaret()

        self._hasCaret = True

    def removeCaret(self):
        if self._hasCaret:
            try:
                self.hideCaret()
                self.destroyCaret()
            except pymfc.Win32Exception:
                # ignore Win32 error. Window may being destroyed.
                pass
        self._hasCaret = False

    def _getTextRect(self):
        wndrc = self.getClientRect()
        return [wndrc[0]+self.MARGIN_LEFT+self._lineNoWidth, wndrc[1], wndrc[2], wndrc[3]]

    def adjustHScrollPos(self, pos):
        loc = self.calcCaretLoc(pos)
        if not loc:
            # pos is not visible
            return
        l, t, r, b = loc

        textrc = self._getTextRect()
        if (l != 0) and (l <= textrc[0]):
            self.hScroll(l - textrc[0] - (textrc[2]-textrc[0])/2)
        elif r >= textrc[2]:
            d = l - (textrc[2]-textrc[0])/2 - textrc[0]
            self.hScroll(d)

    def _getMaxHBarPos(self):
        max_width = self._screen.maxwidth
        if max_width < 1:
            max_width = 1

        wndrc = self._getTextRect()
        maxpos = max_width - (wndrc[2] - wndrc[0])/2
        return max(0, maxpos)
        
    MAX_SBAR = 32766
    def _updateScrollBar(self):
        if not self._screen:
            return
        if not self._parent._showScrollbar:
            return

        max_width = self._getMaxHBarPos()
        if max_width:
            p = float(self.MAX_SBAR) / max_width *  self._hScrollPos
            self._parent._sbarHorz.setScrollInfo(min=0, max=self.MAX_SBAR, pos=int(p), redraw=True)
        else:
            p = 0
            self._parent._sbarHorz.enableWindow(False)

        maxlineno = len(self._buf)
        curlineno = self._screen[0].top
        
        self._parent._sbarVert.setScrollInfo(
            min=0, max=maxlineno, pos=curlineno, redraw=True)

    def vScroll(self, v):
        self.scrollWindow(0, v, invalidate=True)
        self._updateScrollBar()

    def hScroll(self, v):
        prevpos = self._hScrollPos
        self._hScrollPos += v
        self._hScrollPos = max(0, self._hScrollPos)
        self._hScrollPos = min(self._getMaxHBarPos(), self._hScrollPos)
        
#        print "hscroll:", prevpos, v, self._hScrollPos, self._getMaxHBarPos()
        
        rc = self.getClientRect()
        rc = [self.MARGIN_LEFT+self._lineNoWidth, rc[1], rc[2], rc[3]]

        v = prevpos - self._hScrollPos
        if v:
            self.scrollWindow(v, 0, scroll=rc, clip=rc, invalidate=True)

        self._updateScrollBar()
        self.dispCaret()
 
    def top(self):
        if self._screen[0].top == 0:
            return
        self._screen.locate(0)
        self.invalidateRect(None, erase=False)
        self._updateScrollBar()
        self.dispCaret()
        
    def bottom(self):
        end = len(self._buf)
        if self._screen[0].top == end:
            return
        self._screen.locate(end)
        self.invalidateRect(None, erase=False)
        self._updateScrollBar()
        self.dispCaret()
        
    def pageDown(self):
        if self._screen.pageDown() is None:
            return

        self.invalidateRect(None, erase=False)
        self._updateScrollBar()
        self.dispCaret()
        return True


    def pageUp(self):
        if self._screen.pageUp() is None:
            return
        self.invalidateRect(None, erase=False)
        self._updateScrollBar()
        self.dispCaret()
        return True
 
    def lineDown(self):
        if self._screen.rowDown() is None:
            return
        self.invalidateRect(None, erase=False)
        self._updateScrollBar()
        self.dispCaret()
        return True

    def lineUp(self):
        if self._screen.rowUp() is None:
            return
        self.invalidateRect(None, erase=False)
        self._updateScrollBar()
        self.dispCaret()
        return True

    def locate(self, pos):
        if pos > len(self._buf):
            return
        self._screen.locate(pos, top=True)
        self.invalidateRect(None, erase=False)
        self._updateScrollBar()
        self.dispCaret()
        return True

    def left(self):
        self.hScroll(self._hScrollPos*-1)
        
    def right(self):
        self.hScroll(self._getMaxHBarPos()-self._hScrollPos)
        
    def lineLeft(self):
        self.hScroll(-30)
        
    def lineRight(self):
        self.hScroll(30)
        
    def pageLeft(self):
        wndrc = self._getTextRect()
        self.hScroll(-1*(wndrc[2] - wndrc[0])/2)
        
    def pageRight(self):
        wndrc = self._getTextRect()
        self.hScroll((wndrc[2] - wndrc[0])/2)
        
    def h_thumbtrack(self, pos):
        max_width = self._getMaxHBarPos()
        p = int(pos * max_width/float(self.MAX_SBAR))
        self.hScroll(p-self._hScrollPos)

    def isSelected(self):
        sel = self._screen.getSelection()
        return sel and sel[0] != sel[1]

    def getSelectedPos(self):
        return sorted(self._screen.getSelection())
        
    def _updateSelection(self, f, t):
        for idx in self._screen.setSelection(f, t):
            rc = self._screen.getRowRect(idx)
            self.invalidateRect(self._toWinLoc(rc), erase=False)
            
            
    def clearSelection(self):
        for idx in self._screen.clearSelection():
            rc = self._screen.getRowRect(idx)
            self.invalidateRect(self._toWinLoc(rc), erase=False)
            
        for idx in self._screen.clearBlockSelection():
            rc = self._screen.getRowRect(idx)
            self.invalidateRect(self._toWinLoc(rc), erase=False)

    def startSelection(self):
        sel = self._screen.getSelection()
        if sel and sel[0] != sel[1]:
            # selection have already started.
            return
        self._updateSelection(self._caret.pos, self._caret.pos)
        
    def setSelectionTo(self):
        f, t = self._screen.getSelection()
        self._updateSelection(f, self._caret.pos)

    def setSelection(self, f, t):
        self._updateSelection(f, t)
        
    def startMouseSelection(self):
        if not self._mouseSelecting:
            self._mouseSelecting = True
            self._mouseBlockSelecting = False
            if not self._mouseCaptureTimer:
                self._mouseCaptureTimer = wnd.TimerProc(50, self._onMouseMove, self)

            self.setCapture()

    def isBlockSelected(self):
        sel = self._screen.getBlockSelection()
        return sel and sel[0] != sel[1]

    def _updateBlockSelection(self, f, t):
        for idx in self._screen.setBlockSelection(f, t):
            rc = self._screen.getRowRect(idx)
            self.invalidateRect(self._toWinLoc(rc), erase=False)

    def startBlockSelection(self):
        self._updateBlockSelection(self.caret.pos, self.caret.pos)
        
    def setBlockSelectionTo(self):
        f, t = self._screen.getBlockSelection()
        self._updateBlockSelection(f, self.caret.pos)

    def startMouseBlockSelection(self):
        if not self._mouseSelecting:
            self._mouseSelecting = False
            self._mouseBlockSelecting = True
            self.setCapture()

    def getSelectedBlock(self):
        return self._screen.getSelectedBlock()
        
    def getStyleAt(self, pos):
        buflen = len(self._buf)
        if pos < buflen:
            styleidx = self._buf.getStyle(self._caret.pos, self._caret.pos+1)[0]
        elif len(self._buf):
            styleidx = self._buf.getStyle(buflen-1, buflen)[0]
        else:
            styleidx = 0
        
        return self._conf.styles[styleidx]
        

    def getRowSplit(self):
        return self._screen.splitBuf()


    def __onCreate(self, msg):
#        self.initEditor()
        self._idle = wnd.IdleProc(self.__onIdle, self)

#        imm = wnd.ImmContext(msg.wnd)
#
#        style = self._getStyleAt(self._caret.pos)
#        if style:
#            imm.setCompFont(style.nonLatinFont)


    
    def __onIdle(self):
        if self._mode:
            return self._mode.runHighlight()
        else:
            return 0
        
    def _paint(self, dc, rc):
        wndrc = self.getClientRect()
        if not rc:
            rc = wndrc
        width = wndrc[2] - wndrc[0]

        # prepare dc for drawing
        paintdc = dc.createCompatibleDC()
        bmp = dc.createCompatibleBitmap(width, wndrc[3] - wndrc[1])
        orgbmp = paintdc.selectObject(bmp)
        try:
            rowrc = [0, 0, wndrc[2], 0]

            for row in self._screen:
                rowrc[3] = rowrc[1] + row.height
                if util.rectIntersection(rc, rowrc, normalized=True):

                    self._screen.paintRow(row, paintdc, (self._hScrollPos*-1, 0), width)
                    srcrc = [self.MARGIN_LEFT + self._lineNoWidth, rowrc[1], width, rowrc[1]+row.height]

                    dc.bitBlt(srcrc, paintdc, (0,0), srccopy=True)

                rowrc[1] = rowrc[3]
                if rowrc[3] > rc[3]:
                    break
        finally:
            paintdc.selectObject(orgbmp)

        # draw line no
        if self._lineNoWidth:
            linenoStyle = self._conf.linenostyle
            dc.setTextAlign(noupdatecp=True)
            fore, back = linenoStyle.color.text
            dc.setTextColor(fore)
            dc.setBkColor(back)
            font = linenoStyle.latinFont
            orgfont = dc.selectObject(font)
            
            try:
                numRect = [self.MARGIN_LEFT, 0, self._lineNoWidth, 0]
                for row in self._screen:
                    numRect[3] = numRect[1] + row.height
                    if row.isTOL():
                        s = unicode(row.lineNo+1)
                    else:
                        s = u""

                    # clear rect
                    dc.textOut(u"", (numRect[0], numRect[1]), 
                        clipped=True, opaque=True, rc=numRect)

                    nrect = numRect[:]
                    nrect[2] = nrect[2] - 10;
                    dc.drawText(s, nrect, right=True)
                    numRect[1] = numRect[3]
            finally:
                dc.selectObject(orgfont)
                
        # clear below of rows
        if rowrc[3] <= rc[3]:
            rowrc[3] = min(rc[3], wndrc[3])
            dc.fillSolidRect(rowrc, self._conf.bgcolor)

        self._curRows = self._screen[:]
        
    def _onPaint(self, msg):
        if self._hasCaret:
            self.hideCaret()
        dc = gdi.PaintDC(msg.wnd)
        try:
            self._paint(dc, dc.rc)
        finally:
            dc.endPaint()
            if self._hasCaret:
                self.showCaret()

    def _onGetDlgCode(self, msg):
        return 4 # todo: fix pymfclib

    def _onSetCursor(self, msg):
        if msg.htclient:
            self._mode.onSetCursor(self)
            return 1

    def _onSize(self, msg):
        self._setScreenSize()
        self.dispCaret()
        
    def _onChar(self, msg):
        if wnd.getKeyState(wnd.KEY.MENU).down:
            return
        if wnd.getKeyState(wnd.KEY.CONTROL).down:
            return
        
        if msg.char >= u' ' or msg.char in (u'\n\t'):
            s = msg.char * msg.repeat
#            f = time.clock()
            self._mode.onChar(self, s)
#            print time.clock()-f


#            import profile, pstats
#            profile.runctx('self._mode.onChar(self, s)', globals(), locals(), "c:\\a.prof")
#            p = pstats.Stats('c:\\a.prof')
#            p.strip_dirs()
#            p.sort_stats('cumulative')
#            p.print_stats()
        
    def _setImmCompWndPos(self, imm):
        style = self.getStyleAt(self._caret.pos)
        imm.setCompFont(style.nonLatinFont.getLogFont())
        tm = style.nonLatinFont.getTextMetrics()
        
        l, t, r, b = self.calcCaretLoc(self._caret.pos)
        idx = self._screen.getRowIdx(self._caret.pos)
        if idx != -1:
            row = self._screen[idx]
            imm.setCompWndPos((l, t+row.ascent-tm.tmAscent-tm.tmExternalLeading))
        
        
    def _onImeStart(self, msg):
        imm = wnd.ImmContext(msg.wnd)
        self._setImmCompWndPos(imm)
        self.removeCaret()
        return msg.wnd.defWndProc(msg)
        
        
    def _onImeEnd(self, msg):
        self.dispCaret()

    def _onImeComposition(self, msg):
        if msg.resultstr:
            imm = wnd.ImmContext(msg.wnd)
            s = imm.getResultString()
            self._mode.onChar(self, s)
            self._setImmCompWndPos(imm)
            self.updateWindow()
        else:
            return msg.wnd.defWndProc(msg)
        
    def _onImeNotify(self, msg):
        if msg.setopenstatus:
            self.dispCaret()
        
    def _onSetFocus(self, msg):
        self.dispCaret()

    def _onKillFocus(self, msg):
        self.removeCaret()
        
    def _onLButtonDown(self, msg):
        x, y = self._fromWinLoc([msg.x, msg.y])
        
        alt = wnd.getKeyState(wnd.KEY.MENU).down
        ctrl = wnd.getKeyState(wnd.KEY.CONTROL).down
        shift = wnd.getKeyState(wnd.KEY.SHIFT).down
        self._mode.onLButtonDown(self, x, y, alt, ctrl, shift)

    def _onLButtonDblClk(self, msg):
        x, y = self._fromWinLoc([msg.x, msg.y])
        
        alt = wnd.getKeyState(wnd.KEY.MENU).down
        ctrl = wnd.getKeyState(wnd.KEY.CONTROL).down
        shift = wnd.getKeyState(wnd.KEY.SHIFT).down
        self._mode.onLButtonDblClk(self, x, y, alt, ctrl, shift)
        
    def _onMouseMove(self, msg=None):
        if msg is None:
            l, t, r, b = self.getClientRect()

            x, y = self.getCursorPos()
            if x < l + self.MARGIN_LEFT + self._lineNoWidth:
                self.lineLeft()
                x = 0
            elif x > r:
                self.lineRight()
                x = r

            if y < 0:
                self.lineUp()
                y = 0
            elif y > b:
                self.lineDown()
                y = b
        else:
            x = msg.x
            y = msg.y
            
        if self._mouseSelecting:
            if self._screen.getSelection():
                x, y = self._fromWinLoc([x, y])
                pos = self.locToPos((x, y))
                self.caret.locate(pos, saveCol=True)
                self.setSelectionTo()
        elif self._mouseBlockSelecting:
            if self._screen.getBlockSelection():
                x, y = self._fromWinLoc([x, y])
                pos = self.locToPos((x, y))
                self.caret.locate(pos, saveCol=True)
                self.setBlockSelectionTo()
        
        
    def _onLButtonUp(self, msg):
        self._onCancelMode(None)
        
    def _onCancelMode(self, msg):
        if self._mouseSelecting or self._mouseBlockSelecting:
            self.releaseCapture()
            self._mouseSelecting = False
            self._mouseBlockSelecting = False

        if self._mouseCaptureTimer:
            self._mouseCaptureTimer.unRegister()
            self._mouseCaptureTimer = None
        
    def _onMouseWheel(self, msg):
        delta = msg.delta//120
        if delta < 0:
            delta = max(min(20, delta*-1), 3)
            for d in range(delta):
                self.lineDown()
        else:
            delta = max(min(20, delta), 3)
            for d in range(delta):
                self.lineUp()
        return 0
        

class Editor(wnd.Wnd):
    SPLITBTN_WIDTH = 4
    SPLITBTN_WIDTH = 6
    STYLE = wnd.Wnd.STYLE(clientedge=1)

    caret = property(lambda self:self._editorwnd.getCaret())

    def _prepare(self, kwargs):
        super(Editor, self)._prepare(kwargs)
        
        self._showScrollbar = kwargs.get('showsbar', True)
        self._showSplitBtn = False
        
        self._editorwnd = _EditorWnd(parent=self)
        self._sbarVert = wnd.VertScrollBar(parent=self)
        self._sbarHorz = wnd.HorzScrollBar(parent=self)
        
        self._sbarWidth = 0
        self._sbarHeight = 0
        self._sbarColor = pymfc.syscolor.scrollbar
        
        if self._showScrollbar:
            self._sbarWidth = int(pymfc.metric.CXVSCROLL * 10.0 / 10)
            if self._sbarWidth < 1:
                self._sbarWidth = 1
            self._sbarHeight = int(pymfc.metric.CXHSCROLL * 10.0 / 10)
            if self._sbarHeight < 1:
                self._sbarHeight = 1

        self.msglistener.CREATE = self.__onCreate
        self.msgproc.PAINT = self._onPaint
        self.msglistener.SIZE = self.__onSize
        self.msglistener.SETFOCUS = self._onSetFocus
        self.msglistener.VSCROLL = self._onVScroll
        self.msglistener.HSCROLL = self._onHScroll


    def wndReleased(self):
        super(Editor, self).wndReleased()
        self._editorwnd = None
        self._sbarVert = None
        self._sbarHorz = None

    def setConf(self, conf):
        self._editorwnd.setConf(conf)

    def initEditor(self, conf=None, editmode=None):
        self._editorwnd.initEditor(conf=conf, editmode=editmode)

    def getBuffer(self):
        return self._editorwnd._buf

    def getMode(self):
        return self._editorwnd.getMode()
        
    def runCommand(self, cmdname):
        self._editorwnd.runCommand(cmdname)

    def checkCommand(self, cmdname):
        return self._editorwnd.checkCommand(cmdname)

    def getText(self):
        return self._editorwnd.getText()
        
    def setText(self, s):
        return self._editorwnd.setText(s)
        
    def isLastPage(self):
        return self._editorwnd.isLastPage()
        
    def pageDown(self):
        return self._editorwnd.pageDown()
        
    def getRowSplit(self):
        return self._editorwnd.getRowSplit()
        
    def __onCreate(self, msg):
        self._editorwnd.create()
        self._sbarVert.create()
        self._sbarHorz.create()
        self._sbarVert.setScrollInfo(min=0, max=1, pos=0, redraw=True)
        self._sbarHorz.setScrollInfo(min=0, max=1, pos=0, redraw=True)

    def _paintBtn(self, dc, rc):
        l, t, r, b = rc
        rc = [r - self._sbarWidth, t, r, t + self.SPLITBTN_WIDTH]
        dc.fillSolidRect(rc, self._sbarColor)
        rc = [r - self._sbarWidth, t, r, t + self.SPLITBTN_WIDTH]
        dc.drawEdge(raised=True, rect=True, rc=rc)
        
        rc = [l, b - self._sbarHeight, l + self.SPLITBTN_WIDTH, b]
        dc.fillSolidRect(rc, self._sbarColor)
        dc.drawEdge(raised=True, rect=True, soft=True, rc=rc)

    def _paint(self, dc):
        # paint splitter button
        l, t, r, b = self.getClientRect()
        if self._showSplitBtn:
            self._paintBtn(dc, (l, t, r, b))
        rc = [r - self._sbarWidth, b - self._sbarHeight, r, b]
        dc.fillSolidRect(rc, self._sbarColor)

    def _onPaint(self, msg):
        dc = gdi.PaintDC(msg.wnd)
        try:
            self._paint(dc)
        finally:
            dc.endPaint()

    def __onSize(self, msg):
        # resize editor wnd
        w = msg.width - self._sbarWidth
        h = msg.height - self._sbarHeight
        if not self._editorwnd.getHwnd():
            return
        self._editorwnd.setWindowPos(pos=(0,0), size=(w, h))
        
        if self._showScrollbar:
            # resize scroll bars
            if self._showSplitBtn:
                self._sbarVert.setWindowPos(
                    pos=(w, self.SPLITBTN_WIDTH), 
                    size=(self._sbarWidth, h - self.SPLITBTN_WIDTH))

                self._sbarHorz.setWindowPos(
                    pos=(self.SPLITBTN_WIDTH, h), 
                    size=(w-self.SPLITBTN_WIDTH, self._sbarHeight))
            else:
                self._sbarVert.setWindowPos(
                    pos=(w, 0), size=(self._sbarWidth, h))

                self._sbarHorz.setWindowPos(
                    pos=(0, h), size=(w, self._sbarHeight))
                
    def _onSetFocus(self, msg):
        self._editorwnd.setFocus()

    def _onVScroll(self, msg):
        if msg.top:
            self._editorwnd.top()
        elif msg.bottom:
            self._editorwnd.bottom()
        elif msg.pageup:
            self._editorwnd.pageUp()
        elif msg.pagedown:
            self._editorwnd.pageDown()
        elif msg.lineup:
            self._editorwnd.lineUp()
        elif msg.linedown:
            self._editorwnd.lineDown()
        elif msg.thumbtrack:
            self._editorwnd.locate(msg.pos)
        return

    def _onHScroll(self, msg):
        if msg.left:
            self._editorwnd.left()
        elif msg.right:
            self._editorwnd.right()
        elif msg.pageleft:
            self._editorwnd.pageLeft()
        elif msg.pageright:
            self._editorwnd.pageRight()
        elif msg.lineleft:
            self._editorwnd.lineLeft()
        elif msg.lineright:
            self._editorwnd.lineRight()
        elif msg.thumbtrack:
            self._editorwnd.h_thumbtrack(msg.pos)

    