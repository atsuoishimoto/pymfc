# -*- coding: ShiftJIS -*-

# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

 
from pymfc import wnd, app, menu, grid

class TestGrid(grid.ControlGridWnd):
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

        cols = self.getCols()
        for row in self.getRows():
            self.setCell(row, cols[0], grid.GridCell(margin=3))
            self.setCell(row, cols[1], grid.TextCell(u"aaa", margin=3))
            self.setCell(row, cols[2], grid.ControlCell(wnd.Edit(), margin=3))

def run():
    f = wnd.FrameWnd(u"title1")
    f.WNDCLASS_BACKGROUNDCOLOR = 0xffffff
    gridWnd = TestGrid(parent=f, anchor=wnd.Anchor(left=10, top=10, right=-10, bottom=-10),
#        bgcolor=0xffff00,
        bordercolor=0xff0000,
#        headerbgcolor=0x00ff00,
#        headerbordercolor=0x0000ff,
#        headertextcolor=0x00ffff,
#        hiderowheader=True,
        )

    f.create()
    gridWnd.create()
    app.run()

if __name__ == '__main__':
    run()

