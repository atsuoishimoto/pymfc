cdef extern from "pymwnd.h":

    # Window styles
    int WS_BORDER, WS_CAPTION, WS_CHILD, WS_CHILDWINDOW, WS_CLIPCHILDREN
    int WS_CLIPSIBLINGS, WS_DISABLED, WS_DLGFRAME, WS_GROUP, WS_HSCROLL
    int WS_MAXIMIZE, WS_MAXIMIZEBOX, WS_MINIMIZE, WS_MINIMIZEBOX, WS_OVERLAPPED
    int WS_OVERLAPPEDWINDOW, WS_POPUP, WS_POPUPWINDOW, WS_SYSMENU, WS_TABSTOP
    int WS_THICKFRAME, WS_VISIBLE, WS_VSCROLL

    int WS_EX_ACCEPTFILES, WS_EX_APPWINDOW, WS_EX_CLIENTEDGE, WS_EX_CONTEXTHELP
    int WS_EX_CONTROLPARENT, WS_EX_DLGMODALFRAME, WS_EX_LEFT, WS_EX_LEFTSCROLLBAR
    int WS_EX_LTRREADING, WS_EX_MDICHILD, WS_EX_NOPARENTNOTIFY
    int WS_EX_OVERLAPPEDWINDOW, WS_EX_PALETTEWINDOW, WS_EX_RIGHT
    int WS_EX_RIGHTSCROLLBAR, WS_EX_RTLREADING, WS_EX_STATICEDGE, WS_EX_TOOLWINDOW
    int WS_EX_TOPMOST, WS_EX_TRANSPARENT, WS_EX_WINDOWEDGE
    int WS_EX_LAYERED, WS_EX_LAYOUTRTL, WS_EX_NOACTIVATE, WS_EX_NOINHERITLAYOUT

cdef __init_styledict():
     return {
        "border":WS_BORDER,
        "caption":WS_CAPTION,
        "child":WS_CHILD,
        "childwindow":WS_CHILDWINDOW,
        "clipchildren":WS_CLIPCHILDREN,
        "clipsiblings":WS_CLIPSIBLINGS,
        "disabled":WS_DISABLED,
        "dlgframe":WS_DLGFRAME,
        "group":WS_GROUP,
        "hscroll":WS_HSCROLL,
        "maximize":WS_MAXIMIZE,
        "maximizebox":WS_MAXIMIZEBOX,
        "minimize":WS_MINIMIZE,
        "minimizebox":WS_MINIMIZEBOX,
        "overlapped":WS_OVERLAPPED,
        "overlappedwindow":WS_OVERLAPPEDWINDOW,
        "popup":WS_POPUP,
        "popupwindow":WS_POPUPWINDOW,
        "sysmenu":WS_SYSMENU,
        "tabstop":WS_TABSTOP,
        "thickframe":WS_THICKFRAME,
        "visible":WS_VISIBLE,
        "vscroll":WS_VSCROLL,
    }
_std_styles = __init_styledict()

cdef __init_exstyledict():
    return {
        "acceptfiles":WS_EX_ACCEPTFILES,
        "appwindow":WS_EX_APPWINDOW,
        "clientedge":WS_EX_CLIENTEDGE,
        "contexthelp":WS_EX_CONTEXTHELP,
        "controlparent":WS_EX_CONTROLPARENT,
        "dlgmodalframe":WS_EX_DLGMODALFRAME,
        "left":WS_EX_LEFT,
        "leftscrollbar":WS_EX_LEFTSCROLLBAR,
        "ltrreading":WS_EX_LTRREADING,
        "mdichild":WS_EX_MDICHILD,
        "noparentnotify":WS_EX_NOPARENTNOTIFY,
        "ex_overlappedwindow":WS_EX_OVERLAPPEDWINDOW,
        "palettewindow":WS_EX_PALETTEWINDOW,
        "right":WS_EX_RIGHT,
        "rightscrollbar":WS_EX_RIGHTSCROLLBAR,
        "rtlreading":WS_EX_RTLREADING,
        "staticedge":WS_EX_STATICEDGE,
        "toolwindow":WS_EX_TOOLWINDOW,
        "topmost":WS_EX_TOPMOST,
        "transparent":WS_EX_TRANSPARENT,
        "windowedge":WS_EX_WINDOWEDGE,
        "layered":WS_EX_LAYERED,
        "layoutrtl":WS_EX_LAYOUTRTL,
        "noactivate":WS_EX_NOACTIVATE,
        "noinheritlayout":WS_EX_NOINHERITLAYOUT,
    }
_std_ex_styles = __init_exstyledict()

cdef class WndStyle:
    # c attrs are defined in _pymfclib.pxd.
    def __init__(self, *args, **kwargs):
        self.style = self.exStyle = 0
        
        self._styles = _std_styles
        self._exStyles = _std_ex_styles
        self._initTable()

        l = len(args)
        if l == 0:     # ex: style = WndStyle()
            pass
        elif l == 1:   # ex: style = WndStyle(currentStyle)
            style = args[0]
            if isinstance(style, WndStyle):
                self._copyfrom(style)
            else:
                raise TypeError("Invalid style")
        else: # positional params is not supported.
            raise TypeError("Invalid style")
            
        for name, value in kwargs.items():
            setattr(self, name, value)

    def _copyfrom(self, WndStyle _from):
        self.style = _from.style
        self.exStyle = _from.exStyle
        
    def _initTable(self):
        pass

    def __getattr__(self, name):
        v = self._styles.get(name)
        if v is not None:
            return (self.style & v) != 0

        v = self._exStyles.get(name)
        if v is not None:
            return (self.exStyle & v) != 0

        raise AttributeError(name)

    def __setattr__(self, name, value):
        v = self._styles.get(name)
        if v is not None:
            if value:
                self.style = self.style | v
            else:
                self.style = self.style & ~v
        else:
            v = self._exStyles.get(name)
            if v is not None:
                if value:
                    self.exStyle = self.exStyle | v
                else:
                    self.exStyle = self.exStyle & ~v
            else:
#                if name == 'style':
#                    self.style = value
#                elif name == 'exStyle':
#                    self.exStyle = value
#                else:
                raise AttributeError(name)

    def __call__(self, **kwargs):
        ret = self.__class__(self, **kwargs)
        return ret
    
    def dup(self):
        cdef WndStyle ret
        ret = self.__class__()
        ret.style = self.style
        ret.exStyle = self.exStyle
        return ret