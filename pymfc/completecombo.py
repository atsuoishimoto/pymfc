# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import wnd


class _CompleteCombo(object):
    def _prepare(self, kwargs):
        super(_CompleteCombo, self)._prepare(kwargs)
        self.msglistener.CREATE = self.__onCreate
        self.msglistener.EDITCHANGE = self.__onEditChage
    
        self._docomplete = False

    def __onCreate(self, msg):
        self.getEdit().msgproc.KEYDOWN = self.__onEditKeyDown
        
    def __onEditKeyDown(self, msg):
        if msg.key in (wnd.KEY.BACKSPACE, wnd.KEY.DELETE):
            self._docomplete = False
        else:
            self._docomplete = True
        return msg.wnd.defWndProc(msg)
        
    def __onEditChage(self, msg):
        s = self.getText()
        if not self._docomplete:
            return
        s = self.getText()
        f,t = self.getEditSel()
        i = self.selectString(-1, s)
        if i == -1:
            self.setText(s)
            self.setEditSel(f,t)
        else:
            self.setEditSel(len(s), -1)

    
class CompleteCombo(_CompleteCombo, wnd.ComboBox):
    STYLE = wnd.ComboBox.STYLE(sort=1)

class CompleteDropDownCombo(CompleteCombo, wnd.DropDownCombo):
    STYLE = wnd.DropDownCombo.STYLE(sort=1)
