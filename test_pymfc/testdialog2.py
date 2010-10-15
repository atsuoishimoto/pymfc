# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import pymfc.wnd, pymfc.gdi
        
w = pymfc.wnd.FrameWnd()

w.create()

dlg = pymfc.wnd.Dialog(size=(100,100), parent=w, style=pymfc.wnd.Dialog.STYLE(visible=True))
dlg.create()
#dlg.setWindowPos(show=True)
pymfc.app.run()


