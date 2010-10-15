# -*- coding: ShiftJIS -*-
# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import wnd, app, menu, grid, gdi


class TestGrid(grid.ControlGridWnd):
#    STYLE = wnd.Wnd.STYLE(border=False, thickframe=False)
    def _prepare(self, kwargs):
        kwargs['font'] = gdi.StockFont(default_gui=True)
        super(TestGrid, self)._prepare(kwargs)
        
        col1 = grid.GridCol(width=200, label=u'abcdefg')
        col2 = grid.GridCol(width=200, label=unicode('あいうえお', 'mbcs'))
        col3 = grid.GridCol(width=200, label=unicode('１２３４５', 'mbcs'))
        self.appendCols([col1, col2, col3])

        row1 = grid.GridRow(height=100, label=u'abcdefg')
        row2 = grid.GridRow(height=100, label=u'abcdefg')
        row3 = grid.GridRow(height=100, label=u'abcdefg')

        self.appendRows([row1, row2, row3])

        font = gdi.StockFont(default_gui=True)
        self.setCell(row1, col1, grid.TextCell(unicode("あいうえお", 'mbcs'), left=True, top=True))
        self.setCell(row1, col2, grid.TextCell(unicode("かきくけこ", 'mbcs'), center=True, vcenter=True))
        self.setCell(row1, col3, grid.TextCell(unicode("サシスセソサシスセ", 'mbcs'), right=True, bottom=True))

        self.setCell(row2, col1, grid.ControlCell(wnd.Edit(title=u"abc", size=(100, 30)), left=True, top=True))
        self.setCell(row2, col2, grid.ControlCell(wnd.Button(title=u"abc", size=(100, 30)), center=True, vcenter=True))
        self.setCell(row2, col3, grid.ControlCell(wnd.Button(title=u"abc", size=(100, 30)), right=True, bottom=True))


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
        
    for i in range(50):
        c()
    app.run()

if __name__ == '__main__':
    run()

