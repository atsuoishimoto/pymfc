
ctypedef class StyleColor:
    cdef PymStyleColor _color
    
    def __init__(self, **kwargs):
        self.text = self.lf = self.tab = self.fullspc = (0, 0xffffff)
        self.text_sel = self.lf_sel = self.tab_sel = self.fullspc_sel = (0xffffff, 0)

        for name, value in kwargs.items():
            setattr(self, name, value)

    def getBuffer(self):
        return PyMFCPtr_FromVoidPtr(&self._color)
        
    property text:
        def __get__(self):
            return [self._color.text.fore, self._color.text.back]
        def __set__(self, value):
            self._color.text.fore = value[0]
            self._color.text.back = value[1]
    
    property text_sel:
        def __get__(self):
            return [self._color.text_sel.fore, self._color.text_sel.back]
        def __set__(self, value):
            self._color.text_sel.fore = value[0]
            self._color.text_sel.back = value[1]
    
    property lf:
        def __get__(self):
            return [self._color.lf.fore, self._color.lf.back]
        def __set__(self, value):
            self._color.lf.fore = value[0]
            self._color.lf.back = value[1]
    
    property lf_sel:
        def __get__(self):
            return [self._color.lf_sel.fore, self._color.lf_sel.back]
        def __set__(self, value):
            self._color.lf_sel.fore = value[0]
            self._color.lf_sel.back = value[1]
    
    property tab:
        def __get__(self):
            return [self._color.tab.fore, self._color.tab.back]
        def __set__(self, value):
            self._color.tab.fore = value[0]
            self._color.tab.back = value[1]
    
    property tab_sel:
        def __get__(self):
            return [self._color.tab_sel.fore, self._color.tab_sel.back]
        def __set__(self, value):
            self._color.tab_sel.fore = value[0]
            self._color.tab_sel.back = value[1]

    property fullspc:
        def __get__(self):
            return [self._color.fullspc.fore, self._color.fullspc.back]
        def __set__(self, value):
            self._color.fullspc.fore = value[0]
            self._color.fullspc.back = value[1]

    property fullspc_sel:
        def __get__(self):
            return [self._color.fullspc_sel.fore, self._color.fullspc_sel.back]
        def __set__(self, value):
            self._color.fullspc_sel.fore = value[0]
            self._color.fullspc_sel.back = value[1]

cdef class TextStyle:
    cdef public object latinFont
    cdef public object nonLatinFont
    cdef public object color

    def __init__(self, latinFont, nonLatinFont, color):
        self.latinFont = latinFont
        self.nonLatinFont = nonLatinFont
        self.color = color

cdef class ScreenConf:
    cdef PymScreenConf _conf
    cdef object _nowrapchars_top, _nowrapchars_end, _nowrapheaders, _itemize
    cdef public object styles
    cdef public object linenostyle
    
    def __init__(self, styles,
            int linegap, int tab, int wrap, int maxcol,
            int wordwrap, int indentwrap, int forcewrap, 
            nowrapchars, int showtab, int showlf, int showfullspc,
            unsigned long bgcolor, object linenostyle,
            nowrapheaders, itemize):


        if len(styles) == 0:
            raise ValueError("empty styles")

        self.styles = styles
        self.linegap = linegap
        self.tab = tab
        self.wrap = wrap
        self.maxcol = maxcol
        self.wordwrap = wordwrap
        self.indentwrap = indentwrap
        self.forcewrap = forcewrap
        self.showtab = showtab
        self.showlf = showlf
        self.showfullspc = showfullspc
        self.nowrapchars = nowrapchars
        self.bgcolor = bgcolor
        self.linenostyle = linenostyle
        self.nowrapheaders = nowrapheaders
        self.itemize = itemize
        
    def getScreenConf(self):
        return PyMFCPtr_FromVoidPtr(&(self._conf))
        
    property linegap:
        def __get__(self):
            return self._conf.linegap
        def __set__(self, value):
            self._conf.linegap = value

    property tab:
        def __get__(self):
            return self._conf.tab
        def __set__(self, value):
            self._conf.tab = value

    property wrap:
        def __get__(self):
            return self._conf.wrap
        def __set__(self, value):
            self._conf.wrap = value

    property maxcol:
        def __get__(self):
            return self._conf.maxcol
        def __set__(self, value):
            self._conf.maxcol = value

    property wordwrap:
        def __get__(self):
            return self._conf.wordwrap
        def __set__(self, value):
            self._conf.wordwrap = value

    property indentwrap:
        def __get__(self):
            return self._conf.indentwrap
        def __set__(self, value):
            self._conf.indentwrap = value

    property forcewrap:
        def __get__(self):
            return self._conf.forcewrap
        def __set__(self, value):
            self._conf.forcewrap = value

    property showtab:
        def __get__(self):
            return self._conf.showtab
        def __set__(self, value):
            self._conf.showtab = value

    property showlf:
        def __get__(self):
            return self._conf.showlf
        def __set__(self, value):
            self._conf.showlf = value

    property showfullspc:
        def __get__(self):
            return self._conf.showfullspc
        def __set__(self, value):
            self._conf.showfullspc = value

    property nowrapchars:
        def __get__(self):
            return (self._nowrapchars_top, self._nowrapchars_end)

        def __set__(self, value):
            if not isinstance(value[0], unicode):
                raise TypeError("nowrapchars is not unicode")

            if not isinstance(value[1], unicode):
                raise TypeError("nowrapchars is not unicode")

            self._nowrapchars_top = value[0]
            self._nowrapchars_end = value[1]
            self._conf.nowrapchars_top = PyUnicode_AsUnicode(self._nowrapchars_top)
            self._conf.nowrapchars_end = PyUnicode_AsUnicode(self._nowrapchars_end)

    property bgcolor:
        def __get__(self):
            return self._conf.bgcolor
        def __set__(self, value):
            self._conf.bgcolor = value

    property nowrapheaders:
        def __get__(self):
            return self._nowrapheaders

        def __set__(self, value):
            if not isinstance(value, unicode):
                raise TypeError("nowrapheaders is not unicode")

            self._nowrapheaders = value
            self._conf.nowrapheaders = PyUnicode_AsUnicode(self._nowrapheaders)

    property itemize:
        def __get__(self):
            return self._itemize

        def __set__(self, value):
            if not isinstance(value, unicode):
                raise TypeError("itemize is not unicode")

            self._itemize = value
            self._conf.itemize = PyUnicode_AsUnicode(self._itemize)


