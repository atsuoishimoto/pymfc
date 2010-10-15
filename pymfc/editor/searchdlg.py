# -*- coding: ShiftJIS -*-
from __future__ import with_statement

import sys
import pymfc
from pymfc import wnd, layout


class SearchCond:
    def __init__(self):
        self.string = u''
        self.ignorecase = True
        self.matchword = False
        self.replaceto = u''
        self.lastmatch = None
        self.forward = True
        
    def update(self, string, ignorecase, matchword, replaceto):
        self.string = string
        self.ignorecase = ignorecase
        self.matchword = matchword
        self.replaceto = replaceto


LASTSEARCH=SearchCond()
        
class SearchDlg(wnd.Dialog):
    TITLE = u"文字列を検索"
    
    def _prepare(self, kwargs):
        super(SearchDlg, self)._prepare(kwargs)
        
        self._searchwnd = kwargs['searchwnd']
        
        string = u''
        if self._searchwnd.isSelected():
            mode = self._searchwnd.getMode()
            string = mode.getSelection(self._searchwnd)
            if string:
                string = string.splitlines()[0]

        if not string:
            string = LASTSEARCH.string

        ignorecase = LASTSEARCH.ignorecase
        matchword = LASTSEARCH.matchword

        self._layout = layout.Table(parent=self, pos=(15, 15),  adjustparent=True, 
            margin_right=15, margin_bottom=15)

        row = self._layout.addRow()
        cell = row.addCell()
        cell.add(u"検索文字列(&S): ")

        cell = row.addCell(fillhorz=True)
        cell.add(wnd.Edit, width=30, name="edit", title=string)
        cell.add(None)

        cell = row.addCell()
        cell.add(wnd.OkButton, title=u"次を検索(&F)", width=15, name="ok")

        row = self._layout.addRow()
        cell = row.addCell(colspan=2)
        cell = row.addCell()
        cellitem = cell.add(wnd.Button, title=u"前を検索(&P)", width=15, name="prev")
        cellitem.ctrl.msglistener.CLICKED = self.searchPrev
        
        row = self._layout.addRow()
        cell = row.addCell(colspan=2)
        cell.add(wnd.AutoCheckBox, title=u"大文字・小文字を区別しない(&I)", 
            checked=ignorecase, name="ignorecase")

        cell = row.addCell()
        cell.add(wnd.CancelButton, title=u"閉じる(&C)", width=15, name="cancel")

        row = self._layout.addRow()
        cell = row.addCell(colspan=2)
        cell.add(wnd.AutoCheckBox, title=u"単語単位で検索(&W)", checked=matchword, name="matchword")
        
        self.msglistener.CREATE = self.__onCreate
        LASTSEARCH.lastmatch = None
        LASTSEARCH.forward = True

    def wndReleased(self):
        super(SearchDlg, self).wndReleased()
        self._layout = None
        
    def __onCreate(self, msg):
        #Tab Order
        self._layout.ctrls.ignorecase.setWindowPos(after=self._layout.ctrls.edit)
        self._layout.ctrls.matchword.setWindowPos(after=self._layout.ctrls.ignorecase)
        self._layout.ctrls.ok.setWindowPos(after=self._layout.ctrls.matchword)
        self._layout.ctrls.prev.setWindowPos(after=self._layout.ctrls.ok)
        self._layout.ctrls.cancel.setWindowPos(after=self._layout.ctrls.prev)

    def onOk(self, msg):
        self.searchNext()

    def _readSearch(self):
        s = self._layout.ctrls.edit.getText()
        ignorecase = self._layout.ctrls.ignorecase.isChecked()
        matchword = self._layout.ctrls.matchword.isChecked()
        return LASTSEARCH.update(string=s, ignorecase=ignorecase, matchword=matchword, replaceto=u'')

    def searchNext(self, msg=None):
        self._readSearch()
        if not LASTSEARCH.string:
            return
        pos = None
        if LASTSEARCH.lastmatch:
            pos = LASTSEARCH.lastmatch[0]+1
            
        mode = self._searchwnd.getMode()
        mode.searchNext(self._searchwnd, pos)
        
    def searchPrev(self, msg=None):
        self._readSearch()
        if not LASTSEARCH.string:
            return

        pos = None
        if LASTSEARCH.lastmatch:
            pos = LASTSEARCH.lastmatch[1]-1

        mode = self._searchwnd.getMode()
        mode.searchPrev(self._searchwnd, pos)
        

class ReplaceDlg(wnd.Dialog):
    TITLE = u"文字列を置換"
    
    def _prepare(self, kwargs):
        super(ReplaceDlg, self)._prepare(kwargs)
        
        self._searchwnd = kwargs['searchwnd']
        
        string = u''
        if self._searchwnd.isSelected():
            mode = self._searchwnd.getMode()
            string = mode.getSelection(self._searchwnd)
            if string:
                string = string.splitlines()[0]

        if not string:
            string = LASTSEARCH.string

        ignorecase = LASTSEARCH.ignorecase
        matchword = LASTSEARCH.matchword
        replaceto = LASTSEARCH.replaceto
        
        self._layout = layout.Table(parent=self, pos=(15, 15),  adjustparent=True, 
            margin_right=15, margin_bottom=15)

        row = self._layout.addRow()
        cell = row.addCell()
        cell.add(u"検索文字列(&S): ")

        cell = row.addCell(fillhorz=True)
        cell.add(wnd.Edit, width=30, name="edit", title=string)
        cell.add(None)

        cell = row.addCell()
        cellitem = cell.add(wnd.Button, title=u"次を検索(&F)", width=15, name="next")
        cellitem.ctrl.msglistener.CLICKED = self.searchNext

        row = self._layout.addRow()
        cell = row.addCell()
        cell.add(u"置換文字列(&R): ")

        cell = row.addCell(fillhorz=True)
        cell.add(wnd.Edit, width=30, name="replto", title=replaceto)
        cell.add(None)

        cell = row.addCell()
        cellitem = cell.add(wnd.Button, title=u"前を検索(&P)", width=15, name="prev")
        cellitem.ctrl.msglistener.CLICKED = self.searchPrev
        
        row = self._layout.addRow()
        cell = row.addCell(colspan=2)
        cell = row.addCell()
        cell.add(wnd.OkButton, title=u"置換(&E)", width=15, name="ok")

        row = self._layout.addRow()
        cell = row.addCell(colspan=2)
        cell.add(wnd.AutoCheckBox, title=u"大文字・小文字を区別しない(&I)", 
            checked=ignorecase, name="ignorecase")

        cell = row.addCell()
        cellitem = cell.add(wnd.Button, title=u"全て置換(&A)", width=15, name="replall")
        cellitem.ctrl.msglistener.CLICKED = self.replaceAll

        row = self._layout.addRow()
        cell = row.addCell(colspan=2)
        cell.add(wnd.AutoCheckBox, title=u"単語単位で検索(&W)", checked=matchword, name="matchword")

        cell = row.addCell()
        cell.add(wnd.CancelButton, title=u"閉じる(&C)", width=15, name="cancel")

        self.msglistener.CREATE = self.__onCreate
        LASTSEARCH.lastmatch = None
        LASTSEARCH.forward = True
        
    def wndReleased(self):
        super(ReplaceDlg, self).wndReleased()
        self._layout = None
        
    def __onCreate(self, msg):
        #Tab Order
        self._layout.ctrls.replto.setWindowPos(after=self._layout.ctrls.edit)
        self._layout.ctrls.ignorecase.setWindowPos(after=self._layout.ctrls.replto)
        self._layout.ctrls.matchword.setWindowPos(after=self._layout.ctrls.ignorecase)
        self._layout.ctrls.next.setWindowPos(after=self._layout.ctrls.matchword)
        self._layout.ctrls.prev.setWindowPos(after=self._layout.ctrls.next)
        self._layout.ctrls.ok.setWindowPos(after=self._layout.ctrls.prev)
        self._layout.ctrls.replall.setWindowPos(after=self._layout.ctrls.ok)
        self._layout.ctrls.cancel.setWindowPos(after=self._layout.ctrls.replall)

    def onOk(self, msg):
        self.replace()

    def _readSearch(self):
        s = self._layout.ctrls.edit.getText()
        ignorecase = self._layout.ctrls.ignorecase.isChecked()
        sear = self._layout.ctrls.matchword.isChecked()
        matchword = self._layout.ctrls.matchword.isChecked()
        replaceto = self._layout.ctrls.replto.getText()
        return LASTSEARCH.update(string=s, ignorecase=ignorecase, matchword=matchword, replaceto=replaceto)

    def searchNext(self, msg=None):
        self._readSearch()
        if not LASTSEARCH.string:
            return

        pos = None
        if LASTSEARCH.lastmatch:
            pos = LASTSEARCH.lastmatch[0]+1

        mode = self._searchwnd.getMode()
        mode.searchNext(self._searchwnd, pos=pos)
        LASTSEARCH.forward = True
        
    def searchPrev(self, msg=None):
        self._readSearch()
        if not LASTSEARCH.string:
            return
            
        pos = None
        if LASTSEARCH.lastmatch:
            pos = LASTSEARCH.lastmatch[1]-1

        mode = self._searchwnd.getMode()
        mode.searchPrev(self._searchwnd, pos=pos)
        LASTSEARCH.forward = False
        
    def replace(self, msg=None):
        if not LASTSEARCH.lastmatch:
            if LASTSEARCH.forward:
                self.searchNext()
            else:
                self.searchPrev()
        else:
            self._readSearch()
            f, t = LASTSEARCH.lastmatch
            mode = self._searchwnd.getMode()
            mode.replaceString(self._searchwnd, f, t, LASTSEARCH.replaceto)
            if LASTSEARCH.forward:
                self._searchwnd.caret.locate(f+len(LASTSEARCH.replaceto), saveCol=True)
                if not mode.searchNext(self._searchwnd, f+len(LASTSEARCH.replaceto)):
                    LASTSEARCH.lastmatch = None
            else:
                self._searchwnd.caret.locate(f, saveCol=True)
                if not mode.searchPrev(self._searchwnd, f):
                    LASTSEARCH.lastmatch = None

    def replaceAll(self, msg=None):
        self._readSearch()
        if not LASTSEARCH.string:
            return
        mode = self._searchwnd.getMode()

        pos = 0
        mode.buf.undo.beginGroup()
        try:
            while True:
                found = mode.searchNext(self._searchwnd, pos)
                if not found:
                    break
                f, t = found
                mode.replaceString(self._searchwnd, f, t, LASTSEARCH.replaceto)

                pos = f + len(LASTSEARCH.replaceto)
        finally:
            mode.buf.undo.endGroup()
            
        LASTSEARCH.lastmatch = None

if __name__ == '__main__':
    ReplaceDlg(searchwnd=None).doModal()


