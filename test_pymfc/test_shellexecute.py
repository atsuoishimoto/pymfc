# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

from pymfc import shellapi
import os
import time
def run():
    f = open("aaa.txt", "wb")
    f.write("abcdefg")
    f.close()
    
#    shellapi.shellExecute("open", 
#        os.path.abspath("aaa.txt"), "", "", ddewait=True)
#    print shellapi.shellExecute(u"open", 
#        u"c:\\a.txt", u"", u"", ddewait=True, show=True)

    ret = shellapi.shellExecute(u"open", 
        u"c:\\a.bmp", u"", u"", ddewait=True, show=True, nocloseprocess=True)

    if ret:
        ret.wait()
        
if __name__ == '__main__':
    run()

