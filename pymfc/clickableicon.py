from pymfc import wnd, gdi, util, app

# Module clickableicon is obsolute. Use iconbtn instead

class _CaptureWnd(wnd.Wnd):
    def _prepare(self, kwargs):
        super(_CaptureWnd, self)._prepare(kwargs)
        self._obj = kwargs['iconobj']

        self.msglistener.LBUTTONUP = self._obj._onLBtnUp
        self.msglistener.MOUSEMOVE = self._obj._onMouseMove
        self.msglistener.CANCELMODE = self._obj._onCancelMode

    def wndReleased(self):
        super(_CaptureWnd, self).wndReleased()
        self._obj = None

class ClickableIcon(object):
    ICONGAP= 2
    FONT = gdi.StockFont(default_gui=True)
    DROPDOWN_WIDTH = 5
    
    def __init__(self, icon=None, iconsize=None, title=u'', 
            bgcolor=0xffffff, textcolor=0x000000,
            rect=(0,0,0,0), margin=3, thickborder=False,
            raised=True, pushed=False, dropdown=False, 
            onclick=None, ondropdown=None,
            **kwargs):
        
        super(ClickableIcon, self).__init__()

        self._fclicked = onclick
        self._fdropdown = ondropdown
        self._icon = icon
        self._iconSize = iconsize
        assert not self._iconSize or isinstance(self._iconSize, (list, tuple))
        assert self._iconSize or (not self._icon)
        self._margin = margin
        self._text = title
        self._bgColor = bgcolor
        self._fgColor = textcolor
        self._iconBgColor = bgcolor
        
        self._raised = raised
        self._thickBorder = thickborder
        self._underline = None
        self.setRect(rect)
        self._pushed = pushed
        self._dropDown = dropdown

        self._captured = False
        self._pressing = False
        self._dropDownPressing = False
        self._dropDownRaised = False
        
        self._capturewnd = None
        self._parentwnd = None
        
    def setOnClick(self, onclick):
        self._fclicked = onclick

    def setRect(self, rect):
        self._rc = rect
        self._size = rect[2]-rect[0], rect[3]-rect[1]

    def getRect(self, rect):
        return self._rc

    def setSize(self, size):
        self._size = size
        if self._rc:
            self._rc = self._rc[0], self._rc[1], self._rc[0]+size[0], self._rc[1]+size[1]
    
    def getSize(self):
        return self._rc[2:]
        
    def setPos(self, pos):
        self._rc = pos[0], pos[1], pos[0]+self._size[0], pos[1]+self._size[1]

    def getPos(self):
        return self._rc[:2]

    def setIcon(self, icon):
        self._icon = icon
        if not icon:
            self._iconSize = None

    def setBgColor(self, bgcolor):
        self._bgColor = bgcolor
        
    def setIconBgColor(self, bgcolor):
        self._iconBgColor = bgcolor
        
    def setTextColor(self, textcolor):
        self._fgColor = textcolor

    def setUnderlinePen(self, pen):
        self._underline = pen

    def getUnderlinePen(self):
        return self._underline
        
    def pushed(self, f):
        self._pushed = f

    def isPushed(self):
        return self._pushed

    def dropDown(self, f):
        self._dropDownPressing = f

    def isDropDown(self):
        return self._dropDownPressing

    def _calcSize(self, dc):
        if not self._icon and not self._text:
            return (0,0)

        if self._icon and not self._text:
            w, h = self._iconSize[0]+self._margin*2, self._iconSize[1]+self._margin*2
        else:
            textsize = dc.getTextExtent(self._text)
            if not self._icon and self._text:
                w, h =  textsize[0]+self._margin*2, textsize[1]+self._margin*2
            else:
#                print self._margin, self._iconSize, self.ICONGAP, textsize
                w, h = (self._margin*2+self._iconSize[0]+self.ICONGAP+textsize[0], 
                    max(self._iconSize[1], textsize[1])+self._margin*2)

        if self._dropDown:
            w += self.DROPDOWN_WIDTH+self._margin*3
        return w, h

    def calcSize(self, dc):
        orgFont = dc.selectObject(self.FONT)
        try:
            return self._calcSize(dc)
        finally:
            dc.selectObject(orgFont)
        
    def draw(self, dc):
        orgFont = dc.selectObject(self.FONT)
        try:
            if self._bgColor is not None:
                dc.fillSolidRect(self._rc, self._bgColor)

            if self._pressing or self._pushed:
                dc.drawEdge(self._rc,
                    sunkenouter=True, sunkeninner=self._thickBorder, 
                    left=True, top=True, right=True, bottom=True)
            elif self._raised:
                dc.drawEdge(self._rc,
                    raisedouter=True, raisedinner=self._thickBorder,
                    left=True, top=True, right=True, bottom=True)
                
            height = self._rc[3]-self._rc[1]
            left = self._rc[0]+self._margin
            if self._icon:
                top = self._rc[1] + (height-self._iconSize[1])/2
                if self._iconBgColor != self._bgColor:
                    dc.fillSolidRect(
                        (left, top, left+self._iconSize[0], top+self._iconSize[1]), 
                        self._iconBgColor)

                dc.drawIcon((left, top), self._icon, size=(self._iconSize[0], self._iconSize[1]), normal=True)
                left = left+self._iconSize[0]+self.ICONGAP
            
            if self._text:
                textsize = dc.getTextExtent(self._text)
                top = self._rc[1] + (height-textsize[1])/2
                dc.setTextColor(self._fgColor)
                dc.drawText(self._text, (left, top, self._rc[2], self._rc[3]), 
                    end_ellipsis=True, noprefix=True)
                left = left + textsize[0]
                
            if self._underline:
                orgpen = dc.selectObject(self._underline)
                try:
                    dc.moveTo((self._rc[0]+self._margin, self._rc[3]-self._margin))
                    dc.lineTo((left, self._rc[3]-self._margin))
                finally:
                    dc.selectObject(orgpen)
                
            if self._dropDown:
                left += self._margin*2
                pen = gdi.Pen(color=self._fgColor)
                orgpen = dc.selectObject(pen)
                try:
                    y = self._rc[0] + (self._rc[3] - self._rc[0])/2
                    dc.moveTo((left, y))
                    dc.lineTo((left+self.DROPDOWN_WIDTH-1, y))
                    y += 1
                    dc.moveTo((left+1, y))
                    dc.lineTo((left+self.DROPDOWN_WIDTH-2, y))
                    y += 1
                    dc.moveTo((left+2, y))
                    dc.lineTo((left+self.DROPDOWN_WIDTH-3, y))
                    
                    rc = (left-self._margin, self._rc[1]+self._margin, 
                            self._rc[2]-self._margin+1, self._rc[3]-self._margin)
                    if self._dropDownPressing:
                        dc.drawEdge(rc,
                            sunkenouter=True, sunkeninner=False, 
                            left=True, top=True, right=True, bottom=True)
                    elif self._dropDownRaised:
                        dc.drawEdge(rc,
                            raisedouter=True, sunkeninner=False, 
                            left=True, top=True, right=True, bottom=True)
                        
                finally:
                    dc.selectObject(orgpen)

        finally:
            dc.selectObject(orgFont)

    def ptInRect(self, pos):
        return util.ptInRect(pos, self._rc)
            
    def ptInDropDown(self, dc, pos):
        w, h = self.calcSize(dc)
        rc = (self._rc[2]-self.DROPDOWN_WIDTH-self._margin*2, 
                self._rc[1], self._rc[2], self._rc[3])
        return util.ptInRect(pos, rc)
        
    def onSetCursor(self, msg):
        pos = msg.wnd.getCursorPos()
        if self.ptInRect(pos):
            cursor = gdi.Cursor(hand=True)
            cursor.setCursor()
            return True

    def onLBtnDown(self, msg):
        pos = msg.wnd.getCursorPos()
        if self._rc and util.ptInRect(pos, self._rc):
            
            if self._dropDown:
                dc = gdi.ClientDC(msg.wnd)
                try:
                    dd = self.ptInDropDown(dc, pos)
                finally:
                    dc.release()

                if dd:
                    if self._fdropdown:
                        self._fdropdown()
                    return
            
            self._parentwnd = msg.wnd
            self._parentwnd.invalidateRect(self._rc, erase=False)

            assert self._capturewnd is None
            self._capturewnd = _CaptureWnd(parent=self._parentwnd, iconobj=self)
            self._capturewnd.create()
            self._capturewnd.setCapture()

            self._captured = True
            self._pressing = True
        
    def _onLBtnUp(self, msg):
        if self._captured:
            pos = self._parentwnd.getCursorPos()
            self._onCancelMode(msg)
            in_rect = util.ptInRect(pos, self._rc)
            if in_rect:
                self._onClick()

    def _onMouseMove(self, msg):
        pos = self._parentwnd.getCursorPos()
        in_rect = util.ptInRect(pos, self._rc)
        if self._captured:
            if in_rect and not self._pressing:
                self._pressing = True
                self._parentwnd.invalidateRect(None, erase=False)
            elif not in_rect and self._pressing:
                self._pressing = False
                self._parentwnd.invalidateRect(None, erase=False)
            
            
    def _onCancelMode(self, msg):
        if self._captured:
            self._parentwnd.invalidateRect(self._rc, erase=False)
            self._parentwnd = None
            self._capturewnd.releaseCapture()
            self._capturewnd.destroy()
            self._capturewnd = None
            self._pressing = False
            self._captured = False

    def _onClick(self):
        if self._fclicked:
            self._fclicked()


class ClickableIconButton(wnd.Wnd):
    def _prepare(self, kwargs):
        super(ClickableIconButton, self)._prepare(kwargs)
        self._btn = ClickableIcon(title=self._title, **kwargs)
        self._underlinePen = kwargs.get('underlinepen', None)
        self._dropdown = kwargs.get('dropdown', None)
        
        self.msgproc.PAINT = self._onPaint
        self.msgproc.SETCURSOR = self._onSetCursor
        self.msglistener.SIZE = self._onSize
        self.msglistener.LBUTTONDOWN = self._onLBtnDown
        self.msgproc.MOUSEMOVE = self._onMouseMove
        self.msgproc.MOUSELEAVE = self._onMouseLeave

    def wndReleased(self):
        super(ClickableIconButton, self).wndReleased()
        self._btn = None

    def setRect(self, rect):
        self.setWindowPos(rect=rect)
        
    def setIcon(self, icon):
        self._btn.setIcon(icon)

    def calcSize(self, dc=None):
        _dc = dc
        if not dc:
            if self.getHwnd():
                _dc = gdi.ClientDC(self)
            else:
                _dc = gdi.DesktopDC()
        try:
            return self._btn.calcSize(_dc)
        finally:
            if not dc:
                _dc.release()

    def setSize(self, size):
        self._btn.setSize(size)
        self._size = size

    def getSize(self):
        return self._btn.getSize()

    def setBgColor(self, bgcolor):
        self._btn.setBgColor(bgcolor)
        if self.getHwnd():
            self.invalidateRect(None, erase=False)
        
    def setIconBgColor(self, bgcolor):
        self._btn.setIconBgColor(bgcolor)
        if self.getHwnd():
            self.invalidateRect(None, erase=False)
        
    def setTextColor(self, textcolor):
        self._btn.setTextColor(textcolor)
        if self.getHwnd():
            self.invalidateRect(None, erase=False)

    def setUnderlinePen(self, pen):
        self._btn.setUnderlinePen(pen)
        if self.getHwnd():
            self.invalidateRect(None, erase=False)

    def pushed(self, f):
        self._btn.pushed(f)
        if self.getHwnd():
            self.invalidateRect(None, erase=False)

    def isPushed(self):
        return self._btn.isPushed()

    def dropDown(self, f):
        self._btn.dropDown(f)
        if self.getHwnd():
            self.invalidateRect(None, erase=False)

    def isDropDown(self):
        return self._btn.isDropDown()

    def _onSize(self, msg):
        self._btn.setRect((0, 0, msg.width, msg.height))

    def _onPaint(self, msg):
        dc = gdi.PaintDC(msg.wnd)
        try:
            self._btn.draw(dc)
        finally:
            dc.endPaint()

    def _onSetCursor(self, msg):
        return self._btn.onSetCursor(msg)

    def _onMouseMove(self, msg):
        if self._underlinePen:
            cur = self._btn.getUnderlinePen()
            if not cur:
                self._btn.setUnderlinePen(self._underlinePen)
                self.invalidateRect(None, erase=False)
                self.trackMouseEvent(leave=True)

        if self._dropdown:
            pos = msg.x, msg.y
            dc = gdi.ClientDC(msg.wnd)
            try:
                in_dd = self._btn.ptInDropDown(dc, pos)
            finally:
                dc.release()
            if in_dd:
                if not self._btn._dropDownRaised:
                    self._btn._dropDownRaised = True
                    self.invalidateRect(None, erase=False)
                    self.trackMouseEvent(leave=True)
            else:
                if self._btn._dropDownRaised:
                    self._btn._dropDownRaised = False
                    self.invalidateRect(None, erase=False)
        else:
            if self._btn._dropDownRaised:
                self._btn._dropDownRaised = False
                self.invalidateRect(None, erase=False)

    def _onMouseLeave(self, msg):
        if self._underlinePen:
            cur = self._btn.getUnderlinePen()
            if cur:
                self._btn.setUnderlinePen(None)
                self.invalidateRect(None, erase=False)
        
        if self._btn._dropDownRaised:
            self._btn._dropDownRaised = False
            self.invalidateRect(None, erase=False)
            
    def _onLBtnDown(self, msg):
        self._btn.onLBtnDown(msg)




class ClickableIconPanel(wnd.Wnd):
    MARGIN_LEFT = 2
    MARGIN_TOP = 2
    MARGIN_BOTTOM = 2

    MARGIN_BUTTON = 2

    SEPARATOR_WIDTH = 4
    
    def _prepare(self, kwargs):
        super(ClickableIconPanel, self)._prepare(kwargs)
        
        self._buttons = []
        buttons = kwargs.get('buttons', None)
        if buttons:
            self.setButtons(buttons)
        
#        self.msglistener.CREATE = self._onCreate
        self.msgproc.PAINT = self._onPaint
        self.msgproc.SETCURSOR = self._onSetCursor
        self.msglistener.LBUTTONDOWN = self._onLBtnDown
        self.msgproc.MOUSEMOVE = self._onMouseMove
        self.msgproc.MOUSELEAVE = self._onMouseLeave

    def wndReleased(self):
        super(ClickableIconPanel, self).wndReleased()
        self._buttons = None

    def setButtons(self, buttons):
        self._buttons = []

        left = self.MARGIN_LEFT
        top = self.MARGIN_TOP

        dc = gdi.DesktopDC()
        try:
            for btn in buttons:
                if btn:
                    size = btn.calcSize(dc)
                    right = left + size[0]
                    bottom = top+size[1]
                    btn.setRect((left, top, right, bottom))
                    left = right + self.MARGIN_BUTTON
                else:
                    left += self.SEPARATOR_WIDTH

                self._buttons.append(btn)
        finally:
            dc.release()


    def _onPaint(self, msg):
        dc = gdi.PaintDC(msg.wnd)
        try:
            for btn in self._buttons:
                btn.draw(dc)
        finally:
            dc.endPaint()
        
    def _onSetCursor(self, msg):
        for btn in self._buttons:
            if btn.onSetCursor(msg):
                return True
        else:
            cursor = gdi.Cursor(arrow=True)
            cursor.setCursor()
            


    def _onMouseMove(self, msg):
        if self._underlinePen:
            cur = self._btn.getUnderlinePen()
            if not cur:
                self._btn.setUnderlinePen(self._underlinePen)
                self.invalidateRect(None, erase=False)
                self.trackMouseEvent(leave=True)

        if self._dropdown:
            pos = msg.x, msg.y
            dc = gdi.ClientDC(msg.wnd)
            try:
                in_dd = self._btn.ptInDropDown(dc, pos)
            finally:
                dc.release()
            if in_dd:
                if not self._btn._dropDownRaised:
                    self._btn._dropDownRaised = True
                    self.invalidateRect(None, erase=False)
                    self.trackMouseEvent(leave=True)
            else:
                if self._btn._dropDownRaised:
                    self._btn._dropDownRaised = False
                    self.invalidateRect(None, erase=False)
        else:
            if self._btn._dropDownRaised:
                self._btn._dropDownRaised = False
                self.invalidateRect(None, erase=False)

    def _onMouseLeave(self, msg):
        if self._underlinePen:
            cur = self._btn.getUnderlinePen()
            if cur:
                self._btn.setUnderlinePen(None)
                self.invalidateRect(None, erase=False)
        
        if self._btn._dropDownRaised:
            self._btn._dropDownRaised = False
            self.invalidateRect(None, erase=False)
            
    def _onLBtnDown(self, msg):
        self._btn.onLBtnDown(msg)



if __name__ == '__main__':
    f = wnd.FrameWnd("title1")
    f.WNDCLASS_BACKGROUNDCOLOR = 0x00000000
    
    from pymfc import shellapi

    imglist = shellapi.getSysImageList(isSmall=True)
    idx = shellapi.shGetFileInfo(".doc", usefileattributes=True, largeicon=True, sysiconindex=True)
    icon = imglist.getIcon(idx)
    
    btn = ClickableIcon(icon=icon, iconsize=16, bgcolor=None)

    buttons = [btn]

    panel = ClickableIconPanel(parent=f, buttons=buttons)
    panel.WNDCLASS_BACKGROUNDCOLOR = 0x888777
    f.create()
    panel.create()

    def onsize(msg):
        l, t, r, b = f.getClientRect()
        panel.setWindowPos(rect=(0, 0, r, 28))
    f.msglistener.SIZE = onsize
    onsize(None)

    app.run()




#            
#
#class _ToolbarPanel(wnd.Wnd):
#    ICONSIZE = 16
#    ICON_ARROWCURSOR = gdi.Icon(cx=ICONSIZE, cy=ICONSIZE,
#        filename=infopile.getRsrcFilename('icon', 'arrow_cursor.ico'))
#    ICON_RECT = gdi.Icon(cx=ICONSIZE, cy=ICONSIZE,
#        filename=infopile.getRsrcFilename('icon', 'rectangle.ico'))
#    ICON_ROUNDRECT = gdi.Icon(cx=ICONSIZE, cy=ICONSIZE,
#        filename=infopile.getRsrcFilename('icon', 'roundrect.ico'))
#    ICON_ELLIPSE = gdi.Icon(cx=ICONSIZE, cy=ICONSIZE,
#        filename=infopile.getRsrcFilename('icon', 'ellipse.ico'))
#    ICON_LINE = gdi.Icon(cx=ICONSIZE, cy=ICONSIZE,
#        filename=infopile.getRsrcFilename('icon', 'line.ico'))
#    ICON_PAINT = gdi.Icon(cx=ICONSIZE, cy=ICONSIZE,
#        filename=infopile.getRsrcFilename('icon', 'paint.ico'))
#    ICON_PEN = gdi.Icon(cx=ICONSIZE, cy=ICONSIZE,
#        filename=infopile.getRsrcFilename('icon', 'linewidth.ico'))
#    ICON_PENCOLOR = gdi.Icon(cx=ICONSIZE, cy=ICONSIZE,
#        filename=infopile.getRsrcFilename('icon', 'linecolor.ico'))
#    ICON_FONT = gdi.Icon(cx=ICONSIZE, cy=ICONSIZE,
#        filename=infopile.getRsrcFilename('icon', 'font.ico'))
#    ICON_FONTCOLOR = gdi.Icon(cx=ICONSIZE, cy=ICONSIZE,
#        filename=infopile.getRsrcFilename('icon', 'font_color.ico'))
#
#    def _prepare(self, kwargs):
#        super(_ToolbarPanel, self)._prepare(kwargs)
#        
#        self._btn_arrow = clickableicon.ClickableIconButton(
#                parent=self,
#                icon=self.ICON_ARROWCURSOR, iconsize=self.ICONSIZE,
#                bgcolor=DiagramWnd.BGCOLOR_TOOLS, 
#                onclick=self._onArrowClicked)
#        
#        self._btn_rect = clickableicon.ClickableIconButton(
#                parent=self,
#                icon=self.ICON_RECT, iconsize=self.ICONSIZE,
#                bgcolor=DiagramWnd.BGCOLOR_TOOLS,
#                onclick=self._onRectClicked)
#                
#        self._btn_roundrect = clickableicon.ClickableIconButton(
#                parent=self,
#                icon=self.ICON_ROUNDRECT, iconsize=self.ICONSIZE,
#                bgcolor=DiagramWnd.BGCOLOR_TOOLS,
#                onclick=self._onRoundRectClicked)
#
#        self._btn_ellipse = clickableicon.ClickableIconButton(
#                parent=self,
#                icon=self.ICON_ELLIPSE, iconsize=self.ICONSIZE,
#                bgcolor=DiagramWnd.BGCOLOR_TOOLS,
#                onclick=self._onEllipseClicked)
#                
#        self._btn_line = clickableicon.ClickableIconButton(
#                parent=self,
#                icon=self.ICON_LINE, iconsize=self.ICONSIZE,
#                bgcolor=DiagramWnd.BGCOLOR_TOOLS,
#                onclick=self._onLineClicked)
#
#        self._btn_brush = clickableicon.ClickableIconButton(
#                parent=self,
#                icon=self.ICON_PAINT, iconsize=self.ICONSIZE,
#                bgcolor=DiagramWnd.BGCOLOR_TOOLS,
#                onclick=self._onBrushColorClicked,
#                dropdown=True, ondropdown=self._onBrushColorSelect)
#
#        self._btn_pen = clickableicon.ClickableIconButton(
#                parent=self,
#                icon=self.ICON_PEN, iconsize=self.ICONSIZE,
#                bgcolor=DiagramWnd.BGCOLOR_TOOLS,
#                onclick=self._onPenClicked,
#                dropdown=True, ondropdown=self._onPenSelect)
#
#        self._btn_pencolor = clickableicon.ClickableIconButton(
#                parent=self,
#                icon=self.ICON_PENCOLOR, iconsize=self.ICONSIZE,
#                bgcolor=DiagramWnd.BGCOLOR_TOOLS,
#                onclick=self._onPenColorClicked,
#                dropdown=True, ondropdown=self._onPenColorSelect)
#
#        self._btn_font = clickableicon.ClickableIconButton(
#                parent=self,
#                icon=self.ICON_FONT, iconsize=self.ICONSIZE,
#                bgcolor=DiagramWnd.BGCOLOR_TOOLS,
#                onclick=self._onFontClicked,
#                dropdown=True, ondropdown=self._onFontSelect)
#
#        self.msglistener.CREATE = self._onCreate
#        self.msglistener.SIZE = self._onSize
#        self.msgproc.PAINT = self._onPaint
#
#    def _getButtons(self):
#        return [self._btn_arrow, self._btn_rect, self._btn_roundrect,
#            self._btn_ellipse, self._btn_line, None, 
#            self._btn_brush, self._btn_pen, self._btn_pencolor,
#            self._btn_font]
#            
#    def _onCreate(self, msg):
#        btns = self._getButtons()
#
#        dc = gdi.ClientDC(self)
#        try:
#            BTN_GAP = 2
#            l = BTN_GAP
#            t = BTN_GAP
#            for btn in btns:
#                if btn:
#                    btn.create()
#                    w, h = btn.calcSize(dc)
#                    btn.setRect((l, t, l+w, t+h))
#                    l += BTN_GAP+w
#                else:
#                    l += BTN_GAP*2
#        finally:
#            dc.release()
#
#    def _onSize(self, msg):
#        pass
#        
#    def _paint(self, dc, rc):
#        dc.fillSolidRect(rc, color=DiagramWnd.BGCOLOR_TOOLS)
#
#    def _onPaint(self, msg):
#        dc = gdi.PaintDC(msg.wnd)
#        try:
#            self._paint(dc, dc.rc)
#        finally:
#            dc.endPaint()
#    
#    def toolUpdated(self):
#        curTool = self._parent._diagram.getTool()
#        if type(curTool) is SelectTool:
#            cur = self._btn_arrow
#        elif type(curTool) is NewRectTool:
#            cur = self._btn_rect
#        elif type(curTool) is NewRoundRectTool:
#            cur = self._btn_roundrect
#        elif type(curTool) is NewEllipseTool:
#            cur = self._btn_ellipse
#        elif type(curTool) is NewLineTool:
#            cur = self._btn_line
#        
#        for btn in self._getButtons():
#            if btn:
#                if btn is cur:
#                    btn.pushed(True)
#                else:
#                    btn.pushed(False)
#        
#        bgcolor = self._parent._diagram.getBrush().getLogBrush().color
#        self._btn_brush.setIconBgColor(bgcolor)
#
#    def _onArrowClicked(self):
#        self._parent._diagram.setTool(SelectTool())
#        
#    def _onRectClicked(self):
#        self._parent._diagram.setTool(NewRectTool())
#    
#    def _onRoundRectClicked(self):
#        self._parent._diagram.setTool(NewRoundRectTool())
#    
#    def _onEllipseClicked(self):
#        self._parent._diagram.setTool(NewEllipseTool())
#    
#    def _onLineClicked(self):
#        self._parent._diagram.setTool(NewLineTool())
#
#    def _onBrushColorClicked(self):
#        self._parent._diagram.updateShapeBrush()
#
#    def _onBrushColorSelect(self):
#        self._btn_brush.dropDown(True)
#        try:
#            color = self._parent._diagram.getBrush().getLogBrush().color
#            ret = wnd.ColorDialog(color=color).doModal()
#            if ret is not None:
#                brush = gdi.Brush(color=ret)
#                self._parent._diagram.setBrush(brush)
#        finally:
#            self._btn_brush.dropDown(False)
#
#    def _onFontClicked(self):
#        self._parent._diagram.updateShapeFont()
#        
#    def _onFontSelect(self):
#        self._btn_font.dropDown(True)
#        try:
#            lf = self._parent._diagram.getShapeFont().getLogFont()
#            color = self._parent._diagram.getTextColor()
#            dlg = wnd.FontDialog(logfont=lf, color=color, novertfonts=True, noscriptsel=True)
#            ret = dlg.doModal()
#            if ret:
#                font = gdi.Font(logfont=ret)
#                self._parent._diagram.setShapeFont(font, dlg.selectedPoint)
#                self._parent._diagram.setTextColor(dlg.selectedColor)
#        finally:
#            self._btn_font.dropDown(False)
#        
#    def _onPenClicked(self):
#        self._parent._diagram.updateShapePen()
#
#    def _onPenSelect(self):
#        self._btn_pencolor.dropDown(True)
#
#        curwidth = self._parent._diagram.getPenWidth()
#
#        ITEMHEIGHT = 20
#        ITEMWIDTH = 150
#        def _size(item, msg):
#            msg.itemsize = (150, 20)
#            return True
#            
#        def _draw(item, msg):
#            dc = gdi.DC(msg.hdc)
#            rc = msg.rcitem
#            
#            if item._selected:
#                dc.drawEdge(rc, left=1, top=1, right=1, bottom=1, sunken=1)
#            else:
#                dc.fillSolidRect(rc, color=0xc0c0c0)
#
#            if msg.selected:
#                dc.drawEdge(rc, left=1, top=1, right=1, bottom=1, etched=1)
#
#            if item._lineWidth:
#                pen = gdi.Pen(color=0x202020, width=item._lineWidth, endcap_flat=True)
#                orgpen = dc.selectObject(pen)
#                try:
#                    x, y = rc[0]+5, rc[1]+(rc[3]-rc[1])/2
#                    dc.moveTo((x, y))
#                    dc.lineTo((rc[2]-5, y))
#                finally:
#                    dc.selectObject(orgpen)
#        
#        popup = menu.PopupMenu("popup")
#        for i in [0, 1, 2, 4, 6, 8]:
#            item = menu.MenuItem("item%i"%i, "item1", sizeMenu=_size, drawMenu=_draw)
#            item._lineWidth = i
#            item._selected = curwidth == i
#            popup.append(item)
#
#        popup.create()
#
#        rc = self._btn_pencolor.clientToScreen(self._btn_pencolor.getClientRect())
#        height = ITEMHEIGHT*5
#        pos = rc[0], rc[1]-height
#        sel = popup.trackPopup(pos, self, nonotify=True, returncmd=True)
#        if sel:
#            self._parent._diagram.setPenWidth(sel._lineWidth)
#
#        self._btn_pencolor.dropDown(False)
#
#
#    def _onPenColorClicked(self):
#        self._parent._diagram.updateShapePen()
#
#    def _onPenColorSelect(self):
#        self._btn_pencolor.dropDown(True)
#        color = self._parent._diagram.getPenColor()
#        ret = wnd.ColorDialog(color=color).doModal()
#        if ret is not None:
#            self._parent._diagram.setPenColor(ret)
#        self._btn_pencolor.dropDown(False)
#
