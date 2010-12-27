import _pymfclib
import pymfc.wnd


class TrayNotify(_pymfclib._TrayNotify):
    def __init__(self, wnd, icon=None, tip=None):
        notifyid = wnd.allocUserMessage()
        super(TrayNotify, self).__init__(notifyid, icon=icon, tip=tip)

        self._icon = icon
        listener = pymfc.wnd.Listeners(wnd.MSGDEF)
        listener.DESTROY = self._onWndDestroy
        listener.CREATE = self._onWndCreate
        recreate = pymfc.wnd.registerWindowMessage(u"TaskbarCreated")
        listener.setMessage(recreate, self._onWndCreate)
        
        wnd.msglistener.attach(listener, owner=wnd)
        
        
        handler = pymfc.wnd.MsgHandlers(wnd.MSGDEF)
        handler.setMessage(notifyid, self._onNotify)
        
        wnd.msgproc.attach(handler, owner=wnd)
        if wnd.getHwnd():
            self.addIcon(wnd)
    
    def _onWndCreate(self, msg):
        self.addIcon(msg.wnd)
    
    def _onWndDestroy(self, msg):
        self.deleteIcon()

    def _onNotify(self, msg):
        if msg.lparam == 0x0200: # WM_MOUSEMOVE
            self.onMouseMove(msg)
        elif msg.lparam == 0x0201: # WM_LBUTTONDOWN
            self.onLBtnDown(msg)
        elif msg.lparam == 0x0202: # WM_LBUTTONUP
            self.onLBtnUp(msg)
        elif msg.lparam == 0x0203: # WM_LBUTTONDBLCLK
            self.onLBtnDblClk(msg)
        elif msg.lparam == 0x0204: # WM_RBUTTONDOWN
            self.onRBtnDown(msg)
        elif msg.lparam == 0x0205: # WM_RBUTTONDOWN
            self.onRBtnUp(msg)
        elif msg.lparam == 0x0206: # WM_RBUTTONDBLCLK
            self.onRBtnDblClk(msg)
        return 0
        
    def onMouseMove(self, msg):
        pass
        
    def onLBtnDown(self, msg):
        pass
    
    def onLBtnUp(self, msg):
        pass
    
    def onLBtnDblClk(self, msg):
        pass

    def onRBtnDown(self, msg):
        pass

    def onRBtnUp(self, msg):
        pass
    
    def onRBtnDblClk(self, msg):
        pass

