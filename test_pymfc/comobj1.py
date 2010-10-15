import unittest

import pymfc.COM

class test_istream(unittest.TestCase):
    def testCreate(self):
        s = "abcdefg"
        o = pymfc.COM.IStream(buf=s)
        self.failUnlessEqual(o.read(100), s)

    def testRead(self):
        s = "abcdefg"
        o = pymfc.COM.IStream(buf=s)
        self.failUnlessEqual(o.read(1), s[0])

    def testWrite(self):
        s = "abcdefg"
        o = pymfc.COM.IStream(buf=s)
        o.seek(0)
        o.write("1234")
        o.seek(0)
        self.failUnlessEqual(o.read(100), "1234efg")

    def testSeek(self):
        s = "abcdefg"
        o = pymfc.COM.IStream(buf=s)
        self.failUnlessEqual(o.read(100), s)
        self.failUnlessEqual(o.read(100), '')
        
        o.seek(0)
        self.failUnlessEqual(o.read(100), s)
        
        
    def testClone(self):
        s = "abcdefg"
        o = pymfc.COM.IStream(buf=s)
        o2 = o.clone()
        
        self.failUnless(o is not o2)
        self.failUnlessEqual(o.read(100), s)
        self.failUnlessEqual(o2.read(100), s)
        

    def testAll(self):
        for i in range(1):
            self.testWrite()
            self.testSeek()
            self.testClone()
            self.testCreate()
            self.testRead()

if __name__ == '__main__':
    unittest.main()

