# -*- coding: ShiftJIS -*-
from __future__ import with_statement
import types
import pymfc
from pymfc import wnd, gdi

class CellItemBase(object):
    _extendright = False
    def __init__(self, table, aligntop, alignmiddle, alignbottom, font):
        self.table = table
        self._aligntop = aligntop
        self._alignmiddle = alignmiddle
        self._alignbottom=alignbottom
        self._font = font
        self._vscrollpos = 0
        self._cacheWidth = self._cacheHeight = None
        self._xunit = None
        
        if not aligntop and not alignmiddle and not alignbottom:
            self._alignmiddle = True
            
    def isExtendRight(self):
        return self._extendright
        
    def getFont(self):
        return self._font if self._font else self.table.font

    def _calcXUnit(self):
        if self._xunit is not None:
            return self._xunit
        with self.table.getDC(self.getFont()) as dc:
            
            cx, cy = dc.getTextExtent(
               u"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
        self._xunit = int((cx / 26.0 + 1) / 2)
        return self._xunit
        

class CellItem(CellItemBase):
    def __init__(self, table, klass, name, width, height, extendright, extendbottom, 
            aligntop, alignmiddle, alignbottom, font, nrows, **kwargs):

        super(CellItem, self).__init__(table, aligntop, alignmiddle, alignbottom, font)

        self._klass = klass
        self._name = name
        self._width = width
        self._height = height
        self._extendright=extendright
        self._extendbottom=extendbottom
        self._nrows = nrows
        self._kwargs = kwargs
        
        if isinstance(self._klass, (type, types.ClassType)):
            self.ctrl = self._klass(parent=self.table.parent, **self._kwargs)
        else:
            self.ctrl = self._klass
            
    def create(self):
        if not self.ctrl.getHwnd():
            self.ctrl.create()
        self.ctrl.setFont(self.getFont())
        
    def calcWidth(self):
        if self._width is None:
            if self._cacheWidth is not None:
                return self._cacheWidth
                
            title = self._kwargs.get('title', u'')+u'  '
            with self.table.getDC(self.getFont()) as dc:
                width = dc.getTextExtent(title)[0]

                if isinstance(self.ctrl, (wnd.CheckBox, wnd.RadioButton)):
                    self._cacheWidth = width + pymfc.metric.CXEDGE*2 + pymfc.metric.CXMENUCHECK # ????
                else:
                    self._cacheWidth = width + pymfc.metric.CXEDGE*2

                return self._cacheWidth
        elif callable(self._width):
            return self._width(self.table, self.ctrl)
        else:
            return int(self._calcXUnit() * self._width)

    def calcHeight(self, width):
        if self._height is None:
            if self._cacheHeight is not None:
                return self._cacheHeight

            if isinstance(self.ctrl, (wnd.DropDownCombo, wnd.DropDownList)):
                self._cacheHeight = self.table.getCBHeight(self._font)
            elif isinstance(self.ctrl, wnd.Static):
                self._cacheHeight = self.table.getStaticHeight()
            else:
                self._cacheHeight = self.table.getEditHeight(self._font)
            ret = self._cacheHeight

        elif callable(self._height):
            ret = self._height(self.table, self.ctrl, width)
        else:
            ret = int(self.table.getEditHeight(self._font)*self._height)
        return ret
            
    def _calcControlHeight(self, width):
        return self.calcHeight(width)
        
    def setPos(self, left, top, cellrect, width, visible, rowheights, vscrollpos):
        self._vscrollpos = vscrollpos
        
        if not visible:
            self.ctrl.setWindowPos(show=False, rect=(0,0,0,0))
            return
        
        if self._extendbottom:
            height = cellrect[3] - top
        else:
            height = self._calcControlHeight(width)
            
        if self._aligntop:
            top = top
        elif self._alignmiddle:
            top = top + ((cellrect[3]-cellrect[1]) - height) / 2
        else:
            top = cellrect[3] - height
        top = top - self._vscrollpos
        
        if isinstance(self.ctrl, (wnd.DropDownCombo, wnd.DropDownList)):
            self.ctrl.setWindowPos(show=True, rect=(left, top, left+width, top+height+400))
        elif isinstance(self.ctrl, (wnd.GroupBox)):
            height = sum(rowheights[:self._nrows]) + self.table.GAP_ROW * (self._nrows-1)
            self.ctrl.setWindowPos(show=True, rect=(left, top, left+width, top+height))
        else:
            self.ctrl.setWindowPos(show=True, rect=(left, top, left+width, top+height))
            if isinstance(self.ctrl, (wnd.Edit,)):
                # If an edit control has ES_AUTOHSCROLL style and long text,
                # edit control displays only last portion of the text initialy.
                self.ctrl.setSel((0,0))

        self.ctrl.invalidateRect(None, erase=False)
            
    def setVScrollPos(self, vpos):
        d = vpos-self._vscrollpos
        if d:
            l, t, r, b = self.ctrl._parent.screenToClient(self.ctrl.getWindowRect())
            self.ctrl.invalidateRect(None, erase=False)
            self.ctrl.setWindowPos(pos=(l,t-d))

            self._vscrollpos = vpos


class TextCellItem(CellItem):
    def __init__(self, table, text, width, height,
            aligntop, alignmiddle, alignbottom, font, textcolor, **kwargs):

        super(TextCellItem, self).__init__(table, wnd.Static, "", 
            width, height, False, False,
            aligntop, alignmiddle, alignbottom, font, nrows=1, title=text)

        
        self._text = text
        self._textcolor = textcolor
        
        def ctlcolor(msg):
            dc = gdi.DC(hdc=msg.hdc)
            dc.setBkMode(transparent=True)
            if self._textcolor is not None:
                dc.setTextColor(self._textcolor)

            return self.table.bgbrush.getHandle().handle

        self.ctrl.msgproc.CTLCOLORSTATIC = ctlcolor

    def setText(self, text):
        if self._text != text:
            self._text = text
            self._cacheWidth = None
            self._cacheHeight = None

        if self.ctrl.getHwnd():
            self.ctrl.setText(text)

    def calcWidth(self):
        if self._width is None:
            if self._cacheWidth is not None:
                return self._cacheWidth
                
            with self.table.getDC(self.getFont()) as dc:
                size = dc.getTextExtent(self._text)
            self._cacheWidth = size[0]
            return self._cacheWidth
        else:
            return int(self._calcXUnit() * self._width)


    def calcHeight(self, width):
        if self._height is None:
            if self._cacheHeight is not None:
                return self._cacheHeight
                
            with self.table.getDC(self.getFont()) as dc:
                size = dc.getTextExtent(self._text)
            self._cacheHeight = size[1]
            return self._cacheHeight
        else:
            return int(self.table.getEditHeight(self._font)*self._height)
        
    def _calcControlHeight(self, width):
        with self.table.getDC(self.getFont()) as dc:
            size = dc.getTextExtent(self._text)
        return size[1]
        

class _IconWnd(wnd.Wnd):
    def _prepare(self, kwargs):
        super(_IconWnd, self)._prepare(kwargs)
        self._icon = kwargs['icon']
        self.msgproc.PAINT = self._onPaint
        
    def wndReleased(self):
        super(_IconWnd, self).wndReleased()
        
    def _onPaint(self, msg):
        dc = gdi.PaintDC(msg.wnd)
        try:
            dc.drawIcon((0, 0), self._icon, self._icon.getBitmap().getSize(), normal=True)
        finally:
            dc.endPaint()
        
class IconCellItem(CellItem):
    def __init__(self, table, icon, width, height, aligntop, alignmiddle, alignbottom, **kwargs):
        
        self._icon = icon
        self._iconsize = self._icon.getBitmap().getSize()

        super(IconCellItem, self).__init__(table, _IconWnd, "", 
            width, height, False, False,
            aligntop, alignmiddle, alignbottom, None, nrows=1, icon=self._icon)
        
    def calcWidth(self):
        if self._width is None:
            return self._iconsize[0]
        else:
            return int(self._calcXUnit() * self._width)

    def calcHeight(self, width):
        if self._height is None:
            return self._iconsize[1]
        else:
            return int(self.table.getEditHeight(self._font)*self._height)
        

        
class NoneCellItem(CellItemBase):
    def __init__(self, table, width, height, aligntop, alignmiddle, alignbottom, **kwargs):
        super(NoneCellItem, self).__init__(table, aligntop, alignmiddle, alignbottom, font=None)
        self._width = 1 if width is None else width
        self._height = 1 if height is None else height
        
        
    def create(self):
        pass
    
    def calcWidth(self):
        return int(self._calcXUnit()+self._width)
#        with self.table.getDC(self.getFont()) as dc:
#            size = dc.getTextExtent(u" ")
#        return int(size[0]*self._width)

    def calcHeight(self, width):
        if self._cacheHeight is not None:
            return self._cacheHeight
        with self.table.getDC(self.getFont()) as dc:
            size = dc.getTextExtent(u" ")
        self._cacheHeight = int(size[1]*self._height)
        return self._cacheHeight
        
    def setPos(self, left, top, cellrect, width, visible, rowheights, vscrollpos):
        pass
        
    def setVScrollPos(self, vpos):
        pass

        
class Cell(object):
    def __init__(self, table, colspan, rowspan, alignright, aligncenter, fillhorz):
        self._items = []
        self.colspan = colspan
        self.rowspan = rowspan
        self.table = table
        self.fillhorz = fillhorz
        self._alignright = alignright
        self._aligncenter = aligncenter
        
    def add(self, klass, name="", width=None, height=None, extendright=False, 
                extendbottom=False, aligntop=False, alignmiddle=False, alignbottom=False, 
                font=None, textcolor=None, nrows=1, **kwargs):

        if isinstance(klass, unicode):
            item = TextCellItem(self.table, klass, width, height, aligntop=aligntop, alignmiddle=alignmiddle, 
                alignbottom=alignbottom, font=font, textcolor=textcolor)
        elif klass is None:
            item = NoneCellItem(self.table,aligntop=aligntop, alignmiddle=alignmiddle, alignbottom=alignbottom, width=width, height=height)
        elif isinstance(klass, gdi.Icon):
            item = IconCellItem(self.table, klass, width, height, extendright=extendright, extendbottom=extendbottom,
                aligntop=aligntop, alignmiddle=alignmiddle, alignbottom=alignbottom)
        else:
            item = CellItem(self.table, klass, name=name, width=width, height=height, extendright=extendright, 
                    extendbottom=extendbottom, aligntop=aligntop, alignmiddle=alignmiddle, alignbottom=alignbottom,
                    font=font, nrows=nrows, **kwargs)
                
        self._items.append(item)
        if name:
            assert not hasattr(self.table.ctrls, name)
            setattr(self.table.ctrls, name, item.ctrl)
        return item
        
    def create(self):
        for item in self._items:
            item.create()

    def calcColWidth(self):
        if self.colspan > 1:
            return [0]*self.colspan
        else:
            return [self.calcWidth()]
            
    def calcWidth(self):
        return sum(item.calcWidth() for item in self._items)

    def calcHeight(self, width):
        if not self._items:
            return 0
        return max(item.calcHeight(width) for item in self._items)

    def setPos(self, left, top, cellwidth, rowheight, visible, rowheights, vscrollpos):
        cellrect = (left, top, left+cellwidth, top+rowheight)
        widths = [item.calcWidth() for item in self._items]
        
        d = cellwidth-sum(widths)
        if d:
            for n, item in enumerate(self._items):
                if item.isExtendRight():
                    widths[n] += d
                    d = 0
                    break
        
        if not self._alignright:
            if self._aligncenter:
                left = left + d//2
            for width, item in zip(widths, self._items):
                item.setPos(left, top, cellrect, width, visible, rowheights, vscrollpos)
                left += width
        else:
            left = cellrect[2]
            for width, item in reversed(zip(widths, self._items)):
                left -= width
                item.setPos(left, top, cellrect, width, visible, rowheights, vscrollpos)

    def setVScrollPos(self, vpos):
        for item in self._items:
            item.setVScrollPos(vpos)
            

class _RowSpanCell(object):
    rowspan = 1
    fillhorz = False
    
    def __init__(self, colspan):
        self.colspan = colspan

    def create(self):
        pass
        
    def calcColWidth(self):
        return [0]*self.colspan
            
    def calcWidth(self):
        return 0

    def calcHeight(self, width):
        return 0

    def setPos(self, left, top, cellwidth, rowheight, visible, rowheights, vscrollpos):
        pass
        
    def setVScrollPos(self, vpos):
        pass
        
class Row(object):
    def __init__(self, table, fillvert):
        self.table = table
        self.visible = True
        self._fillvert=fillvert
        self._cells = []

    def addCell(self, colspan=1, rowspan=1, alignright=False, aligncenter=False, fillhorz=False):
        cell = Cell(table=self.table, colspan=colspan, rowspan=rowspan, alignright=alignright, aligncenter=aligncenter, fillhorz=fillhorz)
        self._cells.append(cell)
        return cell
        
    def createItems(self):
        for cell in self._cells:
            cell.create()
    
    def getColCount(self):
        return sum(cell.colspan for cell in self._cells)

    def isFillVert(self):
        return self._fillvert
        
    def hasFillHorz(self):
        n = 0
        for cell in self._cells:
            if cell.fillhorz:
                return n
            n += cell.colspan
        
    def _insertRowSpanCell(self, n, cell):
        self._cells.insert(n, cell)
        
    def expandRowSpan(self, rest):
        n = 0
        for cell in self._cells:
            if cell.rowspan > 1:
                for row in rest[:cell.rowspan-1]:
                    row._insertRowSpanCell(n, _RowSpanCell(colspan=cell.colspan))
            n += cell.colspan

    def calcColWidth(self):
        ret = []
        for cell in self._cells:
            ret.extend(cell.calcColWidth())
        return ret
    
    def adjustColWidth(self, colwidths, tablewidth):
        ret = colwidths[:]
        n = 0
        for cell in self._cells:
            w = cell.calcWidth()
                
            curwidth = sum(colwidths[n:n+cell.colspan])
            if curwidth < w:
                widths = colwidths[n:n+cell.colspan]
                adjust = w - curwidth
                widths[-1] = widths[-1] + adjust
                ret[n:n+cell.colspan] = widths
            n += cell.colspan
        return ret

    def calcRowHeight(self, colWidths):
        if not self.visible:
            return 0
            
        n = 0
        ret = 0
        for cell in self._cells:
            width = sum(colWidths[n:n+cell.colspan])
            if cell.rowspan == 1:
                ret = max(ret, cell.calcHeight(width))
            n += cell.colspan
        return ret
        
    def calcRowSpanHeight(self, colWidths):
        n = 0
        for cell in self._cells:
            width = sum(colWidths[n:n+cell.colspan])
            if cell.rowspan > 1:
                yield cell.rowspan, cell.calcHeight(width)

            n += cell.colspan

    def setPos(self, left, top, colWidths, rowHeights, vscrollpos):
        n = 0
        for cell in self._cells:
            cellwidth = sum(colWidths[n:n+cell.colspan])
            height = sum(rowHeights[0:cell.rowspan]) + self.table.GAP_ROW * (cell.rowspan-1)
            cell.setPos(left, top, cellwidth, height, self.visible, rowHeights, vscrollpos)
            left += cellwidth
            n += cell.colspan

    def setVScrollPos(self, vpos):
        for cell in self._cells:
            cell.setVScrollPos(vpos)
                
class _ctrls(object):
    pass
    
class Table(object):
    GAP_ROW = 3
    def __init__(self, parent, pos=(0,0), width=None, font=None, bgcolor=None, 
                margin_right=10, margin_bottom=10, adjustparent=False, centerparent=False,
                extendright=False, extendbottom=False, rowgap=None, vscroll=False):

        self.ctrls = _ctrls()
        self._colWidths = self._rowHeights = ()
        
        self._pos = pos
        self._width = width
    
        self.parent = parent
        self.font = font
        if not self.font:
            self.font = gdi.StockFont(default_gui=True)
            
        self._bgcolor = bgcolor
        if bgcolor is not None:
            self.bgbrush = gdi.Brush(color=bgcolor)
        else:
            self.bgbrush = gdi.Brush(null=True)

        self._margin_right = margin_right
        self._margin_bottom = margin_bottom
        
        self._adjustparent = adjustparent
        self._centerparent = centerparent
        self._extendright = extendright
        self._extendbottom = extendbottom
        
        if rowgap is not None:
            self.GAP_ROW = rowgap
        self._vscroll = vscroll
        self._vscrollpos = 0
        self._maxvscrollpos = 0
        self._hasvscrollbar = False
        
        self._rows = []
        self._msglistener = wnd.Listeners(parent.MSGDEF)
        self._msglistener.CREATE = self._onCreate
        self._msglistener.NCDESTROY = self._onNCDestroy
        self._msglistener.SIZE = self._onSize
        if self._vscroll:
            self._msglistener.VSCROLL = self._onVScroll

        parent.msglistener.attach(self._msglistener)

        if self._vscroll:
            self._msgproc = wnd.MsgHandlers(parent.MSGDEF)
            self._msgproc.MOUSEWHEEL = self._onMouseWheel
            parent.msgproc.attach(self._msgproc)
        else:
            self._msgproc = None

        
    def addRow(self, fillvert=False):
        row = Row(self, fillvert=fillvert)
        self._rows.append(row)
        return row
        
    def getDC(self, font):
        if font is None:
            font = self._font
            
        dc = gdi.DesktopDC()
        return gdi.DCBlock(dc, [font], onexit=dc.release)

    def getEditHeight(self, font=None):
        #    MSDN Q124315
        if not font:
            font = self.font
        tm = font.getTextMetrics()
        return tm.tmHeight+min(tm.tmHeight, self.SYS_TEXTMETRICS.tmHeight)/2+pymfc.metric.CYEDGE#*2
#        tm = self.font.getTextMetrics()
#        return tm.tmHeight+pymfc.metric.CYEDGE*2+3

    def getStaticHeight(self):
        tm = self.font.getTextMetrics()
        return tm.tmHeight+pymfc.metric.CYEDGE*2

    SYSFONT = gdi.StockFont(system=True)
    SYS_TEXTMETRICS = SYSFONT.getTextMetrics()

    def getCBHeight(self, font=None):
        #    MSDN Q124315
        if not font:
            font = self.font
        tm = font.getTextMetrics()
        return tm.tmHeight+min(tm.tmHeight, self.SYS_TEXTMETRICS.tmHeight)/2+pymfc.metric.CYEDGE*2


    def calcSize(self):
        colWidths, rowHeights = self._calcTableSize(0, 0)

        width = self._pos[0] + sum(colWidths) + self._margin_right
        height = self._pos[1] + sum(rowHeights) + self.GAP_ROW * (len(rowHeights)-1) + self._margin_bottom

        return width, height
        
    def adjustParent(self):
        if self._adjustparent:
            colWidths, rowHeights = self._calcTableSize(0, 0)

            width = self._pos[0] + sum(colWidths) + self._margin_right
            height = self._pos[1] + sum(rowHeights) + self.GAP_ROW * (len(rowHeights)-1) + self._margin_bottom

            if not callable(self._adjustparent):
                rc = self.parent.calcWindowRect((0, 0, width, height))
                self.parent.setWindowPos(size=(rc[2]-rc[0], rc[3]-rc[1]))
                
                if self._centerparent:
                    if isinstance(self._centerparent, wnd.WndBase):
                        centerOf = self._centerparent
                    else:
                        centerOf = None
                    self.parent.centerWnd(centerOf)
            else:
                self._adjustparent(self, (width, height))
        
    def initTable(self):
        for row in self._rows:
            row.createItems()

        for n in range(len(self._rows)-1):
            rest = self._rows[n+1:]
            self._rows[n].expandRowSpan(rest)
        
        self.adjustParent()
        
    def _onCreate(self, msg):
        self.initTable()
            
    def _onNCDestroy(self, msg):
        self.parent.msglistener.detach(self._msglistener)
        self._msglistener.clear()
        self._msglistener = None
        
        if self._msgproc is not None:
            self.parent.msgproc.detach(self._msgproc)
            self._msgproc.clear()
            self._msgproc = None
            
        self.parent = None
        self._rows = None
        self._centerparent = None
        self.ctrls = None

    def _calcTableSize(self, tablewidth, tableheight):
        nCols = 0
        for row in self._rows:
            nCols = max(nCols, row.getColCount())

        colWidths = [0]*nCols
        for row in self._rows:
            widths = row.calcColWidth()
            for n, width in enumerate(widths):
                colWidths[n] = max(colWidths[n], width)
        
        for row in self._rows:
            colWidths = row.adjustColWidth(colWidths, tablewidth)

        if self._extendright:
            d = tablewidth - sum(colWidths)
            if d > 0:
                for row in self._rows:
                    n = row.hasFillHorz()
                    if n is not None:
                        colWidths[n] += d
                        break
                else:
                    colWidths[-1] += d

        rowHeights = [row.calcRowHeight(colWidths) for row in self._rows]

        for n, row in enumerate(self._rows):
            for rowspan, height in row.calcRowSpanHeight(colWidths):
                cur = sum(rowHeights[n:n+rowspan])
                if cur < height:
                    rowHeights[n+rowspan-1] += height - cur

        if self._extendbottom:
            d = tableheight - (sum(rowHeights) + (len(rowHeights)-1) * self.GAP_ROW)
            if d > 0:
                for n, row in enumerate(self._rows):
                    if row.isFillVert():
                        rowHeights[n] += d
                        break
                else:
                    rowHeights[-1] += d

        return colWidths, rowHeights
        
    def _onSize(self, msg):
        # todo: following profiling code raises exception.
        # file python bugs.
#        import profile, pstats
#        from profile import Profile
#        Profile.dispatch['c_exception'] = \
#                  Profile.trace_dispatch_return
#
#        profile.runctx('self.resized()', globals(), locals(), "c:\\a.prof")
#        p = pstats.Stats('c:\\a.prof')
#        p.strip_dirs()
#        p.sort_stats('cumulative')
#        p.print_stats()
#
#
        
        self.resized()
        
    def _onVScroll(self, msg):
        rc = self.parent.getClientRect()
        height = rc[3]-rc[1]
        
        if msg.linedown:
            newpos = self._vscrollpos+max(height//5, 20)

        elif msg.lineup:
            newpos = self._vscrollpos-max(height//5, 20)

        elif msg.pagedown:
            newpos = self._vscrollpos+height

        elif msg.pageup:
            newpos = self._vscrollpos-height
            
        elif msg.bottom:
            newpos = self._maxvscrollpos
            
        elif msg.top:
            newpos = 0

        elif msg.thumbtrack:
            info = self.parent.getScrollInfo(vert=True)
            newpos = info.trackpos
        else:
            return

        newpos = max(min(newpos, self._maxvscrollpos), 0)
        if newpos != self._vscrollpos:
            self._vscrollpos = newpos
            
            for row in self._rows:
                row.setVScrollPos(self._vscrollpos)

            self.parent.setScrollInfo(vert=True, min=0, max=self._maxvscrollpos, pos=self._vscrollpos, redraw=True)
            self.parent.invalidateRect(None, erase=False)
            self.parent.updateWindow()

    def _onMouseWheel(self, msg):
        rc = self.parent.getClientRect()
        height = rc[3]-rc[1]
        lineheight = max(height//5, 20)
        
        delta = msg.delta//120
        if delta < 0:
            delta = abs(delta)
        else:
            lineheight = lineheight*-1

        for d in range(delta):
            newpos = self._vscrollpos+lineheight
            newpos = min(newpos, self._maxvscrollpos)
            newpos = max(newpos, 0)

            if newpos == self._vscrollpos:
                break

            self._vscrollpos = newpos
            
            for row in self._rows:
                row.setVScrollPos(self._vscrollpos)

            self.parent.setScrollInfo(vert=True, min=0, max=self._maxvscrollpos, pos=self._vscrollpos, redraw=True)
            self.parent.updateWindow()

        return 0
        

    def resized(self):
        self._colWidths = self._rowHeights = ()

        if not self._rows:
            return
            
        l, t, r, b = self.parent.getClientRect()
        if l == r or t == b:
            return
        
        tableheight = b-t-self._pos[1]-self._margin_bottom
        
        tablewidth = r-l-self._pos[0]-self._margin_right
        if self._width is not None:
            tablewidth = min(self._width, tablewidth)
        
        self._colWidths, self._rowHeights = self._calcTableSize(tablewidth, tableheight)
 
        if self._vscroll:
            sbarchanged = False
            
            height = self._pos[1] + sum(self._rowHeights) + self.GAP_ROW * (len(self._rowHeights)-1) + self._margin_bottom
            if height <= (b-t):
                self._vscrollpos = self._maxvscrollpos = 0
                if self._hasvscrollbar:
                    sbarchanged = True
                    self._hasvscrollbar = False
                    self.parent.showScrollBar(vert=True, show=False)
            else:
                self._maxvscrollpos = height - (b-t)
                self._vscrollpos = min(self._maxvscrollpos, self._vscrollpos)
                if not self._hasvscrollbar:
                    sbarchanged = True
                    self._hasvscrollbar = True
                    self.parent.showScrollBar(vert=True, show=True)
                    self.parent.setScrollInfo(vert=True, min=0, max=self._maxvscrollpos, pos=self._vscrollpos, redraw=True)

            if sbarchanged:
                # If a scrollbar was displayed or hidden, client area will
                # be resized and parent receives new WM_SIZE message.
                return

        t = t+self._pos[1]
        l = l+self._pos[0]
        for n, row in enumerate(self._rows):
            row.setPos(l, t, self._colWidths, self._rowHeights[n:], self._vscrollpos)
            t += self._rowHeights[n] + self.GAP_ROW
        
    def getTableSize(self):
        return self._colWidths, self._rowHeights

    
def f1():
    f = wnd.FrameWnd()
    f.WNDCLASS_BACKGROUNDCOLOR = 0xffc0c0
    wnd.DialogKeyHandler(f)

    
    table1 = Table(parent=f, pos=(100, 50), adjustparent=True, margin_right=100, extendright=True, extendbottom=True, vscroll=True, margin_bottom=10)
    row = table1.addRow()
    cell = row.addCell()
    cell.add(u"2222222222222222222222")
    cell.add(u"あいうおえ")
    cell = row.addCell()
    cell.add(wnd.Edit, width=10)
    cell.add(u"2222222222222222222222")

    row = table1.addRow()
    cell = row.addCell(colspan=2)
    cell.add(u"01234567890123456789")

    row = table1.addRow()
    cell = row.addCell()
    cell.add(u"x")
    cell.add(u" ")
    cell.add(u"01234567890123456789")
    cell = row.addCell()
    cell.add(wnd.Edit, width=10, height=4)
    cell.add(u" ")
    cell.add(wnd.Button, title=u"1111111111", extendbottom=True)
    cell.add(u" abcdefgabcdefgabcdefgabcdefgabcdefg")
    cell = row.addCell()
    cell.add(wnd.Button, title=u"kjnsdkfnssssssss")
    cell.add(u" ")


    row = table1.addRow()
    cell = row.addCell()
    cell.add(u"aaaaaaaaaaaa111")
    cell = row.addCell()
    cell.add(u"bbbbbbbbbbbbbb")

    row = table1.addRow()
    cell = row.addCell()
    cell = row.addCell(colspan=2)
    cell.add(wnd.Button, name="btn1", title=u"222222222", extendright=True)

    f.create()
    
    
def f2():
    f = wnd.FrameWnd()
    f.WNDCLASS_BACKGROUNDCOLOR = 0xffc0c0
    wnd.DialogKeyHandler(f)

    
    table1 = Table(parent=f, pos=(100, 50), extendright=True, extendbottom=True, margin_bottom=100)
    row = table1.addRow(fillvert=True)
    cell = row.addCell()
    cell.add(u"2222222222222222222222")
    cell.add(u"あいうおえ")
    cell = row.addCell()
    cell.add(wnd.Edit, width=10, extendbottom=True, extendright=True)

    row = table1.addRow()
    cell = row.addCell()
    cell.add(u"01234567890123456789")


    f.create()
    
def f3():
    f = wnd.FrameWnd()
    f.WNDCLASS_BACKGROUNDCOLOR = 0xffc0c0
    wnd.DialogKeyHandler(f)

    
    table1 = Table(parent=f, pos=(100, 50))
    row = table1.addRow()
    cell = row.addCell()
    cell.add(u"2222222222222222222222")
    cell.add(u"あいうおえ")
    cell.add(wnd.Edit, width=10, extendbottom=True, extendright=True)

    row = table1.addRow()
    cell = row.addCell(alignright=True)
    cell.add(u"01234567890123456789")
    cell.add(wnd.Edit, width=10)

    row = table1.addRow()
    cell = row.addCell(alignright=True)
    cell.add(wnd.Edit, width=10, height=10)
    cell.add(wnd.Button, title=u"top", aligntop=True)
    cell.add(wnd.Button, title=u"middle", alignmiddle=True)
    cell.add(wnd.Button, title=u"bottom", alignbottom=True)

    row = table1.addRow()
    cell = row.addCell()
    cell.add(wnd.Edit, width=10, height=10)
    cell.add(u"top", aligntop=True)
    cell.add(u"middle", alignmiddle=True)
    cell.add(u"bottom", alignbottom=True)


    f.create()
    
def f4():
    f = wnd.FrameWnd()
    f.WNDCLASS_BACKGROUNDCOLOR = 0xffc0c0
    wnd.DialogKeyHandler(f)

    
    table1 = Table(parent=f, pos=(100, 50))
    row = table1.addRow()
    cell = row.addCell(rowspan=6)
    cell.add(u"111111")
    cell = row.addCell()
    cell.add(u"222222")
    cell = row.addCell()
    cell.add(u"333333")
    cell = row.addCell()
    cell.add(u"444444")

    row = table1.addRow()
    cell = row.addCell(rowspan=5)
    cell.add(u"111111")
    cell = row.addCell()
    cell.add(u"222222")
    cell = row.addCell()
    cell.add(u"333333")
    cell = row.addCell()
    cell.add(u"444444")

    row = table1.addRow()
    cell = row.addCell(rowspan=4)
    cell.add(u"111111")
    cell = row.addCell()
    cell.add(u"222222")
    cell = row.addCell()
    cell.add(u"333333")
    cell = row.addCell()
    cell.add(u"444444")

    row = table1.addRow()
    cell = row.addCell(rowspan=3)
    cell.add(u"111111")
    cell = row.addCell()
    cell.add(u"222222")
    cell = row.addCell()
    cell.add(u"333333")
    cell = row.addCell()
    cell.add(u"444444")

    row = table1.addRow()
    cell = row.addCell(rowspan=2)
    cell.add(u"111111")
    cell = row.addCell()
    cell.add(u"222222")
    cell = row.addCell()
    cell.add(u"333333")
    cell = row.addCell()
    cell.add(u"444444")

    row = table1.addRow()
    cell = row.addCell()
    cell.add(u"111111")
    cell = row.addCell()
    cell.add(u"222222")
    cell = row.addCell()
    cell.add(u"333333")
    cell = row.addCell()
    cell.add(u"444444")

    f.create()
    
    

def f5():
    f = wnd.FrameWnd()
    f.WNDCLASS_BACKGROUNDCOLOR = 0xffc0c0
    wnd.DialogKeyHandler(f)

    
    table1 = Table(parent=f, pos=(100, 50))

    row = table1.addRow()
    cell = row.addCell(rowspan=6)
    cell.add(u"111111")
    cell = row.addCell()
    cell.add(u"222222")
    cell = row.addCell()
    cell.add(u"333333")
    cell = row.addCell()
    cell.add(u"444444")

    f.create()

def f6():
    f = wnd.FrameWnd()
    f.WNDCLASS_BACKGROUNDCOLOR = 0xffc0c0
    wnd.DialogKeyHandler(f)

    
    table1 = Table(parent=f, pos=(100, 50))

    row = table1.addRow()
    cell = row.addCell()
    cell.add(u"111111")
    cell = row.addCell()
    cell.add(u"222222")
    cell = row.addCell()
    cell.add(u"333333")
    cell = row.addCell()
    cell.add(u"444444")

    row = table1.addRow()
    cell = row.addCell()
    cell.add(u"111111")
    cell = row.addCell(colspan=2, rowspan=2)
    cell.add(u"colspan=2, rowspan=2", alignbottom=True)
    cell = row.addCell()
    cell.add(u"444444")

    row = table1.addRow()
    cell = row.addCell()
    cell.add(u"111111")
    cell = row.addCell()
    cell.add(u"444444")

    row = table1.addRow()
    cell = row.addCell()
    cell.add(u"111111")
    cell = row.addCell()
    cell.add(u"222222")
    cell = row.addCell()
    cell.add(u"333333")
    cell = row.addCell()
    cell.add(u"444444")

    f.create()

def f7():
    f = wnd.FrameWnd()
    f.WNDCLASS_BACKGROUNDCOLOR = 0xffc0c0
    wnd.DialogKeyHandler(f)

    
    table1 = Table(parent=f, pos=(100, 50))

    row = table1.addRow()
    cell = row.addCell(alignright=True)
    cell.add(u"タイトル: ")
    cell.add(wnd.Edit, width=10, extendright=True)
    cell.add(None)
    cell.add(wnd.Button, title=u"1111111111")
    
    row = table1.addRow()
    cell = row.addCell()
    cell.add(u"222222222222222222222222222222222222222222222222222222222222222222")
    f.create()

def f8():
    f = wnd.FrameWnd()
    f.WNDCLASS_BACKGROUNDCOLOR = 0xffc0c0

    
    table1 = Table(parent=f, pos=(100, 50))

    row = table1.addRow()
    cell = row.addCell(alignright=True)
    cell.add(u"row1 ")
    
    row = table1.addRow()
    cell = row.addCell()
    cell.add(u"row2 ", height=10, alignmiddle=True)

    row = table1.addRow()
    cell = row.addCell()
    cell.add(u"row3 ")

    f.create()

if __name__ == '__main__':
#    f1()
#    f2()
#    f3()
#    f4()
#    f5()
#    f6()
#    f7()
    f8()
    from pymfc import app
    app.run()

