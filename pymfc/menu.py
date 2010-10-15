# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from _pymfclib import _pymfclib_menu
from _pymfclib_menu import _const_menu
import util

import pymfc.wnd
import weakref, sys, traceback

class MenuMap:
    def __init__(self, idStart=None, idEnd=None):
        # see "TN020: ID Naming and Numbering Conventions" for valid range

        if not idStart:
            idStart = 0x8000
        if not idEnd:
            idEnd = 0xDFFF

        self.hMenu = weakref.WeakValueDictionary()
        self.itemId = weakref.WeakValueDictionary()
        self.idpool = util.IdPool(idStart, idEnd)
        
    def setPopup(self, hmenu, popup):
        '''register popup menu'''
        self.hMenu[hmenu] = popup

    def getPopup(self, hMenu):
        '''retrieve registered popup menu by handle'''
        return self.hMenu.get(hMenu)
        
    def delPopup(self, hMenu):
        '''remove popup menu'''
        del self.hMenu[hMenu]
        
    def getPopupParent(self, child):
        for popup in self.hMenu.values():
            if child in popup.children:
                return popup

    def allocItemId(self):
        '''allocate menu item id'''
        return self.idpool.get()

    def releaseItemId(self, id):
        '''release menu item id'''
        return self.idpool.release(id)

    def setItem(self, item):
        ''' register menu item'''
        self.itemId[item.getHandle()] = item

    def getItem(self, itemid):
        ''' retrieve registered menu item by itemid'''
        return self.itemId.get(itemid)


class MenuBase:
    def __init__(self, menuid, caption, menuMap, updateMenu, desc):
        self.menuid = menuid      # menuid is a string identifies this menu
        self.caption = caption    # text descrives this menu
        self.menuMap = menuMap    # MenuMap object for this menu
        self.updateMenu = updateMenu # function to update this menu
        self.desc = desc          # description for this menu

    def _getItemCount(self):
        '''return number of child menus'''
        return 1

    def getCaption(self):
        return self.caption

    def onInitMenu(self, parent, wnd):
        pass


class PopupMenu(MenuBase):
    def __init__(self, menuid, caption=u"", menuMap=None, updateMenu=None):
        MenuBase.__init__(self, menuid, caption, menuMap, updateMenu, "")

        self.hMenu = None
        self.children = []

    def __del__(self):
        try:
            self.destroy()
        except:
            traceback.print_exc()

    def append(self, item):
        self.children.append(item)
        
    def getHandle(self):
        return self.hMenu

    def create(self, parent=None, menuMap=None):
        assert self.hMenu is None
        
        self.hMenu = _pymfclib_menu._menu_createPopup()
        if parent:
            parent._appendMenu(self, _const_menu.MF_POPUP)
            self.menuMap = parent.menuMap
        else:
            self.menuMap = menuMap
            if self.menuMap is None:
                self.menuMap = MenuMap()

        self.menuMap.setPopup(self.hMenu, self)
        
#        print self.menuid, self.children
        for c in self.children:
            c.create(self)

    def destroy(self):
        if self.getHandle():
            _pymfclib_menu._menu_destroy(self.getHandle())
            self.onDestroy()

    def _onMeasureItem(self, msg):
        if msg.ismenu:
            msg.cont = False    # consume this message
            item = self.getItem(msg.itemid)
            if item.sizeMenu:
                return item.sizeMenu(item, msg)

    def _onDrawItem(self, msg):
        if msg.ismenu:
            msg.cont = False    # consume this message
            item = self.getItem(msg.itemid)
            if item.drawMenu:
                return item.drawMenu(item, msg)
        

    def _onInitMenuPopup(self, msg):
        self.onPopup(self, msg.wnd)

    def trackPopup(self, pos, wnd, nonotify=False, returncmd=False, exclude=None):
        if not self.hMenu:
            self.create()

        handler = pymfc.wnd.MsgHandlers(wnd.MSGDEF)
        handler.MEASUREITEM = self._onMeasureItem
        handler.DRAWITEM = self._onDrawItem
        handler.INITMENUPOPUP = self._onInitMenuPopup
        wnd.msgproc.attach(handler)
        try:
            x, y = pos
            ret = _pymfclib_menu._menu_track_popup_menu(self.getHandle(), x, y, wnd, exclude, nonotify, returncmd)
        finally:
            if wnd.getHwnd():
                wnd.msgproc.detach(handler)

        if returncmd and ret:
            return self.menuMap.getItem(ret)
        return ret

    def onDestroy(self):
        for c in self.children:
            c.onDestroy()
            
        if self.hMenu:
            self.hMenu = None
        
    def _appendMenu(self, item, flags):
        _pymfclib_menu._menu_append(self.getHandle(), flags, item.getHandle(), item.caption)

    def _insertMenu(self, item, flags, pos):
        _pymfclib_menu._menu_insert(self.getHandle(), pos, flags | _const_menu.MF_BYPOSITION, item.getHandle(), item.caption)

    def _deleteItem(self, idx):
        _pymfclib_menu._menu_delete(self.getHandle(), idx, _const_menu.MF_BYPOSITION)
        
    def _getString(self, idx):
        return _pymfclib_menu._menu_getString(self.getHandle(), idx, _const_menu.MF_BYPOSITION)

    def size(self):
        return _pymfclib_menu._menu_itemCount(self.getHandle())
        
    def getIndex(self, menuid):
        i = 0
        for c in self.children:
            if c.menuid == menuid:
                return i
            i += c._getItemCount()

        raise KeyError
    
    def onInitMenu(self, parent, wnd):
        ''' should be called on WM_INITMENU'''
        for c in self.children:
            c.onInitMenu(self, wnd)

    def onPopup(self, parent, wnd):
        ''' should be called on WM_INITMENUPOPUP'''
        if self.updateMenu:
            self.updateMenu(self, parent, wnd)

        for c in self.children:
            c.onPopup(self, wnd)

    def getItem(self, itemId):
        ''' retrieve registered menu item by itemid'''
        return self.menuMap.getItem(itemId)

    def enableItem(self, idx, enabled=False, grayed=False):
        f = _const_menu.MF_BYPOSITION
        if enabled:
            f = f | _const_menu.MF_ENABLED
        else:
            f = f | _const_menu.MF_DISABLED
        if grayed:
            f = f | _const_menu.MF_GRAYED
        _pymfclib_menu._menu_enable_menu_item(self.getHandle(), idx, f)
        

        
class MenuItem(MenuBase):
    def __init__(self, menuid, caption, desc=u"", command=None,
            updateMenu=None, sizeMenu=None, drawMenu=None, grayed=False, checked=False):

        MenuBase.__init__(self, menuid, caption, None, updateMenu, desc)
        self.itemId = None
        self.command = command

        assert sizeMenu and drawMenu or (not sizeMenu and not drawMenu)

        self.sizeMenu=sizeMenu
        self.drawMenu=drawMenu
        
        self._flags = 0
        if grayed:
            self._flags |= _const_menu.MF_GRAYED
        if checked:
            self._flags |= _const_menu.MF_CHECKED
        
    def getHandle(self):
        return self.itemId
    
    def getCommand(self):
        return self.command

    def create(self, parent, pos=None):
        self.menuMap = parent.menuMap

        self.itemId = self.menuMap.allocItemId()
        flag = self._flags | _const_menu.MF_STRING
        if self.sizeMenu:
            flag |= _const_menu.MF_OWNERDRAW

        if pos is None:
            parent._appendMenu(self, flag)
        else:
            parent._insertMenu(self, flag, pos)

        self.menuMap.setItem(self)
        
    def onPopup(self, parent, wnd):
        if self.updateMenu:
            self.updateMenu(self, parent, wnd)

    def onDestroy(self):
        if self.itemId:
            self.menuMap.releaseItemId(self.itemId)
            self.itemId = None



class Separator(MenuItem):
    def __init__(self):
        MenuItem.__init__(self, u'', u'', None, None, u'')
        
    def getHandle(self):
        return -1
    
    def getCommand(self):
        return None

    def create(self, parent, pos=None):
        if pos is None:
            parent._appendMenu(self, _const_menu.MF_STRING | _const_menu.MF_SEPARATOR)
        else:
            parent._insertMenu(self, _const_menu.MF_STRING | _const_menu.MF_SEPARATOR, pos)

    def onDestroy(self):
        pass

class DynMenuItems(MenuBase):
    def __init__(self, menuid, updateMenu):
        assert updateMenu
        
        MenuBase.__init__(self, menuid, u"", None, updateMenu, u"")
        self.dmyItem = None
        self.dynItems = []

    def _newDmyItem(self, parent, wnd):
        if self.dmyItem:
            return
        pos = parent.getIndex(self.menuid)
        dmyItem = MenuItem(u"", u"(__dmy__)", self.menuMap)
        dmyItem.create(parent, pos)
        
        self.dmyItem = dmyItem
    
    def _delDmyItem(self, parent):
        if not self.dmyItem:
            return
        
        pos = parent.getIndex(self.menuid)
        parent._deleteItem(pos)
        self.dmyItem.onDestroy()

        self.dmyItem = None

    def _newDynItems(self, parent, wnd):
        self.dynItems = [item for item in self.updateMenu(self, parent, wnd)]
        pos = parent.getIndex(self.menuid)
        for item in self.dynItems:
            item.create(parent, pos)
            item.onPopup(parent, wnd)
            pos += 1

    def _delDynItems(self, parent):
        pos = parent.getIndex(self.menuid)
        while self.dynItems:
            item = self.dynItems.pop(0)
            parent._deleteItem(pos)
            item.onDestroy()

    def _getItemCount(self):
        if not self.dynItems:
            return 1
        else:
            return len(self.dynItems)

    def create(self, parent):
        self.menuMap = parent.menuMap

    def onInitMenu(self, parent, wnd):
        self._delDynItems(parent)
        self._newDmyItem(parent, wnd)
        
    def onPopup(self, parent, wnd):
        self._delDmyItem(parent)
        self._delDynItems(parent)
        self._newDynItems(parent, wnd)

    def onDestroy(self):
        if self.dmyItem:
            self.dmyItem.onDestroy()
        
        self.dmyItem = None
        
        while self.dynItems:
            item = self.dynItems.pop(0)
            item.onDestroy()

class MenuBar(PopupMenu):
    def __init__(self, menuId, menuMap=None):
        PopupMenu.__init__(self, menuId, u"", menuMap)

    def create(self, menuMap=None):
        if menuMap:
            self.menuMap = menuMap
        self.hMenu = _pymfclib_menu._menu_create()
        self.menuMap.setPopup(self.hMenu, self)

        for c in self.children:
            c.create(self)

def isMenu(h):
    return _pymfclib_menu._menu_ismenu(h)


