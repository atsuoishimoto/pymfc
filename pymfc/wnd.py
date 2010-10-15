# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.
import time, re
from pymfc import app, util

import _pymfclib
from _pymfclib import KEY
from _pymfclib import _keydict, _wndmsg
from _pymfclib import WndStyle, WndClassStyle, DlgStyle, EditStyle, StaticStyle
from _pymfclib import ButtonStyle, ListBoxStyle, ComboBoxStyle, ScrollBarStyle
from _pymfclib import TabCtrlStyle, TreeViewStyle, ListViewStyle, RichEditStyle
from _pymfclib import DateTimeCtrlStyle, ToolTipStyle, WebCtrlStyle

from _pymfclib import msgbox, getKeyState, ImmContext, postThreadMessage, registerWindowMessage
from _pymfclib import GETDLGCODERESULT, getStartupInfo

from pymfc.gdi import Font, Bitmap, Icon, Cursor, Brush, DC, ClientDC, Monitor
import _pymfclib_system

IDOK = 1
IDCANCEL = 2
IDABORT = 3
IDRETRY = 4
IDIGNORE = 5
IDYES = 6
IDNO = 7
IDCLOSE = 8
IDHELP = 9

from _pymfclib import getCursorPos


class MsgHandlers:
    def __init__(self, msgdef):
        self.__dict__['msgdef'] = msgdef.copy()
        self.__dict__['_handlers'] = {}
        self.__dict__['_attached'] = [self]
        self.__dict__['_handlerList'] = [self._handlers]
        self.__dict__['_owner'] = None
        
    def clear(self):
        if self._attached:
            for handler in self._attached:
                if handler is not self:
                    handler.clear()
            
        self.__dict__['msgdef'] = None
        self.__dict__['_handlers'] = None
        self.__dict__['_attached'] = None
        self.__dict__['_handlerList'] = None
        self.__dict__['_owner'] = None
        
    def getHandlers(self):
        return self._handlerList

    def __setattr__(self, key, item):
        msgkey = self.msgdef[key]
        self._handlers[msgkey] = item

    def __getattr__(self, key):
        msgkey = self.msgdef[key]
        return self._handlers[msgkey]

    def __eq__(self, other):
        return id(self) == id(other)
        
    def __repr__(self):
        return repr(self._handlers)

    def __str__(self):
        return repr(self._handlers)
        
    def hasHandler(self, msg):
        if isinstance(msg, str):
            msg = self.msgdef[msg]

        for handler in self._handlerList():
            if msg in handler:
                return True
                
    def setMessage(self, msg, item):
        self._handlers[msg] = item

    def setCommand(self, cmdId, item):
        ''' Dispatch menu item or toolbar command'''
        key = (self.msgdef['COMMAND'], None, cmdId)
        self._handlers[key] = item

    def attach(self, handler, head=True, owner=None):
        if head:
            self._attached.insert(0, handler)
        else:
            self._attached.append(handler)
        
        if owner:
            owner.msglistener.NCDESTROY = lambda msg:self.detach(handler)
        
        # warning: never *update* self._handlerList, replace entire list always
        # Updating self._handlerList will cause UAE at internal message-lookup code.
        self.__dict__['_handlerList'] = [attached._handlers for attached in self._attached]

    def detach(self, handler):
        if handler in self._attached:
            self._attached.remove(handler)
            # warning: never *update* self._handlerList, replace entire list always
            self.__dict__['_handlerList'] = [attached._handlers for attached in self._attached]
            handler.clear()
        
    def dump(self, **keys):
        ret = []
        for d in self._handlerList:
            for key, _  in keys.iteritems():
                f = d.get(self.msgdef[key], None)
                if f:
                    ret.append(f)
        return f
    
class Listeners:
    def __init__(self, msgdef):
        assert msgdef
        self.__dict__['msgdef'] = msgdef.copy()
        self.__dict__['_handlers'] = {}
        self.__dict__['_attached'] = [self]
        self.__dict__['_handlerList'] = [self._handlers]
        self.__dict__['_cleared'] = False
        
    def clear(self):
        if self._attached:
            for handler in self._attached:
                if handler is not self:
                    handler.clear()

        self.__dict__['msgdef'] = None
        self.__dict__['_handlers'] = {}
        self.__dict__['_attached'] = []
        self.__dict__['_handlerList'] = []
        self.__dict__['_cleared'] = True
        
    def getHandlers(self):
        return self._handlerList[:]
        
    def __setattr__(self, key, item):
        if key not in self._handlers:
            msgkey = self.msgdef[key]
            l = self._handlers.setdefault(msgkey, [])
        else:
            l = self._handlers[key]
        l.append(item)

    def __getattr__(self, key):
        msgkey = self.msgdef[key]
        return self._handlers[msgkey]

    def __eq__(self, other):
        return id(self) == id(other)

    def __repr__(self):
        return repr(self._handlers)

    def __str__(self):
        return repr(self._handlers)

    def setMessage(self, msg, item=None):
        l = self._handlers.setdefault(msg, [])
        if item is not None:
            l.append(item)
        
    def setCommand(self, cmdId, item):
        ''' Dispatch menu item or toolbar command'''
        key = (self.msgdef['COMMAND'], None, cmdId)
        l = self._handlers.setdefault(key, [])
        l.append(item)

    def attach(self, handler, head=True, owner=None):
        assert not self._cleared
        
        if head:
            self._attached.insert(0, handler)
        else:
            self._attached.append(handler)
        if owner:
            def ondestroy(msg):
                if not self._cleared:
                    self.detach(handler)
                return

            owner.msglistener.NCDESTROY = ondestroy

        # warning: never *update* self._handlerList, replace entire list always
        # Updating self._handlerList will cause UAE at internal message-lookup code.
        self.__dict__['_handlerList'] = [attached._handlers for attached in self._attached]

    def detach(self, handler):
        if handler in self._attached:
            self._attached.remove(handler)
            # warning: never *update* self._handlerList, replace entire list always
            self.__dict__['_handlerList'] = [attached._handlers for attached in self._attached]
            handler.clear()

    def run(self, key, *args, **kwargs):
        # This method is not called for Window message processing.
        # Cound be used to run custom event handler.
        
        for handler in self.getHandlers():
            if key in handler:
                funcs = handler[key]

                for f in funcs:
                    f(*args, **kwargs)



class KeyHandlers:
    def __init__(self, keymap):
        self.keymap = keymap

    def __repr__(self):
        return repr(self.keymap)

    def addKey(self, func, keys):
        ''' keys arg should be a tuple of (alt, ctrl, shift, key).
        alt, ctrl and shift should be 0 or 1, and key is a character
        or a virtual key code in integer. shift is ignored if key is 
        a character'''

        bind = ()
        nkeys = len(keys)
        
        for idx, k in enumerate(keys):
            alt, ctrl, shift, key = k
            if type(key) is str:
                if ord(key) > 0x20:
                    shift = 0
            bind = bind + ((alt, ctrl, shift, key),)
            if idx+1 != nkeys:
                self.keymap[bind] = None
            else:
                self.keymap[bind] = func
        
#        print "****", self.keymap

    def clear(self):
        self.keymap.clear()

class Anchor(object):
    # todo: Anchor should be able to attach multiple wnds.
    def __init__(self, left=None, top=None, right=None, bottom=None, width=None, height=None, occupy=False, func=None):
        if occupy:
            self._left = 0
            self._top = 0
            self._right = 0
            self._bottom = 0
            
            if left is not None: self._left = left
            if top is not None: self._top = top
            if right is not None: self._right = right
            if bottom is not None: self._bottom = bottom
                
        else:
            self._left = left
            self._top = top
            self._right = right
            self._bottom = bottom

        self._func = func
        self._width = width
        self._height = height
        self._msglistener = None
        self._targetMsglistener = None
        
    def register(self, target):
        if self._msglistener is not None:
            assert 0
            self.unRegister()

        self._target = target

        def onSize(msg):
            self.apply(target)

        self._msglistener = Listeners(target._parent.MSGDEF)
        self._msglistener.SIZE = onSize
        target._parent.msglistener.attach(self._msglistener)

        def onTargetCreate(msg):
            self.apply(target)
            
        def onTargetNCDestroy(msg):
            self.unRegister()

        self._targetMsglistener = Listeners(target.MSGDEF)
        self._targetMsglistener.CREATE = onTargetCreate
        self._targetMsglistener.NCDESTROY = onTargetNCDestroy
        target.msglistener.attach(self._targetMsglistener, head=False)

    def unRegister(self):
        assert self._msglistener is not None

        self._target._parent.msglistener.detach(self._msglistener)
        self._msglistener.clear()
        self._msglistener = None
        
        self._target.msglistener.detach(self._targetMsglistener)
        self._targetMsglistener.clear()
        self._targetMsglistener = None

        self._target = None
        
    def apply(self, target):
        assert self._msglistener is not None
        
        if not target.getHwnd():
            return

        l, t, r, b = target._parent.screenToClient(target.getWindowRect())
        p_l, p_t, p_r, p_b = target._parent.getClientRect()

        if self._func:
            l, t, r, b = self._func(target)

        if isinstance(self._left, int):
            l = p_l+self._left
        elif self._left is not None:
            l = self._left(target)

        if isinstance(self._top, int):
            t = p_t+self._top
        elif self._top is not None:
            t = self._top(target)

        if isinstance(self._right, int):
            r = p_r+self._right
        elif self._right is not None:
            r = self._right(target)

        if isinstance(self._bottom, int):
            b = p_b+self._bottom
        elif self._bottom is not None:
            b = self._bottom(target)
        
        if isinstance(self._width, int):
            r = l+self._width
        elif self._width is not None:
            r = l + self._width(target)

        if isinstance(self._height, int):
            b = t+self._height
        elif self._height is not None:
            b = t + self._height(target)

        target.setWindowPos(rect=(l,t,r,b))



class WndBase(object):
    TITLE = u''
    DEFAULT_WNDCLASS = u''
    STYLE = WndStyle(visible=1, child=1, clipsiblings=0)
    MSGDEF = _pymfclib._msgdict
    CHILDID=0
    RANGE_CHILDID = (20, 0xdfff)
    
    AFX_IDW_PANE_FIRST = 0xe900

    WNDCLASS_CURSOR = 0
    WNDCLASS_BACKGROUNDCOLOR = None
    WNDCLASS_ICON = 0
    WNDCLASS_STYLE = WndClassStyle(dblclks=True)
    
    ROLE = ''
    CONTEXT = False

    __WNDCLASSES = {}
    
    IDOK = 1
    IDCANCEL = 2
    IDABORT = 3
    IDRETRY = 4
    IDIGNORE = 5
    IDYES = 6
    IDNO = 7
    IDCLOSE = 8
    IDHELP = 9

    @classmethod
    def subclassWindow(cls, hwnd, *args, **kwargs):
        ret = cls(*args, **kwargs)
        ret._subclassWindow(hwnd)
        return ret
        
    @classmethod
    def getActiveWindow(cls):
        return _pymfclib._getActiveWindow()
        
    def __init__(self, title=None, parent=None, style=None, 
            pos=(None, None), size=(None, None), wndid=0, anchor=None, autocreate=False, 
            context=False, role="", **kwargs):

        super(WndBase, self).__init__()
        if title is None:
            self._title = self.TITLE
        else:
            self._title = title
        
        self._parent = None
        self._anchor = anchor
        self._autocreate = autocreate

        if parent:
            self.setParentObj(parent)

        if style:
            self._style = style
        else:
            self._style = self.STYLE

        self._pos = pos
        self._size = size
        
        self._wndId = 0
        self._relWndId = False
        
        self._userMsgs = None
        self._idPool = util.IdPool(*self.RANGE_CHILDID)
        self._childWnds = []
        self._wndId = wndid
        
        self.msgproc = MsgHandlers(self.MSGDEF)
        self.msglistener = Listeners(self.MSGDEF)

        self.keymap = KeyHandlers(self._keymap)
        self._currentKeys = []
        
        if context or self.CONTEXT:
            self._context = {}
        else:
            self._context = None
        
        self._roles = None
        role = role if role else self.ROLE
        if role:
            self.setRole(role)
        self._painters = []
        
        self._prepare(kwargs)
    
    def _getMsgMap(self):
        return self.msgproc.getHandlers()
        
    def _getListenerMap(self):
        return self.msglistener.getHandlers()

    def _setWndId(self):
        if self._wndId == 0:
            self._wndId = self.CHILDID
        
        if self._parent and not self._wndId and self._style.child:
            self._wndId = self._parent._allocChildId()
            self._relWndId = True
    
    def _prepare(self, kwargs):
        pass
        
    def _getWndClass(self):
        if self.DEFAULT_WNDCLASS:
            return self.DEFAULT_WNDCLASS
        else:
            hicon = hcursor = 0
            icon = self.WNDCLASS_ICON
            if icon:
                if isinstance(icon, Icon):
                    icon = icon.getHandle()
                    hicon = icon.handle
                elif isinstance(icon, int):
                    hicon = icon
                else:
                    raise ValueError("Invalid icon object:%s", repr(icon))
                
            cursor = self.WNDCLASS_CURSOR
            if cursor:
                cursor = cursor.getHandle()
                hcursor = cursor.handle
                
            color = self.WNDCLASS_BACKGROUNDCOLOR
            
            ret = self.__WNDCLASSES.get((self.WNDCLASS_STYLE.style, hicon, hcursor, color), None)
            if not ret:
                br = None
                if color is not None:
                    br = Brush(color=color)

                ret = self.WNDCLASS_STYLE.register(cursor, br, icon)
                self.__WNDCLASSES[(self.WNDCLASS_STYLE.style, hicon, hcursor, color)] = ret
            return ret

    def _setWndClass(self):
        self._wndClass = self._getWndClass()

    def _addChild(self, child):
        assert child not in self._childWnds
        self._childWnds.append(child)
        
        
    def _delChild(self, child):
        if child in self._childWnds:
            self._childWnds.remove(child)

    def _allocChildId(self):
        i = self._idPool.get()
        return i
    
    def _releaseChildId(self, id):
        self._idPool.release(id)

    
    def _onKeyTranslate(self, virtkey, keydata):
        kstate = _pymfclib.getKeyboardState()

        shift = ctrl = alt = False
        if kstate[KEY.SHIFT] & 0x80:
            shift = True
        if kstate[KEY.CONTROL] & 0x80:
            ctrl = True
        if kstate[KEY.MENU] & 0x80:
            alt = True
        
        kstate[KEY.CONTROL] = 0
        kstate[KEY.RCONTROL] = 0
        kstate[KEY.LCONTROL] = 0
        
        if virtkey >= ord(' '):
            scancode = (keydata >> 16) & 0xff
            ascii = _pymfclib.toAscii(virtkey, scancode, kstate, 0)
            if ascii:
                key = ascii
                if ascii > ' ':
                    shift = False
            else:
                key = [virtkey]
        else:
            key = [virtkey]

        for k in key:
            self._currentKeys.append((alt, ctrl, shift, k))
        
        keys = tuple(self._currentKeys)
        if keys in self._keymap:
            f = self._keymap[keys]
            if f:
                msg = _wndmsg(self, 0, 0, 0)
                msg.keys = keys
                self._currentKeys = []
                ret = f(msg)
                if (ret is not None) and not(isinstance(ret, int)):
                    raise RuntimeError(
                        repr(f) + " should return None or integer")
                return
        else:
            self._currentKeys = []
            actor = self.getActor('KEYBORADSHORTCUT')
            if actor:
                ret = actor.runKeyboardShortcut(alt, ctrl, shift, key)
                if ret:
                    return

        return True
    
    def allocUserMessage(self):
        if not self._userMsgs:
            self._userMsgs = util.IdPool(0x400, 0x7fff)
        return self._userMsgs.get()
        
    def setParentObj(self, parent):
        assert self._parent is None
        assert parent
        assert not self.getHwnd()

        self._parent = parent
        parent._addChild(self)

    def getParentObj(self):
        return self._parent
        
    def setRole(self, role):
        if isinstance(role, (unicode, str)):
            role = (role,)
        else:
            role = tuple(role)

        self._roles = role
        for wnd, context in self.iterContext():
            for role in self._roles:
                wnd.addActor(role, self)
            return
        else:
            raise RuntimeError("Context not found")

    def iterContext(self):
        w = self
        while w:
            context = w._context
            if context is not None:
                yield w, context
            w = w._parent

    def getContext(self):
        for wnd, context in self.iterContext():
            return wnd
            
    def addActor(self, role, actor):
        assert self._context is not None
        self._context[role] = actor

    def getActor(self, role):
        for wnd, context in self.iterContext():
            if role in context:
                return context[role]

    def __saveUpdateRect(self, msg):
        self._lastPaintRC = self.getUpdateRect(False)
        msg.handled = False
        msg.cont = True
        

    def __callOverWrite(self, msg):
        dc = ClientDC(self)
        dc.intersectClipRect(self._lastPaintRC)
        
        for f in self._painters:
            f(self, dc, self._lastPaintRC)

    def addOverWrite(self, f, head=False):
        if not self._painters:
            handlers = MsgHandlers(self.MSGDEF)
            handlers.PAINT = self.__saveUpdateRect
            self.msgproc.attach(handlers)

            listeners = Listeners(self.MSGDEF)
            listeners.PAINT = self.__callOverWrite
            self.msglistener.attach(listeners)
            
        if head:
            self._painters.insert(0, f)
        else:
            self._painters.append(f)
        
    def create(self):
        assert not self.getHwnd()

        self._setWndId()
        self._setWndClass()
        if callable(self._pos):
            pos = self._pos()
        else:
            pos= self._pos
        if callable(self._size):
            size = self._size()
        else:
            size = self._size
        
        if self._anchor:
            self._anchor.register(self)

        self._create(self._style, self._wndClass, self._title, 
            pos[0], pos[1], size[0], size[1], 
            self._parent, self._wndId)
        
        for child in self._childWnds:
            if child._autocreate and not child.getHwnd():
                child.create()
            
        return self
        
    def wndReleased(self):
        if self._parent:
            if self._relWndId:
                self._parent._releaseChildId(self._wndId)
            self._parent._delChild(self)

        if self._roles:
            for wnd, context in self.iterContext():
                for role in self._roles:
                    if context.get(role, None) is self:
                        del context[role]

        self._parent = None
        self._anchor = None
        self.msgproc.clear()
        self.msgproc = None
        self.msglistener.clear()
        self.msglistener = None
        self.keymap.clear()
        self.keymap = None

        super(WndBase, self).wndReleased()
        self._childWnds = None
        self._context = None
        self._painters = None
        
    def runKeyboardShortcut(self, alt, ctrl, shift, key):
        return False

    def getTopWnd(self):
        ret = self
        while ret._parent:
            ret = ret._parent
        return ret

    def getMainWnd(self):
        ret = self
        while (not app.isMainWindow(ret)) and ret._parent:
            ret = ret._parent
        return ret

    def centerWnd(self, centerOf=None):
        l, t, r, b = self.getClientRect()
        width, height = r-l, b-t

        if not centerOf:
            monitor = Monitor(self)
            l, t, r, b = monitor.rcwork
            pos = ((r-l)-width)/2+l, ((b-t)-height)/2+t
        else:
            rc = centerOf.getWindowRect()
            l, t, r, b = self.screenToClient(rc)
            pos = ((r-l)-width)/2+l, ((b-t)-height)/2+t
        self.setWindowPos(pos=pos)

    def enumChildWindows(self):
        for hwnd in self._enumChildWindows():
            obj = fromHandle(hwnd)
            if not obj:
                obj = Wnd.subclassWindow(hwnd)
            yield obj
            
    def callLater(self, elapse, f):
        def timer():
            p.unRegister()
            f()
            
        p = TimerProc(elapse, timer, self)
        
        
    @staticmethod
    def getFocus():
        return _pymfclib._getFocus()
#    getFocus = staticmethod(_getFocus)


class Wnd(WndBase, _pymfclib._wnd):
    def _prepare(self, kwargs):
        super(Wnd, self)._prepare(kwargs)

    def wndReleased(self):
        super(Wnd, self).wndReleased()

class Edit(WndBase, _pymfclib._edit):
    DEFAULT_WNDCLASS = u'EDIT'
    STYLE = EditStyle(visible=1, child=1, tabstop=1, clientedge=1, autohscroll=1)
    MSGDEF = _pymfclib._editmsg

class NumEdit(Edit):
    def _prepare(self, kwargs):
        super(NumEdit, self)._prepare(kwargs)
        self.period = kwargs.get('period', False)
        self.msgproc.CHAR = self.__onChar
        self.msgproc.UPDATE = self.__onUpdate

    def __onChar(self, msg):
        if getKeyState(KEY.MENU).down or getKeyState(KEY.CONTROL).down:
            msg.wnd.defWndProc(msg)
            return
            
        if self.period:
            if msg.char == '.':
                cur = self.getText()
                if u"." in cur:
                    return
                else:
                    msg.wnd.defWndProc(msg)
                    
        if ('0' <= msg.char <= '9') or (ord(msg.char) == KEY.BACKSPACE):
            msg.wnd.defWndProc(msg)
        
    def __onUpdate(self, msg):
        org = self.getText()
        if not self.period:
            s = u"".join(re.findall(ur"[0-9]+", org))
        else:
            s = u"".join(re.findall(ur"[0-9]*\.?[0-9]*", org))
            
        if s != org:
            self.setText(s)

class AutoSelectEdit(Edit):
    def _prepare(self, kwargs):
        super(AutoSelectEdit, self)._prepare(kwargs)
        self.msgproc.SETFOCUS = self.__onSetFocus
        self.msgproc.LBUTTONDOWN = self.__onLButtonDown
        
    def __onSetFocus(self, msg):
        ret = msg.wnd.defWndProc(msg)
        s = self.getText()
        if s:
            self.setSel((0, len(s)))
        return ret
        
    def __onLButtonDown(self, msg):
        if self.getFocus() is not self:
            self.setFocus()
        else:
            return msg.wnd.defWndProc(msg)



class Static(WndBase, _pymfclib._static):
    DEFAULT_WNDCLASS = u'STATIC'
    STYLE = StaticStyle(visible=1, child=1, notify=1)
    MSGDEF = _pymfclib._staticmsg

class _button(WndBase, _pymfclib._button):
    DEFAULT_WNDCLASS = u'BUTTON'
    MSGDEF = _pymfclib._buttonmsg

class Button(_button):
    STYLE = ButtonStyle(visible=1, child=1, tabstop=1, notify=1)

class DefButton(_button):
    STYLE = ButtonStyle(visible=1, child=1, tabstop=1, notify=1, defpushbutton=1)

class OkButton(_button):
    STYLE = ButtonStyle(visible=1, child=1, tabstop=1, notify=1, defpushbutton=1)
    CHILDID=IDOK

class CancelButton(_button):
    STYLE = ButtonStyle(visible=1, child=1, tabstop=1, notify=1)
    CHILDID=IDCANCEL

class RadioButton(_button):
    STYLE = ButtonStyle(visible=1, child=1, tabstop=1, notify=1, radiobutton=1)

    def _prepare(self, kwargs):
        super(RadioButton, self)._prepare(kwargs)
        self.__checked = kwargs.get('checked', False)
        if self.__checked:
            self.msglistener.CREATE = self.__oncreate
        
    def wndReleased(self):
        super(RadioButton, self).wndReleased()

    def __oncreate(self, msg):
        if self.__checked:
            self.setChecked(self.__checked)

class AutoRadioButton(RadioButton):
    STYLE = ButtonStyle(visible=1, child=1, tabstop=1, notify=1, autoradiobutton=1)
    
class CheckBox(_button):
    STYLE = ButtonStyle(visible=1, child=1, tabstop=1, notify=1, checkbox=1)
    def _prepare(self, kwargs):
        super(CheckBox, self)._prepare(kwargs)
        self.__checked = kwargs.get('checked', False)
        if self.__checked:
            self.msglistener.CREATE = self.__oncreate
        
    def wndReleased(self):
        super(CheckBox, self).wndReleased()

    def __oncreate(self, msg):
        if self.__checked:
            self.setChecked(self.__checked)

class AutoCheckBox(CheckBox):
    STYLE = ButtonStyle(visible=1, child=1, tabstop=1, notify=1, autocheckbox=1)

class Tristate(CheckBox):
    STYLE = ButtonStyle(visible=1, child=1, tabstop=1, notify=1, tristate=1)

class AutoTristate(CheckBox):
    STYLE = ButtonStyle(visible=1, child=1, tabstop=1, notify=1, auto3state=1)

class GroupBox(_button):
    STYLE = ButtonStyle(visible=1, child=1, notify=1, groupbox=1)


class ListBox(WndBase, _pymfclib._listbox):
    DEFAULT_WNDCLASS = u'LISTBOX'
    STYLE = ListBoxStyle(visible=1, child=1, tabstop=1, clientedge=1, notify=1, sort=1, vscroll=1)
    MSGDEF = _pymfclib._listboxmsg

    def _prepare(self, kwargs):
        super(ListBox, self)._prepare(kwargs)
        self.__inititems = kwargs.get("inititems", [])
        self.__initidx = kwargs.get("initidx", None)

        if self.__inititems:
            self.msglistener.CREATE = self.__onLBCreate

    def wndReleased(self):
        super(ListBox, self).wndReleased()

    def __onLBCreate(self, msg):
        for item in self.__inititems:
            self.insertItem(-1, item)
        if self.__initidx is not None:
            self.setCurSel(self.__initidx)
        

class _combobox(WndBase, _pymfclib._combobox):
    DEFAULT_WNDCLASS = u'COMBOBOX'
    MSGDEF = _pymfclib._comboboxmsg

    def _prepare(self, kwargs):
        super(_combobox, self)._prepare(kwargs)
        self.msglistener.CREATE = self.__onCBCreate
        self._editWnd = Edit()
        self._editWnd.msgproc.DESTROY = self.__onEditDestroy
        self.__inititems = kwargs.get("inititems", [])
        self.__initidx = kwargs.get("initidx", None)
        
    def wndReleased(self):
        super(_combobox, self).wndReleased()
        self._editWnd.wndReleased()
        self._editWnd = None

    def __onCBCreate(self, msg):
        #todo:
        #The Parts of a Windows Combo Box and How They Relate
        #Last reviewed: November 2, 1995
        #Article ID: Q65881

        hEdit = self._getDlgItem(0x3e9)
        if hEdit:
            self._editWnd._subclassWindow(hEdit)
        
        for item in self.__inititems:
            self.insertItem(-1, item)
        if self.__initidx is not None:
            self.setCurSel(self.__initidx)
            
    def __onEditDestroy(self, msg):
        ret = msg.wnd.defWndProc(msg)
        msg.wnd._unsubclassWindow()
        return ret

    def getEdit(self):
        return self._editWnd

    editWnd = property(getEdit)
    
class ComboBox(_combobox):
    STYLE = ComboBoxStyle(visible=1, child=1, tabstop=1, clientedge=1, simple=1, 
        autohscroll=1, vscroll=1)
    STYLE = ComboBoxStyle(visible=1, child=1, simple=1)

class DropDownCombo(_combobox):
    STYLE = ComboBoxStyle(visible=1, child=1, tabstop=1, clientedge=1, dropdown=1, 
        autohscroll=1, vscroll=1)

# Doesn't derive _combobox, since DropDownList doesn't have edit control.
class DropDownList(WndBase, _pymfclib._combobox):
    DEFAULT_WNDCLASS = u'COMBOBOX'
    MSGDEF = _pymfclib._comboboxmsg
    STYLE = ComboBoxStyle(visible=1, child=1, tabstop=1, clientedge=1, dropdownlist=1, 
        autohscroll=1, vscroll=1)

    def _prepare(self, kwargs):
        super(DropDownList, self)._prepare(kwargs)
        self.msglistener.CREATE = self.__onCBCreate
        self.__inititems = kwargs.get("inititems", [])
        self.__initidx = kwargs.get("initidx", None)
        
    def wndReleased(self):
        super(DropDownList, self).wndReleased()

    def __onCBCreate(self, msg):
        for item in self.__inititems:
            self.insertItem(-1, item)
        if self.__initidx is not None:
            self.setCurSel(self.__initidx)


class _scrollbar(WndBase, _pymfclib._scrollbar):
    DEFAULT_WNDCLASS = u'SCROLLBAR'
    STYLE = ScrollBarStyle(visible=1, child=1)

class VertScrollBar(_scrollbar):
    STYLE = ScrollBarStyle(_scrollbar.STYLE, vert=1)
    
class HorzScrollBar(_scrollbar):
    STYLE = ScrollBarStyle(_scrollbar.STYLE, horz=1)
    

class ImageList(_pymfclib._imagelist):
    dragShowNoLock = staticmethod(_pymfclib.pymfc_Imagelist_dragShowNoLock)

class TabCtrl(WndBase, _pymfclib._tabctrl):
    DEFAULT_WNDCLASS =u'SysTabControl32'
    STYLE = TabCtrlStyle(visible=1, child=1, tabstop=1, tabs=1, clipchildren=1)
    MSGDEF = _pymfclib._tabctrlmsg

class TreeView(WndBase, _pymfclib._treeview):
    DEFAULT_WNDCLASS = u'SysTreeView32'
    STYLE = TreeViewStyle(visible=1, child=1, tabstop=1, clientedge=1, hasbuttons=1, haslines=1, linesatroot=1)
    MSGDEF = _pymfclib._treeviewmsg

    def getEditControl(self, editcls=Edit):
        return self._getEditControl(editcls)

from _pymfclib import _tvitem as TreeItem

class ListView(WndBase, _pymfclib._listview):
    DEFAULT_WNDCLASS = u'SysListView32'
    STYLE = ListViewStyle(visible=1, child=1, tabstop=1, clientedge=1)
    MSGDEF = _pymfclib._listviewmsg

    def getEditControl(self, editcls=Edit):
        return self._getEditControl(editcls)

class DateTimeCtrl(WndBase, _pymfclib._datetimectrl):
    DEFAULT_WNDCLASS = u'SysDateTimePick32'
    STYLE = DateTimeCtrlStyle(visible=1, child=1, tabstop=1, clientedge=1)
    MSGDEF = _pymfclib._datetimectrlmsg


from _pymfclib import _lvitem as ListItem
from _pymfclib import _lvcolumn as ListColumn

CharFormat = _pymfclib._charFormat
ParaFormat = _pymfclib._paraFormat
class RichEdit(WndBase, _pymfclib._richedit):
    DEFAULT_WNDCLASS = u'RichEdit20W'
    STYLE = RichEditStyle(visible=1, child=1, tabstop=1, clientedge=1, 
        autohscroll=0, autovscroll=1, multiline=True)
    MSGDEF = _pymfclib._richeditmsg


class _Dialog(WndBase):
    STYLE = DlgStyle(sysmenu=1, caption=1, dlgframe=1, popup=1,
                modalframe=1, threedlook=1, visible=1)

    def __init__(self, title=u'', size=(0, 0), pos=(None, None), style=None, 
            parent=None, font=u'', fontSize=1, **kwargs):
        
        self._fontFace = font
        self._fontSize = fontSize

        super(_Dialog, self).__init__(
            title, size=size, pos=pos, style=style, parent=parent, **kwargs)

        if self.WNDCLASS_BACKGROUNDCOLOR is not None:
            self._bgbrush = Brush(color=self.WNDCLASS_BACKGROUNDCOLOR)
            self.msgproc.CTLCOLORDLG = self.__onCtlcolor
            
    def _prepare(self, kwargs):
        super(_Dialog, self)._prepare(kwargs)
        self.msglistener.INITDIALOG = self.__onInitDialog
        self.msgproc.COMMAND = self.__onCommand
        
    def dlu(self, pos=(), x=None, y=None):
        # Convert dialog unit into device unit

        # Q145994
        dc = DesktopDC()
        org = dc.selectObject(self.getFont())
        try:
            tm = dc.getTextMetrics()
            yunit = tm.tmHeight/8.0
            cx, cy = dc.getTextExtent(
               u"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
            xunit = ((cx / 26.0 + 1) / 2)/4.0

            if pos:
                x, y = pos
                return int(x*xunit), int(y*yunit)
            elif x is not None:
                return int(x*xunit)
            elif y is not None:
                return int(y*yunit)
            else:
                raise ValueError()
            
        finally:
            dc.selectObject(org)
            dc.release()

    def setDefaultValue(self, result):
        self._defaultValue = result

    def setResultValue(self, result):
        if not hasattr(self, '_defaultValue'):
            raise RuntimeError("self.setDedaultValue() should be called before you use self.setResultValue()")
        self._resultValue = result

    def getResultValue(self):
        if hasattr(self, '_resultValue'):
            return self._resultValue

    def doModal(self):
        ret = self._doModal(self._style.style, self._title or self.TITLE, 
            self._size[0], self._size[1], self._pos[0], self._pos[1], 
            self._fontFace, self._fontSize)
        
        if ret == -1:
            if hasattr(self, '_defaultValue'):
                return self._defaultValue

        if hasattr(self, '_resultValue'):
            return self._resultValue
        return ret

    def create(self):
        self._createDialog(self._parent, self._style.style, self._title, 
            self._size[0], self._size[1], self._pos[0], self._pos[1], 
            self._fontFace, self._fontSize)
        
    def __onInitDialog(self, msg):
        font = self.getFont()
        for c in self._childWnds:
            if not c.getHwnd():
                c.create()
                c.setFont(font)
        return True


    def __onCommand(self, msg):
        if msg.notifycode == 0:
            if msg.id == IDOK: # IDOK
                return self.onOk(msg)
            elif msg.id == IDCANCEL: # IDCANCEL
                return self.onCancel(msg)
        msg.wnd.defWndProc(msg)

    def __onCtlcolor(self, msg):
        dc = DC(hdc=msg.hdc)
        return self._bgbrush.getHandle().handle

    def onOk(self, msg):
        return msg.wnd.defWndProc(msg)

    def onCancel(self, msg):
        return msg.wnd.defWndProc(msg)

#class CancelButton(_button):
#    STYLE = ButtonStyle(visible=1, child=1, tabstop=1, notify=1)
#    CHILDID=2 # IDCANCEL


class Dialog(_Dialog, _pymfclib._dialog):
    pass

class FileDialog(_Dialog, _pymfclib._filedialog):
    def __init__(self, parent=None, title=u"", filename=u"", defext=u"", initdir=u"", 
            filter=(), filterindex=0, height=0, 
            readonly=False, overwriteprompt=False, hidereadonly=False,
            nochangedir=False, showhelp=False, novalidate=False, multiselect=False,
            extensiondifferent=False, pathmustexist=False, filemustexist=False,
            createprompt=False, shareaware=False, noreadonlyreturn=False, notestfilecreate=False,
            nonetworkbutton=False, nodereferencelinks=False,
            enableincludenotify=False, enablesizing=False, **kwargs):
        
        self._parent = parent
        self._title = title
        self._filename = filename
        self._defext = defext
        self._initdir = initdir
        self._filter = filter
        self._filterindex = filterindex
        self._height = height
        self._readonly = readonly
        self._overwriteprompt = overwriteprompt
        self._hidereadonly = hidereadonly
        self._nochangedir = nochangedir
        self._showhelp = showhelp
        self._novalidate = novalidate
        self._allowmultiselect = multiselect
        self._extensiondifferent = extensiondifferent
        self._pathmustexist = pathmustexist
        self._filemustexist = filemustexist
        self._createprompt = createprompt
        self._shareaware = shareaware
        self._noreadonlyreturn = noreadonlyreturn
        self._notestfilecreate = notestfilecreate
        self._nonetworkbutton = nonetworkbutton
        self._nodereferencelinks = nodereferencelinks
        self._enableincludenotify = enableincludenotify
        self._enablesizing = enablesizing

        super(FileDialog, self).__init__(title, (0,0), **kwargs)

    def _domodal(self, isopen):
#        filter = (('type-name', ('*.txt', '*.doc')),
#                  ('type-name2', ('*.txt2', '*.doc2')),)

        ff = [name + u'\0' + u';'.join(exts)+u'\0' 
                for name, exts in self._filter]
        sfilter = ''.join(ff)+u'\0\0'
        
        if not self._parent:
            parent = self.getFocus()
            parent = None
        else:
            parent = self._parent

        return _pymfclib._filedialog._doModal(self,
            isopen,
            parent=parent,
            title = self._title,
            filename = self._filename,
            defext = self._defext,
            initdir = self._initdir,
            filter = sfilter,
            filterindex = self._filterindex,
            height = self._height, 
            readonly = self._readonly,
            overwriteprompt = self._overwriteprompt,
            hidereadonly = self._hidereadonly,
            nochangedir = self._nochangedir,
            showhelp = self._showhelp,
            novalidate = self._novalidate,
            allowmultiselect = self._allowmultiselect,
            extensiondifferent = self._extensiondifferent,
            pathmustexist = self._pathmustexist,
            filemustexist = self._filemustexist,
            createprompt = self._createprompt,
            shareaware = self._shareaware,
            noreadonlyreturn = self._noreadonlyreturn,
            notestfilecreate = self._notestfilecreate,
            nonetworkbutton = self._nonetworkbutton,
            nodereferencelinks = self._nodereferencelinks,
            enableincludenotify = self._enableincludenotify,
            enablesizing = self._enablesizing,
        )

    def openDlg(self):
        return self._domodal(True)

    def saveDlg(self):
        return self._domodal(False)

class ColorDialog(_Dialog, _pymfclib._colordialog):
    def __init__(self, parent=None,
        color=None, anycolor=0, fullopen=0, preventfullopen=0, 
        showhelp=0, solidcolor=0, **kwargs):
        
        self._parent = parent
        self._color = color
        self._anycolor = anycolor
        self._fullopen = fullopen
        self._preventfullopen = preventfullopen
        self._showhelp = showhelp
        self._solidcolor = solidcolor
#        self._height = height
        
        super(ColorDialog, self).__init__(u'', (0,0), **kwargs)

    def doModal(self):
        if not self._parent:
            parent = None
        else:
            parent = self._parent

        return _pymfclib._colordialog._doModal(
            self,
            parent = self._parent,
            color = self._color,
            anycolor = self._anycolor,
            fullopen = self._fullopen,
            preventfullopen = self._preventfullopen,
            showhelp = self._showhelp,
            solidcolor = self._solidcolor,
            height = 0
        )

class FontDialog(_Dialog, _pymfclib._fontdialog):
    def __init__(self, parent=None, dc=None, logfont=None, color=0, stylename=u"",
        apply=0, both=0, ttonly=0, effects=0, fixedpitchonly=0,
        forcefontexist=0, nooemfonts=0, nofacesel=0, noscriptsel=0, 
        nostylesel=0, nosizesel=0, nosimulations=0, novectorfonts=0, 
        novertfonts=0, printerfonts=0, scalableonly=0, screenfonts=0,
        scriptsonly=0, selectscript=0, showhelp=0, wysiwyg=0, 
        limitsize=None, **kwargs):
        
        self._parent = parent
        self._dc = dc
        self._logfont = logfont
        self._color = color
        self._stylename = stylename
        self._apply = apply
        self._both = both
        self._ttonly = ttonly
        self._effects = effects
        self._fixedpitchonly = fixedpitchonly
        self._forcefontexist = forcefontexist
        self._nooemfonts = nooemfonts
        self._nofacesel = nofacesel
        self._noscriptsel = noscriptsel
        self._nostylesel = nostylesel
        self._nosizesel = nosizesel
        self._nosimulations = nosimulations
        self._novectorfonts = novectorfonts
        self._novertfonts = novertfonts
        self._printerfonts = printerfonts
        self._scalableonly = scalableonly
        self._screenfonts = screenfonts
        self._scriptsonly = scriptsonly
        self._selectscript = selectscript
        self._showhelp = showhelp
        self._wysiwyg = wysiwyg

        self._limitsize = limitsize

        super(FontDialog, self).__init__(u'', (0,0), **kwargs)

    def doModal(self):
        if not self._parent:
            parent = None
        else:
            parent = self._parent

        return _pymfclib._fontdialog._doModal(
            self,
            parent = self._parent,
            dc = self._dc,
            logfont = self._logfont,
            color = self._color,
            style = self._stylename,
            apply = self._apply,
            both = self._both,
            ttonly = self._ttonly,
            effects = self._effects,
            fixedpitchonly = self._fixedpitchonly,
            forcefontexist = self._forcefontexist,
            nooemfonts = self._nooemfonts,
            nofacesel = self._nofacesel,
            noscriptsel = self._noscriptsel,
            nostylesel = self._nostylesel,
            nosizesel = self._nosizesel,
            nosimulations = self._nosimulations,
            novectorfonts = self._novectorfonts,
            novertfonts = self._novertfonts,
            printerfonts = self._printerfonts,
            scalableonly = self._scalableonly,
            screenfonts = self._screenfonts,
            scriptsonly = self._scriptsonly,
            selectscript = self._selectscript,
            showhelp = self._showhelp,
            wysiwyg = self._wysiwyg,
            limitsize = self._limitsize
        )


class PrintDialog(_Dialog, _pymfclib._printdialog):
    def __init__(self, parent=None,
        devmode=None, devicename=None,
        allpages=1, selection=0, pagenums=0, noselection=1, nopagenums=1,
        collate=0, printtofile=0, printsetup=0, nowarning=0, returndc=0,
        returnic=0, returndefault=0, showhelp=0, enableprinthook=0,
        usedevmodecopies=1, disableprinttofile=0, hideprinttofile=1, 
        nonetworkbutton=0,
        frompage=0, topage=0, minpage=0, maxpage=0, ncopies=1, **kwargs):
        
        self._parent = parent
        self._devmode = devmode
        self._devicename = devicename
        self._allpages = allpages
        self._selection = selection
        self._pagenums = pagenums
        self._noselection = noselection
        self._nopagenums = nopagenums
        self._collate = collate
        self._printtofile = printtofile
        self._printsetup = printsetup
        self._nowarning = nowarning
        self._returndc = returndc
        self._returnic = returnic
        self._returndefault = returndefault
        self._showhelp = showhelp
        self._usedevmodecopies = usedevmodecopies
        self._disableprinttofile = disableprinttofile
        self._hideprinttofile = hideprinttofile
        self._nonetworkbutton = nonetworkbutton
        self._frompage = frompage
        self._topage = topage
        self._minpage = minpage
        self._maxpage = maxpage
        self._ncopies = ncopies
                
        super(PrintDialog, self).__init__(u'', (0,0), **kwargs)

    def doModal(self):
        if not self._parent:
            parent = None
        else:
            parent = self._parent

        return _pymfclib._printdialog._doModal(
            self,
            parent = self._parent,
            devmode = self._devmode, devicename = self._devicename, allpages = self._allpages, 
            selection = self._selection, pagenums = self._pagenums,
            noselection = self._noselection, nopagenums = self._nopagenums,
            collate = self._collate, printtofile = self._printtofile, 
            printsetup = self._printsetup, nowarning = self._nowarning, 
            returndc = self._returndc, returnic = self._returnic,
            returndefault = self._returndefault, showhelp = self._showhelp,
            usedevmodecopies = self._usedevmodecopies, 
            disableprinttofile = self._disableprinttofile, 
            hideprinttofile = self._hideprinttofile,
            nonetworkbutton = self._nonetworkbutton, frompage = self._frompage,
            topage = self._topage, minpage = self._minpage,
            maxpage = self._maxpage, ncopies = self._ncopies
        )


class PropertyPage(WndBase, _pymfclib._propertypage):
    STYLE = DlgStyle(visible=1, sysmenu=1, caption=1, popup=1, modalframe=1)

    def __init__(self, title, parent=None, style=None, size=(None, None), font=u'', fontSize=10, **kwargs):
        super(PropertyPage, self).__init__(title=title, parent=parent, style=style, size=size, font=font, fontSize=fontSize, **kwargs)

        self._fontFace = font
        self._fontSize = fontSize

        self._create(self._size[0], self._size[1], self._style, self._title, self._fontFace, self._fontSize)

    def _onInitDialog(self, msg):
        pass

class PropertySheet(WndBase, _pymfclib._propertysheet):
    STYLE = DlgStyle(visible=1, sysmenu=1, caption=1, popup=1, modalframe=1)

    def doModal(self):
        return self._doModal(self._parent, self._title, 0)


class _FrameBase(WndBase):
    def _prepare(self, kwargs):
        super(_FrameBase, self)._prepare(kwargs)
        self._menu = kwargs.get('menu', None)
        
#        self.msgproc.ERASEBKGND = self._onEraseBkGnd
        self.msgproc.COMMAND = self.__onCommand
        self.msgproc.INITMENU = self.__onInitMenu
        self.msgproc.INITMENUPOPUP = self.__onInitMenuPopup
        
        app.addMainWindow(self)
        
    def setMenu(self, menu):
        self._menu = menu
        if self.getHwnd():
            self._setMenu(menu.getHandle())

    def create(self):
        if self._menu:
            self._wndId = self._menu.getHandle()
        else:
            self._wndId = 0

        super(_FrameBase, self).create()
        return self
    
    def wndReleased(self):
        self._menu = None
        super(_FrameBase, self).wndReleased()

#    def _onEraseBkGnd(self, msg):
#        return 1

    def __onCommand(self, msg):
        if msg.notifycode < 1:
            # from menu or accel
            if self._onMenu(msg):
                return
        msg.wnd.defWndProc(msg)
            
    def __onInitMenu(self, msg):
        if self._menu:
            self._menu.onInitMenu(None, self)

    def __onInitMenuPopup(self, msg):
        if self._menu:
            popup = self._menu.menuMap.getPopup(msg.hmenupopup)
            if popup:
                parent = self._menu.menuMap.getPopupParent(popup)
                self._menu.onPopup(parent, self)
                msg.result = 0
                return

        return self.defWndProc(msg)

    def _onMenu(self, msg):
        if self._menu:
            item = self._menu.getItem(msg.id)
            if item:
                if item.command:
                    item.command(msg)
                return True


class FrameWnd(_FrameBase, _pymfclib._frame):
    STYLE = WndStyle(visible=1, overlappedwindow=1, windowedge=1)

class MDIFrame(_FrameBase, _pymfclib._mdiframe):
    STYLE = WndStyle(visible=1, overlappedwindow=1)

    def _onMenu(self, msg):
        child = self.getActive()
        if child:
            if child._onMenu(msg):
                return True
        return super(MDIFrame, self)._onMenu(msg)

class MDIChild(_FrameBase, _pymfclib._mdichild):
    STYLE = WndStyle(visible=1, child=1, overlappedwindow=1, windowedge=1)

    def _setWndId(self):
        pass

#    def create(self):
#        WndBase.create(self)
#        return self

class StatusBar(WndBase, _pymfclib._statusbar):
    def __init__(self, title=u"", parent=None, indicators=(), **kwargs):
        self._indicators = indicators[:]
        super(StatusBar, self).__init__(parent=parent, **kwargs)

    def create(self):
        if self._anchor:
            self._anchor.register(self)
        self._create(self._parent, self._indicators)
        return self

class ToolBar(WndBase, _pymfclib._toolbar):
    MSGDEF = _pymfclib._toolbarmsg
    def __init__(self, title=u"", parent=None, wndId=0, left=0, top=0, right=0, bottom=0, **kwargs):
        super(ToolBar, self).__init__(title=title, parent=parent, wndId=wndId, **kwargs)
        self._left = left
        self._top = top
        self._right = right
        self._bottom = bottom
        
    def create(self):
        self._create(self._parent, self._title, self._wndId, 
                self._left, self._top, self._right, self._bottom)
        return self

class ToolTip(WndBase, _pymfclib._tooltip):
    MSGDEF = _pymfclib._tooltipmsg
    STYLE = ToolTipStyle(popup=1, noprefix=1, alwaystip=1)

    def create(self):
        self._createToolTip(self._style, self._parent)

        # ToolTip should be destroyed when the parent dead.
        if self._parent:
            self._parent.msglistener.NCDESTROY = self.__onParentDestroy
        return self

    def __onParentDestroy(self, msg):
        if self.getHwnd():
            self.destroy()

class _WebCtrlEvent(object):
    def __init__(self):
        self.__dict__['_handlers'] = {}
        
    def __setattr__(self, key, item):
        self._handlers[key.lower()] = item

    def __getattr__(self, key):
        return self._handlers[key.lower()]

    def _getHandler(self, key):
        return self._handlers.get(key.lower(), None)

class WebCtrl(WndBase, _pymfclib._webctrl):
    STYLE = WebCtrlStyle(visible=1, child=1, tabstop=1, clientedge=0, border=0)
    MSGDEF = _pymfclib._webwndwmsg
    
    def _prepare(self, kwargs):
        self.events = _WebCtrlEvent()
        super(WebCtrl, self)._prepare(kwargs)

    def wndReleased(self):
        super(WebCtrl, self).wndReleased()
    
class HotKeyCtrl(WndBase, _pymfclib._hotkeyctrl):
    MSGDEF = _pymfclib._hotkeymsg
    DEFAULT_WNDCLASS = u'msctls_hotkey32'


def getDesktopWindow():
    ret = Wnd()
    ret._subclassWindow(_pymfclib._getDesktopWindow(), temp=True)
    return ret


def fromHandle(hwnd):
    return _pymfclib._fromHandle(hwnd)



class _IdleDispatcher(object):
    def __init__(self):
        self._funcs = []
        app.setIdleProc(self)
        
        self._idx = None

    def register(self, f):
        self._funcs.append(f)
    
    def unRegister(self, f):
        self._funcs.remove(f)

    def resume(self):
        self._idx = None
        
    def __call__(self):
        if self._idx is None:
            self._idx = 0
            
        if self._idx < len(self._funcs):
            f = self._funcs[self._idx]
            ret = f()
            if ret:
                return True
            else:
                self._idx += 1

        if self._idx >= len(self._funcs):
            self._idx = None
            return False
        else:
            return True



class IdleProc(object):
    DISPATCHER = None
    def __init__(self, f, wnd=None):
        self._f = f
        self._wnd = wnd

        if not IdleProc.DISPATCHER:
            IdleProc.DISPATCHER = _IdleDispatcher()
        IdleProc.DISPATCHER.register(self)
        
        if wnd:
            self._msglistener = Listeners(wnd.MSGDEF)
            self._msglistener.NCDESTROY = self.__onNCDestroy
            
            wnd.msglistener.attach(self._msglistener)
    
    def unRegister(self):
        IdleProc.DISPATCHER.unRegister(self)
        if self._wnd:
            self._wnd.msglistener.detach(self._msglistener)
            self._msglistener = None
            self._wnd = None

    def __call__(self):
        import time
        ret = self._f()  # returns 0 if task is finished, 1 otherwise
#        print time.clock(),self._f, ret
        return ret
        
    def __onNCDestroy(self, msg):
        self.unRegister()

class _TimerDispatcher(object):
    def __init__(self):
        self._funcs = {}
        app.setTimerProcs(self._funcs)

    def register(self, proc, elapse):
        timerId = _pymfclib_system.setTimer(elapse)
        self._funcs[timerId] = proc
        return timerId
        
    def unRegister(self, id):
        del self._funcs[id]
        _pymfclib_system.killTimer(0, id)
        

class TimerProc(object):
    DISPATCHER = None
    def __init__(self, elapse, f, wnd=None):
        self._elapse = elapse
        self._f = f
        self._wnd = wnd

        if not TimerProc.DISPATCHER:
            TimerProc.DISPATCHER = _TimerDispatcher()
        self._timerId = TimerProc.DISPATCHER.register(self, self._elapse)
        
        if wnd:
            self._msglistener = Listeners(wnd.MSGDEF)
            self._msglistener.NCDESTROY = self.__onNCDestroy
            
            wnd.msglistener.attach(self._msglistener)
            
    def unRegister(self):
        if self._timerId:
            TimerProc.DISPATCHER.unRegister(self._timerId)
            self._timerId = None
            if self._wnd:
                self._wnd.msglistener.detach(self._msglistener)
                self._msglistener = None
        self._f = self._wnd = None

    def __call__(self):
        self._f()

    def __onNCDestroy(self, msg):
        self.unRegister()





class DialogKeyHandler(object):
    def __init__(self, parent, initfocus=True, onok=None, oncancel=None):
        self._childHwnd = set()
        self._shortcuts = {}
        self._parent = parent
        self._onok = onok
        self._oncancel = oncancel
        self._initfocus = initfocus
        self._curfocus = None
        
        listener = Listeners(parent.MSGDEF)
        listener.PARENTNOTIFY = self.__onParentNotify
        listener.NCDESTROY = self.__onNCDestroy
        listener.ACTIVATE = self.__onActivate
        listener.SETFOCUS = self.__onSetFocus
        listener.LBUTTONDOWN = self.__onLBtnDown
        listener.COMMAND = self.__onCommand
        listener.KEYDOWN = self.__onControlKeydown

        self._parent.msglistener.attach(listener)

        if self._parent.getHwnd():
            self._collectChildren()

    RE_GETSHORTCUT = re.compile(ur"(?<!&)&([a-zA-Z0-9])")


    def _registerctrl(self, control):
        hwnd = control.getHwnd().handle
        if hwnd in self._childHwnd:
            return
        self._childHwnd.add(hwnd)

        listener = Listeners(control.MSGDEF)
        listener.KEYDOWN = self.__onControlKeydown
        listener.SYSKEYDOWN = self.__onControlSysKeydown
        listener.SETFOCUS = self.__onControlSetFocus
        listener.LBUTTONDOWN = self.__onControlLBtnDown
        listener.PARENTNOTIFY = self.__onParentNotify
        control.msglistener.attach(listener)
        
        msgproc = MsgHandlers(control.MSGDEF)
        msgproc.CHAR = self.__onControlChar
        
        control.msgproc.attach(msgproc)
        
        classname = control.getClassName().upper()
        if classname == u'STATIC':
            if control._parent is self._parent:
                label = control.getText()
                m = self.RE_GETSHORTCUT.search(label)
                if m:
                    shortcut = m.group(1)
                    self._shortcuts[shortcut.upper()] = control

        elif classname == u'COMBOBOX':
            f_edit = getattr(control, 'getEdit', None)
            if f_edit:
                edit = f_edit()
                if edit.getHwnd():
                    edit.msglistener.attach(listener)
                    edit.msgproc.attach(msgproc)
        
        

    def _collectChildren(self, top=None):
        
        if not top:
            top = self._parent

        for ctrl in top.enumChildWindows():
            self._registerctrl(ctrl)
            self._collectChildren(top=ctrl)

        if self._initfocus:
            next = self._parent.getNextDlgTabItem(0)
            if next and next.getHwnd():
                next.setFocus()
                self._initfocus = False

        
    def __onParentNotify(self, msg):
        if msg.get("created", None):
            control = msg.control
            if not control:
                control = Wnd.subclassWindow(msg.get("created"))

            self._collectChildren()
            

        elif msg.get("destroyed", None):
            hwnd = msg.destroyed
            if hwnd in self._childHwnd:
                self._childHwnd.remove(hwnd)
        return

    def __onActivate(self, msg):
        self.__onSetFocus(None)
        
    def __onNCDestroy(self, msg):
        self._childHwnd = None
        self._shortcuts = None
        self._parent = None
        self._onok = None
        self._oncancel = None
        self._curfocus = None
        
    def __onSetFocus(self, msg):
        if self._curfocus and self._curfocus.getHwnd():
            self._curfocus.setFocus()
        else:
            next = self._parent.getNextDlgTabItem(0)
            if next and next.getHwnd():
                self._initfocus = False
                next.setFocus()


    def __onLBtnDown(self, msg):
        if self._curfocus and self._curfocus.getHwnd():
            self._curfocus.setFocus()
        else:
            self._parent.setFocus()
            
    def __onCommand(self, msg):
        if msg.notifycode == 0 or msg.notifycode == 1:
            if msg.id == IDOK:
                self.__onCmdOk()
            elif msg.id == IDCANCEL:
                self.__onCmdCancel()

    def __onControlKeydown(self, msg):
        if msg.key == 9 and not getKeyState(KEY.CONTROL).down: # tab key pressed
            prev = getKeyState(KEY.SHIFT).down
            next = self._parent.getNextDlgTabItem(msg.wnd, prev)
            if next and next.getHwnd():
                next.setFocus()
        elif msg.key == 0x0d: # enter
            if msg.wnd.getClassName().upper() == u'EDIT':
                if msg.wnd.getWindowStyle().wantreturn:
                    return
            if msg.wnd.getClassName().upper() == u'BUTTON':
                wmcommand, bnclicked = msg.wnd.MSGDEF['CLICKED']
                self._parent.sendMessage(wmcommand, (msg.wnd.getDlgCtrlID(), bnclicked), msg.wnd.getHwnd())
                return
            self.__onCmdOk()
        elif msg.key == 0x1b and self._oncancel: # escape
            self.__onCmdCancel()

    def __onControlSysKeydown(self, msg):
        key = chr(msg.key).upper()
        ctl = self._shortcuts.get(key, None)
        if ctl and ctl.getHwnd():
            next = self._parent.getNextDlgTabItem(ctl)
            if next and next.getHwnd():
                next.setFocus()

    def __onControlSetFocus(self, msg):
        self._curfocus = msg.wnd

    def __onControlLBtnDown(self, msg):
        focused = self._parent.getFocus()
        if msg.wnd.getClassName().upper() == u'STATIC':
            next = self._parent.setFocus()
            

    def __onControlChar(self, msg):
        if msg.char == u'\r':
            wantreturn = getattr(msg.wnd.getWindowStyle(), 'wantreturn', None)
            if wantreturn:
                msg.handled = False
            return 0

        if msg.char not in u'\t':
            msg.handled = False
            return

        return 0
        
    def __onCmdOk(self):
        if self._onok:
            self._onok()
    
    def __onCmdCancel(self):
        if self._oncancel:
            self._oncancel()

