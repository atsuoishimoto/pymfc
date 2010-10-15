import sys
sys.path = ['.'] + sys.path

from test.test_support import verbose, run_unittest
import dmybufre as re
from sre import Scanner
import sys, os, traceback
from weakref import proxy

# Misc tests from Tim Peters' re.doc

# WARNING: Don't change details in these tests if you don't know
# what you're doing. Some of these tests were carefuly modeled to
# cover most of the code.

import unittest

class ReTests(unittest.TestCase):

    def test_weakref(self):
        s = 'QabbbcR'
        x = re.compile('ab+c')
        y = proxy(x)
        self.assertEqual(x.findall('QabbbcR'), y.findall('QabbbcR'))

    def test_search_star_plus(self):
        self.assertEqual(re.search('x*', 'axx').span(0), (0, 0))
        self.assertEqual(re.search('x*', 'axx').span(), (0, 0))
        self.assertEqual(re.search('x+', 'axx').span(0), (1, 3))
        self.assertEqual(re.search('x+', 'axx').span(), (1, 3))
        self.assertEqual(re.search('x', 'aaa'), None)
        self.assertEqual(re.match('a*', 'xxx').span(0), (0, 0))
        self.assertEqual(re.match('a*', 'xxx').span(), (0, 0))
        self.assertEqual(re.match('x*', 'xxxa').span(0), (0, 3))
        self.assertEqual(re.match('x*', 'xxxa').span(), (0, 3))
        self.assertEqual(re.match('a+', 'xxx'), None)

    def test_re_findall(self):
        self.assertEqual(re.findall(":+", "abc"), [])
        self.assertEqual(re.findall(":+", "a:b::c:::d"), [":", "::", ":::"])
        self.assertEqual(re.findall("(:+)", "a:b::c:::d"), [":", "::", ":::"])
        self.assertEqual(re.findall("(:)(:*)", "a:b::c:::d"), [(":", ""),
                                                               (":", ":"),
                                                               (":", "::")])

    def test_bug_117612(self):
        self.assertEqual(re.findall(r"(a|(b))", "aba"),
                         [("a", ""),("b", "b"),("a", "")])

    def test_re_match(self):
        self.assertEqual(re.match('a', 'a').groups(), ())
        self.assertEqual(re.match('(a)', 'a').groups(), ('a',))
        self.assertEqual(re.match(r'(a)', 'a').group(0), 'a')
        self.assertEqual(re.match(r'(a)', 'a').group(1), 'a')
        self.assertEqual(re.match(r'(a)', 'a').group(1, 1), ('a', 'a'))

        pat = re.compile('((a)|(b))(c)?')
        self.assertEqual(pat.match('a').groups(), ('a', 'a', None, None))
        self.assertEqual(pat.match('b').groups(), ('b', None, 'b', None))
        self.assertEqual(pat.match('ac').groups(), ('a', 'a', None, 'c'))
        self.assertEqual(pat.match('bc').groups(), ('b', None, 'b', 'c'))
        self.assertEqual(pat.match('bc').groups(""), ('b', "", 'b', 'c'))

        # A single group
        m = re.match('(a)', 'a')
        self.assertEqual(m.group(0), 'a')
        self.assertEqual(m.group(0), 'a')
        self.assertEqual(m.group(1), 'a')
        self.assertEqual(m.group(1, 1), ('a', 'a'))

        pat = re.compile('(?:(?P<a1>a)|(?P<b2>b))(?P<c3>c)?')
        self.assertEqual(pat.match('a').group(1, 2, 3), ('a', None, None))
        self.assertEqual(pat.match('b').group('a1', 'b2', 'c3'),
                         (None, 'b', None))
        self.assertEqual(pat.match('ac').group(1, 'b2', 3), ('a', None, 'c'))

    def test_re_groupref_exists(self):
        self.assertEqual(re.match('^(\()?([^()]+)(?(1)\))$', '(a)').groups(),
                         ('(', 'a'))
        self.assertEqual(re.match('^(\()?([^()]+)(?(1)\))$', 'a').groups(),
                         (None, 'a'))
        self.assertEqual(re.match('^(\()?([^()]+)(?(1)\))$', 'a)'), None)
        self.assertEqual(re.match('^(\()?([^()]+)(?(1)\))$', '(a'), None)
        self.assertEqual(re.match('^(?:(a)|c)((?(1)b|d))$', 'ab').groups(),
                         ('a', 'b'))
        self.assertEqual(re.match('^(?:(a)|c)((?(1)b|d))$', 'cd').groups(),
                         (None, 'd'))
        self.assertEqual(re.match('^(?:(a)|c)((?(1)|d))$', 'cd').groups(),
                         (None, 'd'))
        self.assertEqual(re.match('^(?:(a)|c)((?(1)|d))$', 'a').groups(),
                         ('a', ''))

    def test_re_groupref(self):
        self.assertEqual(re.match(r'^(\|)?([^()]+)\1$', '|a|').groups(),
                         ('|', 'a'))
        self.assertEqual(re.match(r'^(\|)?([^()]+)\1?$', 'a').groups(),
                         (None, 'a'))
        self.assertEqual(re.match(r'^(\|)?([^()]+)\1$', 'a|'), None)
        self.assertEqual(re.match(r'^(\|)?([^()]+)\1$', '|a'), None)
        self.assertEqual(re.match(r'^(?:(a)|c)(\1)$', 'aa').groups(),
                         ('a', 'a'))
        self.assertEqual(re.match(r'^(?:(a)|c)(\1)?$', 'c').groups(),
                         (None, None))

    def test_groupdict(self):
        self.assertEqual(re.match('(?P<first>first) (?P<second>second)',
                                  'first second').groupdict(),
                         {'first':'first', 'second':'second'})

    def test_repeat_minmax(self):
        self.assertEqual(re.match("^(\w){1}$", "abc"), None)
        self.assertEqual(re.match("^(\w){1}?$", "abc"), None)
        self.assertEqual(re.match("^(\w){1,2}$", "abc"), None)
        self.assertEqual(re.match("^(\w){1,2}?$", "abc"), None)

        self.assertEqual(re.match("^(\w){3}$", "abc").group(1), "c")
        self.assertEqual(re.match("^(\w){1,3}$", "abc").group(1), "c")
        self.assertEqual(re.match("^(\w){1,4}$", "abc").group(1), "c")
        self.assertEqual(re.match("^(\w){3,4}?$", "abc").group(1), "c")
        self.assertEqual(re.match("^(\w){3}?$", "abc").group(1), "c")
        self.assertEqual(re.match("^(\w){1,3}?$", "abc").group(1), "c")
        self.assertEqual(re.match("^(\w){1,4}?$", "abc").group(1), "c")
        self.assertEqual(re.match("^(\w){3,4}?$", "abc").group(1), "c")

        self.assertEqual(re.match("^x{1}$", "xxx"), None)
        self.assertEqual(re.match("^x{1}?$", "xxx"), None)
        self.assertEqual(re.match("^x{1,2}$", "xxx"), None)
        self.assertEqual(re.match("^x{1,2}?$", "xxx"), None)

        self.assertNotEqual(re.match("^x{3}$", "xxx"), None)
        self.assertNotEqual(re.match("^x{1,3}$", "xxx"), None)
        self.assertNotEqual(re.match("^x{1,4}$", "xxx"), None)
        self.assertNotEqual(re.match("^x{3,4}?$", "xxx"), None)
        self.assertNotEqual(re.match("^x{3}?$", "xxx"), None)
        self.assertNotEqual(re.match("^x{1,3}?$", "xxx"), None)
        self.assertNotEqual(re.match("^x{1,4}?$", "xxx"), None)
        self.assertNotEqual(re.match("^x{3,4}?$", "xxx"), None)

    def test_getattr(self):
        self.assertEqual(re.match("(a)", "a").pos, 0)
        self.assertEqual(re.match("(a)", "a").endpos, 1)
        self.assertEqual(re.match("(a)", "a").regs, ((0, 1), (0, 1)))
        self.assertNotEqual(re.match("(a)", "a").re, None)

    def test_special_escapes(self):
        self.assertEqual(re.search(r"\b(b.)\b",
                                   "abcd abc bcd bx").group(1), "bx")
        self.assertEqual(re.search(r"\B(b.)\B",
                                   "abc bcd bc abxd").group(1), "bx")
        self.assertEqual(re.search(r"\b(b.)\b",
                                   "abcd abc bcd bx", re.LOCALE).group(1), "bx")
        self.assertEqual(re.search(r"\B(b.)\B",
                                   "abc bcd bc abxd", re.LOCALE).group(1), "bx")
        self.assertEqual(re.search(r"\b(b.)\b",
                                   "abcd abc bcd bx", re.UNICODE).group(1), "bx")
        self.assertEqual(re.search(r"\B(b.)\B",
                                   "abc bcd bc abxd", re.UNICODE).group(1), "bx")
        self.assertEqual(re.search(r"^abc$", "\nabc\n", re.M).group(0), "abc")
        self.assertEqual(re.search(r"^\Aabc\Z$", "abc", re.M).group(0), "abc")
        self.assertEqual(re.search(r"^\Aabc\Z$", "\nabc\n", re.M), None)
        self.assertEqual(re.search(r"\b(b.)\b",
                                   u"abcd abc bcd bx").group(1), "bx")
        self.assertEqual(re.search(r"\B(b.)\B",
                                   u"abc bcd bc abxd").group(1), "bx")
        self.assertEqual(re.search(r"^abc$", u"\nabc\n", re.M).group(0), "abc")
        self.assertEqual(re.search(r"^\Aabc\Z$", u"abc", re.M).group(0), "abc")
        self.assertEqual(re.search(r"^\Aabc\Z$", u"\nabc\n", re.M), None)
        self.assertEqual(re.search(r"\d\D\w\W\s\S",
                                   "1aa! a").group(0), "1aa! a")
        self.assertEqual(re.search(r"\d\D\w\W\s\S",
                                   "1aa! a", re.LOCALE).group(0), "1aa! a")
        self.assertEqual(re.search(r"\d\D\w\W\s\S",
                                   "1aa! a", re.UNICODE).group(0), "1aa! a")

    def test_ignore_case(self):
        self.assertEqual(re.match("abc", "ABC", re.I).group(0), "ABC")
        self.assertEqual(re.match("abc", u"ABC", re.I).group(0), "ABC")

    def test_bigcharset(self):
        self.assertEqual(re.match(u"([\u2222\u2223])",
                                  u"\u2222").group(1), u"\u2222")
        self.assertEqual(re.match(u"([\u2222\u2223])",
                                  u"\u2222", re.UNICODE).group(1), u"\u2222")

    def test_anyall(self):
        self.assertEqual(re.match("a.b", "a\nb", re.DOTALL).group(0),
                         "a\nb")
        self.assertEqual(re.match("a.*b", "a\n\nb", re.DOTALL).group(0),
                         "a\n\nb")

    def test_non_consuming(self):
        self.assertEqual(re.match("(a(?=\s[^a]))", "a b").group(1), "a")
        self.assertEqual(re.match("(a(?=\s[^a]*))", "a b").group(1), "a")
        self.assertEqual(re.match("(a(?=\s[abc]))", "a b").group(1), "a")
        self.assertEqual(re.match("(a(?=\s[abc]*))", "a bc").group(1), "a")
        self.assertEqual(re.match(r"(a)(?=\s\1)", "a a").group(1), "a")
        self.assertEqual(re.match(r"(a)(?=\s\1*)", "a aa").group(1), "a")
        self.assertEqual(re.match(r"(a)(?=\s(abc|a))", "a a").group(1), "a")

        self.assertEqual(re.match(r"(a(?!\s[^a]))", "a a").group(1), "a")
        self.assertEqual(re.match(r"(a(?!\s[abc]))", "a d").group(1), "a")
        self.assertEqual(re.match(r"(a)(?!\s\1)", "a b").group(1), "a")
        self.assertEqual(re.match(r"(a)(?!\s(abc|a))", "a b").group(1), "a")

    def test_ignore_case(self):
        self.assertEqual(re.match(r"(a\s[^a])", "a b", re.I).group(1), "a b")
        self.assertEqual(re.match(r"(a\s[^a]*)", "a bb", re.I).group(1), "a bb")
        self.assertEqual(re.match(r"(a\s[abc])", "a b", re.I).group(1), "a b")
        self.assertEqual(re.match(r"(a\s[abc]*)", "a bb", re.I).group(1), "a bb")
        self.assertEqual(re.match(r"((a)\s\2)", "a a", re.I).group(1), "a a")
        self.assertEqual(re.match(r"((a)\s\2*)", "a aa", re.I).group(1), "a aa")
        self.assertEqual(re.match(r"((a)\s(abc|a))", "a a", re.I).group(1), "a a")
        self.assertEqual(re.match(r"((a)\s(abc|a)*)", "a aa", re.I).group(1), "a aa")

    def test_category(self):
        self.assertEqual(re.match(r"(\s)", " ").group(1), " ")

    def test_getlower(self):
        import _sre
        self.assertEqual(_sre.getlower(ord('A'), 0), ord('a'))
        self.assertEqual(_sre.getlower(ord('A'), re.LOCALE), ord('a'))
        self.assertEqual(_sre.getlower(ord('A'), re.UNICODE), ord('a'))

        self.assertEqual(re.match("abc", "ABC", re.I).group(0), "ABC")
        self.assertEqual(re.match("abc", u"ABC", re.I).group(0), "ABC")

    def test_not_literal(self):
        self.assertEqual(re.search("\s([^a])", " b").group(1), "b")
        self.assertEqual(re.search("\s([^a]*)", " bb").group(1), "bb")

    def test_search_coverage(self):
        self.assertEqual(re.search("\s(b)", " b").group(1), "b")
        self.assertEqual(re.search("a\s", "a ").group(0), "a ")

    def test_re_escape(self):
        p=""
        for i in range(0, 256):
            p = p + chr(i)
            self.assertEqual(re.match(re.escape(chr(i)), chr(i)) is not None,
                             True)
            self.assertEqual(re.match(re.escape(chr(i)), chr(i)).span(), (0,1))

        pat=re.compile(re.escape(p))
        self.assertEqual(pat.match(p) is not None, True)
        self.assertEqual(pat.match(p).span(), (0,256))


    def test_constants(self):
        self.assertEqual(re.I, re.IGNORECASE)
        self.assertEqual(re.L, re.LOCALE)
        self.assertEqual(re.M, re.MULTILINE)
        self.assertEqual(re.S, re.DOTALL)
        self.assertEqual(re.X, re.VERBOSE)

    def test_flags(self):
        for flag in [re.I, re.M, re.X, re.S, re.L]:
            self.assertNotEqual(re.compile('^pattern$', flag), None)

    def test_sre_character_literals(self):
        for i in [0, 8, 16, 32, 64, 127, 128, 255]:
            self.assertNotEqual(re.match(r"\%03o" % i, chr(i)), None)
            self.assertNotEqual(re.match(r"\%03o0" % i, chr(i)+"0"), None)
            self.assertNotEqual(re.match(r"\%03o8" % i, chr(i)+"8"), None)
            self.assertNotEqual(re.match(r"\x%02x" % i, chr(i)), None)
            self.assertNotEqual(re.match(r"\x%02x0" % i, chr(i)+"0"), None)
            self.assertNotEqual(re.match(r"\x%02xz" % i, chr(i)+"z"), None)
        self.assertRaises(re.error, re.match, "\911", "")

    def test_sre_character_class_literals(self):
        for i in [0, 8, 16, 32, 64, 127, 128, 255]:
            self.assertNotEqual(re.match(r"[\%03o]" % i, chr(i)), None)
            self.assertNotEqual(re.match(r"[\%03o0]" % i, chr(i)), None)
            self.assertNotEqual(re.match(r"[\%03o8]" % i, chr(i)), None)
            self.assertNotEqual(re.match(r"[\x%02x]" % i, chr(i)), None)
            self.assertNotEqual(re.match(r"[\x%02x0]" % i, chr(i)), None)
            self.assertNotEqual(re.match(r"[\x%02xz]" % i, chr(i)), None)
        self.assertRaises(re.error, re.match, "[\911]", "")

    def test_bug_113254(self):
        self.assertEqual(re.match(r'(a)|(b)', 'b').start(1), -1)
        self.assertEqual(re.match(r'(a)|(b)', 'b').end(1), -1)
        self.assertEqual(re.match(r'(a)|(b)', 'b').span(1), (-1, -1))

    def test_bug_527371(self):
        # bug described in patches 527371/672491
        self.assertEqual(re.match(r'(a)?a','a').lastindex, None)
        self.assertEqual(re.match(r'(a)(b)?b','ab').lastindex, 1)
        self.assertEqual(re.match(r'(?P<a>a)(?P<b>b)?b','ab').lastgroup, 'a')
        self.assertEqual(re.match("(?P<a>a(b))", "ab").lastgroup, 'a')
        self.assertEqual(re.match("((a))", "a").lastindex, 1)

    def test_bug_545855(self):
        # bug 545855 -- This pattern failed to cause a compile error as it
        # should, instead provoking a TypeError.
        self.assertRaises(re.error, re.compile, 'foo[a-')

    def test_bug_418626(self):
        # bugs 418626 at al. -- Testing Greg Chapman's addition of op code
        # SRE_OP_MIN_REPEAT_ONE for eliminating recursion on simple uses of
        # pattern '*?' on a long string.
        self.assertEqual(re.match('.*?c', 10000*'ab'+'cd').end(0), 20001)
        self.assertEqual(re.match('.*?cd', 5000*'ab'+'c'+5000*'ab'+'cde').end(0),
                         20003)
        self.assertEqual(re.match('.*?cd', 20000*'abc'+'de').end(0), 60001)
        # non-simple '*?' still used to hit the recursion limit, before the
        # non-recursive scheme was implemented.
        self.assertEqual(re.search('(a|b)*?c', 10000*'ab'+'cd').end(0), 20001)

    def test_bug_612074(self):
        pat=u"["+re.escape(u"\u2039")+u"]"
        self.assertEqual(re.compile(pat) and 1, 1)

    def test_stack_overflow(self):
        # nasty cases that used to overflow the straightforward recursive
        # implementation of repeated groups.
        self.assertEqual(re.match('(x)*', 50000*'x').group(1), 'x')
        self.assertEqual(re.match('(x)*y', 50000*'x'+'y').group(1), 'x')
        self.assertEqual(re.match('(x)*?y', 50000*'x'+'y').group(1), 'x')

    def test_scanner(self):
        def s_ident(scanner, token): return token
        def s_operator(scanner, token): return "op%s" % token
        def s_float(scanner, token): return float(token)
        def s_int(scanner, token): return int(token)

        scanner = Scanner([
            (r"[a-zA-Z_]\w*", s_ident),
            (r"\d+\.\d*", s_float),
            (r"\d+", s_int),
            (r"=|\+|-|\*|/", s_operator),
            (r"\s+", None),
            ])

        self.assertNotEqual(scanner.scanner.scanner("").pattern, None)

        self.assertEqual(scanner.scan("sum = 3*foo + 312.50 + bar"),
                         (['sum', 'op=', 3, 'op*', 'foo', 'op+', 312.5,
                           'op+', 'bar'], ''))

    def test_bug_448951(self):
        # bug 448951 (similar to 429357, but with single char match)
        # (Also test greedy matches.)
        for op in '','?','*':
            self.assertEqual(re.match(r'((.%s):)?z'%op, 'z').groups(),
                             (None, None))
            self.assertEqual(re.match(r'((.%s):)?z'%op, 'a:z').groups(),
                             ('a:', 'a'))

    def test_bug_725106(self):
        # capturing groups in alternatives in repeats
        self.assertEqual(re.match('^((a)|b)*', 'abc').groups(),
                         ('b', 'a'))
        self.assertEqual(re.match('^(([ab])|c)*', 'abc').groups(),
                         ('c', 'b'))
        self.assertEqual(re.match('^((d)|[ab])*', 'abc').groups(),
                         ('b', None))
        self.assertEqual(re.match('^((a)c|[ab])*', 'abc').groups(),
                         ('b', None))
        self.assertEqual(re.match('^((a)|b)*?c', 'abc').groups(),
                         ('b', 'a'))
        self.assertEqual(re.match('^(([ab])|c)*?d', 'abcd').groups(),
                         ('c', 'b'))
        self.assertEqual(re.match('^((d)|[ab])*?c', 'abc').groups(),
                         ('b', None))
        self.assertEqual(re.match('^((a)c|[ab])*?c', 'abc').groups(),
                         ('b', None))

    def test_bug_725149(self):
        # mark_stack_base restoring before restoring marks
        self.assertEqual(re.match('(a)(?:(?=(b)*)c)*', 'abb').groups(),
                         ('a', None))
        self.assertEqual(re.match('(a)((?!(b)*))*', 'abb').groups(),
                         ('a', None, None))

    def test_bug_764548(self):
        # bug 764548, re.compile() barfs on str/unicode subclasses
        try:
            unicode
        except NameError:
            return  # no problem if we have no unicode
        class my_unicode(unicode): pass
        pat = re.compile(my_unicode("abc"))
        self.assertEqual(pat.match("xyz"), None)

    def test_finditer(self):
        iter = re.finditer(r":+", "a:b::c:::d")
        self.assertEqual([item.group(0) for item in iter],
                         [":", "::", ":::"])

    def test_bug_926075(self):
        try:
            unicode
        except NameError:
            return # no problem if we have no unicode
        self.assert_(re.compile('bug_926075') is not
                     re.compile(eval("u'bug_926075'")))


    def test_bug_581080(self):
        iter = re.finditer(r"\s", "a b")
        self.assertEqual(iter.next().span(), (1,2))
        self.assertRaises(StopIteration, iter.next)

        scanner = re.compile(r"\s").scanner("a b")
        self.assertEqual(scanner.search().span(), (1, 2))
        self.assertEqual(scanner.search(), None)

    def test_bug_817234(self):
        iter = re.finditer(r".*", "asdf")
        self.assertEqual(iter.next().span(), (0, 4))
        self.assertEqual(iter.next().span(), (4, 4))
        self.assertRaises(StopIteration, iter.next)


def run_re_tests():
    from test.re_tests import benchmarks, tests, SUCCEED, FAIL, SYNTAX_ERROR
    if verbose:
        print 'Running re_tests test suite'
    else:
        # To save time, only run the first and last 10 tests
        #tests = tests[:10] + tests[-10:]
        pass

    for t in tests:
        sys.stdout.flush()
        pattern = s = outcome = repl = expected = None
        if len(t) == 5:
            pattern, s, outcome, repl, expected = t
        elif len(t) == 3:
            pattern, s, outcome = t
        else:
            raise ValueError, ('Test tuples should have 3 or 5 fields', t)

        try:
            obj = re.compile(pattern)
        except re.error:
            if outcome == SYNTAX_ERROR: pass  # Expected a syntax error
            else:
                print '=== Syntax error:', t
        except KeyboardInterrupt: raise KeyboardInterrupt
        except:
            print '*** Unexpected error ***', t
            if verbose:
                traceback.print_exc(file=sys.stdout)
        else:
            try:
                result = obj.search(s)
            except re.error, msg:
                print '=== Unexpected exception', t, repr(msg)
            if outcome == SYNTAX_ERROR:
                # This should have been a syntax error; forget it.
                pass
            elif outcome == FAIL:
                if result is None: pass   # No match, as expected
                else: print '=== Succeeded incorrectly', t
            elif outcome == SUCCEED:
                if result is not None:
                    # Matched, as expected, so now we compute the
                    # result string and compare it to our expected result.
                    start, end = result.span(0)
                    vardict={'found': result.group(0),
                             'groups': result.group(),
                             'flags': result.re.flags}
                    for i in range(1, 100):
                        try:
                            gi = result.group(i)
                            # Special hack because else the string concat fails:
                            if gi is None:
                                gi = "None"
                        except IndexError:
                            gi = "Error"
                        vardict['g%d' % i] = gi
                    for i in result.re.groupindex.keys():
                        try:
                            gi = result.group(i)
                            if gi is None:
                                gi = "None"
                        except IndexError:
                            gi = "Error"
                        vardict[i] = gi
                    repl = eval(repl, vardict)
                    if not isinstance(expected, unicode):
                        expected = unicode(expected, 'iso-8859-1')
                    if repl != expected:
                        print '=== grouping error', t,
                        print repr(repl) + ' should be ' + repr(expected)
                else:
                    print '=== Failed incorrectly', t

                # Try the match on a unicode string, and check that it
                # still succeeds.
                try:
                    result = obj.search(unicode(s, "latin-1"))
                    if result is None:
                        print '=== Fails on unicode match', t
                except NameError:
                    continue # 1.5.2
                except TypeError:
                    continue # unicode test case

                # Try the match on a unicode pattern, and check that it
                # still succeeds.
                obj=re.compile(unicode(pattern, "latin-1"))
                result = obj.search(s)
                if result is None:
                    print '=== Fails on unicode pattern match', t

                # Try the match with the search area limited to the extent
                # of the match and see if it still succeeds.  \B will
                # break (because it won't match at the end or start of a
                # string), so we'll ignore patterns that feature it.

                if pattern[:2] != '\\B' and pattern[-2:] != '\\B' \
                               and result is not None:
                    obj = re.compile(pattern)
                    result = obj.search(s, result.start(0), result.end(0) + 1)
                    if result is None:
                        print '=== Failed on range-limited match', t

                # Try the match with IGNORECASE enabled, and check that it
                # still succeeds.
                obj = re.compile(pattern, re.IGNORECASE)
                result = obj.search(s)
                if result is None:
                    print '=== Fails on case-insensitive match', t

                # Try the match with LOCALE enabled, and check that it
                # still succeeds.
                obj = re.compile(pattern, re.LOCALE)
                result = obj.search(s)
                if result is None:
                    print '=== Fails on locale-sensitive match', t

                # Try the match with UNICODE locale enabled, and check
                # that it still succeeds.
                obj = re.compile(pattern, re.UNICODE)
                result = obj.search(s)
                if result is None:
                    print '=== Fails on unicode-sensitive match', t

def test_main():
    run_unittest(ReTests)
    run_re_tests()

if __name__ == "__main__":
    test_main()
