from pymfc.editor import bufre
import time

class TokenState(object):
    def __init__(self, name, regex, func, cursor=None):
        self.name = name
        self.regex = regex
        self.func = func
        self.cursor = cursor

STATE_NONE = 0

class Tokenizer(object):
    def __init__(self):
        self._state_pattern = {}
        self._state_func = {}

        regexes = []
        state = 1

        for tokenstate in self._getStateList():
            name = tokenstate.name
            regex = tokenstate.regex
            func = tokenstate.func
            
            regex = u'(?P<%s>%s)' % (name, regex)
            regexes.append(regex)
            self._state_pattern[name] = (func, state)
            if func:
                self._state_func[func] = func
            state += 1
        
        self._reobj = bufre.compile(u'|'.join(regexes))

    def _getStateList(self):
        return self.STATE_LIST
        
    def getToken(self, buf, pos):
        SEARCH_LEN=512
        state=STATE_NONE
        if pos:  # get current state
            state = buf.getStyle(pos-1, pos)[0]

        begin = pos
        while 1:
#            print "+++++++++++++", state
            if state != STATE_NONE:
                # find position where current state finishes
                f = self._state_func.get(state)
                if callable(f):
                    for token in f(buf, pos, state):
                        yield token
                    pos = self._pos # token function should update self._pos
                elif f:
                    # todo: searching for closing token should be done by dumb text searching
                    stop = buf.getEOL(min(pos+SEARCH_LEN, len(buf)))
                    m = f.search(buf, pos, stop)
                    if not m:
                        yield (state, begin, stop)
                        if stop == len(buf):
                            return
                        else:
                            pos = stop
                            continue
                    
                    if m.lastgroup == u"ESCAPE":
                        pos = m.end()
                        continue
                    end = m.end()
                    yield (state, begin, end)
                    pos = end

            # find next state
            if pos >= len(buf):
                return
            state=STATE_NONE
            stop = buf.getEOL(min(pos+SEARCH_LEN, len(buf)))
            m = self._reobj.search(buf, pos, stop)
            if not m:
                # no tokens found in this range
                if pos != stop:
                    yield (STATE_NONE, pos, stop)

                if stop == len(buf):
                    # finished?
                    return

                pos = stop
                continue

            else:
                # token found
                begin, end = m.span()
                if pos != begin:
                    yield (STATE_NONE, pos, begin)

                func, state = self._state_pattern[m.lastgroup] # get next state
                if not func:
                    yield (state, begin, end)

                pos = end


class Highlight(object):
    def __init__(self, buf, tokenizer):
        self._buf = buf
        self._tokenizer = tokenizer
        self._updatePos = 0       # position to begin highlighting at next time
        self._lastUpdatePos = 0   # highlighted up to this position

        self._tokenIter = None
    
    def updated(self, pos):
        self._updatePos = min(self._updatePos, self._buf.getTOL(pos))
        
    def highLight(self, mode, single=False):
        buf = self._buf
        if not self._tokenIter or (self._updatePos != self._lastUpdatePos):
            # if never highlighted or buffer have modified,
            if self._updatePos != len(buf):
                # And if highlighting have not been finished yet,
                # then start new highlighting loop.
                
                # highliting should be stared from top of modified line.
                tol = buf.getTOL(self._updatePos)
                self._tokenIter = self._tokenizer.getToken(self._buf, tol)
                self._lastUpdatePos = tol  

        if self._tokenIter:
            if not single:
                stoppos = min(len(buf), self._lastUpdatePos + 512)
                stoppos = buf.getEOL(stoppos)
            else:
                stoppos = buf.getEOL(self._lastUpdatePos)

            styles = []
            try:
                while True:
                    # get tokens
                    state, begin, end = self._tokenIter.next()
                    styles.append((state, begin, end))
                    self._lastUpdatePos = end
                    self._updatePos = end

                    styles.append((state, begin, end))

                    if end > stoppos:
                        break
            except StopIteration:
                pass
                
            if styles:
                # update character styles
                buf.setStyles(styles)
                f = styles[0][1]
                t = styles[-1][2]

                # tell windows to update screen
                for wnd in mode.getWnds():
                    wnd.onStyleUpdated(f, t)
            
            if self._lastUpdatePos < len(self._buf):
                return True  # not finished yet
            
        self._tokenIter = None
        self._lastUpdatePos = 0
        return 0
