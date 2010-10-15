# Copyright (c) 2001- Atsuo Ishimoto
# See LICENSE for details.

import _pymfclib_editor

class UndoList:
    INSERTED=0
    DELETED=1
    REPLACED=2
    GROUP=3
    ENDGROUP=4

    def __init__(self, buf):
        self._buf = buf
        self.clear()
        
    def clear(self):
        self._actions = []
        self._savePos = 0
        self._redoPos = 0
        self._closed = False
        
    def _undoInsert(self, action, mode):
        pos, s, oldpos, caretpos = action[1]
        self._buf.delete(pos, pos+len(s))
        if mode:
            mode.bufModified(pos, 0, len(s))
        self._redoPos -= 1
        
        return oldpos
        
    def _redoInsert(self, action, mode):
        pos, s, oldpos, caretpos = action[1]
        self._buf.ins(pos, s)
        if mode:
            mode.bufModified(pos, len(s), 0)
        self._redoPos += 1
        return caretpos
        
    def _undoDelete(self, action, mode):
        pos, s, oldpos, caretpos = action[1]
        self._buf.ins(pos, s)
        if mode:
            mode.bufModified(pos, len(s), 0)
        self._redoPos -= 1
        return oldpos
        
    def _redoDelete(self, action, mode):
        pos, s, oldpos, caretpos = action[1]
        self._buf.delete(pos, pos+len(s))
        if mode:
            mode.bufModified(pos, 0, len(s))
        self._redoPos += 1
        return caretpos
        
    def _undoReplace(self, action, mode):
        pos, s, delchars, oldpos, caretpos = action[1]
        self._buf.delete(pos, pos+len(s))
        self._buf.ins(pos, delchars)
        if mode:
            mode.bufModified(pos, len(delchars), len(s))
        self._redoPos -= 1
    
        return oldpos
        
    def _redoReplace(self, action, mode):
        pos, s, delchars, oldpos, caretpos = action[1]
        self._buf.delete(pos, pos+len(delchars))
        self._buf.ins(pos, s)
        if mode:
            mode.bufModified(pos, len(s), len(delchars))
        self._redoPos += 1
        return caretpos
        
    def _undo(self, mode, action, all):
        id = action[0]
        if id == self.INSERTED:
            return self._undoInsert(action, mode)
        elif id == self.DELETED:
            return self._undoDelete(action, mode)
        elif id == self.REPLACED:
            return self._undoReplace(action, mode)
        elif id == self.GROUP:
            ret = action[1].undo(mode, True)
            self._redoPos -= 1
            return ret
        
        # never reach here
        assert 0

    def undo(self, mode, all=False):
        if all:
            for action in self._actions[self._redoPos - 1::-1]:
                newpos = self._undo(mode, action, True)
        else:
            if not self.canUndo():
                raise RuntimeError()
            action = self._actions[self._redoPos - 1]
            newpos = self._undo(mode, action, True)
        return newpos
    
    def _redo(self, mode, action, all):
        id = action[0]
        if id == self.INSERTED:
            return self._redoInsert(action, mode)
        elif id == self.DELETED:
            return self._redoDelete(action, mode)
        elif id == self.REPLACED:
            return self._redoReplace(action, mode)
        elif id == self.GROUP:
            ret = action[1].redo(mode, True)
            self._redoPos += 1
            return ret
        
        # never reach here
        assert 0

    def redo(self, mode, all=False):
        if all:
            for action in self._actions[self._redoPos:]:
                newpos = self._redo(mode, action, True)
        else:
            if not self.canRedo():
                raise RuntimeError()
            action = self._actions[self._redoPos]
            newpos = self._redo(mode, action, True)
        return newpos
    
    def isDirty(self):
        return self._redoPos != self._savePos
    
    def canUndo(self):
        return self._redoPos != 0
    
    def canRedo(self):
        return self._redoPos < len(self._actions)
    
    def _putAction(self, action, arg=None):
        if self._closed:
            return False
        
        # cannot redo anymore
        del self._actions[self._redoPos:]
        if self._savePos > len(self._actions):
            self._savePos = -1

        # In group undo?
        if self._actions:
            last = self._actions[-1]
            if last[0] == self.GROUP:
                if last[1]._putAction(action, arg):
                    # remove empty group
                    if last[1]._closed and not last[1]._actions:
                        del self._actions[-1]
                        self._redoPos = len(self._actions)
                    return True

        # put to the current action if group is not found
        if action == self.ENDGROUP:
            self._closed = True
        else:
            self._actions.append((action, arg))
            self._redoPos = len(self._actions)
        return True

    def inserted(self, pos, s, oldpos, caretpos):
        self._putAction(self.INSERTED, (pos, s, oldpos, caretpos))
    
    def deleted(self, pos, s, oldpos, caretpos):
        self._putAction(self.DELETED, (pos, s, oldpos, caretpos))
    
    def replaced(self, pos, inschars, delchars, oldpos, caretpos):
        self._putAction(self.REPLACED, (pos, inschars, delchars, oldpos, caretpos))
    
    def beginGroup(self):
        self._putAction(self.GROUP, UndoList(self._buf))
    
    def endGroup(self):
        self._putAction(self.ENDGROUP)
    
    def saved(self):
        self._savePos = self._redoPos
    
    
class Buffer(_pymfclib_editor.Buffer):
    def __init__(self):
        super(Buffer, self).__init__()
        self._undo = UndoList(self)

    def _getUndoList(self):
        return self._undo
    undo = property(_getUndoList)

    def bufModified(self, pos, inslen, dellen):
        pass

    def ins(self, pos, s):
        super(Buffer, self).ins(pos, s)
        self.bufModified(pos, len(s), 0)

    def delete(self, pos, posto):
        super(Buffer, self).delete(pos, posto)
        self.bufModified(pos, 0, posto-pos)

    def replace(self, pos, posto, s):
        super(Buffer, self).replace(pos, posto, s)
        self.bufModified(pos, len(s), posto-pos)


