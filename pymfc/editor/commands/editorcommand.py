import re
import pymfc

class Command(object):
    NOREC=False

    def __init__(self, mode):
        self._mode = mode
        
    @classmethod
    def getId(cls):
        return cls.COMMANDID
    
    @classmethod
    def isRecordable(cls):
        return not cls.NOREC
    
    def isEnabled(self, wnd):
        return True

# caret commands
class CaretRight(Command):
    COMMANDID = "caret.right"
    def run(self, wnd, *args, **kwargs):
        wnd.clearSelection()
        wnd.caret.right()

class CaretRightSelect(Command):
    COMMANDID = "caret.right.select"
    def run(self, wnd, *args, **kwargs):
        wnd.startSelection()
        wnd.caret.right()
        wnd.setSelectionTo()

class CaretWordRight(Command):
    COMMANDID = "caret.wordright"
    def run(self, wnd, *args, **kwargs):
        pos = wnd.caret.pos
        next = self._mode.getNextWordBreak(pos)
        if pos != next:
            wnd.clearSelection()
            wnd.caret.right(next-pos)

class CaretWordRightSelect(Command):
    COMMANDID = "caret.wordright.select"
    def run(self, wnd, *args, **kwargs):
        pos = wnd.caret.pos
        next = self._mode.getNextWordBreak(pos)
        if pos != next:
            wnd.startSelection()
            wnd.caret.right(next-pos)
            wnd.setSelectionTo()

class CaretLeft(Command):
    COMMANDID = "caret.left"
    def run(self, wnd, *args, **kwargs):
        wnd.clearSelection()
        wnd.caret.left()

class CaretLeftSelect(Command):
    COMMANDID = "caret.left.select"
    def run(self, wnd, *args, **kwargs):
        wnd.startSelection()
        wnd.caret.left()
        wnd.setSelectionTo()

class CaretWordLeft(Command):
    COMMANDID = "caret.wordleft"
    def run(self, wnd, *args, **kwargs):
        pos = wnd.caret.pos
        prev = self._mode.getPrevWordBreak(pos)
        if pos != prev:
            wnd.clearSelection()
            wnd.caret.left(pos-prev)

class CaretWordLeftSelect(Command):
    COMMANDID = "caret.wordleft.select"
    def run(self, wnd, *args, **kwargs):
        pos = wnd.caret.pos
        prev = self._mode.getPrevWordBreak(pos)
        if pos != prev:
            wnd.startSelection()
            wnd.caret.left(pos-prev)
            wnd.setSelectionTo()

class CaretUp(Command):
    COMMANDID = "caret.up"
    def run(self, wnd, *args, **kwargs):
        wnd.clearSelection()
        wnd.caret.up()

class CaretUpSelect(Command):
    COMMANDID = "caret.up.select"
    def run(self, wnd, *args, **kwargs):
        wnd.startSelection()
        wnd.caret.up()
        wnd.setSelectionTo()

class CaretDown(Command):
    COMMANDID = "caret.down"
    def run(self, wnd, *args, **kwargs):
        wnd.clearSelection()
        wnd.caret.down()

class CaretDownSelect(Command):
    COMMANDID = "caret.down.select"
    def run(self, wnd, *args, **kwargs):
        wnd.startSelection()
        wnd.caret.down()
        wnd.setSelectionTo()

class CaretPageDown(Command):
    COMMANDID = "caret.pagedown"
    def run(self, wnd, *args, **kwargs):
        wnd.clearSelection()
        if not wnd.caret.pageDown():
            wnd.caret.locate(self._mode.buf.getSize(), saveCol=False)

class CaretPageDownSelect(Command):
    COMMANDID = "caret.pagedown.select"
    def run(self, wnd, *args, **kwargs):
        wnd.startSelection()
        if not wnd.caret.pageDown():
            wnd.caret.locate(self._mode.buf.getSize(), saveCol=False)
        wnd.setSelectionTo()

class CaretPageUp(Command):
    COMMANDID = "caret.pageup"
    def run(self, wnd, *args, **kwargs):
        wnd.clearSelection()
        if not wnd.caret.pageUp():
            wnd.caret.locate(0, saveCol=False)

class CaretPageUpSelect(Command):
    COMMANDID = "caret.pageup.select"
    def run(self, wnd, *args, **kwargs):
        wnd.startSelection()
        if not wnd.caret.pageUp():
            wnd.caret.locate(0, saveCol=False)
        wnd.setSelectionTo()

class CaretSelectAll(Command):
    COMMANDID = 'caret.select.all'
    def run(self, wnd, *args, **kwargs):
        wnd.clearSelection()
        wnd.setSelection(0, len(self._mode.buf))
    
class CaretHome(Command):
    COMMANDID = "caret.home"
    def run(self, wnd, *args, **kwargs):
        wnd.clearSelection()
        wnd.caret.home()

class CaretHomeSelect(Command):
    COMMANDID = "caret.home.select"
    def run(self, wnd, *args, **kwargs):
        wnd.startSelection()
        wnd.caret.home()
        wnd.setSelectionTo()

class CaretEnd(Command):
    COMMANDID = "caret.end"
    def run(self, wnd, *args, **kwargs):
        wnd.clearSelection()
        wnd.caret.end()

class CaretEndSelect(Command):
    COMMANDID = "caret.end.select"
    def run(self, wnd, *args, **kwargs):
        wnd.startSelection()
        wnd.caret.end()
        wnd.setSelectionTo()

class CaretTop(Command):
    COMMANDID = "caret.top"
    def run(self, wnd, *args, **kwargs):
        wnd.clearSelection()
        wnd.caret.top()

class CaretTopSelect(Command):
    COMMANDID = "caret.top.select"
    def run(self, wnd, *args, **kwargs):
        wnd.startSelection()
        wnd.caret.top()
        wnd.setSelectionTo()

class CaretBottom(Command):
    COMMANDID = "caret.bottom"
    def run(self, wnd, *args, **kwargs):
        wnd.clearSelection()
        wnd.caret.bottom()

class CaretBottomSelect(Command):
    COMMANDID = "caret.bottom.select"
    def run(self, wnd, *args, **kwargs):
        wnd.startSelection()
        wnd.caret.bottom()
        wnd.setSelectionTo()


# edit commands

class EditToggleInsMode(Command):
    COMMANDID = "edit.insmode.toggle"
    def run(self, wnd, *args, **kwargs):
        return # not implemented yet!
        
class EditLinefeed(Command):
    COMMANDID = "edit.linefeed"
    def run(self, wnd, *args, **kwargs):
        if not self._mode.isReadOnly():
            self._mode.newline(wnd)

class EditDelete(Command):
    COMMANDID = "edit.delete"
    def run(self, wnd, *args, **kwargs):
        if not self._mode.isReadOnly():
            self._mode.delete(wnd)

class EditWordDelete(Command):
    COMMANDID = "edit.worddelete"
    def run(self, wnd, *args, **kwargs):
        if not self._mode.isReadOnly():
            self._mode.deleteWord(wnd)

class EditBackspace(Command):
    COMMANDID = "edit.backspace"
    def run(self, wnd, *args, **kwargs):
        if not self._mode.isReadOnly():
            self._mode.backspace(wnd)

class EditWordBackspace(Command):
    COMMANDID = "edit.wordbackspace"
    def run(self, wnd, *args, **kwargs):
        if not self._mode.isReadOnly():
            self._mode.backspaceWord(wnd)

class EditUndo(Command):
    COMMANDID = "edit.undo"
    def run(self, wnd, *args, **kwargs):
        if not self._mode.isReadOnly():
            self._mode.undo(wnd)

    def isEnabled(self, wnd):
        return self._mode.getBuf().undo.canUndo()


class EditRedo(Command):
    COMMANDID = "edit.redo"
    def run(self, wnd, *args, **kwargs):
        if not self._mode.isReadOnly():
            self._mode.redo(wnd)

    def isEnabled(self, wnd):
        return self._mode.getBuf().undo.canRedo()

class EditClipCopy(Command):
    COMMANDID = "edit.clipboard.copy"
    def run(self, wnd, *args, **kwargs):
        sel = self._mode.getSelection(wnd)
        if isinstance(sel, unicode):
            s = u"\r\n".join(sel.split(u"\n"))
        elif isinstance(sel, (list, tuple)):
            s = u"\r\n".join(sel)
        else:
            return
        wnd.openClipboard()
        try:
            wnd.emptyClipboard()
            wnd.setClipboardText(s)
        finally:
            wnd.closeClipboard()
            
    def isEnabled(self, wnd):
        return wnd.isSelected() or wnd.isBlockSelected()

class EditClipCut(Command):
    COMMANDID = "edit.clipboard.cut"    

    def run(self, wnd, *args, **kwargs):
        if not self._mode.isReadOnly():
            sel = self._mode.getSelection(wnd)
            if isinstance(sel, unicode):
                s = u"\r\n".join(sel.split(u"\n"))
            elif isinstance(sel, (list, tuple)):
                s = u"\r\n".join(sel)
            else:
                return
            wnd.openClipboard()
            try:
                wnd.emptyClipboard()
                wnd.setClipboardText(s)
            finally:
                wnd.closeClipboard()

            self._mode.delete(wnd)

    def isEnabled(self, wnd):
        if not self._mode.isReadOnly():
            return wnd.isSelected() or wnd.isBlockSelected()

class EditClipPaste(Command):
    COMMANDID = "edit.clipboard.paste"

    def run(self, wnd, *args, **kwargs):
        cf = pymfc.ClipFormat(unicodetext=True)
        if not wnd.isClipboardFormatAvailable(cf):
            return

        if not self._mode.isReadOnly():
            wnd.openClipboard()
            try:
                s = wnd.getClipboardText()
                s = re.sub(ur"\r\n", ur"\n", s)
                self._mode.putString(wnd, s)
            finally:
                wnd.closeClipboard()

    def isEnabled(self, wnd):
        cf = pymfc.ClipFormat(unicodetext=True)
        return wnd.isClipboardFormatAvailable(cf)
            

class EditIndent(Command):
    COMMANDID = "edit.indent"

    def run(self, wnd, *args, **kwargs):
        if not self._mode.isReadOnly():
            self._mode.indent(wnd)
                        
        
class EditUnIndent(Command):
    COMMANDID = "edit.unindent"

    def run(self, wnd, *args, **kwargs):
        if not self._mode.isReadOnly():
            self._mode.unIndent(wnd)
        
        
class EditBeginSearch(Command):
    COMMANDID = "edit.search.begin"

    def run(self, wnd, *args, **kwargs):
        from pymfc.editor import searchdlg
        searchdlg.SearchDlg(searchwnd=wnd).doModal()
        wnd.setFocus()

class EditBeginReplace(Command):
    COMMANDID = "edit.replace.begin"

    def run(self, wnd, *args, **kwargs):
        from pymfc.editor import searchdlg
        searchdlg.ReplaceDlg(searchwnd=wnd).doModal()
        wnd.setFocus()

class EditSearchAgain(Command):
    COMMANDID = "edit.search.again"

    def run(self, wnd, *args, **kwargs):
        wnd.getMode().searchNext(wnd)

class EditSearchBackwardAgain(Command):
    COMMANDID = "edit.search.again.backward"

    def run(self, wnd, *args, **kwargs):
        wnd.getMode().searchPrev(wnd)



