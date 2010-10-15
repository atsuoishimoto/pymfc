# -*- coding: ShiftJIS -*-

# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

 
from pymfc import wnd, app, menu, grid

class TestCell(grid.GridCell, wnd.ListView):
    STYLE = wnd.ListView.STYLE(clipsiblings=True, windowedge=True, clientedge=False)
    def __init__(self, *args, **kwargs):
        grid.GridCell.__init__(self)
        wnd.ListView.__init__(self, *args, **kwargs)
        
    def _rcUpdated(self, wnd):
        margin = 1
        l, t, r, b = self._rc
        pos = l, t
        size = r-l-3, b-t-2
        wnd._defer = self.deferWindowPos(wnd._defer, pos=pos, size=size)

class TestGrid(grid.GridWnd):
#    STYLE = wnd.Wnd.STYLE(border=False, thickframe=False)
    def _prepare(self, kwargs):
        super(TestGrid, self)._prepare(kwargs)
        
        self.appendCols(
            [grid.GridCol(width=200, label=u'abcdefg'), 
             grid.GridCol(width=100, label=u'あいうえお'),
             grid.GridCol(width=300, label=u'１２３４５')])

        self.appendRows(
            [grid.GridRow(height=100, label=u'abcdefg'), 
             grid.GridRow(height=50, label=unicode('あいうえお', "mbcs")), 
             grid.GridRow(height=100, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             grid.GridRow(height=25, label=u'かきくけこ'),
             ])

        for col in self.getCols():
            for row in self.getRows():
                self.setCell(row, col, TestCell(parent=self._gridPane))
#                self._grid.setCell(row, col, grid.GridCell())
        
        
    def _onCreate(self, msg):
        super(TestGrid, self)._onCreate(msg)
        for cell in self._grid.getCells():
            cell.create()
    
    def _updateCellRect(self):
        n = len(self._grid.getCols()) * len(self._grid.getRows())
        self._gridPane._defer = self.beginDeferWindowPos(n)

        super(TestGrid, self)._updateCellRect()

        self.endDeferWindowPos(self._gridPane._defer)


def run():
    def c():
        f = wnd.FrameWnd(u"title1")
        gridWnd = TestGrid(parent=f)
        
        def onSize(msg):
            gridWnd.setWindowPos(size=(msg.width, msg.height))

        f.create()
        gridWnd.create()

        f.msglistener.SIZE=onSize
        gridWnd.setWindowPos(size=f.getClientRect()[2:])
        
    for i in range(10):
        c()
    app.run()

if __name__ == '__main__':
    run()

