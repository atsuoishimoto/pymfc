#cdef extern from "pymwnd.h":
#    int VK_LBUTTON, VK_RBUTTON, VK_CANCEL, VK_MBUTTON, VK_BACK, VK_TAB
#    int VK_CLEAR, VK_RETURN, VK_SHIFT, VK_CONTROL, VK_MENU, VK_PAUSE
#    int VK_CAPITAL, VK_KANA, VK_HANGUL, VK_JUNJA, VK_FINAL, VK_HANJA
#    int VK_KANJI, VK_ESCAPE, VK_CONVERT, VK_NONCONVERT, VK_ACCEPT
#    int VK_MODECHANGE, VK_SPACE, VK_PRIOR, VK_NEXT, VK_END, VK_HOME, VK_LEFT
#    int VK_UP, VK_RIGHT, VK_DOWN, VK_SELECT, VK_PRINT, VK_EXECUTE, VK_SNAPSHOT
#    int VK_INSERT, VK_DELETE, VK_HELP, VK_LWIN, VK_RWIN, VK_APPS, VK_NUMPAD0
#    int VK_NUMPAD1, VK_NUMPAD2, VK_NUMPAD3, VK_NUMPAD4, VK_NUMPAD5, VK_NUMPAD6
#    int VK_NUMPAD7, VK_NUMPAD8, VK_NUMPAD9, VK_MULTIPLY, VK_ADD, VK_SEPARATOR
#    int VK_SUBTRACT, VK_DECIMAL, VK_DIVIDE, VK_F1, VK_F2, VK_F3, VK_F4, VK_F5
#    int VK_F6, VK_F7, VK_F8, VK_F9, VK_F10, VK_F11, VK_F12, VK_F13, VK_F14
#    int VK_F15, VK_F16, VK_F17, VK_F18, VK_F19, VK_F20, VK_F21, VK_F22, VK_F23
#    int VK_F24, VK_NUMLOCK, VK_SCROLL, VK_PROCESSKEY, VK_ATTN, VK_CRSEL, VK_EXSEL
#    int VK_EREOF, VK_PLAY, VK_ZOOM, VK_NONAME, VK_PA1, VK_OEM_CLEAR
#
#KEY = __CONSTDEF()
#
#cdef __init_keydef(object key):
#    key.LBUTTON = VK_LBUTTON
#    key.RBUTTON = VK_RBUTTON
#    key.CANCEL = VK_CANCEL
#    key.MBUTTON = VK_MBUTTON
#    key.BACKSPACE = VK_BACK
#    key.TAB = VK_TAB
#    key.CLEAR = VK_CLEAR
#    key.ENTER = VK_RETURN
#    key.SHIFT = VK_SHIFT
#    key.CONTROL = VK_CONTROL
#    key.MENU = VK_MENU
#    key.PAUSE = VK_PAUSE
#    key.CAPITAL = VK_CAPITAL
#    key.KANA = VK_KANA
#    key.HANGUL = VK_HANGUL
#    key.JUNJA = VK_JUNJA
#    key.FINAL = VK_FINAL
#    key.HANJA = VK_HANJA
#    key.KANJI = VK_KANJI
#    key.ESC = VK_ESCAPE
#    key.CONVERT = VK_CONVERT
#    key.NONCONVERT = VK_NONCONVERT
#    key.ACCEPT = VK_ACCEPT
#    key.MODECHANGE = VK_MODECHANGE
#    key.SPACE = VK_SPACE
#    key.PGUP = VK_PRIOR
#    key.PGDN = VK_NEXT
#    key.END = VK_END
#    key.HOME = VK_HOME
#    key.LEFT = VK_LEFT
#    key.UP = VK_UP
#    key.RIGHT = VK_RIGHT
#    key.DOWN = VK_DOWN
#    key.SELECT = VK_SELECT
#    key.PRINT = VK_PRINT
#    key.EXECUTE = VK_EXECUTE
#    key.SNAPSHOT = VK_SNAPSHOT
#    key.INSERT = VK_INSERT
#    key.DELETE = VK_DELETE
#    key.HELP = VK_HELP
#    key.LWIN = VK_LWIN
#    key.RWIN = VK_RWIN
#    key.APPS = VK_APPS
#    key.NUMPAD0 = VK_NUMPAD0
#    key.NUMPAD1 = VK_NUMPAD1
#    key.NUMPAD2 = VK_NUMPAD2
#    key.NUMPAD3 = VK_NUMPAD3
#    key.NUMPAD4 = VK_NUMPAD4
#    key.NUMPAD5 = VK_NUMPAD5
#    key.NUMPAD6 = VK_NUMPAD6
#    key.NUMPAD7 = VK_NUMPAD7
#    key.NUMPAD8 = VK_NUMPAD8
#    key.NUMPAD9 = VK_NUMPAD9
#    key.MULTIPLY = VK_MULTIPLY
#    key.ADD = VK_ADD
#    key.SEPARATOR = VK_SEPARATOR
#    key.SUBTRACT = VK_SUBTRACT
#    key.DECIMAL = VK_DECIMAL
#    key.DIVIDE = VK_DIVIDE
#    key.F1 = VK_F1
#    key.F2 = VK_F2
#    key.F3 = VK_F3
#    key.F4 = VK_F4
#    key.F5 = VK_F5
#    key.F6 = VK_F6
#    key.F7 = VK_F7
#    key.F8 = VK_F8
#    key.F9 = VK_F9
#    key.F10 = VK_F10
#    key.F11 = VK_F11
#    key.F12 = VK_F12
#    key.F13 = VK_F13
#    key.F14 = VK_F14
#    key.F15 = VK_F15
#    key.F16 = VK_F16
#    key.F17 = VK_F17
#    key.F18 = VK_F18
#    key.F19 = VK_F19
#    key.F20 = VK_F20
#    key.F21 = VK_F21
#    key.F22 = VK_F22
#    key.F23 = VK_F23
#    key.F24 = VK_F24
#    key.NUMLOCK = VK_NUMLOCK
#    key.SCROLL = VK_SCROLL
#    key.PROCESSKEY = VK_PROCESSKEY
#    key.ATTN = VK_ATTN
#    key.CRSEL = VK_CRSEL
#    key.EXSEL = VK_EXSEL
#    key.EREOF = VK_EREOF
#    key.PLAY = VK_PLAY
#    key.ZOOM = VK_ZOOM
#    key.NONAME = VK_NONAME
#    key.PA1 = VK_PA1
#    key.OEM_CLEAR = VK_OEM_CLEAR
#
#__init_keydef(KEY)



cdef void __init_keydef(KEY):
    for name, value in _keydict.items():
        setattr(KEY, name, value)

KEY = __CONSTDEF()
__init_keydef(KEY)

