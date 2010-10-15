import _pymfclib_editor
from _pymfclib_editor import StyleColor, TextStyle, ScreenConf, Screen

class _caret:
    def __init__(self, wnd, screen):
        self._pos = 0
        self._lastCol = 0

        self._wnd = wnd
        self._screen = screen

    def _saveLastCol(self):
        idx = self._screen.getRowIdx(self._pos)
        row = self._screen[idx]
        self._lastCol = row.posToCol(self._pos) + row.indentCol
        
    def showPos(self, pos=None, top=False, mid=False, bot=False):
        '''Ensure pos is displayed. Scroll if pos is out of screen'''
        if pos is None:
            pos = self._pos
        idx = self._screen.getRowIdx(pos)
        if idx == -1:
            self._screen.locate(pos, top=top, mid=mid, bot=bot, refresh=False)
            self._wnd.screenUpdated()
            self._wnd.adjustHScrollPos(pos)
            return

        l, t, r, b = self._screen.getRowRect(idx)
        height = self._screen.height
        if b >= height:
            if idx != 0:
                # caret is not at top of screen row.
                removed = 0
                
                while (idx > 0) and (b >= height):
                    row = self._screen.rowDown()
                    idx -= 1
                    removed += row.height
                    b -= row.height

                self._screen.completeRows()
                self._wnd.vScroll(removed*-1)

        self._wnd.adjustHScrollPos(pos)
        
    def locate(self, pos, top=False, mid=False, bot=False, saveCol=False):
        '''Set catet position'''
        assert pos <= len(self._wnd.buf)
        
        self._pos = pos
        self.showPos(self._pos, top, mid, bot)
        self.show()
        if saveCol:
            self._saveLastCol()

    
    def show(self):
        '''Update caret position on screen'''
        self._wnd.dispCaret()

    def right(self, n=1):
        self.showPos(self._pos, mid=True)
        if self._pos + n > len(self._wnd.buf):
            self.show()
            return False

        self._pos += n
        self.showPos(self._pos, bot=True)
        self.show()
        
        self._saveLastCol()
        return True
        
    def left(self, n=1):
        self.showPos(self._pos, mid=True)
        if self._pos < n:
            return False
        self._pos -= n
        v = 0
        while self._pos < self._screen[0].top:
            row = self._screen.rowUp()
            if not row:
                break
            v += row.height
        if v:
            self._wnd.vScroll(v)

        self.showPos(self._pos, top=True)
        self.show()

        self._saveLastCol()
        return True

    def up(self):
        self.showPos(self._pos, mid=True)
        idx = self._screen.getRowIdx(self._pos)
        currow = self._screen[idx]
        if currow.top == 0:
            return False
        
        if idx == 0:
            row = self._screen.rowUp()
            if not row:
                return False
            if row.height:
                self._wnd.vScroll(row.height)
            idx += 1
        
        nextrow = self._screen[idx-1]
        nextcol = self._lastCol
        if nextrow.indentCol:
            nextcol = max(0, nextcol - nextrow.indentCol)
        
        self._pos = nextrow.colToPos(nextcol)
        self.showPos(self._pos, top=True)
        self.show()
#        print "==========", len(self._screen._rows)
        
    def down(self):
        self.showPos(self._pos, mid=True)
        idx = self._screen.getRowIdx(self._pos)
#        print "'''''''", idx, self._pos, self._screen._topRow, len(self._screen._rows)
        currow = self._screen[idx]
        if currow.isLastRow():
            return False
        
        if idx < len(self._screen) - 1:
            idx = idx + 1
        else:
            v = 0
            while currow == self._screen[-1]:
                row = self._screen.rowDown()
                if not row:
                    break
                v += row.height
            if v:
                self._wnd.vScroll(v*-1)
        
            idx = self._screen.getRowIdx(self._pos)
            if idx == -1:
                idx = 0
            else:
                idx = idx + 1

        nextrow = self._screen[idx]
        nextcol = self._lastCol
        if nextrow.indentCol:
            nextcol = max(0, nextcol - nextrow.indentCol)
        
        self._pos = nextrow.colToPos(nextcol)
        self.showPos(self._pos, bot=True)
        self.show()
#        print "down:^^^", idx, row.top, row.end, self._pos, `self._wnd.buf.get(row.top, row.end)`
        
    def home(self):
        self.showPos(self._pos, mid=True)
        idx = self._screen.getRowIdx(self._pos)
        row = self._screen[idx]
        self._pos = row.top
        
        self.showPos(self._pos, mid=True)
        self.show()
        self._saveLastCol()

    def end(self):
        self.showPos(self._pos, mid=True)
        idx = self._screen.getRowIdx(self._pos)
        row = self._screen[idx]
        if row.isLastRow():
            self._pos = row.end
        else:
            self._pos = row.end - 1
        self.showPos(self._pos, mid=True)
        self.show()
        self._saveLastCol()

    def top(self):
        self._pos = 0
        self.showPos(self._pos)

        self.show()
        self._saveLastCol()

    def bottom(self):
        self._pos = len(self._wnd.buf)
        self.showPos(self._pos, bot=True)
        self.show()
        self._saveLastCol()

    def pageDown(self):
        self.showPos(self._pos, mid=True)
        previdx = self._screen.getRowIdx(self._pos)
        
        if self._wnd.pageDown():
            maxidx = self._screen.getBottomRowIdx()
            idx = min(previdx, maxidx)
            row = self._screen[idx]
            self._pos = row.colToPos(self._lastCol)
            self.showPos(self._pos, bot=True)
            self.show()
            return True
            
    def pageUp(self):
        self.showPos(self._pos, mid=True)
        previdx = self._screen.getRowIdx(self._pos)
        
        if self._wnd.pageUp():
            maxidx = self._screen.getBottomRowIdx()
            idx = min(previdx, maxidx)
            row = self._screen[idx]
            self._pos = row.colToPos(self._lastCol)
            self.showPos(self._pos, bot=True)
            self.show()
            return True
        
    def _getPos(self):
        return self._pos
    pos = property(_getPos)
    
    def getLoc(self):
        return self._wnd.getCaretLoc(self._pos)


Screen = _pymfclib_editor.Screen
