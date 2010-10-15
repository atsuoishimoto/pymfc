import struct, sys

INT = 0x00
# |0000|num |                                    ::: 0 <= num <= 12
# |0000|1101|.... 8-bit int ....  		 ::: -128 <= num <= 127
# |0000|1110|.... 16-bit little endian int ....  ::: -32768 <= num <= 32767
# |0000|1111|.... 32-bit little endian int ....  ::: -2147483648 <= num <= 2147483647

LONG = 0x10
# |0010|len |                                    ::: len <= 12
# |0010|1101|.... 8-bit int ....  		 ::: len <= 127
# |0010|1110|.... 16-bit little endian int ....  ::: len <= 32767
# |0010|1111|.... 32-bit little endian int ....  ::: len <= 2147483647

FLOAT = 0x20
# |0010|    |.... 64-bit IEEE floating point number...|

STR = 0x30
# |0011|len |                                    ::: len <= 12
# |0011|1101|.... 8-bit int ....  		 ::: len <= 127
# |0011|1110|.... 16-bit little endian int ....  ::: len <= 32767
# |0011|1111|.... 32-bit little endian int ....  ::: len <= 2147483647

USTR = 0x40  # encoded in utf-8
# |0100|len |                                    ::: len <= 12
# |0100|1101|.... 8-bit int ....  		 ::: len <= 127
# |0100|1110|.... 16-bit little endian int ....  ::: len <= 32767
# |0100|1111|.... 32-bit little endian int ....  ::: len <= 2147483647

DATETIME = 0x50
# |0101|    |

TUPLE = 0x60
# |0110|len |                                    ::: len <= 12
# |0110|1101|.... 8-bit int ....  		 ::: len <= 127
# |0110|1110|.... 16-bit little endian int ....  ::: len <= 32767
# |0110|1111|.... 32-bit little endian int ....  ::: len <= 2147483647

LIST = 0x70

DICT = 0x80

REFS = 0xE0
# |1110|num |                                    ::: num <= 12
# |1110|1101|.... 8-bit int ....  		 ::: num <= 256
# |1110|1110|.... 16-bit little endian int ....  ::: num <= 65535
# |1110|1111|.... 32-bit little endian int ....  ::: num <= 2147483647

SPECIALS = 0xF0
# |1111|0000| ::: None
# |1111|0001| ::: True
# |1111|0010| ::: False


class Serializer:
    def __init__(self):
        self._nummap = {}
        self._strmap = {}
        self._ustrmap = {}
        self._objs = []
        self._buildings = set()

    def _build_num(self, flag, num):
        if 0 <= num <= 12:
            return chr(flag | num)
        
        if -128 <= num <= 127:
            return "%c" % (flag+13) + struct.pack("<b", num)
            
        if -32768 <= num <= 32767:
            return "%c" % (flag+14) + struct.pack("<h", num)
        
        if -2147483648 <= num <= 2147483647:
            return "%c" % (flag+15) + struct.pack("<i", num)
        

    def _build_long(self, flag, num):
        s = str(num)
        slen = len(s)
        # check len
        if slen <= 14:
            return "%c" % (flag + slen) + s
        else:
            return "%c" % (flag + 15) + struct.pack("<i", slen) + s
        

    def _build_ref(self, n):
        s = self._build_num(REFS, n)
        if not s:
            raise ValueError("Too many object")
        return s
        
    def _handle_num(self, num):
        n = self._nummap.get(num)
        if n is not None:
            return self._build_ref(n)

        s = self._build_num(INT, num)
        if s and len(s) <= 3:
            # num is small. Don't use object table.
            return s

        if not s:
            s = self._build_long(LONG, num)

        pos = len(self._objs)
        self._objs.append(s)
        self._nummap[num] = pos
        return self._build_ref(pos)

    def _build_str(self, flag, s):
        slen = len(s)
        if slen >= 2147483647:
            raise ValueError("string too long")

        return self._build_num(flag, slen) + s


    def _handle_string(self, s):
        n = self._strmap.get(s)
        if n is not None:
            return self._build_ref(n)

        s = self._build_str(STR, s)
        if len(s) <= 4:
            return s

        pos = len(self._objs)
        self._objs.append(s)
        self._strmap[s] = pos
        return self._build_ref(pos)

    def _handle_unicode(self, s):
        n = self._ustrmap.get(s)
        if n is not None:
            return self._build_ref(n)

        s = s.encode("utf-8")
        s = self._build_str(USTR, s)
        if len(s) <= 5:
            return s

        pos = len(self._objs)
        self._objs.append(s)
        self._ustrmap[s] = pos
        return self._build_ref(pos)

    def _handle_float(self, f):
        return chr(FLOAT) + struct.pack('>d', f)
        
    def _handle_tuple(self, t):
        objid = id(t)
        if objid in self._buildings:
            raise ValueError('Circular refecence(%s)' % t)

        self._buildings.add(objid)
        subitems = [self._build(item) for item in t]
        s = self._build_num(TUPLE, len(t)) + "".join(subitems)

        pos = len(self._objs)
        self._objs.append(s) 
        return self._build_ref(pos)

    def _handle_list(self, l):
        objid = id(l)
        if objid in self._buildings:
            raise ValueError('Circular refecence(%s)' % l)

        self._buildings.add(objid)
        subitems = [self._build(item) for item in l]
        s = self._build_num(LIST, len(l)) + "".join(subitems)

        pos = len(self._objs)
        self._objs.append(s) 
        return self._build_ref(pos)

    def _handle_dict(self, d):
        objid = id(d)
        if objid in self._buildings:
            raise ValueError('Circular refecence(%s)' % d)

        self._buildings.add(objid)
        subitems = []
        for k, v in d.iteritems():
            subitems.append(self._build(k))
            subitems.append(self._build(v))
            
        s = self._build_num(DICT, len(d)) + "".join(subitems)

        pos = len(self._objs)
        self._objs.append(s) 
        return self._build_ref(pos)

    TYPEMAP = {
        int:_handle_num,
        long:_handle_num,
        str:_handle_string,
        unicode:_handle_unicode,
        float:_handle_float,
        tuple:_handle_tuple,
        list:_handle_list,
        dict:_handle_dict,
    }

    def _build(self, obj):
        f = self.TYPEMAP.get(type(obj))
        return f(self, obj)

    def dumps(self, obj):
        s = self._build(obj)
        self._objs.append(s)
        return "".join(self._objs)



class Loader:
    def __init__(self):
        self._objs = []

    def _load_num(self, s, pos):
        n = ord(s[pos]) & 0x0f
        if n <= 12:
            return pos+1, n
        if n == 13:
            return pos+2, struct.unpack('b', s[pos+1])[0]
        if n == 14:
            return pos+3, struct.unpack('<h', s[pos+1:pos+3])[0]
        if n == 15:
            return pos+5, struct.unpack('<i', s[pos+1:pos+5])[0]
        raise ValueError("Invalid data")
        
    def _handle_num(self, s, pos):
        pos, val = self._load_num(s, pos)
        return pos, val
        
    def _handle_long(self, s, pos):
        pos, slen = self._load_num(s, pos)
        if slen < 0:
            raise ValueError("Invalid data")
        s = s[pos:pos+slen]
        val = int(s)
        return pos+slen, val
        
    def _handle_str(self, s, pos):
        pos, slen = self._load_num(s, pos)
        if slen < 0:
            raise ValueError("Invalid data")
        val = s[pos:pos+slen]
        return pos+slen, val
        
    def _handle_ustr(self, s, pos):
        pos, val = self._handle_str(s, pos)
        return pos, unicode(val, "utf-8")
    
    def _handle_float(self, s, pos):
        return pos+9, struct.unpack('>d', s[pos+1:pos+9])[0]
    
    def _handle_tuple(self, s, pos):
        pos, nitems = self._load_num(s, pos)
        if nitems < 0:
            raise ValueError("Invalid data")
        
        items = []
        for n in range(nitems):
            pos, val = self._load(s, pos)
            items.append(val)
        return pos, tuple(items)

    def _handle_list(self, s, pos):
        pos, nitems = self._load_num(s, pos)
        if nitems < 0:
            raise ValueError("Invalid data")
        
        items = []
        for n in range(nitems):
            pos, val = self._load(s, pos)
            items.append(val)
        return pos, items

    def _handle_dict(self, s, pos):
        pos, nitems = self._load_num(s, pos)
        if nitems < 0:
            raise ValueError("Invalid data")
        
        d = {}
        for n in range(nitems):
            pos, key = self._load(s, pos)
            pos, val = self._load(s, pos)
            d[key] = val
        return pos, d


    def _handle_ref(self, s, pos):
        pos, n = self._load_num(s, pos)
        val = self._objs[n]
        return pos, val


    TYPEMAP = {
        INT:_handle_num,
        LONG:_handle_long,
        STR:_handle_str,
        USTR:_handle_ustr,
        FLOAT:_handle_float,
        TUPLE:_handle_tuple,
        LIST:_handle_list,
        DICT:_handle_dict,
        REFS:_handle_ref
    }
    
    def _load(self, s, pos):
        flag = ord(s[pos]) & 0xf0
        f = self.TYPEMAP[flag]
        pos, val = f(self, s, pos)
        return pos, val
        
    def loads(self, s):
        pos = 0
        end = len(s)
        while pos < end:
            pos, val = self._load(s, pos)
            self._objs.append(val)
        return self._objs[-1]
        

hex(224)

oo = [1,2,255, 2.2, -1, -100, -10000, -10000000, -10000000000,
    ('a', 'b', 'cdddddddddddddddddd'), 
    3, 5555555,
    {1:2},{3:{4:5}},{("1","2","3"):['abcdefghmflkasmdflkasmflkmflksdlkam']}
]

#oo = {1:1}
for i in range(100):
    ss = Serializer().dumps(oo)
l = Loader().loads(ss)
print l == oo, len(ss), l


#oo = ("a",2,3,4,5,6,7,"abcdefghijklmnopdddddddddddddddasdadasdasdqrst",9,0,1,2,3,0xfffff)
##oo = ("a","a","a","a","a","a","a","a","a","a",)
#
#print Serializer().dumps(oo)
#
import pickle
s = pickle.dumps(oo, -1)
print len(s)
print s
#pickle.loads(s)
#
#97./129
#100./138
#
#repr(2.2)