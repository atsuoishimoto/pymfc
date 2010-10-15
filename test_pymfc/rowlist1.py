from pymfc import app, wnd, gdi, rowlist

w = wnd.FrameWnd()
w.WNDCLASS_BACKGROUNDCOLOR = 0xffffff
w.WNDCLASS_CURSOR = gdi.Cursor(arrow=True)
w.create()



class TestRowInfo(rowlist.RowInfo):
    def __init__(self, data):
        super(TestRowInfo, self).__init__()
        self._data = data
    
    def __repr__(self):
        return "<<<<<" + self._data+ ">>>>>>"
        
    def calcHeight(self, dc, width, wnd, idx):
        size = dc.getTextExtent(self._data)
        
        if wnd.isFocused(idx):
            return size[1]*2
        else:
            return size[1]
    
    def onPaint(self, dc, wnd, idx):
        if self._rect:
            dc.fillSolidRect(self._rect, 0xffffff)
            t = self._data
            if wnd.isFocused(idx):
                t = u"*" + t
            if wnd.isSelected(idx):
                t = u"-" + t
        
            dc.drawText(t, self._rect)
    
    def onFocusChanged(self, focused, wnd, idx):
        wnd.rowHeightChanged(idx)
        pass
        
list = rowlist.RowList(parent=w, multisel=True, pos=(0,0), size=(200,100))
list.WNDCLASS_BACKGROUNDCOLOR = 0xffffff
list.create()
list.appendRows([TestRowInfo(unicode(i)) for i in range(20000)])

app.run()



