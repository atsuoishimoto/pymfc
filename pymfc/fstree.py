# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import pymfc
from pymfc import wnd
import _pymfclib

_desktop = _pymfclib.SHItemIdList(desktop=True)
_sysImages = _desktop.getSysImageList(small=True)

class FSTree(wnd.TreeView):
    def _prepare(self, kwargs):
        super(FSTree, self)._prepare(kwargs)
        self._items = {}
        self._desktop = _desktop
        self._icons  = _sysImages

        self.msglistener.CREATE = self.onCreate
        self.msgproc.ITEMEXPANDING = self._onItemExpanding
        self.msgproc.ITEMDELETED = self._onDeleteItem

    def onCreate(self, msg):
        self.setImageList(normal=self._icons)
        self.addRoot(self._desktop)
    
    def addRoot(self, itemid):
        item = wnd.TreeItem()
        item.text = itemid.getDisplayName()
        idx = itemid.getSysIconIndex(small=True)
        item.image = idx
        item.selectedimage = idx

        item.children = 1
        self.insert(item)

        self._items[item.hitem.handle] = itemid
    
    def wndReleased(self):
        super(FSTree, self).wndReleased()
        self._items = None
        
    def _onDeleteItem(self, msg):
        del self._items[msg.hitem.handle]
        
    def _onItemExpanding(self, msg):
        if msg.collapse:
            return
        if self.getChildItem(msg.hitem):
            # displayed already
            return
        # get parent itemidlist
        item = self._items[msg.hitem.handle]

        subitems = []
        for subitem in item.getSubItems(nonfolder=True, hidden=True, wnd=self):
            # check item type
            ancestor = subitem.filesystemancestor
            filesystem = subitem.filesystem
            dispname = subitem.getDisplayName()
            if not ancestor:
                if not filesystem:
                    continue
            dispname = subitem.getDisplayName()
            if filesystem: # get filename for sort
                filename = subitem.getFilename().lower()
            else:
                filename = u""
            subitems.append((not ancestor, filesystem, filename, dispname, subitem))

        subitems.sort()

        # create tree items
        child = wnd.TreeItem()
        for not_ancestor, filesystem, filename, dispname, subitem in subitems:
            child.text = dispname
            
            # get icon index
            # todo: Very slow. Move to background thread.
            idx = subitem.getSysIconIndex(small=True)
            child.image = idx
            child.selectedimage = idx
            
#            print not_ancestor, filesystem, dispname
            
            # if item is container or item has subfolder, item can be expanded.
            if not_ancestor and not subitem.hassubfolder:
                child.children = 0
            else:
                child.children = 1

            self.insert(child, parent=msg.hitem)
            self._items[child.hitem.handle] = subitem

    def getItemFilename(self, hitem):
        if hitem:
            itemid = self._items.get(hitem.handle)
            if itemid:
                try:
                    return itemid.getFilename()
                except pymfc.Win32Exception:
                    pass


