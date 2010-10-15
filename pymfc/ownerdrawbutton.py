import pymfc
from pymfc import wnd, gdi

class OwnerDrawButton(wnd.Button):
    STYLE = wnd.Button.STYLE(ownerdraw=True)

    def _prepare(self, kwargs):
        super(OwnerDrawButton, self)._prepare(kwargs)
        self.msgproc.DRAWITEM = self.onDrawItem
        
    def wndReleased(self):
        super(OwnerDrawButton, self).wndReleased()

    def fillButton(self, msg, dc):
        color = pymfc.syscolor.btnface
        dc.fillSolidRect(msg.rcitem, color)
        
    def drawText(self, msg, dc):
        text = self.getText()
        color = pymfc.syscolor.btntext
        dc.setTextColor(color)
        font = gdi.StockFont(default_gui=True)
        dc.selectObject(font)
        dc.drawText(text, msg.rcitem, center=True, vcenter=True)
        
    def draw(self, msg):
        dc = gdi.DC(msg.hdc)
        self.fillButton(msg, dc)
        self.drawText(msg, dc)

        if msg.itemselected:
            dc.drawEdge(msg.rcitem, sunken=True, rect=True)
        else:
            dc.drawEdge(msg.rcitem, raised=True, rect=True)
        
        if msg.focus:
            l, t, r, b = msg.rcitem
            l+= 3; t+=3; r-=3; b-=3;
            dc.drawFocusRect((l, t, r, b))

    def onDrawItem(self, msg):
        msg.cont = False   # consume this message
        self.draw(msg)
    


class OwnerDrawDropDownList(wnd.DropDownList):
    STYLE = wnd.DropDownList.STYLE(ownerdrawfixed=True)
    def _prepare(self, kwargs):
        super(OwnerDrawDropDownList, self)._prepare(kwargs)
        self.msgproc.MEASUREITEM = self._onMeasureItem
        self.msgproc.DRAWITEM = self._onDrawItem
        
    def wndReleased(self):
        super(OwnerDrawDropDownList, self).wndReleased()

    def getItemSize(self, itemid):
        return (100, 20)

    def drawItem(self, dc, rc, itemid, itemdata, focus):
        dc.fillSolidRect(rc, color=0x0000ff)
        dc.drawText(unicode(itemid), rc, noprefix=True)
        if focus:
            dc.drawFocusRect(rc)
                    
    def _onMeasureItem(self, msg):
        msg.itemsize = self.getItemSize(msg.itemid)
        return True
    
    def _onDrawItem(self, msg):
        itemid = msg.itemid
        rc = msg.rcitem
        itemdata = msg.itemdata
        hdc = msg.hdc
        focus = msg.itemfocused
        
        dc = gdi.DC(hdc=msg.hdc)
        
        self.drawItem(dc, rc, itemid, itemdata, focus)
        