# -*- coding: ShiftJIS -*-

import time
import pymfc
from pymfc import wnd, gdi, util, app

class _CaptureWnd(wnd.Wnd):
    def _prepare(self, kwargs):
        super(_CaptureWnd, self)._prepare(kwargs)
        self._obj = kwargs['iconobj']

        self.msglistener.LBUTTONUP = self._onLBtnUp
        self.msglistener.MOUSEMOVE = self._onMouseMove
        self.msglistener.CANCELMODE = self._onCancelMode

    def _onLBtnUp(self, msg):
        self._obj.onLBtnUp(self._parent, self._parent.getCursorPos())

    def _onMouseMove(self, msg):
        self._obj.onMouseMove(self._parent, self._parent.getCursorPos())

    def _onCancelMode(self, msg):
        self._obj.onCancelMode(self._parent)

    def wndReleased(self):
        super(_CaptureWnd, self).wndReleased()
        self._obj = None
        
class IconButton(object):
    ICONGAP= 2

    DROPDOWNGAP=2
    DROPDOWN_WIDTH = 11
    
    FONT = gdi.StockFont(default_gui=True)
    EDGECOLOR_LIGHT = 0xffffff
    EDGECOLOR_SHADE = 0x808080
    
    def __init__(self, icon=None, iconsize=None, title=u'', tooltipmsg=u'',
            bgcolor=None, textcolor=0x000000,
            rect=(0,0,0,0), margin=3, thickborder=False,
            pushed=False, dropdown=False, disabled=False, cycleicons=(),
            onclick=None, onrclick=None, ondropdown=None, font=None, horz=True,
            ondrawbackground=None,
            **kwargs):

        self._fclicked = onclick
        self._frclicked = onrclick
        self._fdropdown = ondropdown
        self._fdrawbackground = ondrawbackground
        if font is not None:
            self.FONT = font
            
        self._iconSize = iconsize
        if not self._iconSize:
            if icon:
                _i = icon
            elif cycleicons:
                _i = cycleicons[0]
            else:
                _i = None
            if _i:
                self._iconSize = _i.getBitmap().getSize()
                
        self._margin = margin
        self._text = title
        self._tooltipmsg = tooltipmsg
        self._bgColor = bgcolor
        self._fgColor = textcolor
        self._iconBgColor = bgcolor
        self._cycleicons = cycleicons
        
        self._iconlist = []
        if icon:
            self._iconlist.append(icon)
        if self._cycleicons:
            self._iconlist.extend(self._cycleicons)
        self._iconIdx = 0
        
        self._raised = False
        self._thickBorder = thickborder
        self.setRect(rect)
        self._pushed = pushed
        self._dropDown = dropdown
        self._disabled = disabled
        self._horz = horz
        
        self._captured = False
        self._pressing = False
        self._dropDownPressing = False
        self._dropDownRaised = False
        
        self._capturewnd = None
        
        self._prepare(kwargs)
        
    def _prepare(self, kwargs):
        pass
        
    def destroy(self):
        if self._captured:
            self._raised = False
            self._pressing = False
            self._captured = False
            self._capturewnd.releaseCapture()
            self._capturewnd.destroy()
            self._capturewnd = None
            
        self._fclicked = None
        self._frclicked = None
        self._fdropdown = None
        self._fdrawbackground = None
        self._iconlist = None
    
    def setOnClick(self, onclick):
        self._fclicked = onclick

    def setOnRClick(self, onrclick):
        self._frclicked = onrclick

    def setOnDropDown(self, ondropdown):
        self._fdropdown = ondropdown

    def setOnDrawBackground(self, ondrawbackground):
        self._fdrawbackground = ondrawbackground

    def setText(self, text):
        self._text = text
        
    def getText(self):
        return self._text
        
    def getToolTipMsg(self):
        return self._tooltipmsg
        
    def setRect(self, rect):
        self._rc = rect
        
    def setWindowPos(self, rect):
        self.setRect(rect)
        
    def getRect(self):
        return self._rc

    def getIcon(self):
        if self._iconlist:
            return self._iconlist[self._iconIdx]
        else:
            return None

    def setIcon(self, icon):
        assert len(self._iconlist) <= 1
        self._iconlist = []
        if icon:
            self._iconlist.append(icon)
            
    def setIconSize(self, size):
        self._iconSize = size
    
    def getIconSize(self):
        if not self._iconlist:
            return (0,0)

        if isinstance(self._iconSize, tuple):
            return self._iconSize
        else:
            return self._iconSize(self)
        
    def cycleIcon(self):
        self._iconIdx += 1
        if self._iconIdx >= len(self._iconlist):
            self._iconIdx = 0
        return self._iconIdx

    def getCycleIndex(self):
        return self._iconIdx
        
    def setBgColor(self, bgcolor):
        self._bgColor = bgcolor
        
    def setIconBgColor(self, bgcolor):
        self._iconBgColor = bgcolor
        
    def setTextColor(self, textcolor):
        self._fgColor = textcolor

    def pushed(self, f):
        self._pushed = f

    def isPushed(self):
        return self._pushed

    def dropDown(self, f):
        self._dropDownPressing = f

    def isDropDown(self):
        return self._dropDownPressing

    def setDisabled(self, disabled):
        ret = self._disabled != disabled
        self._disabled = disabled
        return ret
        
    def _calcSize(self, dc):
        icon = self.getIcon()
        if not icon and not self._text:
            return (0,0)
        
        iconsize = self.getIconSize()
        if icon and not self._text:
            w, h = iconsize[0]+self._margin*2, iconsize[1]+self._margin*2
        else:
            textsize = dc.getTextExtent(self._text)
            if not icon and self._text:
                w, h =  textsize[0]+self._margin*2, textsize[1]+self._margin*2
            else:
                if self._horz:
                    w, h = (self._margin*2+iconsize[0]+self.ICONGAP+textsize[0], 
                        max(iconsize[1], textsize[1])+self._margin*2)
                else:
                    w, h = (max(iconsize[0], textsize[0]) + self._margin*2,
                        iconsize[1] + textsize[1]+self._margin*2)
                    
        if self._dropDown:
            w += self.DROPDOWN_WIDTH+self.DROPDOWNGAP
        return w, h

    def calcSize(self, dc):
        orgFont = dc.selectObject(self.FONT)
        try:
            return self._calcSize(dc)
        finally:
            dc.selectObject(orgFont)
        
    def draw(self, dc, wndrc):
        dc.setBkMode(transparent=True)
        orgFont = dc.selectObject(self.FONT)
        try:
            if self._fdrawbackground:
                self._fdrawbackground(dc, self._rc)
            elif self._bgColor is not None:
                dc.fillSolidRect(self._rc, self._bgColor)

            if self._fclicked:
                if self._pressing or self._pushed:
                    self.__drawEdge(dc, self._rc, raised=False)
                elif self._raised:
                    self.__drawEdge(dc, self._rc, raised=True)
            
            height = self._rc[3]-self._rc[1]
            width = self._rc[2]-self._rc[0]
            left = self._rc[0]+self._margin
            icon = self.getIcon()
            iconsize = self.getIconSize()
            
            if self._text:
                textsize = dc.getTextExtent(self._text)
            else:
                textsize = (0,0)

            if icon:
                if self._horz:
                    top = self._rc[1] + (height-iconsize[1])/2
                else:
                    if self._text:
                        top = self._rc[1] + (height-iconsize[1]-textsize[1])/2
                    else:
                        top = self._rc[1] + (height-iconsize[1])/2
                    left = self._rc[0] + (width-iconsize[0])/2

                if self._iconBgColor != self._bgColor:
                    if self._iconBgColor is not None:
                        dc.fillSolidRect(
                            (left, top, left+iconsize[0], top+iconsize[1]), 
                            self._iconBgColor)

                if isinstance(icon, gdi.Icon):
                    if not self._disabled:
                        dc.drawIcon((left, top), icon, (iconsize[0], iconsize[1]), normal=True)
                    else:
                        dc.drawState((left, top), (iconsize[0], iconsize[1]), icon, disabled=True)
                else:
                    iconrc = (left, top, left+iconsize[0], top+iconsize[1])
                    icon(self, dc, iconrc, wndrc, self._disabled)
                    
                left = left+iconsize[0]+self.ICONGAP
            
            if self._text:
                dc.setTextColor(self._fgColor)
                if self._horz:
                    top = self._rc[1] + (height-textsize[1])/2
                    center=False
                else:
                    top = self._rc[3] - textsize[1] - self._margin
                    left = self._rc[0] + self._margin
                    center=True
                    
                dc.drawText(self._text, (left, top, self._rc[2] - self._margin, self._rc[3]), 
                    end_ellipsis=True, noprefix=True, center=center)
                left = left + textsize[0]
                
            if self._dropDown:
                left = self._rc[2]-self.DROPDOWN_WIDTH-self._margin
                pen = gdi.Pen(color=0, solid=True)
                orgpen = dc.selectObject(pen)
                try:
                    rc = (left, self._rc[1]+self.DROPDOWNGAP, 
                            self._rc[2]-self._margin, self._rc[3]-self.DROPDOWNGAP)
                    x = rc[0] + (rc[2] - rc[0]) / 2
                    y = rc[1] + (rc[3] - rc[1]) / 2 - 1

                    dc.moveTo((x - 2, y))
                    dc.lineTo((x + 2, y))
                    y += 1
                    dc.moveTo((x - 1, y))
                    dc.lineTo((x + 1, y))
                    y += 1
                    dc.moveTo((x, y))
                    dc.lineTo((x, y))
                    
                    if self._dropDownPressing:
                        self.__drawEdge(dc, rc, raised=False)
                    elif self._dropDownRaised:
                        self.__drawEdge(dc, rc, raised=True)
                        
                finally:
                    dc.selectObject(orgpen)

        finally:
            dc.selectObject(orgFont)

    def __drawEdge(self, dc, rc, raised):
        penlight = gdi.Pen(color=self.EDGECOLOR_LIGHT, solid=True)
        penshade = gdi.Pen(color=self.EDGECOLOR_SHADE, solid=True)
        try:
            if raised:
                orgpen = dc.selectObject(penlight)
            else:
                orgpen = dc.selectObject(penshade)

            x1, y1, x2, y2 = rc
            dc.moveTo((x1, y2 - 1))
            dc.lineTo((x1, y1))
            dc.lineTo((x2 - 1, y1))

            if raised:
                dc.selectObject(penshade)
            else:
                dc.selectObject(penlight)

            dc.lineTo((x2 - 1, y2 - 1))
            dc.lineTo((x1, y2 - 1))

        finally:
            dc.selectObject(orgpen)

    def ptInRect(self, pos):
        return util.ptInRect(pos, self._rc)
            
    def ptInDropDownRect(self, pos):
        rc = (self._rc[2]-self.DROPDOWN_WIDTH-self.DROPDOWNGAP,
                self._rc[1], self._rc[2], self._rc[3])
        return util.ptInRect(pos, rc)
        
    def _onClick(self, wnd):
        if self._fclicked and not self._disabled:
            self._fclicked(wnd, self)

    def onSetCursor(self, wnd, pos):
        if self.ptInRect(pos):
            cursor = gdi.Cursor(hand=True)
            cursor.setCursor()
            return True

    def onLBtnDown(self, wnd, pos):
        if self._rc and self.ptInRect(pos):
            if self._dropDown:
                if self.ptInDropDownRect(pos):
                    if self._fdropdown and not self._disabled:
                        self._fdropdown(wnd, self)
                    return True
            
            wnd.invalidateRect(self._rc, erase=False)

            assert self._capturewnd is None
            self._capturewnd = _CaptureWnd(parent=wnd, iconobj=self)
            self._capturewnd.create()
            self._capturewnd.setCapture()

            self._raised = False
            self._captured = True
            self._pressing = True
            return True
            
    def onLBtnUp(self, wnd, pos):
        if self._captured:
            wnd.invalidateRect(self._rc, erase=False)
            self.onCancelMode(wnd)
            in_rect = util.ptInRect(pos, self._rc)
            if in_rect:
                self._onClick(wnd)

    def onRBtnUp(self, wnd, pos):
        if self._rc and self.ptInRect(pos):
            if self._frclicked:
                self._frclicked(wnd, self)

    def updateBorder(self, wnd, pos):
        in_rect = self.ptInRect(pos)
        updated = False
            
        if self._captured:
            if in_rect and not self._pressing:
                self._pressing = True
                updated = True
            elif not in_rect and self._pressing:
                self._pressing = False
                updated = True
        else:
            if self.ptInDropDownRect(pos):
                if not self._dropDownRaised:
                    self._dropDownRaised = True
                    updated = True
            else:
                if self._dropDownRaised:
                    self._dropDownRaised = False
                    updated = True

            if self._fclicked and in_rect and not self._raised:
                self._raised = True
                updated = True

            elif not in_rect and self._raised:
                self._raised = False
                updated = True

        if updated:
            wnd.trackMouseEvent(leave=True)
            wnd.invalidateRect(self._rc, erase=False)
        return updated

    def onMouseMove(self, wnd, pos):
        return self.updateBorder(wnd, pos)

    def onMouseLeave(self, wnd):
        if self._dropDownRaised or self._raised:
            self._dropDownRaised = self._raised = False
            wnd.invalidateRect(None, erase=False)
            
    def onCancelMode(self, wnd):
        if self._captured:
            self._raised = False
            self._pressing = False
            self._captured = False
            wnd.invalidateRect(self._rc, erase=False)
            self._capturewnd.releaseCapture()
            self._capturewnd.destroy()
            self._capturewnd = None

class ControlButton(object):
    SYSFONT = gdi.StockFont(system=True)
    SYS_TEXTMETRICS = SYSFONT.getTextMetrics()

    def __init__(self, ctrl, size=None, tooltipmsg=u''):
        self.ctrl = ctrl
        self.size = size
        self._tooltipmsg = tooltipmsg

    def destroy(self):
        self.ctrl.destroy()

    def getSize(self):
        if isinstance(self.ctrl, (wnd.DropDownCombo, wnd.DropDownList)):
            if self.ctrl.getHwnd():
                font = self.ctrl.getFont()
                if not font:
                    font = self.SYSFONT
                tm = font.getTextMetrics()
                height = tm.tmHeight+min(tm.tmHeight, self.SYS_TEXTMETRICS.tmHeight)/2+pymfc.metric.CYEDGE*2
                l, t, r, b = self.ctrl.getWindowRect()
                return r-l, height
            else:
                return (10,10)

        size = self.ctrl._size
        if None in size:
            if self.ctrl.getHwnd():
                l, t, r, b = self.ctrl.getWindowRect()
                size = (r-l, b-t)
            else:
                size = (10,10)
        return size
    
    def getToolTipMsg(self):
        return self._tooltipmsg
        

    def redraw(self):
        if self.ctrl and self.ctrl.getHwnd():
            self.ctrl.invalidateRect(None, erase=False)

class IconButtons(object):
    MARGIN_LEFT = 2
    MARGIN_RIGHT = 2
    MARGIN_TOP = 2
    MARGIN_BOTTOM = 2
    MARGIN_BUTTON = 2

    BACKGROUND_COLOR = 0xc0c0c0

    def __init__(self, buttons=()):
        self._buttons = []
        if buttons:
            self.setButtons(buttons)

        self._tooltip = None
        self._rect = (0,0,0,0)
        self._handlers = None

    def bindWnd(self, parentWnd):
        
        assert not self._handlers

        self._parentWnd = parentWnd
        
        msgproc = wnd.MsgHandlers(parentWnd.MSGDEF)
        msgproc.SETCURSOR = self.onSetCursor
        msgproc.LBUTTONDOWN = self.onLBtnDown
        msgproc.RBUTTONUP = self.onRBtnUp
        msgproc.LBUTTONDBLCLK = self.onLBtnDblClk

        msglistener = wnd.Listeners(parentWnd.MSGDEF)
        msglistener.CREATE = self.onCreate
        msglistener.MOUSEMOVE = self.onMouseMove
        msglistener.MOUSELEAVE = self.onMouseLeave
        msglistener.NCDESTROY = self.onNCDestroy
        self._handlers = (msgproc, msglistener)
        
        parentWnd.msgproc.attach(msgproc)
        parentWnd.msglistener.attach(msglistener)
        
        
    def unbindWnd(self):
        if self._handlers:
            msgproc, msglistener = self._handlers
            self._parentWnd.msgproc.detach(msgproc)
            self._parentWnd.msglistener.detach(msglistener)
            self._handlers = None

    def setMargin(self, left=None, top=None, right=None, bottom=None, button=None):
        if left is not None:
            self.MARGIN_LEFT = left
        
        if top is not None:
            self.MARGIN_TOP = top
        
        if right is not None:
            self.MARGIN_RIGHT = right
        
        if bottom is not None:
            self.MARGIN_BOTTOM = bottom
        
        if button is not None:
            self.MARGIN_BUTTON = button

    def getRect(self):
        return self._rect
        
    def getButtons(self):
        return self._buttons

    def _createWndButtons(self, items):
        for btn in self._buttons:
            if btn and not isinstance(btn, IconButton) and not btn.ctrl.getHwnd():
                btn.ctrl.create()
        
    def setButtons(self, buttons):
        for btn in self._buttons:
            btn.destroy()

        self._buttons = []
        for btn in buttons:
            if btn is None:
                self._buttons.append(btn)
            elif isinstance(btn, (IconButton, ControlButton)):
                self._buttons.append(btn)
            else:
                btn = ControlButton(btn)
                self._buttons.append(btn)
                
        if self._parentWnd.getHwnd():
            self._createWndButtons(self._buttons)
            self.setRect(None, self._rect)

    def setToolTip(self, wnd, tooltip):
        self._tooltip = tooltip
        if self._tooltip.getHwnd():
            self.resetToolTip(wnd)    
            for n, btn in enumerate(self._buttons):
                if isinstance(btn, IconButton):
                    msg = btn.getToolTipMsg()
                    if msg:
                        btnrect = btn.getRect()
                        rect = util.rectIntersection(btnrect, self.getRect())
                        if rect:
                            self._tooltip.addTool(n+1, wnd, rect, msg, subclass=True)
                elif btn:
                    msg = getattr(btn.ctrl, "iconbtn_tooltipmsg", None)
                    if not msg:
                        msg = btn.getToolTipMsg()
                    if msg:
                        btnrect = btn.ctrl.getClientRect()
                        rect = util.rectIntersection(btnrect, self.getRect())
                        if rect:
                            self._tooltip.addTool(n+1, btn.ctrl, rect, msg, subclass=True)
                    
    def resetToolTip(self, wnd):
        if not self._tooltip:
            return

        if not self._tooltip.getHwnd():
            return
            
        for n in range(self._tooltip.getToolCount()):
            self._tooltip.delTool(n+1, wnd)


    def paint(self, dc):
        if self.BACKGROUND_COLOR is not None:
            dc.fillSolidRect(self._rect, self.BACKGROUND_COLOR)
        for btn in self._buttons:
            if isinstance(btn, IconButton):
                btn.draw(dc, self._rect)
            elif btn:
                btn.redraw()

    def onCreate(self, msg):
        self._createWndButtons(self._buttons)
        
    def onSetCursor(self, msg):
        if not msg.htclient:
            return msg.wnd.defWndProc(msg)

        pos = msg.wnd.getCursorPos()
        if not util.ptInRect(pos, self._rect):
            msg.cont = True
            msg.handled = False
            return

        for btn in self._buttons:
            if isinstance(btn, IconButton):
                if btn.onSetCursor(msg.wnd, pos):
                    msg.cont = False
                    return True
        else:
            msg.cont = True
            msg.handled = False

    def updateBorders(self, wnd, pos):
        if util.ptInRect(pos, self._rect):
            for btn in self._buttons:
                if isinstance(btn, IconButton):
                    btn.onMouseMove(wnd, pos)
        else:
            for btn in self._buttons:
                if isinstance(btn, IconButton):
                    btn.onMouseLeave(wnd)
            
    def onMouseMove(self, msg):
        pos = msg.wnd.getCursorPos()
        self.updateBorders(msg.wnd, pos)

    def onLBtnDown(self, msg):
        pos = msg.wnd.getCursorPos()
        if not util.ptInRect(pos, self._rect):
            msg.handled = False
            return

        # get focus if child window has the focus.
        # does nothing if other window has the focus.
        focus = msg.wnd.getFocus()
        if isinstance(focus, wnd.WndBase):
            parent = focus._parent
            while parent:
                if parent is self:
                    self.setFocus()
                    break
                parent = parent._parent

        for btn in self._buttons:
            if isinstance(btn, IconButton):
                if btn.ptInRect(pos):
                    btn.onLBtnDown(msg.wnd, pos)
                    msg.cont = False
                    return

    def onLBtnDblClk(self, msg):
        pos = msg.wnd.getCursorPos()
        if not util.ptInRect(pos, self._rect):
            msg.handled = False
            return

        # consume WM_LBUTTONDBLCLK on buttons
        for btn in self._buttons:
            if isinstance(btn, IconButton):
                if btn.ptInRect((msg.x, msg.y)):
                    msg.cont = False
                    return

    def onRBtnUp(self, msg):
        pos = msg.wnd.getCursorPos()
        if not util.ptInRect(pos, self._rect):
            msg.handled = False
            return

        for btn in self._buttons:
            if isinstance(btn, IconButton):
                if btn.ptInRect(pos):
                    btn.onRBtnUp(msg.wnd, pos)
                    msg.cont = False
                    return

    def onMouseLeave(self, msg):
        for btn in self._buttons:
            if isinstance(btn, IconButton):
                btn.onMouseLeave(msg.wnd)
    
    def onNCDestroy(self, msg):
        self.unbindWnd()
        
        for btn in self._buttons:
            if isinstance(btn, IconButton):
                btn.destroy()

        self._buttons = None
        self._tooltip = None
        self._rect = None
        self._handlers = None
        self._parentWnd = None
    
class HorzIconButtons(IconButtons):
    SEPARATOR_WIDTH = 6

    def __init__(self, buttons=(), aligntop=False, alignmid=False, alignbot=False):
        super(HorzIconButtons, self).__init__(buttons)
        
        self._aligntop = aligntop or (not aligntop and not alignmid and not alignbot)
        self._alignmid = alignmid
        self._alignbot = alignbot

    def setRect(self, wnd, rc, dc=None):
        self._rect = rc
        left = rc[0]+self.MARGIN_LEFT
        top = rc[1]+self.MARGIN_TOP
        orgdc = dc
        if not dc:
            dc = gdi.DesktopDC()
        bottom = rc[3]-self.MARGIN_BOTTOM
        height = bottom-top
        try:
            for btn in self._buttons:
                if isinstance(btn, IconButton):
                    size = btn.calcSize(dc)
                    right = left + size[0]
                    if self._aligntop:
                        t = top
                    elif self._alignmid:
                        t = top + (height-size[1])/2
                    else:
                        t = bottom - size[1]
                        
                    b = t+size[1]
                    btn.setRect((left, t, right, b))
                    left = right + self.MARGIN_BUTTON

                elif btn is not None:
                    # control
                    size = btn.getSize()

                    right = left + size[0]
                    bottom = top+size[1]
                    
                    if self._aligntop:
                        t = top
                    elif self._alignmid:
                        t = top + (height-size[1])/2
                    else:
                        t = bottom - size[1]
                        
                    if btn.ctrl.getHwnd():
                        btn.ctrl.setWindowPos(pos=(left, t))
                    else:
                        btn._pos = (left, t)
                    left = right + self.MARGIN_BUTTON
                else:
                    left += self.SEPARATOR_WIDTH
        finally:
            if not orgdc:
                dc.release()

        if wnd:
            if self._tooltip:
                self.setToolTip(wnd, self._tooltip)
            try:
                cursorpos = wnd.getCursorPos()
            except pymfc.Win32Exception:
                cursorpos = (0, 0)
                
            self.updateBorders(wnd, cursorpos)

class VertIconButtons(IconButtons):
    SEPARATOR_WIDTH = 6

    def __init__(self, buttons=(), alignleft=False, aligncenter=False, alignright=False, fillhorz=False):
        super(VertIconButtons, self).__init__(buttons)
        
        self._alignleft = alignleft or (not alignleft and not aligncenter and not alignright)
        self._aligncenter = aligncenter
        self._alignright = alignright
        self._fillhorz = fillhorz
        
    def setRect(self, wnd, rc, dc=None):
        self._rect = rc
        left = rc[0]+self.MARGIN_LEFT
        right = rc[2]-self.MARGIN_RIGHT
        width = right - left
        top = rc[1]+self.MARGIN_TOP
        orgdc = dc
        if not dc:
            dc = gdi.DesktopDC()
        try:
            for btn in self._buttons:
                if isinstance(btn, IconButton):
                    size = btn.calcSize(dc)
                    if self._fillhorz:
                        size = (width, size[1])
                        
                    r = left + size[0]
                    bottom = top + size[1]
                    
                    if self._alignleft:
                        l = left
                    elif self._aligncenter:
                        l = left + (width-size[0])/2
                    else:
                        l = right - size[1]
                        
                    b = top+size[1]
                    btn.setRect((l, top, r, b))
                    top = b + self.MARGIN_BUTTON

                elif btn is not None:
                    # control
                    size = btn.getSize()
                    if self._fillhorz:
                        size = (width, size[1])

                    r = left + size[0]
                    bottom = top + size[1]
                    
                    if self._alignleft:
                        l = left
                    elif self._aligncenter:
                        l = left + (width-size[0])/2
                    else:
                        l = right - size[1]
                        
                    b = top+size[1]
                        
                    if btn.ctrl.getHwnd():
                        btn.ctrl.setWindowPos(pos=(l, top))
                    else:
                        btn._pos = (l, top)
                    top = b + self.MARGIN_BUTTON
                else:
                    top += self.SEPARATOR_WIDTH
        finally:
            if not orgdc:
                dc.release()

        if wnd:
            if self._tooltip:
                self.setToolTip(wnd, self._tooltip)
            self.updateBorders(wnd, wnd.getCursorPos())

class IconButtonBar(wnd.Wnd):
    WNDCLASS_BACKGROUNDCOLOR = 0xc0c0c0
    WNDCLASS_STYLE = wnd.WndClassStyle(dblclks=False)
    
    def _prepare(self, kwargs):
        super(IconButtonBar, self)._prepare(kwargs)
        
        self._tooltip = wnd.ToolTip(parent=self)
        self.msglistener.CREATE = self.__onCreate
        self.msglistener.SIZE = self._onSize

        self._buttons = self._createIconButtons(kwargs)
        self._buttons.bindWnd(self)

        btns = kwargs.get('buttons', None)
        if btns:
            self._buttons.setButtons(btns)

        self._ondrawbackground = kwargs.get('ondrawbackground', None)

        self.msgproc.PAINT = self._onPaint
        self.msgproc.SETCURSOR = self._onSetCursor

    def wndReleased(self):
        super(IconButtonBar, self).wndReleased()
        self._ondrawbackground = None
        self._buttons = None
        self._tooltip = None

    def setButtons(self, buttons):
        self._buttons.setButtons(buttons)
        if self.getHwnd():
            self._buttons.setToolTip(self, self._tooltip)

    def getButtons(self):
        return self._buttons.getButtons()

    def setMargin(self, left=None, top=None, right=None, bottom=None, button=None):
        return self._buttons.setMargin(left, top, right, bottom, button)
        
    def __onCreate(self, msg):
        self._tooltip.create()
        self._buttons.setToolTip(self, self._tooltip)
        self._buttons.BACKGROUND_COLOR = self.WNDCLASS_BACKGROUNDCOLOR

    def _draw(self, dc, rc):
        if self._ondrawbackground:
            self._ondrawbackground(dc, rc)
        elif self.WNDCLASS_BACKGROUNDCOLOR is not None:
            dc.fillSolidRect(rc, self.WNDCLASS_BACKGROUNDCOLOR)
        self._buttons.paint(dc)
        
    def _onPaint(self, msg):
        dc = gdi.PaintDC(msg.wnd)
        paintdc = dc.createCompatibleDC()
        clientrc = self.getClientRect()
        bmp = dc.createCompatibleBitmap(clientrc[2]-clientrc[0], clientrc[3]-clientrc[1])
        orgbmp = paintdc.selectObject(bmp)
        try:
            self._draw(paintdc, dc.rc)
        finally:
            dc.bitBlt(dc.rc, paintdc, dc.rc, srccopy=True)
            dc.endPaint()
    
    def layout(self):
        self._buttons.setRect(self, self.getClientRect())
        self.invalidateRect(None, erase=False)
        
    def _onSize(self, msg):
        self._buttons.setRect(self, self.getClientRect())

    def _onSetCursor(self, msg):
        cursor = gdi.Cursor(arrow=True)
        cursor.setCursor()

class HorzIconButtonBar(IconButtonBar):
    def _prepare(self, kwargs):
        super(HorzIconButtonBar, self)._prepare(kwargs)
        self._sep = kwargs.get('bottom_separator', False)
        
    def _draw(self, dc, rc):
        super(HorzIconButtonBar, self)._draw(dc, rc)
        if self._sep:
            rc = self.getClientRect()
            dc.drawEdge(rc, sunkenouter=True, raisedinner=True, bottom=True)
    

    def wndReleased(self):
        super(HorzIconButtonBar, self).wndReleased()

    def _createIconButtons(self, kwargs):
        aligntop = kwargs.get('aligntop', False)
        alignmid = kwargs.get('alignmid', False)
        alignbot = kwargs.get('alignbot', False)

        return HorzIconButtons(aligntop=aligntop, alignmid=alignmid, alignbot=alignbot)
        
class VertIconButtonBar(IconButtonBar):
    def _prepare(self, kwargs):
        super(VertIconButtonBar, self)._prepare(kwargs)
        
    def wndReleased(self):
        super(VertIconButtonBar, self).wndReleased()

    def _createIconButtons(self, kwargs):
        alignleft = kwargs.get('alignleft', False)
        aligncenter = kwargs.get('aligncenter', False)
        alignright = kwargs.get('alignright', False)
        fillhorz = kwargs.get('fillhorz', False)
        return VertIconButtons(alignleft=alignleft, aligncenter=aligncenter, alignright=alignright, fillhorz=fillhorz)

class Separator(IconButton):
    def __init__(self, vert=True):
        if vert:
            super(Separator, self).__init__(iconsize=(1, 16), icon=self._drawVertBar)
        else:
            super(Separator, self).__init__(iconsize=(16, 1), icon=self._drawHorzBar)
            
    def _drawVertBar(self, icon, dc, iconrc, wndrc, disabled):
        l, t, r, b = wndrc
        l = iconrc[0]
        r = (l+iconrc[2])/2
        t += 5
        b -= 5
        dc.drawEdge((l, t, r, b), bump=True, right=True)

    def _drawHorzBar(self, icon, dc, iconrc, wndrc, disabled):
        l, t, r, b = wndrc
        l = wndrc[0]+5
        r = wndrc[2]-5
        t = icontrc[1]
        b = (t+wndrc[3])/2

        dc.drawEdge((l, t, r, b), bump=True, flat=True, bottom=True)

        

#if __name__ == '__main__':
#    from pymfc import shellapi
#    imglist = shellapi.getSysImageList(isSmall=True)
#
#    idx = shellapi.shGetFileInfo(u".doc", usefileattributes=True, largeicon=True, sysiconindex=True)
#    icon = imglist.getIcon(idx)
#
#    from pymfc import wndpanel
#    class dlg(wnd.Dialog):
#        def _prepare(self, kwargs):
#            super(dlg, self)._prepare(kwargs)
#            panels = wndpanel.ChildPanelList(parent=self, adjustparent=True)
#            panel = wndpanel.ChildPanel(self, panellist=panels)
#            btns = HorzIconButtonBar(parent=self)
#            btn = IconButton(icon=icon, iconsize=(16,16))
#            btns.setButtons([btn])
#            
#            c = (btns, (100, 20))
#            panel.setCtrls([
#                ((c,),)])
#            
#    dlg().doModal()

if __name__ == '__main__':
    f = wnd.FrameWnd(u"title1")
    f.WNDCLASS_BACKGROUNDCOLOR = 0x000000
    panel = HorzIconButtonBar(parent=f)
#    panel = VertIconButtonBar(parent=f)
    

    
    from pymfc import shellapi

    imglist = shellapi.getSysImageList(isSmall=True)

    def rclicked(wnd, btn):
        print "rclicked"
        
    idx = shellapi.shGetFileInfo(u".doc", usefileattributes=True, largeicon=True, sysiconindex=True)
    icon = imglist.getIcon(idx)
    btn1 = IconButton(icon=icon, iconsize=(16,16), bgcolor=None, tooltipmsg=u"あいうえお", title=u"ワード", 
        raised=False, dropdown=True, thickborder=True, onrclick=rclicked)

    idx = shellapi.shGetFileInfo(u".xls", usefileattributes=True, smallicon=True, sysiconindex=True)
    icon = imglist.getIcon(idx)
    btn2 = IconButton(icon=icon, iconsize=(16,16), bgcolor=None, raised=False, tooltipmsg=u"かきくけこ")

    idx = shellapi.shGetFileInfo(u".ppt", usefileattributes=True, largeicon=True, sysiconindex=True)
    icon = imglist.getIcon(idx)
    btn3 = IconButton(icon=icon, iconsize=(16,16), bgcolor=None, dropdown=True, title=u"パワポ", raised=False)

    idx = shellapi.shGetFileInfo(u".ppt", usefileattributes=True, largeicon=True, sysiconindex=True)
    icon = imglist.getIcon(idx)
    btn4 = IconButton(title=u"last", icon=icon, iconsize=(16,16), bgcolor=None, dropdown=True, raised=False, pushed=True)

    sep = Separator(20)
    
    edit = wnd.Edit(parent=panel, size=(100, 20), title=u"")
    combo = wnd.DropDownCombo(parent=panel, size=(100, 100), title=u"")
    buttons = [btn1, btn2, None, btn3, sep, edit, combo, btn4]

    def f99(msg):
        print combo.getClientRect()
    combo.msglistener.SIZE = f99
    
    panel.setButtons(buttons)

    def oncreate(msg):
        panel.create()
    f.msglistener.CREATE = oncreate

    def onsize(msg):
        l, t, r, b = f.getClientRect()
        panel.setWindowPos(rect=(0, 0, r, b))
        panel.invalidateRect(None, erase=False)
    f.msglistener.SIZE = onsize

    f.create()
#    combo.addItem(u"113")
#    combo.addItem(u"111")
#    combo.addItem(u"1122333")
#    combo.addItem(u"1131")
#    combo.addItem(u"112211")
    app.run()




