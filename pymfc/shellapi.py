# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from _pymfclib import SHItemIdList, shGetFileInfo, shGetSpecialFolderPath
from _pymfclib import CSIDL, shellExecute

_desktop = None

def getDesktop():
    global _desktop
    if not _desktop:
        _desktop = SHItemIdList(desktop=True)
    return _desktop

_sysImagelist = _smallSysImagelist = None

def getSysImageList(isSmall):
    desktop = getDesktop()
    global _sysImagelist, _smallSysImagelist
    if isSmall:
        if not _smallSysImagelist:
            _smallSysImagelist = desktop.getSysImageList(small=True)
        return _smallSysImagelist
    else:
        if not _sysImagelist:
            _sysImagelist = desktop.getSysImageList()
        return _sysImagelist


