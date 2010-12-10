import time, re
from pymfc import gdi
from pymfc.editor import buffer, bufre, highlight
from pymfc.editor.commands import KEY




class URLTokenizer(highlight.Tokenizer):

    url = ur"\bhttp://[-\w.~/?&=;:#%+]+"
    mailto = ur"\b[-\w.~/?&=;:#%+]+@[-\w.]+"

    STATE_LIST = [
        highlight.TokenState(u'URL', url, None, cursor=gdi.Cursor(hand=True)),
#        highlight.TokenState(u'MAILTO', mailto, None, cursor=gdi.Cursor(hand=True)),
    ]


class Mode(object):
    MODENAME = ''
    tabIndent = True
    tabSize = 8
    indentSize = 4
    
    def __init__(self, buf):
        self._buf = buf
        self._wnds = []
        self._initCommands()
        self._tokenizer = self._getTokenizer()
        if self._tokenizer:
            self._highlight = highlight.Highlight(self._buf, self._tokenizer)
        else:
            self._highlight = None
            
        self._readonly = False
        
    def _getTokenizer(self):
#        return URLTokenizer()
        return None

    def _initCommands(self):
        commands = self._loadCommands()
        self._commands = dict([(cmd.getId(), cmd(self)) for cmd in commands])
        self._keymap = self._loadKeyMap()

    def _loadCommands(self):
        return getCommands()
    
    def _loadKeyMap(self):
        return getKeyMap()

    def addKeymap(self, key, cmdname):
        self._keymap[key] = cmdname

        for wnd in self._wnds:
            wnd.registerKeyMap(self._keymap)

        
    def addCommand(self, cmd):
        self._commands[cmd.getId()] = cmd(self)
        
    def isReadOnly(self):
        return self._readonly
    
    def setReadOnly(self, readonly):
        self._readonly = readonly
        
    def getBuf(self):
        return self._buf
    buf = property(getBuf)
    
    def attachWnd(self, wnd):
        self._wnds.append(wnd)
        wnd.registerKeyMap(self._keymap)
        
    def detachWnd(self, wnd):
        self._wnds.remove(wnd)

    def getWnds(self):
        return self._wnds
        
    def runHighlight(self):
        if self._highlight:
            return self._highlight.highLight(self)
        else:
            return 0

    def bufModified(self, pos, inslen, dellen):
        for wnd in self._wnds:
            wnd.onBufModified(pos, inslen, dellen)
        
        if self._highlight:
            self._highlight.updated(pos)
            self._highlight.highLight(self, single=True)
        
    def runKeyCommand(self, wnd, keys, cmdname):
        cmd = self._commands[cmdname]
        cmd.run(wnd, keys=keys)
    
    def runCommand(self, wnd, cmdname):
        cmd = self._commands[cmdname]
        cmd.run(wnd)
        
    def checkCommand(self, wnd, cmdname):
        cmd = self._commands[cmdname]
        return cmd.isEnabled(wnd)

    def putString(self, wnd, s, insert=False):
        if not s:
            return
        if wnd.isSelected():
            f, t = wnd.getSelectedPos()
            if f != t:
                self.replaceString(wnd, f, t, s)
                return
        elif wnd.isBlockSelected():
            blocks = wnd.getSelectedBlock()
            if not blocks:
                return
            s = re.split(u"[\r\n]+", s)
            if not lines:
                self._delSelection(wnd)
                return

            reps = zip(blocks, lines)
            dels = blocks[len(reps):]
            ins = u"\n".join(lines[len(reps):])
            if ins:
                reps[-1] = (reps[-1][0], reps[-1][1]+u"\n"+ins)
            self._buf.undo.beginGroup()
            try:
                dels.reverse() # delete from latter block
                for f, t in dels:
                    self.delString(wnd, f, t, f, moveCaret=False)
                    
                reps.reverse() # replace from latter block first
                for (f, t), s in reps:
                    if f != t:
                        self.replaceString(wnd, f, t, s, moveCaret=False)
                wnd.caret.locate(f, top=True, saveCol=True)
            finally:
                self._buf.undo.endGroup()
            return

        if wnd.isInsMode() or insert:
            self.insertString(wnd, wnd.caret.pos, s)
        else:
            inslen = len(s)
            pos = wnd.caret.pos
            posto = min(pos+inslen, self._buf.getLineFeed(pos))
            self.replaceString(wnd, pos, posto, s)

    def insertString(self, wnd, pos, s, moveCaret=True, oldpos=None):
        if oldpos is None:
            oldpos = wnd.caret.pos
        self._buf.ins(pos, s)

        self.bufModified(pos, len(s), 0)
        if moveCaret:
            wnd.caret.right(len(s))
        self._buf.undo.inserted(pos, s, oldpos, wnd.caret.pos)
        wnd.clearSelection()
        
    def replaceString(self, wnd, pos, posto, s, moveCaret=True, oldpos=None):
        if oldpos is None:
            oldpos = wnd.caret.pos
        deled = self._buf[pos:posto]
        self._buf.delete(pos, posto)
        self._buf.ins(pos, s)
        self.bufModified(pos, len(s), len(deled))
        if moveCaret:
            wnd.caret.locate(pos+len(s), saveCol=True)
        self._buf.undo.replaced(pos, s, deled, oldpos, wnd.caret.pos)
        wnd.clearSelection()
        
    def delString(self, wnd, f, t, newpos, moveCaret=True, oldpos=None):
        if f < t:
            if oldpos is None:
                oldpos = wnd.caret.pos
            s = self._buf.get(f, t)
            self._buf.delete(f, t)
            self.bufModified(f, 0, t-f)
            if moveCaret:
                wnd.caret.locate(f, saveCol=True)
            self._buf.undo.deleted(f, s, oldpos, newpos)
            wnd.clearSelection()
            return s

    def onSetCursor(self, wnd):
        loc = wnd.getCursorPos()
        pos = wnd.locToPos(loc)
        
        if self._tokenizer and (pos < len(self._buf)-1):
            style = self._buf.getStyle(pos, pos+1)[0]
            if style:
                cursor = self._tokenizer.STATE_LIST[style-1].cursor
                if cursor:
                    cursor.setCursor()
                    return
            
        cursor = gdi.Cursor(ibeam=True)
        cursor.setCursor()
        
    def onChar(self, wnd, char):
        if self._readonly:
            return
        self.putString(wnd, char)

    def onLButtonDown(self, wnd, x, y, alt, ctrl, shift):
        wnd.setFocus()
        
        x = max(0, x)
        pos = wnd.locToPos((x, y))
        if not shift and not ctrl and not alt:
            wnd.clearSelection()
            wnd.caret.locate(pos, saveCol=True)
            wnd.startSelection()
            wnd.startMouseSelection()
        elif shift and not ctrl and not alt:
            wnd.startSelection()
            wnd.caret.locate(pos, saveCol=True)
            wnd.setSelectionTo()
            wnd.startMouseSelection()
        elif not shift and not ctrl and alt:
            wnd.clearSelection()
            wnd.caret.locate(pos, saveCol=True)
            wnd.startBlockSelection()
            wnd.startMouseBlockSelection()

        
    def onLButtonDblClk(self, wnd, x, y, alt, ctrl, shift):
        wnd.setFocus()
        pos = wnd.locToPos((x, y))
        word = self.getWord(pos)
        if word[0] != word[1]:
            wnd.caret.locate(word[1], saveCol=True)
            wnd.setSelection(word[0], word[1])
        
        
    def _delSelection(self, wnd):
        if wnd.isSelected():
            f, t = wnd.getSelectedPos()
            if f != t:
                self.delString(wnd, f, t, f, moveCaret=False)
                wnd.caret.locate(f, top=True, saveCol=True)
                return True
        elif wnd.isBlockSelected():
            blocks = wnd.getSelectedBlock()
            blocks.reverse() # delete from latter block first
            self._buf.undo.beginGroup()
            try:
                for f, t in blocks:
                    self.delString(wnd, f, t, f, moveCaret=False)
                wnd.caret.locate(f, top=True, saveCol=True)
            finally:
                self._buf.undo.endGroup()
            return True
    
    def getSelection(self, wnd):
        if wnd.isSelected():
            f, t = wnd.getSelectedPos()
            if f != t:
                return self._buf[f:t]
        elif wnd.isBlockSelected():
            blocks = wnd.getSelectedBlock()
            return [self._buf[f:t] for f,t in blocks]
        
        
    def delete(self, wnd):
        if self._delSelection(wnd):
            return

        pos = wnd.caret.pos
        if pos < len(self._buf):
            self.delString(wnd, pos, pos+1, pos, moveCaret=False)
            wnd.caret.showPos()
            wnd.caret.show()

    def deleteWord(self, wnd):
        if self._delSelection(wnd):
            return

        pos = wnd.caret.pos
        next = self.getNextWordBreak(pos)
        if pos != next:
            self.delString(wnd, pos, next, pos, moveCaret=False)
            wnd.caret.showPos()
            wnd.caret.show()

    def backspace(self, wnd):
        if self._delSelection(wnd):
            return

        pos = wnd.caret.pos
        if pos and pos <= len(self._buf):
            wnd.caret.locate(pos-1, top=True, saveCol=True)
            self.delString(wnd, pos-1, pos, pos-1, moveCaret=False, oldpos=pos)

    def backspaceWord(self, wnd):
        if self._delSelection(wnd):
            return

        pos = wnd.caret.pos
        next = self.getPrevWordBreak(pos)
        if pos != next:
            self.delString(wnd, next, pos, next, moveCaret=False)
            wnd.caret.locate(next, top=True, saveCol=True)

    RE_INDENT = bufre.compile(ur"[ \t]+")
    def _getIndentWS(self, tol):
        eol = self._buf.getEOL(tol)
        m = self.RE_INDENT.match(self._buf, tol, eol)
        if not m:
            return (tol, tol)
        else:
            return m.span()
    
    def _countIndentCol(self, ws):
        cspc = 0
        for c in ws:
            if c == u'\t':
                cspc = cspc + self.tabSize - cspc % self.tabSize
            elif c == u' ':
                cspc = cspc + 1
            else:
                break
        return cspc
    
    def _buildIndentWS(self, col):
        if col < 0:
            col = 0
        if self.tabIndent:
            ctab = col / self.tabSize
            cspc = col % self.tabSize
            return u'\t' * ctab + ' ' * cspc
        else:
            return u' ' * col

    def indent(self, wnd):
        if not wnd.isSelected():
            # no selection
            pos = wnd.caret.pos
            tol = self._buf.getTOL(pos)

            # if cursor is not at top of line, then
            # don't indent but put tab(\t) char.
            f, t = self._getIndentWS(tol)
            if pos > t:
                self.putString(wnd, u"\t")
            else:
                ws = self._buf[f:t]
                ncol = self._countIndentCol(ws)
                ws = self._buildIndentWS(ncol+self.indentSize)
                self.replaceString(wnd, f, t, ws)
        else:
            # has selection
            selfrom, selto = wnd.getSelectedPos()
            f_eol = self._buf.getEOL(selfrom)
            t_eol = self._buf.getEOL(selto)

            if f_eol == t_eol:
                # single line selection
                self.putString(wnd, u"\t")
            else:
                # multi line selection

                # adjust indent range
                t_tol = self._buf.getTOL(selto)
                seltop = f_tol = self._buf.getTOL(selfrom)
                selend = t_eol
                
                if selto and (selto == t_tol):
                    selend = t_tol
                    t_eol = t_tol - 1
                else:
                    selend = t_eol
                    
                self._buf.undo.beginGroup()
                try:
                    lines = []
                    while f_tol < t_eol:
                        eol = self._buf.getEOL(f_tol)
                        f, t = self._getIndentWS(f_tol)
                        ws = self._buf[f:t]
                        ncol = self._countIndentCol(ws)
                        wsnew = self._buildIndentWS(ncol+self.indentSize)
                        diff = len(wsnew)-len(ws)
                        self.replaceString(wnd, f, t, wsnew)
                        f_tol = eol+diff
                        t_eol = t_eol+diff
                        selend = selend+diff

                    wnd.setSelection(seltop, selend)
                    wnd.caret.locate(selend, saveCol=True)
                finally:
                    self._buf.undo.endGroup()

    def unIndent(self, wnd):
        if not wnd.isSelected():
            # no selection
            pos = wnd.caret.pos
            tol = self._buf.getTOL(pos)

            f, t = self._getIndentWS(tol)
            ws = self._buf[f:t]
            ncol = self._countIndentCol(ws)
            ws = self._buildIndentWS(ncol-self.indentSize)
            self.replaceString(wnd, f, t, ws)
        else:
            # has selection
            selfrom, selto = wnd.getSelectedPos()
            f_eol = self._buf.getEOL(selfrom)
            t_eol = self._buf.getEOL(selto)

            # adjust indent range
            t_tol = self._buf.getTOL(selto)
            seltop = f_tol = self._buf.getTOL(selfrom)
            selend = t_eol
            
            if selto and (selto == t_tol):
                selend = t_tol
                t_eol = t_tol - 1
            else:
                selend = t_eol
            
            self._buf.undo.beginGroup()
            try:
                lines = []
                seltop = f_tol = self._buf.getTOL(selfrom)
                while f_tol < t_eol:
                    eol = self._buf.getEOL(f_tol)
                    f, t = self._getIndentWS(f_tol)
                    ws = self._buf[f:t]
                    ncol = self._countIndentCol(ws)
                    wsnew = self._buildIndentWS(ncol-self.indentSize)
                    diff = len(wsnew)-len(ws)
                    self.replaceString(wnd, f, t, wsnew)
                    f_tol = eol+diff
                    t_eol = t_eol+diff
                    selend = selend+diff

                wnd.setSelection(seltop, selend)
                wnd.caret.locate(selend, saveCol=True)
            finally:
                self._buf.undo.endGroup()

        
    def newline(self, wnd):
        pos = wnd.caret.pos
        tol = self._buf.getTOL(pos)
        f, t = self._getIndentWS(tol)
        s = self._buf[f:min(t, pos)]
        self.putString(wnd, u"\n"+s, insert=True)
        return

    def undo(self, wnd):
        if self._buf.undo.canUndo():
            newpos = self._buf._undo.undo(self)
            wnd.clearSelection()
            wnd.caret.locate(newpos, mid=True, saveCol=True)

    def redo(self, wnd):
        if self._buf.undo.canRedo():
            newpos = self._buf._undo.redo(self)
            wnd.clearSelection()
            wnd.caret.locate(newpos, mid=True, saveCol=True)

    '''
    hiragana
    3040-309f

    katakana
    30A0-30FF

    CJK Symbols and Punctuation
    3000-303f

    Katakana Phonetic Extensions
    31F0-31FF

    Enclosed CJK Letters and Months
    3200-32ff

    CJK Compatibility
    Range: 3300-33FF

    CJK Unified Ideographs Extension A
    Range: 3400-4DBF

    CJK Unified Ideographs
    Range: 4E00-F9FAF

    Private Use Area
    Range: E000-F8FF

    CJK Compatibility Ideographs
    Range: F900-FAFF

    CJK Compatibility Forms
    Range: FE30-FE4F

    Halfwidth and Fullwidth Forms
    Range: FF00-FFEF
    '''

    #todo: these expressions should be defined in LANG package.

    re_wordchar = ur"(?P<WORDCHAR>[a-zA-Z0-9_]+)"
    re_lf = ur"(?P<LF>\u000a)"
    re_ws = ur"(?P<WS>[\u0009\u000b-\u000d\u0020]+)"
    re_cntl = ur"(?P<CNTL>[\u0000-\u0008\u000e-\u001f\u007f]+)"
    re_symbol = ur"(?P<SYMBOL>[\u0021-\u002f\u003a-\u0040\u005b-\u0060\u007b-\u007d]+)"
    
    # both hiragana and katakana contains \u30fc(KATAKANA-HIRAGANA PROLONGED SOUND MARK)
    re_hiragana = ur"(?P<HIRAGANA>[\u3040-\u309f\u30fc]+)" 
    re_katakana = ur"(?P<KATAKANA>[\u30a0-\u30ff\u30fc]+)"
    re_half_kana = ur"(?P<HALF_KANA>[\uff61-\uff9f]+)"
    re_full_ws = ur"(?P<FULL_WS>\u3000+)"
    re_cjk_symbol = ur"(?P<CJK_SYMBOL>[\u3001-\u303f]+)"
    re_full_alnum = ur"(?P<FULL_ALNUM>[\uff10-\uff19\uff21-\uff3a\uff41-\uff5a]+)"
    re_full_symbol = ur"(?P<FULL_SYMBOL>[\uff00-\uff0f\uff20\uff3b-\uff40\uff5b-\uff60\uffa0-\uffef]+)"
    
    re_wordbreak = bufre.compile("|".join([
        re_wordchar, re_lf, re_ws, re_cntl, re_symbol, re_hiragana, 
        re_katakana, re_half_kana, re_full_ws, re_cjk_symbol, re_full_alnum, 
        re_full_symbol]))
    
    def _splitWord(self, f, t):
        last = f
        for m in self.re_wordbreak.finditer(self._buf, f, t):
            start = m.start()
            end = m.end()
            s = m.group()
            if start != last:
                yield (last, start, self._buf[last:start])
            yield (start, end, s)
            last = end
        if last != t:
            yield (last, t, self._buf[last:t])

    def getNextWordBreak(self, pos):
        tol = self._buf.getTOL(pos)
        eol = self._buf.getEOL(pos)

        ret = tol - 1
        if ret < 0:
            ret = 0

        for f, t, s in self._splitWord(tol, eol):
            if (pos < f):
                return f
        else:
            return eol

    def getPrevWordBreak(self, pos):
        tol = self._buf.getTOL(pos)
        eol = self._buf.getEOL(pos)

        if pos == tol:
            return max(tol-1, 0)

        ret = tol
        for f, t, s in self._splitWord(tol, eol):
            if pos <= t:
                if f == pos:
                    return ret
                elif f < pos:
                    return f
                ret = f
        else:
            return ret

    def getWord(self, pos):
        size = len(self._buf)
        if pos == size:
            end = pos
        elif self._buf[pos:pos+1] == u'\n':
            end = pos
        else:
            end = self.getNextWordBreak(pos)

        tol = self.buf.getTOL(pos)
        if pos == tol:
            top = pos
        else:
            top = self.getPrevWordBreak(end)
        return (top, end)

    def _searchNext(self, wnd, cond, pos=None):
        searchlen = len(cond.string)
        if not searchlen:
            return -1
            
        selfrom = selto = -1
        if pos is None:
            pos = wnd.caret.pos

        to = len(self._buf)
        while pos < to:
            ret = self._buf.findString(pos, to, cond.string, not cond.ignorecase, True)
            if ret == -1:
                return -1

            if cond.matchword:
                bf, bt = self.getWord(ret)
                ef, et = self.getWord(ret+searchlen-1)
                if bf != ret or et != ret+searchlen:
                    pos = ret + 1
                    continue
            return ret
        return -1

    def searchNext(self, wnd, pos=None):
        from pymfc.editor import searchdlg
        pos = self._searchNext(wnd, searchdlg.LASTSEARCH, pos)
        
        if pos != -1:
            searchdlg.LASTSEARCH.lastmatch = (pos, pos+len(searchdlg.LASTSEARCH.string))
            selto = pos+len(searchdlg.LASTSEARCH.string)
            wnd.caret.locate(selto, saveCol=True)
            wnd.setSelection(pos, selto)
            return (pos, selto)
            
    def _searchPrev(self, wnd, cond, pos=None):
        searchlen = len(cond.string)
        if not searchlen:
            return -1

        selfrom = selto = -1
        if pos is None:
            pos = wnd.caret.pos

        to = 0
        while pos>=0:
            ret = self._buf.findString(to, pos, cond.string, not cond.ignorecase, False)
            if ret == -1:
                return -1

            if cond.matchword:
                bf, bt = self.getWord(ret)
                ef, et = self.getWord(ret+searchlen-1)
                if bf != ret or et != ret+searchlen:
                    if pos == 0:
                        return -1
                    pos = ret+searchlen-1
                    continue
            
            return ret

        return -1

    def searchPrev(self, wnd, pos=None):
        from pymfc.editor import searchdlg
        pos = self._searchPrev(wnd, searchdlg.LASTSEARCH, pos)
        if pos != -1:
            searchdlg.LASTSEARCH.lastmatch = (pos, pos+len(searchdlg.LASTSEARCH.string))
            wnd.caret.locate(pos, saveCol=True)
            selto = pos+len(searchdlg.LASTSEARCH.string)
            wnd.setSelection(pos, selto)
            return (pos, selto)
            
#    def searchPrev(self, wnd):
#        from pymfc.editor import searchdlg
#        if not wnd.isSelected():
#            # no selection
#            selfrom = selto = -1
#            pos = wnd.caret.pos
#        else:
#            # has selection
#            selfrom, selto = wnd.getSelectedPos()
#            pos = selfrom
#        to = 0
#
#        cond = searchdlg.LASTSEARCH
#        ret = self._buf.findString(to, pos, cond.string, not cond.ignorecase, False)
#        if ret == -1:
#            return
#        if ret == pos and (selto==ret+len(cond.string)):
#            pos += 1
#            ret = self._buf.findString(to, pos, cond.string, not cond.ignorecase, False)
#            if ret == -1:
#                return
#        wnd.caret.locate(ret, saveCol=True)
#        wnd.setSelection(ret, ret+len(cond.string))
#        

        

def getCommands():
    from pymfc.editor.commands import editorcommand
    commands = [
        # cursor commands
        editorcommand.CaretRight, editorcommand.CaretRightSelect, 
        editorcommand.CaretWordRight, editorcommand.CaretWordRightSelect, 
        editorcommand.CaretLeft, editorcommand.CaretLeftSelect,
        editorcommand.CaretWordLeft, editorcommand.CaretWordLeftSelect,
        editorcommand.CaretUp, editorcommand.CaretUpSelect,
        editorcommand.CaretDown, editorcommand.CaretDownSelect,

        editorcommand.CaretPageDown, editorcommand.CaretPageDownSelect,
        editorcommand.CaretPageUp, editorcommand.CaretPageUpSelect,
        
        editorcommand.CaretHome, editorcommand.CaretHomeSelect,
        editorcommand.CaretEnd, editorcommand.CaretEndSelect,
        editorcommand.CaretTop, editorcommand.CaretTopSelect, 
        editorcommand.CaretBottom, editorcommand.CaretBottomSelect, 
        editorcommand.CaretSelectAll,

        # edit commands
        editorcommand.EditToggleInsMode, 
        editorcommand.EditLinefeed, 
        editorcommand.EditDelete, editorcommand.EditWordDelete, 
        editorcommand.EditBackspace, editorcommand.EditWordBackspace, 
        editorcommand.EditUndo, editorcommand.EditRedo, 
        editorcommand.EditClipCopy, editorcommand.EditClipCut,
        editorcommand.EditClipPaste,
        editorcommand.EditIndent, editorcommand.EditUnIndent,
        editorcommand.EditBeginSearch, editorcommand.EditBeginReplace,
        editorcommand.EditSearchAgain, 
        editorcommand.EditSearchBackwardAgain,
    ]
    return commands

def getKeyMap():
    keys = {
        # cursor command
        ((0, 0, 0, KEY.RIGHT),):"caret.right",
        ((0, 0, 1, KEY.RIGHT),):"caret.right.select",

        ((0, 1, 0, KEY.RIGHT),):"caret.wordright",
        ((0, 1, 1, KEY.RIGHT),):"caret.wordright.select",

        ((0, 0, 0, KEY.LEFT),):"caret.left",
        ((0, 0, 1, KEY.LEFT),):"caret.left.select",

        ((0, 1, 0, KEY.LEFT),):"caret.wordleft",
        ((0, 1, 1, KEY.LEFT),):"caret.wordleft.select",

        ((0, 0, 0, KEY.DOWN),):"caret.down",
        ((0, 0, 1, KEY.DOWN),):"caret.down.select",

        ((0, 0, 0, KEY.UP),):"caret.up",
        ((0, 0, 1, KEY.UP),):"caret.up.select",

        ((0, 0, 0, KEY.HOME),):"caret.home",
        ((0, 0, 1, KEY.HOME),):"caret.home.select",

        ((0, 0, 0, KEY.END),):"caret.end",
        ((0, 0, 1, KEY.END),):"caret.end.select",

        ((0, 1, 0, KEY.HOME),):"caret.top",
        ((0, 1, 1, KEY.HOME),):"caret.top.select",

        ((0, 1, 0, KEY.END),):"caret.bottom",
        ((0, 1, 1, KEY.END),):"caret.bottom.select",

        ((0, 0, 0, KEY.PGDN),):"caret.pagedown",
        ((0, 0, 1, KEY.PGDN),):"caret.pagedown.select",

        ((0, 0, 0, KEY.PGUP),):"caret.pageup",
        ((0, 0, 1, KEY.PGUP),):"caret.pageup.select",

        ((0, 1, 0, 'a'),):"caret.select.all",
        ((0, 1, 0, 'A'),):"caret.select.all",

        # edit command
        ((0, 0, 0, KEY.INSERT),):"edit.insmode.toggle",
        ((0, 0, 0, KEY.ENTER),):"edit.linefeed",
        ((0, 0, 0, KEY.TAB),):"edit.indent",
        ((0, 0, 1, KEY.TAB),):"edit.unindent",
        ((0, 0, 0, KEY.DELETE),):"edit.delete",
        ((0, 1, 0, KEY.DELETE),):"edit.worddelete",
        ((0, 0, 0, KEY.BACKSPACE),):"edit.backspace",
        ((0, 1, 0, KEY.BACKSPACE),):"edit.wordbackspace",

        ((0, 1, 0, 'z'),):"edit.undo",
        ((0, 1, 0, 'Z'),):"edit.undo",
        ((0, 1, 0, 'y'),):"edit.redo",
        ((0, 1, 0, 'Y'),):"edit.redo",

        ((0, 1, 0, 'x'),):"edit.clipboard.cut",
        ((0, 1, 0, 'X'),):"edit.clipboard.cut",
        ((0, 1, 0, 'c'),):"edit.clipboard.copy",
        ((0, 1, 0, 'C'),):"edit.clipboard.copy",
        ((0, 1, 0, 'v'),):"edit.clipboard.paste",
        ((0, 1, 0, 'V'),):"edit.clipboard.paste",

        ((0, 1, 0, 'f'),):"edit.search.begin",
        ((0, 1, 0, 'F'),):"edit.search.begin",
        ((0, 1, 0, 'r'),):"edit.replace.begin",
        ((0, 1, 0, 'R'),):"edit.replace.begin",
        ((0, 0, 0, KEY.F3),):"edit.search.again",
        ((0, 0, 1, KEY.F3),):"edit.search.again.backward",

#        ((0, 1, 0, KEY.F5),):"recordcommand.toggle",
#        ((0, 0, 0, KEY.F5),):"recordcommand.replay",


        # file menu
#        ((0, 1, 0, 'n'),):"file.new",
#        ((0, 1, 0, 'o'),):"file.open",
#        ((0, 1, 0, 's'),):"file.save",

    }

    return keys
