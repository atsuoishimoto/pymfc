# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import pymfc.wnd


print pymfc.wnd.getDesktopWindow().getWindowRect()
for i in range(100):
    pymfc.wnd.getDesktopWindow().getWindowRect()

