cdef extern from "pymwnd.h":
    TCHAR *pymRegisterWndClass(unsigned long, HANDLE, HANDLE, HANDLE)

    # class styles
    int CS_VREDRAW
    int CS_HREDRAW
    int CS_DBLCLKS
    int CS_OWNDC
    int CS_CLASSDC
    int CS_PARENTDC
    int CS_NOCLOSE
    int CS_SAVEBITS
    int CS_BYTEALIGNCLIENT
    int CS_BYTEALIGNWINDOW
    int CS_GLOBALCLASS

cdef class WndClassStyle:
    cdef public unsigned int style
    
    def __init__(self, *args, **kwargs):
        self.style = 0
        
        l = len(args)
        if l == 0:
            pass
        elif l == 1:
            style = args[0]
            if isinstance(style, WndClassStyle):
                self.style = style.style
            else:
                raise TypeError("Invalid class style")
        else:
            raise TypeError("Invalid class style")
            
        for name, value in kwargs.items():
            setattr(self, name, value)
        
        
    cdef __set_style(self, int mask, int flag):
        if flag:
            self.style = self.style | mask
        else:
            self.style = self.style & ~mask

    def register(self, cursor=None, brush=None, icon=None):
        cdef unsigned long style
        cdef HANDLE lcursor, lbrush, licon
        cdef TCHAR *ret
        
        lcursor = NULL
        lbrush = NULL
        licon = NULL
        
        if not cursor:
            lcursor = NULL
        elif PyMFCHandle_IsHandle(cursor):
            lcursor=PyMFCHandle_AsHandle(cursor)
        else:
            lcursor = PyMFCHandle_AsHandle(cursor.getHandle())

        if not brush:
            lbrush = NULL
        elif PyMFCHandle_IsHandle(brush):
            lbrush = PyMFCHandle_AsHandle(brush)
        else:
            lbrush = PyMFCHandle_AsHandle(brush.detach())

        if not icon:
            licon=NULL
        elif isinstance(icon, int):
            licon = MAKEINTRESOURCE(icon)
        elif PyMFCHandle_IsHandle(icon):
            licon = PyMFCHandle_AsHandle(icon)
        else:
            licon = PyMFCHandle_AsHandle(icon.detach())
        
        style = self.style
        ret = pymRegisterWndClass(style, lcursor, lbrush, licon)
        return _fromWideChar(ret)
        
        
    property vredraw:
        def __get__(self): 
            return (self.style & CS_VREDRAW) != 0
        def __set__(self, int value): 
            self.__set_style(CS_VREDRAW, value)


    property hredraw:
        def __get__(self): 
            return (self.style & CS_HREDRAW) != 0
        def __set__(self, int value): 
            self.__set_style(CS_HREDRAW, value)


    property dblclks:
        def __get__(self): 
            return (self.style & CS_DBLCLKS) != 0
        def __set__(self, int value): 
            self.__set_style(CS_DBLCLKS, value)


    property owndc:
        def __get__(self): 
            return (self.style & CS_OWNDC) != 0
        def __set__(self, int value): 
            self.__set_style(CS_OWNDC, value)


    property classdc:
        def __get__(self): 
            return (self.style & CS_CLASSDC) != 0
        def __set__(self, int value): 
            self.__set_style(CS_CLASSDC, value)


    property parentdc:
        def __get__(self): 
            return (self.style & CS_PARENTDC) != 0
        def __set__(self, int value): 
            self.__set_style(CS_PARENTDC, value)


    property noclose:
        def __get__(self): 
            return (self.style & CS_NOCLOSE) != 0
        def __set__(self, int value): 
            self.__set_style(CS_NOCLOSE, value)


    property savebits:
        def __get__(self): 
            return (self.style & CS_SAVEBITS) != 0
        def __set__(self, int value): 
            self.__set_style(CS_SAVEBITS, value)


    property bytealignclient:
        def __get__(self): 
            return (self.style & CS_BYTEALIGNCLIENT) != 0
        def __set__(self, int value): 
            self.__set_style(CS_BYTEALIGNCLIENT, value)


    property bytealignwindow:
        def __get__(self): 
            return (self.style & CS_BYTEALIGNWINDOW) != 0
        def __set__(self, int value): 
            self.__set_style(CS_BYTEALIGNWINDOW, value)


    property globalclass:
        def __get__(self): 
            return (self.style & CS_GLOBALCLASS) != 0
        def __set__(self, int value): 
            self.__set_style(CS_GLOBALCLASS, value)


