
cdef class ScreenRow:
    cdef object _buf
    cdef PymScreenRow _row
    
    property top:
        def __get__(self):
            return self._row.top
            
    property end:
        def __get__(self):
            return self._row.end
    
    property width:
        def __get__(self):
            cdef long ret, p
            ret = 0
            for p from 0 <= p < (self._row.end - self._row.top):
                ret = ret + self._row.chars[p].width
            return ret + self._row.indent

    property lineNo:
        def __get__(self):
            return self._row.lineNo

    property height:
        def __get__(self):
            return self._row.height
    
    property ascent:
        def __get__(self):
            return self._row.ascent
    
    property indent:
        def __get__(self):
            return self._row.indent
    
    property indentCol:
        def __get__(self):
            return self._row.indentCol
    
    def __init__(self, object buf):
        self._buf = buf
        
    def __dealloc__(self):
        if self._row.chars:
            free(self._row.chars)

    cdef int _isLastRow(self):
        cdef long p
        p = self._buf.getSize()
        if self._row.end == p:
            if self._row.top == self._row.end:
                return 1
            p = self._row.end-self._row.top-1
            if self._row.chars[p].c != c'\n':
                return 1
        return 0

    def getBuffer(self):
        return PyMFCPtr_FromVoidPtr(&self._row)
        
    def isLastRow(self):
        return self._isLastRow()

    def isTOL(self):
        if self._row.top == 0:
            return 1
        if self._buf.get(self._row.top-1, self._row.top) == unicode('\n'):
            return 1
    
    def isEOL(self):
        if self._isLastRow():
            return 1
        if self._row.top != self._row.end:
            if self._row.chars[self._row.end - 1].c == c'\n':
                return 1

    def colToPos(self, long col):
        cdef long pos, ret
        cdef int curcol
        
        curcol = 0
        ret = self._row.top
        for pos from 0 <= pos < (self._row.end - self._row.top):
            if (curcol + self._row.chars[pos].col > col):
                break
            if self._row.chars[pos].c == c'\n':
                break
            curcol = curcol + self._row.chars[pos].col
            ret = ret + 1
        else:
            if self._isLastRow() == 0:
                return self._row.end - 1
        return ret

    def posToCol(self, long pos):
        cdef long p, ret
        if pos <= self._row.top:
            return 0
        ret = 0
        for p from 0 <= p < (self._row.end - self._row.top):
            if p + self._row.top == pos:
                return ret
            ret = ret + self._row.chars[p].col
        return ret

    def locToPos(self, int x):
        cdef long pos
        x = x - self._row.indent
        for pos from 0 <= pos < (self._row.end - self._row.top):
            if x < self._row.chars[pos].width / 2:
                return pos + self._row.top
            x = x - self._row.chars[pos].width

        if self._isLastRow() != 0:
            return self._row.end
        else:
            return self._row.end - 1

    def posToLoc(self, long pos):
        cdef int left, right
        cdef long p

        if pos < self._row.top:
            return None
        if pos > self._row.end:
            return None
        
        left = right = self._row.indent

        for p from 0 <= p < (pos - self._row.top):
            left = left + self._row.chars[p].width
        
        if pos == self._row.end:
            right = left # pos points end of row. No character.
        else:
            right = left + self._row.chars[pos - self._row.top].width

        return left, right
    

    def setSelection(self, long start, long end):
        cdef int ret
        cdef long i
        cdef PymScreenChar *c

        ret = 0
        
        i = self._row.top
        while i < start and i < self._row.end:
            c = &self._row.chars[i - self._row.top]
            if c.selected == 1:
                ret = 1
                c.selected = 0
            i = i + 1

        while i < end and i < self._row.end:
            c = &self._row.chars[i - self._row.top]
            if c.selected == 0:
                ret = 1
                c.selected = 1
            i = i + 1
        while i < self._row.end:
            c = &self._row.chars[i - self._row.top]
            if c.selected == 1:
                ret = 1
                c.selected = 0
            i = i + 1

        return ret;

    def setBlockSelection(self, long blockStart, long blockStartX, blockEnd, blockEndX):
        cdef int ret
        cdef long i, p
        cdef PymScreenChar *c
        cdef long width
        ret = 0
        width = 0
        
        if blockStart >= self._row.end or blockEnd < self._row.top:
            for p from self._row.top <= p < self._row.end:
                c = &self._row.chars[p - self._row.top]
                if c.selected == 1:
                    ret = 1
                    c.selected = 0
            return ret

        for p from self._row.top <= p < self._row.end:
            c = &self._row.chars[p - self._row.top]
            if blockStartX <= width < blockEndX:
                if c.selected == 0:
                    ret = 1
                    c.selected = 1
            else:
                if c.selected == 1:
                    ret = 1
                    c.selected = 0
            width = width + c.width
        return ret
    
    def getSelectedBlock(self, long blockStart, long blockStartX, blockEnd, blockEndX):
        cdef long i, f, t
        cdef PymScreenChar *c
        cdef long width

        if blockStart >= self._row.end or blockEnd < self._row.top:
            return None

        width = 0
        f = t = 0
        for f from self._row.top <= f < self._row.end:
            c = &self._row.chars[f - self._row.top]
            if blockStartX <= width:
                break
            width = width + c.width
        else:
            return None
        
        for t from f <= t < self._row.end:
            c = &self._row.chars[t - self._row.top]
            if width >= blockEndX:
                break
            width = width + c.width
        
        return (f, t)

    def compare(self, ScreenRow row):
        cdef int size
        
        if self._row.height != row._row.height:
            return 1
        size = self._row.end - self._row.top
        if size != row._row.end - row._row.top:
            return 2
        if self._row.lineNo != row._row.lineNo:
            return 3
        if self._row.indent != row._row.indent:
            return 4
        if 0 != memcmp(self._row.chars, row._row.chars, size * sizeof(PymScreenChar)):
            return 5

        return 0

    def ppp(self):
        cdef long p
        for p from 0 <= p < (self._row.end - self._row.top):
            u = PyUnicode_FromWideChar(&self._row.chars[p].c, 1)
            print "...", u
    
    def qqq(self):
        cdef long p
        ret = []
        for p from 0 <= p < (self._row.end - self._row.top):
            ret.append(self._row.chars[p].selected)
        return ret

cdef class Screen:
    cdef object _device
    cdef Buffer _buf
    cdef int _width, _height
    cdef readonly long _topRow
    cdef long _isSelected, _selFrom, _selTo
    cdef object _isBlockSelected, _blockSelFrom, _blockSelTo
    cdef ScreenConf _conf
    cdef readonly object _rows

    cdef PymScreenConf *_p_conf
    cdef int _nStyles
    cdef PymTextStyle *_styles
    
    property conf:
        def __get__(self):
            return self._conf
            
    property width:
        def __get__(self):
            return self._width
    
    property height:
        def __get__(self):
            return self._height
    
    property maxwidth:
        def __get__(self):
            cdef int ret, h, w
            cdef ScreenRow row
            ret = 0
            h = 0
            for row in self._rows[self._topRow:]:
                if h > self._height:
                    break
                w = row.width
                if ret < w:
                    ret = w
                h = h + row.height
            if ret < 1:
                ret = 1
            return ret

    def __init__(self, device, buf, conf, width=0, height=0):
        self._device = device
        self._buf = buf
        self._conf = conf
        self._p_conf = <PymScreenConf*>PyMFCPtr_AsVoidPtr(conf.getScreenConf())
        self._width = width
        self._height = height
        self._topRow = 0
        self._isSelected = 0
        self._selFrom = 0
        self._selTo = 0
        self._isBlockSelected = 0
        self._blockSelFrom = self._blockSelTo = (0,(0, 0))
        self._rows = []

        self._buildStyles()
    
    def __dealloc__(self):
        if self._styles:
            free(self._styles)

    def __len__(self):
        return len(self._rows) - self._topRow

    def __getitem__(self, int n):
        cdef int l
        if n < 0:
            l = len(self)
            n = l + n
        n = self._topRow + n
        return self._rows[n]

    def __getslice__(self, int i, int j):
        i = max(i, 0)
        j = max(j, 0)
        j = min(j, len(self))

        return self._rows[self._topRow+i:self._topRow+j]

    cdef _buildStyles(self):
        cdef PymTextStyle* p
        
        self._nStyles = len(self._conf.styles)
        self._styles = <PymTextStyle*>malloc(self._nStyles*sizeof(PymTextStyle))
        if self._styles == NULL:
            raise MemoryError

        p = self._styles
        for style in self._conf.styles:
            memcpy(&(p.color), PyMFCPtr_AsVoidPtr(style.color.getBuffer()), sizeof(PymStyleColor))

            font = style.latinFont
            p.latinFont.hFont = PyMFCHandle_AsHandle(font.getHandle())
            lf = font.getLogFont()
            memcpy(&(p.latinFont.lf), PyMFCPtr_AsVoidPtr(lf.getBuffer()), sizeof(LOGFONT))
            self._device.selectObject(font)
            tm = self._device.getTextMetrics()
            memcpy(&(p.latinFont.tm), PyMFCPtr_AsVoidPtr(tm.getBuffer()), sizeof(TEXTMETRIC))
            p.latinFont.spcWidth = self._device.getTextExtent(unicode(" "))[0]
            
            
            font = style.nonLatinFont
            p.noLatinFont.hFont = PyMFCHandle_AsHandle(font.getHandle())
            lf = font.getLogFont()
            memcpy(&(p.noLatinFont.lf), PyMFCPtr_AsVoidPtr(lf.getBuffer()), sizeof(LOGFONT))
            self._device.selectObject(font)
            tm = self._device.getTextMetrics()
            memcpy(&(p.noLatinFont.tm), PyMFCPtr_AsVoidPtr(tm.getBuffer()), sizeof(TEXTMETRIC))
            p.noLatinFont.spcWidth = self._device.getTextExtent(unicode(" "))[0]
            
            p = p + 1;
            

    cdef _removeTrailRows(self):
        cdef int h, i
        h = 0
        
        for i from self._topRow <= i < len(self._rows):
            row = self._rows[i]
            if h > self._height:
                if row.isTOL():
                    del self._rows[i:]
                    break

            h = h + row.height

    def rowUp(self):
        if self._topRow > 0:
            self._topRow = self._topRow - 1
            return self._rows[self._topRow]

        row = self._rows[0]
        pos = row.top
        if not pos:
            return None

        top = self._buf.getTOL(pos-1)
        end = self._buf.getEOL(top)
        new_rows = self._rowsplit(self._device, top, end)
        self._rows[0:0] = new_rows
        self._topRow = len(new_rows)-1

        self.completeRows()
        self._removeTrailRows()

        return self._rows[self._topRow]
        
    def rowDown(self):
        if self._rows[self._topRow].isLastRow():
            return None

        curtop = self._rows[self._topRow]
        
        if self._topRow <> 0:
            # remove upper rows
            if self._rows[self._topRow].isTOL():
                del self._rows[0:self._topRow]
                self._topRow = 0
                
        self._topRow = self._topRow + 1
        self.completeRows()

        return curtop

    def pageUp(self):
        if self._rows[self._topRow].top == 0:
            return None
        
        pos = self._rows[self._topRow].top
        self.locate(pos, bot=True)
        return self._rows[self._topRow]

    def pageDown(self):
        if self._rows[self._topRow].isLastRow():
            return None
        
        idx = self.getBottomRowIdx()
        if idx == 0:
            top = self._rows[self._topRow].end
        else:
            top = self._rows[self._topRow+idx].top

        self.locate(top, top=True)
        return self._rows[self._topRow]



    def getSelRange(self):
        if self._isSelected:
            if self._selFrom < self._selTo:
                return self._selFrom, self._selTo
            else:
                return self._selTo, self._selFrom
            
    def getBlockSelRange(self):
        if self._blockSelFrom[0] == self._blockSelTo[0]:
            start = end = startx = endx = 0
        else:
            if self._blockSelFrom[0] < self._blockSelTo[0]:
                start, end = self._blockSelFrom[0], self._blockSelTo[0]
            else:
                start, end = self._blockSelTo[0], self._blockSelFrom[0]
                
            if self._blockSelFrom[1][0] < self._blockSelTo[1][0]:
                startx, endx = self._blockSelFrom[1][0], self._blockSelTo[1][0]
            else:
                startx, endx = self._blockSelTo[1][0], self._blockSelFrom[1][0]
        return start, startx, end, endx

    cdef object _updateSelection(self, rows):
        cdef int i, modified
        cdef long isSelected, selFrom, selTo
        cdef long isBlockSelected, blockPosFrom, blockXFrom, blockPosTo, blockXTo

        ret = []
        isSelected = self._isSelected
        if isSelected:
            selFrom, selTo = self.getSelRange()
        else:
            selFrom = selTo = 0
        
        isBlockSelected = self._isBlockSelected
        if isBlockSelected:
            blockPosFrom, blockXFrom, blockPosTo, blockXTo = self.getBlockSelRange()
        else:
            blockPosFrom = blockXFrom = blockPosTo = blockXTo = 0

        for i from 0 <= i < len(rows):
            modified = 0
            row = rows[i]
            
            if row.setSelection(selFrom, selTo):
                modified = 1
            
            if isBlockSelected:
                if row.setBlockSelection(blockPosFrom, blockXFrom,
                        blockPosTo, blockXTo):
                    modified = 1

            if modified:
                ret.append(i)
        return ret

    cdef object _rowsplit(self, object device, long top, long end):
        rows = PymBuf_SplitRow(
            top, end, ScreenRow, self._width, PyMFCHandle_AsHandle(device.getHandle()), 
            self._buf, self._p_conf, self._nStyles, self._styles)
        self._updateSelection(rows)

        return rows

    def locate(self, long pos, int top=0, int mid=0, int bot=0, refresh=1):
        cdef long toppos, endpos
        cdef int idx
        
        assert pos <= len(self._buf)

        toppos = self._buf.getTOL(pos)
        endpos = self._buf.getEOL(toppos)
        
        self._rows = self._rowsplit(self._device, toppos, endpos)
        self._topRow = 0

        for row in self._rows:
            if pos < row.end:
                break
            if row.isLastRow():
                break
            self._topRow = self._topRow + 1

        cdef int minheight
        if bot:
            minheight = self._height - self._rows[self._topRow].height
            if minheight < 0:
                minheight = 0
        elif mid:
            minheight = self._height / 2
        else:
            minheight = 0

        cdef int height
        height = self._rows[self._topRow].height
        while height < minheight:
            if self._topRow == 0:
                endpos = self._rows[0].top
                if endpos == 0:
                    break
                toppos = self._buf.getTOL(endpos-1)

                rows = self._rowsplit(self._device, toppos, endpos)
                
                self._rows[0:0] = rows
                self._topRow = self._topRow + len(rows)
                
            self._topRow = self._topRow - 1
            assert self._topRow >= 0
            height = height + self._rows[self._topRow].height

        assert self._rows
        self.completeRows()

    def completeRows(self):
        if self._rows[-1].isLastRow():
            return

        # check current height
        cdef int maxheight, height, i
        maxheight = self._height
        height = 0
        i = 0
        for row in self._rows[self._topRow:]:
            if i and (height > maxheight):
                # remove unnecessary rows
                if self._buf.getTOL(row.top) == row.top:
                    del self._rows[i+self._topRow:]
                break
            i = i + 1
            height = height + row.height
        
#        print "@@@@@@@@@@@@@@@@", self._topRow, len(self._rows), height, self._height, self._width
        while height <= maxheight:
            top = self._rows[-1].end
            end = self._buf.getEOL(top)
            for row in self._rowsplit(self._device, top, end):
                height = height + row.height
                self._rows.append(row)

            if row.isLastRow():
                break

            if height >= maxheight:
                break

#        for row in self._rows:
#            print row.top, row.end, `self._buf[row.top:row.end]`
    
    def setScreenSize(self, int width, int height):
        self._width = width
        self._height = height
        
        if self._rows:
            pos = self._rows[self._topRow].top
            self.locate(pos)


    cdef _selChanged(self):
        updated = self._updateSelection(self._rows)
        ret = []
        for idx in updated:
            if idx >= self._topRow:
                ret.append(idx-self._topRow)
        return ret
        
    def setSelection(self, long selFrom, long selTo):
        if self._isSelected and (self._selFrom == selFrom) and (self._selTo == selTo):
            return ()

        self._selFrom = selFrom
        self._selTo = selTo
        self._isSelected = 1
        
        return self._selChanged()

    def clearSelection(self):
        self._isSelected = 0
        self._selFrom = self._selTo = 0
        return self._selChanged()
        
    def getSelection(self):
        if self._isSelected:
            return (self._selFrom, self._selTo)

    def setBlockSelection(self, selFrom, selTo):
        self._isBlockSelected = 1
        
        rc = self.calcCharLoc(selFrom)
        self._blockSelFrom = (selFrom, rc)

        rc = self.calcCharLoc(selTo)
        self._blockSelTo = (selTo, rc)

        return self._selChanged()

    def clearBlockSelection(self):
        self._isBlockSelected = 0
        self._blockSelFrom = self._blockSelTo = 0
        return self._selChanged()

    def getBlockSelection(self):
        if self._isBlockSelected:
            return (self._blockSelFrom[0], self._blockSelTo[1])

    def getSelectedBlock(self):
        cdef long toppos, endpos
        cdef object block
        cdef long blockPosFrom, blockXFrom, blockPosTo, blockXTo
        
        if not self._isBlockSelected:
            return []

        blockPosFrom, blockXFrom, blockPosTo, blockXTo = self.getBlockSelRange()
        toppos = self._buf.getTOL(blockPosFrom)
        
        ret= []
        while toppos <= blockPosTo and (toppos < self._buf.getSize()):
            endpos = self._buf.getEOL(toppos)
            rows = self._rowsplit(self._device, toppos, endpos)
            for row in rows:
                block = row.getSelectedBlock(
                        blockPosFrom, blockXFrom, blockPosTo, blockXTo)
                if block:
                    ret.append(block)
            toppos = endpos
        return ret

    cdef int _getRowIdx(self, long pos):
        cdef int i
        for i from 0 <= i < len(self._rows): 
            row = self._rows[i]
            if pos < row.top:
                return -1
            if pos < row.end:
                return i
            if pos == row.end and row.isLastRow():
                return i
        return -1
        
    def getRowIdx(self, long pos):
        cdef int ret
        ret = self._getRowIdx(pos)
        if ret != -1:
            if ret >=  self._topRow:
                ret = ret -  self._topRow
            else:
                ret = -1
        return ret

    def getRowRect(self, int idx):
        cdef int i, l, t, r, b

        t = 0
        for i from 0 <= i < idx: 
            t = t + self._rows[i+self._topRow].height

        b = t + self._rows[idx+self._topRow].height
        l = 0
        r = self._rows[idx+self._topRow].width
        
        return (l, t, r, b)
    
    def getBottomRowIdx(self):
        cdef int i, height, rowlen, h
        
        height = 0
        rowlen = len(self._rows)
        for i from 0 <= i < rowlen - self._topRow: 
            h = self._rows[i+self._topRow].height
            
            if h + height > self._height:
                if i != 0:
                    return i - 1
                else:
                    return 0
            height = height + h
        return rowlen - self._topRow - 1
        
    def getCharRect(self, long pos):
        cdef long n, i, l, t, r, b
        n = self.getRowIdx(pos)
        if n == -1:
            return None
        t = 0
        for i from 0 <= i < n: 
            t = t + self._rows[i+self._topRow].height
        
        row = self._rows[n+self._topRow]
        b = t + row.height
        t = t + self._conf.linegap
        l, r = row.posToLoc(pos)
        
        return l, t, r, b

    def calcCharLoc(self, pos):
        n = self.getRowIdx(pos)
        if n != -1:
            row = self._rows[n+self._topRow]
            return row.posToLoc(pos)
        else:
            toppos = self._buf.getTOL(pos)
            endpos = self._buf.getEOL(toppos)
            rows = self._rowsplit(self._device, toppos, endpos) 
            for row in rows:
                if pos < row.end:
                    return row.posToLoc(pos)

    def paintRow(self, row, dc, pos, width):
        rows = PymEditor_PaintRow(row, dc, pos[0], pos[1], width, self._p_conf, self._nStyles, self._styles)


    def splitBuf(self):
        cdef long toppos, endpos
        cdef HDC hdc
        
        hdc = PyMFCHandle_AsHandle(self._device.getHandle())
        toppos= 0
        
        ret = []
        while True:
            endpos = self._buf.getEOL(toppos)
            rows = PymBuf_SplitRow(
                toppos, endpos, ScreenRow, self._width, hdc, 
                self._buf, self._p_conf, self._nStyles, self._styles)
            
            for row in rows:
                ret.append((row.top, row.end, row.indentCol))
                if row.isLastRow():
                    return ret
            toppos = endpos
        