# -*- coding: ShiftJIS -*-
import re
from pymfc import wnd, gdi, syscolor


#todo: calc combobox height.
#    MSDN Q124315
#    
#    FONT = gdi.StockFont(default_gui=True)
#    SYSFONT = gdi.StockFont(system=True)
#    TEXTMETRICS = FONT.getTextMetrics()
#    SYS_TEXTMETRICS = SYSFONT.getTextMetrics()
#    TEXTHEIGHT = TEXTMETRICS.tmHeight+min(TEXTMETRICS.tmHeight, SYS_TEXTMETRICS.tmHeight)/2+pymfc.metric.CYEDGE*2

class _PanelCell(object):
    def __init__(self):
        self._children = []
        self._rc = []
        
    def setChildren(self, children):
        self._children = children

    def _iterChildren(self):
        for ctrl, (w, h) in self._children:
            yield w, h, ctrl

    def calcSize(self):
        height = 0
        width = 0
        for w, h, ctrl in self._iterChildren():
            height = max(height, h)
            width += w
        return width, height

    def setRect(self, rc):
        self._rc = rc
        l, t, r, b = self._rc
        rowHeight = b-t
        for w, h, ctrl in self._iterChildren():
            if ctrl:
                ctrlTop = t+(rowHeight-h)//2+1
                if isinstance(ctrl, (wnd.DropDownCombo, wnd.DropDownList)):
                    ctrl.setWindowPos(rect=(l, ctrlTop, l+w, ctrlTop+h+400))
                else:
                    ctrl.setWindowPos(rect=(l, ctrlTop, l+w, ctrlTop+h))
            l += w

class ChildPanel(object):
    MARGIN_TOP = 5
    MARGIN_LEFT = 5
    GAP_ROW = 3
    GAP_COL = 3

    def __init__(self, parent=None, font=None, bgcolor=None, pos=(0,0), 
        autocreatechildren=True, adjustparent=False, panellist=None):

        self._panellist = panellist
        if self._panellist:
            assert not adjustparent
            self._panellist._addPanel(self)
            
        self._parent = None
        if parent:
            self.setParent(parent)

        self._font = font
        if not self._font:
            self._font = gdi.StockFont(default_gui=True)

        self._bgcolor = bgcolor
        if bgcolor is not None:
            self._bgbrush = gdi.Brush(color=bgcolor)
        else:
            self._bgbrush = gdi.Brush(null=True)
            
        self.setPos(pos)
        self._autocreatechildren = autocreatechildren
        self._adjustparent = adjustparent

        self._ctrls = []
        self._panelRect = (0,0,0,0)
        
    def setParent(self, parent):
        assert not self._parent
        self._parent = parent
        if not self._panellist:
            self._msglistener = wnd.Listeners(parent.MSGDEF)
            self._msglistener.CREATE = self._onCreate
            self._msglistener.DESTROY = self._onDestroy

            parent.msglistener.attach(self._msglistener)

    def detach(self):
        if not self._panellist and self._parent:
            self._parent.msglistener.detach(self._msglistener)
            
        self._msglistener = None
        self._parent = None
        self._ctrls = self._cells = None
        self._adjustparent = None
        self._panellist = None
        
    def setPos(self, pos):
        self._pos = pos
    
    def updatePos(self, pos):
        self.setPos(pos)
        self._setCellRect(self._cells, self._widths, self._heights)
        
    def dlu(self, pos=(), x=None, y=None):
        # Convert dialog unit into device unit
        
                
        # Q145994
        dc = gdi.DesktopDC()
        org = dc.selectObject(self._font)
        try:
            tm = dc.getTextMetrics()
            yunit = tm.tmHeight/8.0
            cx, cy = dc.getTextExtent(
               u"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
            xunit = ((cx / 26.0 + 1) / 2)/4.0

            if pos:
                x, y = pos
                return int(x*xunit), int(y*yunit)
            elif x is not None:
                return int(x*xunit)
            elif y is not None:
                return int(y*yunit)
            else:
                raise ValueError()
            
        finally:
            dc.selectObject(org)
            dc.release()

    def setCtrls(self, ctrls):
        self._ctrls = ctrls

    def getPanelRect(self):
        return self._panelRect
        
    def _buildCells(self, ctrls):
        if ctrls:
            numCols = max([len(row) for row in ctrls])
        else:
            numCols = 0
        numRows = len(ctrls)

        cells = []
            
        for r in range(numRows):
            cells.append([_PanelCell() for n in range(numCols)])

        for nRow, row in enumerate(ctrls):
            for nCol, col in enumerate(row):
                cells[nRow][nCol].setChildren(col)
        return cells

    def _calcCellSize(self, cells):
        if not cells:
            return 0,0
        widths = [0]*len(cells[0])
        heights = [0]*len(cells)

        for nRow, row in enumerate(cells):
            for nCol, cell in enumerate(row):
                w, h = cell.calcSize()
                widths[nCol] = max(w, widths[nCol])
                heights[nRow] = max(h, heights[nRow])
        return widths, heights

    def _setCellRect(self, cells, widths, heights):
        if self._pos:
            left, top = self._pos
        else:
            left = top = 0
        left += self.MARGIN_LEFT
        top += self.MARGIN_TOP
        
        rowBottom = top
        colRight = left
        
        for nRow, row in enumerate(cells):
            rowBottom = top + heights[nRow]
            colLeft = left
            for nCol, cell in enumerate(row):
                cell = cells[nRow][nCol]
                colRight = colLeft + widths[nCol]
                cell.setRect((colLeft, top, colRight, rowBottom))
                colLeft = colRight + self.GAP_COL
            top = rowBottom + self.GAP_ROW

        self._panelRect = self._pos[0], self._pos[1], colRight, rowBottom

    def _buildStaticWnd(self, s):
        
        ret = wnd.Static(title=s, parent=self._parent)
#        brush=gdi.Brush(null=True)

        def ctlcolor(msg):
            dc = gdi.DC(hdc=msg.hdc)
            dc.setBkMode(transparent=True)
            return self._bgbrush.getHandle().handle

        ret.msgproc.CTLCOLORSTATIC = ctlcolor
        ret.create()
        ret.setFont(self._font)

        dc = gdi.DesktopDC()
        org = dc.selectObject(self._font)
        try:
            size = dc.getTextExtent(s)
        finally:
            dc.selectObject(org)

        return ret, size

    def _buildCtrls(self):
        ctrls = []
        for row in self._ctrls:
            ctrls.append([])
            for cell in row:
                ctrls[-1].append([])
                for item in cell:
                    if isinstance(item, unicode):
                        pair = self._buildStaticWnd(item)
                    elif isinstance(item, (list, tuple)):
                        ctrl, size = item
                        if isinstance(ctrl, wnd.WndBase):
                            if not ctrl.getHwnd():
                                if not self._autocreatechildren:
                                    continue
                                if not ctrl.getParentObj():
                                    ctrl.setParentObj(self._parent)
                                ctrl.create()
                            ctrl.setFont(self._font)
                            
                        size = self.dlu(size)
                        pair = (ctrl, size)
                    else:
                        pair = (None, self.dlu((4, 8)))

                    ctrls[-1][-1].append(pair)
        return ctrls

    def _onCreate(self, msg):
        self.build()

    def build(self):
        self._ctrls = self._buildCtrls()
        self._cells = self._buildCells(self._ctrls)
        self._widths, self._heights = self._calcCellSize(self._cells)
        self._setCellRect(self._cells, self._widths, self._heights)

        if self._adjustparent:
            l, t, r, b = self.getPanelRect()
            if not callable(self._adjustparent):
                rc = self._parent.calcWindowRect((0, 0, r, b))
                self._parent.setWindowPos(size=(rc[2]-rc[0], rc[3]-rc[1]))
            else:
                self._adjustparent(self, (r, b))

    def _onDestroy(self, msg):
        self.detach()


class ChildPanelList(object):
    def __init__(self, parent, pos=(0,0), adjustparent=False):
        self._pos = pos
        self._adjustparent = adjustparent
        self._panels = []

        self._msglistener = wnd.Listeners(parent.MSGDEF)
        self._msglistener.CREATE = self._onCreate
        self._msglistener.DESTROY = self._onDestroy
        
        self._parent = parent
        self._parent.msglistener.attach(self._msglistener)
        
    def _addPanel(self, panel):
        self._panels.append(panel)
    
    def _onCreate(self, msg):
        x, y = self._pos
        maxwidth = 0
        
        for panel in self._panels:
            panel.setPos((x, y))
            panel._onCreate(None)
            l, t, r, b = panel.getPanelRect()
            maxwidth = max(maxwidth, r)
            y = b
        if self._adjustparent:
            if not callable(self._adjustparent):
                rc = self._parent.calcWindowRect((0, 0, maxwidth, y))
                self._parent.setWindowPos(size=(rc[2]-rc[0], rc[3]-rc[1]))
            else:
                self._adjustparent(self, (maxwidth, y))

    def _onDestroy(self, msg):
        self.detach()
        
    def detach(self):
        for panel in self._panels:
            panel._onDestroy(None)
        self._parent.msglistener.detach(self._msglistener)
        self._msglistener = None
        self._panels = None
        self._parent = None
        

class DialogKeyHandler(object):
    def __init__(self, parent, initfocus=True, onok=None, oncancel=None):
        self._shortcuts = {}
        self._parent = parent
        self._onok = onok
        self._oncancel = oncancel
        self._focusset = not initfocus
        self._curfocus = None
        
        listener = wnd.Listeners(parent.MSGDEF)
        listener.PARENTNOTIFY = self.__onParentNotify
        listener.NCDESTROY = self.__onNCDestroy
        listener.ACTIVATE = self.__onActivate
        listener.SETFOCUS = self.__onSetFocus
        listener.LBUTTONDOWN = self.__onLBtnDown
        listener.COMMAND = self.__onCommand
        listener.KEYDOWN = self.__onControlKeydown

        self._parent.msglistener.attach(listener)

    RE_GETSHORTCUT = re.compile(ur"(?<!&)&([a-zA-Z0-9])")
    def __onParentNotify(self, msg):
        if msg.get("created", None):
            control = msg.control
            if not control:
                control = Wnd.subclassWindow(msg.get("created"))

            listener = wnd.Listeners(control.MSGDEF)
            listener.KEYDOWN = self.__onControlKeydown
            listener.SYSKEYDOWN = self.__onControlSysKeydown
            listener.SETFOCUS = self.__onControlSetFocus
            listener.LBUTTONDOWN = self.__onControlLBtnDown
            control.msglistener.attach(listener)
            
            msgproc = wnd.MsgHandlers(control.MSGDEF)
            msgproc.GETDLGCODE = self.__onControlGetDlgCode
            msgproc.CHAR = self.__onControlChar
            
            control.msgproc.attach(msgproc)

            classname = control.getClassName().upper()
            if classname == u'STATIC':
                label = control.getText()
                m = self.RE_GETSHORTCUT.search(label)
                if m:
                    shortcut = m.group(1)
                    self._shortcuts[shortcut.upper()] = control

            elif classname == u'COMBOBOX':
                f_edit = getattr(control, 'getEdit', None)
                if f_edit:
                    edit = f_edit()
                    if edit.getHwnd():
                        edit.msglistener.attach(listener)
                        edit.msgproc.attach(msgproc)

            if not self._focusset:
                if control.isWindowEnabled() and control.getWindowStyle().tabstop:
                    control.setFocus()
                    self._focusset = True
            
    def __onActivate(self, msg):
        if self._curfocus and self._curfocus.getHwnd():
            self._curfocus.setFocus()

    def __onNCDestroy(self, msg):
        self._parent = None
        self._onok = None
        self._oncancel = None
        
    def __onSetFocus(self, msg):
        if self._curfocus and self._curfocus.getHwnd():
            self._curfocus.setFocus()

    def __onLBtnDown(self, msg):
        if self._curfocus and self._curfocus.getHwnd():
            self._curfocus.setFocus()
        else:
            self._parent.setFocus()
            
    def __onCommand(self, msg):
        if msg.notifycode == 0 or msg.notifycode == 1:
            if msg.id == wnd.IDOK:
                self.__onCmdOk()
            elif msg.id == wnd.IDCANCEL:
                self.__onCmdCancel()

    def __onControlKeydown(self, msg):
        if msg.key == 9: # tab key pressed
            prev = wnd.getKeyState(wnd.KEY.SHIFT).down
            next = self._parent.getNextDlgTabItem(msg.wnd, prev)
            if next and next.getHwnd():
                next.setFocus()
        elif msg.key == 0x0d: # enter
            if msg.wnd.getClassName().upper() == u'EDIT':
                if msg.wnd.getWindowStyle().wantreturn:
                    return
            self.__onCmdOk()
        elif msg.key == 0x1b and self._oncancel: # escape
            self.__onCmdCancel()

    def __onControlSysKeydown(self, msg):
        key = chr(msg.key).upper()
        ctl = self._shortcuts.get(key, None)
        if ctl:
            next = self._parent.getNextDlgTabItem(ctl)
            next.setFocus()

    def __onControlSetFocus(self, msg):
        self._curfocus = msg.wnd

    def __onControlLBtnDown(self, msg):
        focused = self._parent.getFocus()
        # commented out following codes.
        # Dropdown combobox doesn't work properly.

#        if focused is not msg.wnd:
#            # wnd wasn't focused by mouse click.
#            # select current control again
#
#            if self._curfocus and self._curfocus.getHwnd():
#                self._curfocus.setFocus()

    def __onControlGetDlgCode(self, msg):
        return 4  # wantallkeys

    def __onControlChar(self, msg):
        if msg.char == u'\r':
            wantreturn = getattr(msg.wnd.getWindowStyle(), 'wantreturn', None)
            if wantreturn:
                return msg.wnd.defWndProc(msg)
            return 0

        if msg.char not in  u'\t':
            return msg.wnd.defWndProc(msg)

        return 0
        
    def __onCmdOk(self):
        if self._onok:
            self._onok()
    
    def __onCmdCancel(self):
        if self._oncancel:
            self._oncancel()

class TabPage(wnd.Wnd):
    WNDCLASS_BACKGROUNDCOLOR = 0xc0c0c0
    def _prepare(self, kwargs):
        super(TabPage, self)._prepare(kwargs)
        self._panel = ChildPanel(parent=self)
        
    def wndReleased(self):
        super(TabPage, self).wndReleased()
        self._panel = None
            
    def setCtrls(self, ctrls):
        self._panel.setCtrls(ctrls)
    
    def getPanel(self):
        return self._panel
        

class Tab(wnd.TabCtrl):
    def _prepare(self, kwargs):
        super(Tab, self)._prepare(kwargs)
        self._adjustFrame = kwargs['adjustframe']
        
        self._pos=(0,0)
        self._size=(0,0)
        self.msglistener.CREATE = self._onCreate
        self.msglistener.SELCHANGE = self._onSelChange
        self.msglistener.SIZE = self._onSize
        
        self._pages = []
    
    def wndReleased(self):
        super(Tab, self).wndReleased()
        self._pages = None
        self._adjustFrame = None
        
    def setPages(self, pages):
        """ pages: list of tuple(wnd, title, panel)"""
        self._pages = pages
    
    def setTabSize(self):
        tabwidth, tabheight = 0, 0
        for page, title, panel  in self._pages:
            l, t, r, b = panel.getPanelRect()
            tabwidth = max(tabwidth, w)
            tabheight = max(tabheight, h)

        reqrc = self.adjustRect(True, (0, 0, tabwidth, tabheight))

        reqsize = reqrc[2]-reqrc[0], reqrc[3]-reqrc[1]
        self._adjustFrame(reqsize)
        
        
    def _onCreate(self, msg):
        for n, (page, title, panel) in enumerate(self._pages):
            if not page.getHwnd():
                page.create()
            self.insertItem(n, title)

        self.setCurSel(0)
        self._onSelChange(None)
        self.setTabSize()
        
    def _resizePages(self):
        curpage = self.getCurSel()
        
        for n, (page, title, panel) in enumerate(self._pages):
            if page.getHwnd():
                if n == curpage:
                    rc = self.adjustRect(False, self.getClientRect())
                    page.setWindowPos(show=True, rect=rc)
                else:
                    page.setWindowPos(show=False)
        pass
    def _onSelChange(self, msg):
        self._resizePages()
        
    def _onSize(self, msg):
        self._resizePages()


if __name__ == '__main__':
    f = wnd.FrameWnd()
    f.WNDCLASS_BACKGROUNDCOLOR = 0xffc0c0
    panel = ChildPanel(f, font=gdi.Font(face=u"ＭＳ ゴシック", point=20, shiftjis_charset=True))
    ctrls = [
        [(u"abcdefg",), ((wnd.Edit(title=u"ddddd"), (100,11)),)],
        [(u"abcdefg0123456789あいうえお",), (), ((wnd.Edit(title=u"ddddd"), (100,11)),)],
        [(u"abcdefg0123456789あいうえお",), ((wnd.Edit(title=u"ddddd"), (100,11)),)],
        [(u"abcdefg0123456789あいうえお",), ((wnd.Edit(title=u"ddddd"), (100,11)),)],
        [(u"abcdefg0123456789あいうえお",), ((wnd.Edit(title=u"ddddd"), (100,11)),)],
#        [(),(),("あああああああああああああああ",)]
    ]
#    ctrls = [
#        [("abcdefg ", (wnd.Edit(title="ddddd"), (100,11)), None, "あいうえお")],
#        [
#            ("abcdefg",), 
#            ((wnd.Button(title="lkmlkm"), (100,11)),)
#        ],
#        [
#            (),
#            ("abcdefg",), 
#        ],
#    ]
    panel.setCtrls(ctrls)

    f.create()
    
    from pymfc import app
    app.run()


