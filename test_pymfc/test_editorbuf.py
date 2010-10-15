# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import unittest
from pymfc.editor.buffer import Buffer


class test_buffer(unittest.TestCase):
    def testIns(self):
        buf = Buffer()
        s = u"abcdefg"
        buf.ins(0, s)
#        ret = buf.get(0, len(s))
#        self.failUnlessEqual(s, ret)
#        self.failUnlessEqual(buf.getSize(), len(s))
        
#        buf.ins(len(s), s)
#        ret = buf.get(0, len(s)*2)
#        self.failUnlessEqual(s*2, ret)
#        self.failUnlessEqual(buf.getSize(), len(s)*2)
        
    def testDel(self):
        buf = Buffer()
        s = u"abcdefg"
        buf.ins(0, s)
        
        for i in range(len(s)):
            i += 1
            buf.delete(0, 1)
            ret = buf.get(0, len(s)-i)
            self.failUnlessEqual(s[i:], ret)
            self.failUnlessEqual(buf.getSize(), len(s)-i)

    def testRep(self):
        buf = Buffer()
        s = u"abcdefg"
        buf.ins(0, s)
        buf.replace(1, 3, u"123456789")
        ret = buf.get(0, len(buf))
        self.failUnlessEqual(ret, u"a123456789defg")
        
    def testFind(self):
        def test_char():
            # character search
            ret = buf.find(0, len(s), u'0')
            self.failUnlessEqual(ret, 0)
            
            ret = buf.find(0, 3, u'3')
            self.failUnlessEqual(ret, -1)
            
            ret = buf.find(0, 4, u'3')
            self.failUnlessEqual(ret, 3)
            
            ret = buf.find(0, len(s), u'j')
            self.failUnlessEqual(ret, 19)
            
            # check case
            ret = buf.find(0, len(s), u'j', case=False)
            self.failUnlessEqual(ret, 19)
            
            ret = buf.find(0, len(s), u'J')
            self.failUnlessEqual(ret, -1)
            
            ret = buf.find(0, len(s), u'J', case=False)
            self.failUnlessEqual(ret, 19)
            
            # backward search
            ret = buf.find(0, len(s), u'j', forward=False)
            self.failUnlessEqual(ret, 39)
            
            ret = buf.find(0, len(s), u'0', forward=False)
            self.failUnlessEqual(ret, 20)
            
            ret = buf.find(0, 20, u'0', forward=False)
            self.failUnlessEqual(ret, 0)
            
            ret = buf.find(1, 20, u'0', forward=False)
            self.failUnlessEqual(ret, -1)
            
            # backward/caseless
            ret = buf.find(0, len(s), u'j', forward=False, case=False)
            self.failUnlessEqual(ret, 39)
            
            ret = buf.find(0, len(s), u'J', forward=False, case=False)
            self.failUnlessEqual(ret, 39)
            
            ret = buf.find(0, 19, u'J', forward=False, case=False)
            self.failUnlessEqual(ret, -1)

        def test_str():
            # string search
            ret = buf.findString(0, len(s), u'123')
            self.failUnlessEqual(ret, 1)

            ret = buf.findString(1, len(s), u'123')
            self.failUnlessEqual(ret, 1)

            ret = buf.findString(2, len(s), u'123')
            self.failUnlessEqual(ret, 21)

            ret = buf.findString(22, len(s), u'123')
            self.failUnlessEqual(ret, -1)

            ret = buf.findString(20, len(s), u'hij')
            self.failUnlessEqual(ret, 37)

            ret = buf.findString(20, 39, u'hij')
            self.failUnlessEqual(ret, -1)

            # case check
            ret = buf.findString(0, len(s), u'123', case=False)
            self.failUnlessEqual(ret, 1)

            ret = buf.findString(1, len(s), u'123', case=False)
            self.failUnlessEqual(ret, 1)

            ret = buf.findString(2, len(s), u'123', case=False)
            self.failUnlessEqual(ret, 21)

            ret = buf.findString(22, len(s), u'123', case=False)
            self.failUnlessEqual(ret, -1)

            ret = buf.findString(20, len(s), u'hij', case=False)
            self.failUnlessEqual(ret, 37)

            ret = buf.findString(20, len(s), u'HIJ', case=False)
            self.failUnlessEqual(ret, 37)

            ret = buf.findString(20, 39, u'hij', case=False)
            self.failUnlessEqual(ret, -1)

            # backward
            ret = buf.findString(0, len(s), u'123', forward=0)
            self.failUnlessEqual(ret, 21)

            ret = buf.findString(0, len(s), u'hij', forward=0)
            self.failUnlessEqual(ret, 37)

            ret = buf.findString(0, len(s)-1, u'hij', forward=0)
            self.failUnlessEqual(ret, 17)

            ret = buf.findString(0, 20, u'hij', forward=0)
            self.failUnlessEqual(ret, 17)

            ret = buf.findString(0, 19, u'hij', forward=0)
            self.failUnlessEqual(ret, -1)

            ret = buf.findString(0, 20, u'012', forward=0)
            self.failUnlessEqual(ret, 0)

            ret = buf.findString(1, 20, u'012', forward=0)
            self.failUnlessEqual(ret, -1)

            # backward/case
            ret = buf.findString(0, len(s), u'123', forward=0, case=0)
            self.failUnlessEqual(ret, 21)

            ret = buf.findString(0, len(s), u'HIJ', forward=0, case=0)
            self.failUnlessEqual(ret, 37)

            ret = buf.findString(0, len(s)-1, u'HIJ', forward=0, case=0)
            self.failUnlessEqual(ret, 17)

            ret = buf.findString(0, 20, u'HIJ', forward=0, case=0)
            self.failUnlessEqual(ret, 17)

            ret = buf.findString(0, 19, u'HIJ', forward=0, case=0)
            self.failUnlessEqual(ret, -1)

            ret = buf.findString(0, 20, u'012', forward=0, case=0)
            self.failUnlessEqual(ret, 0)

            ret = buf.findString(1, 20, u'012', forward=0, case=0)
            self.failUnlessEqual(ret, -1)

        def test_oneof():
            ret = buf.findOneOf(0, len(s), u'0')
            self.failUnlessEqual(ret, (0,0))
            
            ret = buf.findOneOf(0, len(s), u'10')
            self.failUnlessEqual(ret, (0,1))
            
            ret = buf.findOneOf(0, 3, u'345')
            self.failUnlessEqual(ret, None)
            
            ret = buf.findOneOf(0, 4, u'345')
            self.failUnlessEqual(ret, (3, 0))
            
            ret = buf.findOneOf(0, len(s), u'jkl')
            self.failUnlessEqual(ret, (19, 0))

            # backward
            ret = buf.findOneOf(0, len(s), u'jkl', forward=False)
            self.failUnlessEqual(ret, (39, 0))
            
            ret = buf.findOneOf(0, len(s), u'0', forward=False)
            self.failUnlessEqual(ret, (20, 0))
            
            ret = buf.findOneOf(0, 20, u'0', forward=False)
            self.failUnlessEqual(ret, (0, 0))
            
            ret = buf.find(1, 20, u'0', forward=False)
            self.failUnlessEqual(ret, -1)
            


        buf = Buffer()
        s = u"0123456789abcdefghij0123456789abcdefghij"
        buf.ins(0, s)
        
        test_char()
        test_str()
        test_oneof()
        
        # move gap and try again
        buf.ins(20, u'a')
        buf.delete(20, 21)
        test_char()
        test_str()
        test_oneof()
        
        # move gap and try again
        buf.ins(0, u'a')
        buf.delete(0, 1)
        test_char()
        test_str()
        test_oneof()
        
        

    def testStyle(self):
        buf = Buffer()
        s = u"abcdefg"
        buf.ins(0, s)
        
        buf.setStyles([(1, 0, len(s))])
        ret = buf.getStyle(0, len(s))
        self.failUnlessEqual(ret, [1]*len(s))

        for i in range(len(s)):
            buf.setStyles([(i, i, i+1)])
            ret = buf.getStyle(i, i+1)
            self.failUnlessEqual(ret, [i])

    def testLine(self):
        buf = Buffer()
        s = u'''012345678
112345678
212345678
312345678
'''
        s = "\n".join([l.strip() for l in s.split("\n")])
        buf.ins(0, s)
        
        self.failUnlessEqual(buf.getTOL(0), 0)
        self.failUnlessEqual(buf.getTOL(5), 0)
        self.failUnlessEqual(buf.getTOL(9), 0)
        
        self.failUnlessEqual(buf.getEOL(0), 10)
        self.failUnlessEqual(buf.getEOL(5), 10)
        self.failUnlessEqual(buf.getEOL(9), 10)
        
        self.failUnlessEqual(buf.getTOL(10), 10)
        self.failUnlessEqual(buf.getTOL(15), 10)
        self.failUnlessEqual(buf.getTOL(19), 10)
        
        self.failUnlessEqual(buf.getEOL(10), 20)
        self.failUnlessEqual(buf.getEOL(15), 20)
        self.failUnlessEqual(buf.getEOL(19), 20)
        
        self.failUnlessEqual(buf.getTOL(20), 20)
        self.failUnlessEqual(buf.getTOL(25), 20)
        self.failUnlessEqual(buf.getTOL(29), 20)
        
        self.failUnlessEqual(buf.getEOL(20), 30)
        self.failUnlessEqual(buf.getEOL(25), 30)
        self.failUnlessEqual(buf.getEOL(29), 30)
        
        self.failUnlessEqual(buf.getTOL(30), 30)
        self.failUnlessEqual(buf.getTOL(35), 30)
        self.failUnlessEqual(buf.getTOL(39), 30)
        
        self.failUnlessEqual(buf.getEOL(30), 40)
        self.failUnlessEqual(buf.getEOL(35), 40)
        self.failUnlessEqual(buf.getEOL(39), 40)
        
        self.failUnlessEqual(buf.getTOL(40), 40)
        self.failUnlessEqual(buf.getEOL(40), 40)

        self.failUnlessEqual(buf.getLineNo(0), 0)
        self.failUnlessEqual(buf.getLineNo(40), 4)
        

    def testUndo_ins(self):
        buf = Buffer()

        s1 = u"abcdefg"
        buf.ins(0, s1)
        buf.undo.inserted(0, s1, 0, 0)

        s2 = u"12345"
        buf.ins(len(s1), s2)
        buf.undo.inserted(len(s1), s2, len(s1), len(s1))

        newpos = buf.undo.undo(False)
        self.failUnlessEqual(newpos, len(s1))
        self.failUnlessEqual(s1, buf.get(0, len(buf)))
        
        newpos = buf.undo.undo(False)
        self.failUnlessEqual(newpos, 0)
        self.failUnlessEqual(u'', buf.get(0, len(buf)))

    def testUndo_del(self):
        buf = Buffer()

        s1 = u"abcdefg"
        buf.ins(0, s1)
        buf.undo.inserted(0, s1, 0, 0)

        buf.delete(2,4)
        buf.undo.deleted(2, s1[2:4], 2, 2)

        newpos = buf.undo.undo(False)
        self.failUnlessEqual(newpos, 2)
        self.failUnlessEqual(s1, buf.get(0, len(buf)))

        newpos = buf.undo.undo(False)
        self.failUnlessEqual(newpos, 0)
        self.failUnlessEqual(u"", buf.get(0, len(buf)))

    def testUndo_repl(self):
        buf = Buffer()

        s1 = u"abcdefg"
        buf.ins(0, s1)

        rep = u"123"
        buf.replace(2,4,rep)
        buf.undo.replaced(2, rep, s1[2:4], 2, 2)

        newpos = buf.undo.undo(False)
        self.failUnlessEqual(s1, buf.get(0, len(buf)))

        newpos = buf.undo.redo(False)
        
        rr = u"ab123efg"
        self.failUnlessEqual(rr, buf.get(0, len(buf)))
        
        
    def testUndo_group(self):
        buf = Buffer()

        s1 = u"abcdefg"
        buf.ins(0, s1)
        buf.undo.inserted(0, s1, 0, 0)

        buf.undo.beginGroup()
        s2 = u"123"
        buf.ins(len(s1), s2)
        buf.undo.inserted(len(s1), s2, len(s1), len(s1))

        buf.undo.beginGroup()

        s3 = u"xyz"
        buf.ins(len(s1), s3)
        buf.undo.inserted(len(s1), s3, len(s1), len(s1))

        buf.undo.endGroup()

        p = len(buf)-1
        buf.delete(p, len(buf))
        buf.undo.deleted(p, s3[-1], p, p)

        self.failUnlessEqual(s1+s3+s2[:-1], buf.get(0, len(buf)))

        buf.undo.endGroup()

        newpos = buf.undo.undo(False)
        self.failUnlessEqual(len(s1), newpos)
        self.failUnlessEqual(s1, buf.get(0, len(buf)))

        newpos = buf.undo.undo(False)
        self.failUnlessEqual(0, newpos)
        self.failUnlessEqual(u'', buf.get(0, len(buf)))

    def testRedo_ins(self):
        buf = Buffer()

        s1 = u"abcdefg"
        buf.ins(0, s1)
        buf.undo.inserted(0, s1, 0, 0)

        s2 = u"12345"
        buf.ins(len(s1), s2)
        buf.undo.inserted(len(s1), s2, len(s1), len(s1))

        buf.undo.undo(False)
        buf.undo.undo(False)

        newpos = buf.undo.redo(False)
        self.failUnlessEqual(newpos, 0)
        self.failUnlessEqual(s1, buf.get(0, len(buf)))

        newpos = buf.undo.redo(False)
        self.failUnlessEqual(newpos, len(s1))
        self.failUnlessEqual(s1+s2, buf.get(0, len(buf)))

    def testRedo_del(self):
        buf = Buffer()

        s1 = u"abcdefg"
        buf.ins(0, s1)
        buf.undo.inserted(0, s1, 0, 0)

        buf.delete(2,4)
        buf.undo.deleted(2, s1[2:4], 2, 2)

        newpos = buf.undo.undo(False)
        newpos = buf.undo.undo(False)

        newpos = buf.undo.redo(False)
        self.failUnlessEqual(newpos, 0)
        self.failUnlessEqual(s1, buf.get(0, len(buf)))

        newpos = buf.undo.redo(False)
        self.failUnlessEqual(newpos, 2)
        self.failUnlessEqual(s1[:2]+s1[4:], buf.get(0, len(buf)))

    def testRedo_group(self):
        buf = Buffer()
#1
        s1 = u"abcdefg"
        buf.ins(0, s1)
        buf.undo.inserted(0, s1, 0, 0)

#2
        buf.undo.beginGroup()
        s2 = u"123"
        buf.ins(len(s1), s2)
        buf.undo.inserted(len(s1), s2, len(s1), len(s1))

        buf.undo.beginGroup()

        s3 = u"xyz"
        buf.ins(len(s1+s2), s3)
        buf.undo.inserted(len(s1+s2), s3, len(s1+s2), len(s1+s2))

        buf.undo.endGroup()

        p = len(buf)-1
        buf.delete(p, len(buf))
        buf.undo.deleted(p, s3[-1], p, p)
        
        buf.undo.endGroup()

        newpos = buf.undo.undo(False)
        newpos = buf.undo.undo(False)

        newpos = buf.undo.redo(False)
        self.failUnlessEqual(0, newpos)
        self.failUnlessEqual(s1, buf.get(0, len(buf)))

        newpos = buf.undo.redo(False)
        self.failUnlessEqual(len(s1+s3+s2[:-1]), newpos)
        self.failUnlessEqual(s1+s2+s3[:-1], buf.get(0, len(buf)))



if __name__ == '__main__':
    unittest.main()

