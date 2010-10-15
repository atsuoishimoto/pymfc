# -*- coding: ShiftJIS -*-

import sys, string, time, math, collections, re
import pymfc
from pymfc import gdi, wnd, COM, menu, layout

class SearchTextDlg(wnd.Dialog):
    CONTEXT=True
    TITLE=u"文字列を検索"

    def _prepare(self, kwargs):
        super(SearchTextDlg, self)._prepare(kwargs)
        self._doc = kwargs['doc']
        
        self._layout = layout.Table(parent=self, adjustparent=True, pos=(5,5), rowgap=5, margin_bottom=5)
        row = self._layout.addRow()
        cell = row.addCell()
        cell.add(u"検索文字列: ")
        cell.add(wnd.Edit, name="edit", title=u"", width=60)
        self._layout.ctrls.edit.msglistener.CHANGE = self._onEditChange
        
        row = self._layout.addRow()
        cell = row.addCell(alignright=True)
        cell.add(wnd.OkButton, title=u"検索", name='ok')
        cell.add(None)
        cell.add(wnd.CancelButton, title=u"キャンセル", name='cancel')

        self._searchFrom = None

        self.setDefaultValue(None)
        
    def wndReleased(self):
        super(SearchTextDlg, self).wndReleased()
        self._doc = None
        
    def onOk(self, msg=None):
        text = self._layout.ctrls.edit.getText()
        if text:
            ret = self._doc.searchNext(text, self._searchFrom)
            if not ret:
                self.msgbox(u"テキストが見つかりませんでした", u"", ok=True)
                self.setResultValue(None)
                self.endDialog(self.IDCANCEL)
            else:
                lineno, nobj, col = ret
                self._searchFrom = (lineno, nobj, col+1)

    def onCancel(self, msg=None):
        self.setResultValue(None)
        self.endDialog(self.IDCANCEL)

    def _onEditChange(self, msg):
        text = self._layout.ctrls.edit.getText()
        if text:
            self._layout.ctrls.ok.enableWindow(True)
        else:
            self._layout.ctrls.ok.enableWindow(False)
    

class HR(object):
    height = 1
    def __init__(self, margin_left=0, margin_right=0):
        self.margin_left=margin_left
        self.margin_right = margin_right
        
class Node(object):
    ISBLOCK = False

    def __init__(self):
        self._children = []
        
    def free(self):
        for obj, style, action in self._children:
            if isinstance(obj, Node):
                obj.free()
        self._children = []
        
    def add(self, obj, style, action):
        # Style for block should not be specified here.
        assert (not getattr(obj, 'ISBLOCK', False)) or (not style)
        assert (isinstance(obj, (unicode, gdi.Icon, Node, HR)))
        self._children.append((obj, style, action))

    def isBlock(self):
        return self.ISBLOCK
        
    def iterElems(self):
        def f():
            stack = [(self, iter(self._children))]

            while stack:
                node, curiter = stack.pop()
                for obj, style, action in curiter:
                    if isinstance(obj, Node):
                        stack.append((node, curiter))
                        stack.append((obj, iter(obj._children)))
                        yield None, obj, True, None
                        break
                    else:
                        yield node, obj, style, action
                else:
                    yield None, node, False, None
        return f()


class Block(Node):
    ISBLOCK = True
    def __init__(self, style):
        super(Block, self).__init__()
        self.style = style

class Doc(Block):
    pass

class Background(object):
    def draw(self, row, dc, pos, width, isfirstrow, islastrow):
        pass
        
class Style(object):
    def __init__(self, font, textcolor=None, bgcolor=None, nowrap=False, 
            margin_left=0, margin_right=0, margin_top=0, margin_bottom=0,
            lineheight=1.1, listitem=None, background=None, top=False, 
            middle=False, bottom=False):
        
        self.textcolor = textcolor
        self.bgcolor = bgcolor
        
        self.font = font
        self.tm = self.font.getTextMetrics()
        self.nowrap = nowrap
        self.margin_left = margin_left
        self.margin_right = margin_right
        self.margin_top = margin_top
        self.margin_bottom = margin_bottom
        self.lineheight = lineheight
        self.top = top
        self.middle = middle

        if not top and not middle:
            bottom = True
        self.bottom = bottom
        
        if listitem is not None:
            w, h = listitem.getBitmap().getSize()
            self.listitem = (listitem, w, h)
            self.margin_left += w
        else:
            self.listitem = None
            
        self.background=background
        
class Action(object):
    def __init__(self):
        pass

    def onLButtonDown(self, wnd, node, style):
        return True

    def onLButtonClicked(self, wnd, node, style):
        pass

    def onRButtonClicked(self, wnd, node, style):
        pass

    def onMouseHovered(self, wnd, node, style):
        pass

    def onDragOver(self, wnd, node, msg):
        pass
    
    def onDrop(self, wnd, node, msg):
        pass
    
    
class ScreenBuilder:
    def __init__(self):
        pass

    def buildRow(self, width, root, dc):
        self._blocks = [root]
        self._rows = [ScreenRow(self._blocks, True)]

        # todo: Creating ScreenRow instance could be defered until text data arrives?
        # It would be more effecient and code would be shoter.

        for node, obj, style, action in root.iterElems():
            if isinstance(obj, Node):
                if obj.isBlock():
                    if style == True:
                        # begin new Node
                        self._blocks.append(obj)
                        lastrow = self._rows[-1]
                        if lastrow.isEmpty():
                            lastrow.blockStarted(obj)
                        else:
                            assert not self._rows[-1].isEmpty()
                            self._rows.append(ScreenRow(self._blocks, True))
                    else:
                        #end node
                        assert self._blocks[-1] is obj
                        
                        last = self._rows[-1]
                        if last.isEmpty():
                            # if last row is empty, remove the line. But if the line
                            # is only line in the current block, then newline.
                            if last.isfirstrow:
                                last.add(obj, u"\r", [0],   # todo: define BlankRow class to present empty row
                                    obj.style.tm.tmHeight, obj.style, None)
                            else:
                                del self._rows[-1]
                        
                        self._rows[-1].blockEnded(obj)
                        del self._blocks[-1]

                        if len(self._blocks) == 0:
                            # Document finished.
                            break
                            
                        # Add new row for next block.
                        assert not self._rows[-1].isEmpty()
                        self._rows.append(ScreenRow(self._blocks, False))
            else:
                self.splitObj(node, width, dc, obj, style, action)

        for row in self._rows:
            row.completed()

        return self._rows

    def splitObj(self, node, width, dc, obj, style, action):
        assert node
        if isinstance(obj, unicode):
            self.splitText(node, width, dc, obj, style, action)
        elif isinstance(obj, HR):
            self._rows[-1].add(node, obj, [0], obj.height, style, action)
            assert not self._rows[-1].isEmpty()
            self._rows.append(ScreenRow(self._blocks, False))
        else:
            # icon
            w, h = obj.getBitmap().getSize()
            currow = self._rows[-1]
            if (currow.isEmpty()) or (currow.width + w < width):
                currow.add(node, obj, [w], h, style, action)
            else:
                assert not self._rows[-1].isEmpty()
                self._rows.append(ScreenRow(self._blocks, False))
                self._rows[-1].add(node, obj, [w], h, style, action)

    WRAPCHARS = unicode(string.ascii_letters)
    KINSOKUCHARS=u"。、,.!;"
    
    def splitText(self, node, width, dc, s, style, action):
        dc.selectObject(style.font)
        
        lines = [l.expandtabs() for l in s.split(u"\n")]
        nlines = len(lines)
        for line in lines:
            dx, (w,h) = dc.getTextExtentEx(line, sys.maxint) # todo: calculate text extent when creating node.
            for i in range(len(dx)-1, 0, -1):
                dx[i] = dx[i] - dx[i-1]

            if self._blocks[-1].style.nowrap:
                self._rows[-1].add(node, line, dx, h, style, action)
            else:
                while line:
                    currow = self._rows[-1]
                    w = width - currow.width
                    
                    for n, p in enumerate(dx):
                        w -= p
                        if w < 0 and line[n] != u' ':
                            break
                    else:
                        n += 1

                    if n == 0:
                        # no more room!
                        if currow.isEmpty():
                            # row should contain at least one character
                            n = 1
                        else:
                            row = ScreenRow(self._blocks, False)
                            if line[0] in self.KINSOKUCHARS:
                                items, remains = self.kinsoku(currow.items)
                                currow.setItems(items)
                                row.setItems(remains)
                            elif line[0] in self.WRAPCHARS:
                                items, remains = self.wordWrap(currow.items)
                                currow.setItems(items)
                                row.setItems(remains)
                                
                            assert not self._rows[-1].isEmpty()
                            self._rows.append(row)
                            continue

                    s = line[:n]
                    d = dx[:n]
                    currow.add(node, s, d, h, style, action)

                    line = line[n:]
                    dx = dx[n:]
            
            nlines = nlines - 1
            if nlines != 0:
                if self._rows[-1].isEmpty():
                    self._rows[-1].add(node, u"\r", [0], 
                        style.tm.tmHeight, style, None)

                assert not self._rows[-1].isEmpty()
                self._rows[-1].setNewLineRow()
                self._rows.append(ScreenRow(self._blocks, False))

    def kinsoku(self, items):
        # find word break
        for i_obj in range(len(items)-1, -1, -1):
            node, obj, widths, height, style, action = items[i_obj]
            if not isinstance(obj, unicode):
                i_pos = None
                break
            
            for i_pos in range(len(obj)-2, -1, -1):
                c = obj[i_pos]
                if c not in unicode(string.ascii_letters):
                    break
            else:
                continue
                
            break
        else:
            return items, []
        
        return self._splitItems(items, i_obj, i_pos)
        
    def wordWrap(self, items):
        # find word break
        for i_obj in range(len(items)-1, -1, -1):
            node, obj, widths, height, style, action = items[i_obj]
            if not isinstance(obj, unicode):
                i_pos = None
                break
            for i_pos in range(len(obj)-1, -1, -1):
                c = obj[i_pos]
                if c == u' ' or (c not in unicode(string.ascii_letters)):
                    break
            else:
                continue
                
            break
        else:
            return items, []
        
        return self._splitItems(items, i_obj, i_pos)
        
    def _splitItems(self, items, i_obj, i_pos):
        # split row
        obj = items[i_obj][1]

        if not isinstance(obj, unicode):
            newitems = items[:i_obj+1]
            rest = items[i_obj+1:]
        else:
            if len(items) == 1 and len(items[0][1]) == 1:
                # each line should contain at least one character.
                return items, []

            node, obj, widths, height, style, action = items[i_obj]
            if i_pos == len(obj)-1:
                pre = [(node, obj, widths, height, style, action)]
                post = []
            else:
                pre = [(node, obj[:i_pos+1], widths[:i_pos+1], height, style, action)]
                post =[(node, obj[i_pos+1:], widths[i_pos+1:], height, style, action)] 
            
            newitems = items[:i_obj] + pre
            rest = post + items[i_obj+1:]
        
        return newitems, rest



class ScreenRow(object):
    @property
    def items(self):
        return self._objs
        
    def __init__(self, blocks, isfirstrow):
        self._objs = []  # list of tuple(node, obj, widths, height, style, action)
        assert isinstance(blocks, list)
        self.blocks = blocks[:]  # Beware blocks ought to be copied.
        self.isfirstrow = isfirstrow
        self._firstrowof = set() # indicates blocks which this row is first-row
        self._lastrowof = set()   # indicates blocks which this row is last-row
        self._hasnewline = False
        if isfirstrow:
            self._firstrowof.add(self.blocks[-1])

        self.style = self.blocks[-1].style
        self.height = 0
        self.ascent = 0
        self.descent = 0
        
        self._margin_left = sum(block.style.margin_left for block in self.blocks)
        self._margin_right = sum(block.style.margin_right for block in self.blocks)
        self.width = self._margin_left+self._margin_right

    def add(self, node, obj, widths, height, style, action):
        self._objs.append((node, obj, widths, height, style, action))
        self.width += sum(widths)

    def blockStarted(self, block):
        assert not self._objs
        self.blocks.append(block)
        self._firstrowof.add(block) # For newly appended blocks, 
                                    # this row is always first-row.
        self.isfirstrow = True
        self.style = self.blocks[-1].style
        self._margin_left += self.style.margin_left
        self._margin_right += self.style.margin_right
        self.width = self._margin_left+self._margin_right
        
    def blockEnded(self, block):
        self._lastrowof.add(block) # For newly appended blocks, 
                                   

    def setItems(self, objs):
        self._objs = objs
        self.width = self._margin_left+self._margin_right

        for node, obj, widths, height, style, action in self._objs:
            self.width += sum(widths)

    def setNewLineRow(self):
        self._hasnewline = True

    def completed(self):
        if self.isfirstrow and self.style.listitem:
            icon, w, h = self.style.listitem
            self.ascent = max(self.ascent, h)

        leading = 0
        imgheight = 0
        for node, obj, widths, height, style, action in self._objs:
            self.ascent = max(self.ascent, style.tm.tmAscent-style.tm.tmInternalLeading)
            leading = max(leading, style.tm.tmInternalLeading+style.tm.tmExternalLeading)
            self.descent = max(self.descent, style.tm.tmDescent)

            if not isinstance(obj, unicode):
                imgheight = max(imgheight, height)

        self._margin_top = sum(block.style.margin_top for block in self._firstrowof)
        self._margin_bottom = sum(block.style.margin_bottom for block in self._lastrowof)
        
        # Images should be placed above the baseline.
        d = imgheight - (self.ascent+leading)
        if d > 0:
            leading += d

        if self.style.lineheight >= 1.0:
            h = self.ascent+self.descent
            d = int(math.ceil(h*self.style.lineheight))-h
            
            if d < leading:
                d = leading

            self.height = h+d
        else:
            self.height = int(math.ceil((self.ascent+self.descent)*self.style.lineheight))

        self.height += self._margin_top + self._margin_bottom

    def isEmpty(self):
        return not self._objs
        
    def isBlank(self):
        for node, obj, widths, height, style, action in self._objs:
            if not isinstance(obj, unicode):
                return False
            if obj.strip():
                return False
        return True
        
    def getEndPos(self):
        return len(self._objs)-1, len(self._objs[-1][2])
        
    def hasNode(self, node):
        for _node, obj, widths, height, style, action in self._objs:
            if node is _node:
                return True

        
    def getLocation(self, pos):
        x, y = pos
        w = self._margin_left
        for nobj, (node, obj, widths, height, style, action) in enumerate(self._objs):
            s = sum(widths)
            if x >= w + s:
                w += s
                continue
            
            for nchar, cw in enumerate(widths):
                if x < w + cw:
                    return nobj, nchar
                w += cw
        return self.getEndPos()
        

    def getObject(self, nobj, nchar):
        node, obj, widths, height, style, action = self._objs[nobj]
        return node, style, action

    def _drawText(self, dc, pos, obj, widths, height, style, action):
        if obj <> u"\r":
            dc.selectObject(style.font)
            if style.textcolor is not None:
                dc.setTextColor(style.textcolor)

            if style.bgcolor is not None:
                dc.setBkColor(style.bgcolor)
                dc.setBkMode(transparent=False)
                opaque = True
            else:
                opaque = False
                dc.setBkMode(transparent=True)
            
            
            if style.top:
                x, y = pos[0], pos[1]+self._margin_top
            elif style.middle:
                x, y = pos[0], pos[1]+self._margin_top+(self.height-self._margin_top-self._margin_bottom)/2-(self.descent+style.tm.tmAscent)/2
            else:
                x, y = pos[0], pos[1]+self.height-self.descent-style.tm.tmAscent-self._margin_bottom
                
            rc = pos[0], pos[1]+self._margin_top, pos[0]+sum(widths), pos[1]+self.height-self._margin_bottom
            dc.textOut(obj, (x, y), rc=rc, opaque=opaque)

    def _drawIcon(self, dc, pos, obj, widths, height, style, action):
        if style.top:
            pos = pos[0], pos[1]+self._margin_top
        elif style.middle:
            pos = pos[0], pos[1]+self._margin_top+(self.height-self._margin_top-self._margin_bottom)/2-(self.descent+height)/2
        else:
            pos = pos[0], pos[1]+self.height-self.descent-height-self._margin_bottom
        l, t, r, b = pos[0], pos[1], pos[0]+widths[0], pos[1]+height
        if style.bgcolor is not None:
            dc.fillSolidRect((l, t, r, b), style.bgcolor)
        dc.drawIcon(pos, obj, (widths[0], height), normal=True)

    def _drawHR(self, dc, pos, obj, width, widths, height, style, action):
        if style.bgcolor is not None:
            l, t, r, b = pos[0], pos[1], pos[0]+width, pos[1]+self.height
            dc.fillSolidRect((l, t, r, b), style.bgcolor)

        l, t, r, b = (pos[0]+obj.margin_left, 
            pos[1]+(self.height-self._margin_top-self._margin_bottom)/2,
            pos[0]+width-obj.margin_right, 
            pos[1]+(self.height-self._margin_top-self._margin_bottom)/2)

        color = style.textcolor if style.textcolor is not None else 0
        pen = gdi.Pen(color=color, solid=True)
        dc.selectObject(pen)
        dc.moveTo((l, t))
        dc.lineTo((r, b))
        
    def _getSelRange(self, lineno, selrange):
        selfrom, selto = selrange
        (from_lineno, from_obj, from_col), (to_lineno, to_obj, to_col) = selrange
        
        if from_lineno <= lineno <= to_lineno:
            selfrom_obj = selfrom_col = selto_obj = selto_col = None
            if from_lineno < lineno:
                selfrom_obj = 0
                selfrom_col = 0

            if from_lineno == lineno:
                selfrom_obj = from_obj
                selfrom_col = from_col
            
            if to_lineno > lineno:
                selto_obj = len(self._objs)
                selto_col = None

            if to_lineno == lineno:
                selto_obj = to_obj
                selto_col = to_col
            return selfrom_obj, selfrom_col, selto_obj, selto_col
        else:
            return None
            
        
    def _showSelection(self, dc, pos, lineno, selrange):
        invrange = self._getSelRange(lineno, selrange)
        if not invrange:
            return
            
        invfrom_obj, invfrom_col, invto_obj, invto_col = invrange

        x_from = self._margin_left
        for n in range(invfrom_obj):
            node, obj, widths, height, style, action = self._objs[n]
            x_from += sum(widths)
        
        if invfrom_obj < len(self._objs):
            node, obj, widths, height, style, action = self._objs[invfrom_obj]
            x_from += sum(widths[:invfrom_col])

        x_to = self._margin_left
        for n in range(invto_obj):
            node, obj, widths, height, style, action = self._objs[n]
            x_to += sum(widths)

        if invto_obj < len(self._objs):
            node, obj, widths, height, style, action = self._objs[invto_obj]
            x_to += sum(widths[:invto_col])
        
        dc.invertRect((x_from, pos[1], x_to, pos[1]+self.height))
        
    def _getNodeRange(self, l, target):
        objs = iter(self._objs)
        r = 0
        for node, obj, widths, height, style, action in objs:
            if node is target:
                r = l + sum(widths)
                break
            l += sum(widths)
        else:
            return
        
        for node, obj, widths, height, style, action in objs:
            if node is not target:
                break
            r += sum(widths)
        return l, r
        
    def draw(self, dc, pos, width, lineno, selrange, activenode, hoveredNode):
        right = pos[0]+width
        contentpos = pos[0]+self._margin_left, pos[1]
        
        for block in reversed(self.blocks):
            if block.style.bgcolor is not None:
                l, t = pos
                dc.fillSolidRect((l, t, l+width, t+self.height), block.style.bgcolor)
                break

        for block in self.blocks:
            style = block.style
            if style.background:
                style.background.draw(self, dc, pos, width, 
                    block in self._firstrowof, block in self._lastrowof)

        if self.isfirstrow and self.style.listitem:
            l, t = contentpos
            icon, w, h = self.style.listitem
            l -= w
            t = t+self.height-self.descent-h-self._margin_bottom
            dc.drawIcon((l, t), icon, (w, h), normal=True)

        l, t = contentpos
        for node, obj, widths, height, style, action in self._objs:
            if isinstance(obj, unicode):
                self._drawText(dc, (l, t), obj, widths, height, style, action)
            elif isinstance(obj, HR):
                w = right - l - self._margin_right
                self._drawHR(dc, (l, t), obj, w, widths, height, style, action)
            else:
                self._drawIcon(dc, (l, t), obj, widths, height, style, action)

            l += sum(widths)
        
        if selrange:
            self._showSelection(dc, contentpos, lineno, selrange)

        if activenode:
            l, t = contentpos
            noderange = self._getNodeRange(l, activenode)
            if noderange:
                l, r = noderange
                dc.drawFocusRect((l, t, r, t+self.height))

        if hoveredNode:
            l, t = contentpos
            noderange = self._getNodeRange(l, hoveredNode)
            if noderange:
                l, r = noderange
                dc.drawEdge((l, t, r, t+self.height-self._margin_bottom), raisedinner=True, raisedouter=True, bottom=True)


            
    def iterRowText(self, selfrom_obj, selfrom_col, selto_obj, selto_col):
        if selfrom_obj >= len(self._objs):
            yield 0, 0, 0, u''
            return

        # get first object
        node, obj, widths, height, style, action = self._objs[selfrom_obj]
        if isinstance(obj, unicode):
            if selto_obj != selfrom_obj:
                s = obj[selfrom_col:]
                if s:
                    yield selfrom_obj, selfrom_col, len(obj), s
            else:
                s = obj[selfrom_col:selto_col]
                if s:
                    yield selfrom_obj, selfrom_col, selto_col, s
        
        if selfrom_obj == selto_obj:
            return
        
        # get center objects
        for n in range(selfrom_obj+1, selto_obj):
            if n >= len(self._objs):
                break
            node, obj, widths, height, style, action = self._objs[n]
            if isinstance(obj, unicode):
                if obj:
                    yield n, 0, len(obj), obj
        
        # get last object
        if (selto_obj < len(self._objs)) and (selto_obj != selfrom_obj):
            node, obj, widths, height, style, action = self._objs[selto_obj]
            if isinstance(obj, unicode):
                ret = obj[:selto_col]
                if ret:
                    yield selto_obj, 0, selto_col, ret
        
    def getSelText(self, lineno, selrange):
        selrange = self._getSelRange(lineno, selrange)
        if not selrange:
            return u''

        selfrom_obj, selfrom_col, selto_obj, selto_col = selrange
        ret = u"".join(ret[3] for ret in self.iterRowText(
                    selfrom_obj, selfrom_col, selto_obj, selto_col))

        if ret and ret == u'\r':
            return u"\n"

        if self._hasnewline or self._lastrowof:
            if selto_obj >= len(self._objs):
                ret += u'\n'
            elif selto_obj == len(self._objs)-1:
                node, obj, widths, height, style, action = self._objs[selto_obj]
                if isinstance(obj, unicode):
                    if selto_col >= len(obj):
                        ret += u'\n'
                else:
                    ret += u'\n'
        return ret
    
    def hasLineBreak(self):
        return self._hasnewline or self._lastrowof

class Screen(object):
    def __init__(self):
        self._rows = []
        self._activeNode = None
        self._hoveredNode = None
        
    def setRows(self, rows):
        self._rows = rows
        
    def setActiveNode(self, node):
        self._activeNode = node
        
    def setHoveredNode(self, node):
        self._hoveredNode = node

    def getHoveredNode(self):
        return self._hoveredNode

    def getRow(self, pos):
        lineno, nobj, nchar = pos
        return self._rows[lineno]
        
    def iterRows(self, n):
        while n < len(self._rows):
            yield self._rows[n]
            n += 1

    def getObject(self, pos):
        lineno, nobj, nchar = pos
        return self._rows[lineno].getObject(nobj, nchar)

    def draw(self, dc, rc, top, selrange):
        l = rc[0]
        t = rc[1]
        width = rc[2]-rc[0]
        lineno = top
        for row in self._rows[top:]:  # todo: avoid list copy
            row.draw(dc, (l, t), width, lineno, selrange, self._activeNode, self._hoveredNode)
            t += row.height
            if t > rc[3]:
                break
            lineno += 1

    def getRowCount(self):
        return len(self._rows)
        
    def getHeight(self):
        return sum(row.height for row in self._rows)
        
    def getPageBottom(self, height, top):
        pos = top
        while pos < len(self._rows):
            row = self._rows[pos]
            if row.height >= height:
                return max(top, pos-1)
            height -= row.height
            pos += 1
        else:
            return len(self._rows)-1 if self._rows else 0
        
    def getPageTop(self, height, bottom):
        total = self._rows[bottom].height
        while bottom > 0:
            row = self._rows[bottom-1]
            total += row.height
            if height < total:
                return bottom
            bottom -= 1
        return 0
        
    def getPrevPage(self, height, top):
        total = self._rows[top].height
        while top > 0:
            top -= 1
            row = self._rows[top]
            total += row.height
            if height <= total:
                return top
        return 0
        
    def getLastPage(self, height):
        if not self._rows:
            return 0
        total = self._rows[-1].height
        n = len(self._rows)-1
        while n >= 1:
            row = self._rows[n-1]
            total += row.height
            if total > height:
                break
            n -= 1
        return n
        
    def getLocation(self, pos, top):
        # returns tuple (rowno, obj, index) or None
        x, y = pos
        
        h = 0
        n = top
        for row in self._rows[top:]:
            h += row.height
            if y < h:
                loc = row.getLocation(pos)
                if not loc:
                    return
                return n, loc[0], loc[1]
            n += 1

    def getSelText(self, selrange):
        if selrange and selrange[0] and selrange[1]:
            selrange = sorted(selrange)
        else:
            return u''

        ret = []
        for n, row in enumerate(self._rows):
            s = row.getSelText(n, selrange)
            if s:
                ret.append(s)
        return u"".join(ret)

    def getAllRange(self):
        f = (0,0,0)
        if not self._rows:
            return f, f
        else:
            lastpos = self._rows[-1].getEndPos()
            return f, (len(self._rows)-1, lastpos[0], lastpos[1])
    
    def findNodeRow(self, node):
        for n, row in enumerate(self._rows):
            if row.hasNode(node):
                f = n
                break
        else:
            return None
        
        for n, row in enumerate(self._rows[n+1:]):
            if not row.hasNode(node):
                t = n
                break
        else:
            t = len(self._rows)
        
        return (f, t)
        
    def iterTextLines(self, posfrom):
        if posfrom is None:
            posfrom = (0, 0, 0)
        from_lineno, from_obj, from_col = posfrom
        
        line = []
        positions = []
        nrow = from_lineno
        
        for row in self._rows[from_lineno:]:
            endobj, endcol = row.getEndPos()
            for nobj, colfrom, colto, str in row.iterRowText(from_obj, from_col, endobj, endcol):
                positions.append((nrow, nobj, colfrom, colto, str))
                line.append(str)
                
            if row.hasLineBreak():
                yield positions, u"".join(line)
                positions = []
                line = []
            
            from_obj = from_col = 0
            nrow += 1
        
        if positions:
            yield positions, u"".join(line)
            
    re_wordchar = ur"(?P<WORDCHAR>[a-zA-Z0-9_]+)"
    re_lf = ur"(?P<LF>\u000a)"
    re_ws = ur"(?P<WS>[\u0009\u000b-\u000d\u0020]+)"
    re_cntl = ur"(?P<CNTL>[\u0000-\u0008\u000e-\u001f\u007f]+)"
    re_symbol = ur"(?P<SYMBOL>[\u0021-\u002f\u003a-\u0040\u005b-\u0060\u007b-\u007d]+)"
    
    # both hiragana and katakana contains \u30fc(KATAKANA-HIRAGANA PROLONGED SOUND MARK)
    re_hiragana = ur"(?P<HIRAGANA>[\u3040-\u309f\u30fc]+)" 
    re_katakana = ur"(?P<KATAKANA>[\u30a0-\u30ff\u30fc]+)"
    re_half_kana = ur"(?P<HALF_KANA>[\uff61-\uff9f]+)"
    re_full_ws = ur"(?P<FULL_WS>\u3000+)"
    re_cjk_symbol = ur"(?P<CJK_SYMBOL>[\u3001-\u303f]+)"
    re_full_alnum = ur"(?P<FULL_ALNUM>[\uff10-\uff19\uff21-\uff3a\uff41-\uff5a]+)"
    re_full_symbol = ur"(?P<FULL_SYMBOL>[\uff00-\uff0f\uff20\uff3b-\uff40\uff5b-\uff60\uffa0-\uffef]+)"

    re_wordbreak = re.compile(u"|".join([
        re_wordchar, re_lf, re_ws, re_cntl, re_symbol, re_hiragana, 
        re_katakana, re_half_kana, re_full_ws, re_cjk_symbol, re_full_alnum, 
        re_full_symbol]))

    def iterTextWords(self, from_lineno):
        # find top row of current text
        texttop_lineno = from_lineno
        while texttop_lineno > 0 and not self._rows[texttop_lineno-1].hasLineBreak():
            texttop_lineno -= 1

        for objs, line in self.iterTextLines((texttop_lineno, 0, 0)):
            # break line into words
            last = 0
            words = []
            for m in self.re_wordbreak.finditer(line, 0):
                start = m.start()
                end = m.end()
                s = m.group()
                
                if start != last:
                    words.append((last, start, s[last:start]))
                
                words.append((start, end, s))
                last = end
            
            if last != len(line):
                words.append((last, len(line), line[last:]))
            
            if not objs or not words:
                return
                
            iterobjs = iter(objs)
            nrow, nobj, colfrom, colto, str = iterobjs.next()
            for f, t, word in words:
                wordlen = t-f
                wordstart = (nrow, nobj, colfrom)
                while wordlen:
                    if colfrom == colto:
                        nrow, nobj, colfrom, colto, str = iterobjs.next()

                    objlen = colto-colfrom
                    if wordlen <= objlen:
                        wordend = (nrow, nobj, colfrom+wordlen)
                        colfrom += wordlen
                        wordlen = 0
                    else:
                        wordlen -= objlen
                        colfrom = colto
                        
                yield (wordstart, wordend, word)

    def search(self, s, posfrom):
        assert s
        if posfrom is None:
            posfrom = (0, 0, 0)

        s = s.lower()
        for objs, line in self.iterTextLines(posfrom):
            index = line.lower().find(s)
            if index == -1:
                continue
            
            curcol = 0
            for nrow, nobj, colfrom, colto, str in objs:
                strlen = len(str)
                if curcol+strlen > index:
                    f_matchrow = nrow
                    f_matchobj = nobj
                    f_matchcol = index-curcol+colfrom
                    break

                curcol += strlen
            else:
                assert 0 # never reach here
                
            endindex = index+len(s)
            curcol = 0
            for nrow, nobj, colfrom, colto, str in objs:
                strlen = len(str)
                if curcol+strlen >= endindex:
                    t_matchrow = nrow
                    t_matchobj = nobj
                    t_matchcol = endindex-curcol+colfrom
                    break

                curcol += strlen
            else:
                t_matchrow = nrow
                t_matchobj = nobj
                t_matchcol = colto
                
            return ((f_matchrow, f_matchobj, f_matchcol), (t_matchrow, t_matchobj, t_matchcol))
            
        
        

class FancyTextWnd(wnd.Wnd):
    MOUSEACTIVATE = True
    NOHIDESEL = False
    def _prepare(self, kwargs):
        super(FancyTextWnd, self)._prepare(kwargs)
        self._screenWidth = None
        self._doc = None
        self._showvbar = False
        self._vpos = 0
        self._lastScrollPage = 0
        self._selRange = []
        self._mouseSelecting = False
        self._mouseCheckTimer = None
        self._clickedAt = None
        self._mouseMoved = False
        self._lastSearch = None
        
        self._screen = Screen()
        self.msgproc.PAINT = self._onPaint
        self.msgproc.SETCURSOR = self._onSetCursor

        self.msgproc.CREATE = self._onCreate
        self.msglistener.SIZE = self._onSize
        self.msglistener.KEYDOWN = self._onKeyDown
        self.msglistener.VSCROLL = self._onVScroll
        self.msglistener.LBUTTONDOWN = self._onLButtonDown
        self.msglistener.LBUTTONUP = self._onLButtonUp
        self.msglistener.LBUTTONDBLCLK = self._onLButtonDblClk
        self.msglistener.RBUTTONDOWN = self._onRButtonDown
        self.msglistener.RBUTTONUP = self._onRButtonUp
        self.msglistener.MOUSEMOVE = self._onMouseMove
        self.msglistener.MOUSELEAVE = self._onMouseLeave
        self.msglistener.MOUSEHOVER = self._onMouseHover
        self.msglistener.CANCELMODE = self._onCancelMode
        self.msglistener.SETFOCUS = self._onSetFocus
        self.msglistener.KILLFOCUS = self._onKillFocus
        
        self.msgproc.MOUSEWHEEL = self._onMouseWheel
        
    def wndReleased(self):
        super(FancyTextWnd, self).wndReleased()
        if self._doc:
            self._doc.free()
        self._doc = None
        self._screen = None
        self._dropTarget = None
        self._mouseCheckTimer = None
        
    def setDocument(self, doc):
        if self._doc:
            self._doc.free()
            
        self._vpos = 0
        self._screen = Screen()
        self._doc = doc
        self._screenWidth = None
        
        if self.getHwnd():
            rc = self.getClientRect()
            width = rc[2]-rc[0]

            self._updateRows(width)
            self._updateScrollBar()
            self.invalidateRect(None, erase=False)
        
    def showNode(self, node):
        noderows = self._screen.findNodeRow(node)
        if not noderows:
            return
        self._ensureVisible(noderows[0])

    def getSelText(self):
        return self._screen.getSelText(self._selRange)

    def setWidth(self, width):
        assert self.getHwnd()

        self._updateRows(width)
        self.invalidateRect(None, erase=False)
        self._updateScrollBar()

    def _updateRows(self, width):
        if not self.getHwnd():
            return

        self._selRange = []
        if not self._doc:
            self._screen.setRows([])
            self._vpos = 0
            return

        if self._screenWidth is not None and self._screenWidth == width:
            return

        self._screenWidth = width

        dc = gdi.ClientDC(self)
        try:
            rows = ScreenBuilder().buildRow(width, self._doc, dc)
#            if not self._showvbar:
#                # Vertical sbar is hidden. Remove rows out of screen bounds.
#                for n, row in enumerate(rows):
#                    if height - row.height < 0:
#                        break
#                    height -= row.height
#                else:
#                    n = len(rows)
#
#                if n == 0:
#                    # One row, at least.
#                    n = 1
#                rows = rows[:n]
#
            self._screen.setRows(rows)
        finally:
            dc.release()

    def _onCreate(self, msg):
        self._showvbar = self.getWindowStyle().vscroll
        self._dropTarget = COM.OleDropTarget()
        self._dropTarget.register(self)

        return self.defWndProc(msg)

    def _onSize(self, msg):
        rc = self.getClientRect()
        width = rc[2]-rc[0]

        self._updateRows(width)
        self.invalidateRect(None, erase=False)
        self._updateScrollBar()
        
    def _paint(self, dc, rc):
        wndrc = self.getClientRect()
        if self._doc.style.bgcolor is not None:
            dc.fillSolidRect(wndrc, self._doc.style.bgcolor)
        else:
            dc.fillSolidRect(rc, 0xffffff)

        selrange = None
        if self.NOHIDESEL or self.getFocus() == self:
            if self._selRange and self._selRange[0] and self._selRange[1]:
                selrange = sorted(self._selRange)
        
        self._screen.draw(dc, wndrc, self._vpos, selrange)
        
    def _onPaint(self, msg):
        if not self._doc:
            return self.defWndProc(msg)
            
        dc = gdi.PaintDC(self)
        try:
            rc = dc.rc
            wndrc = self.getClientRect()

            paintdc = dc.createCompatibleDC()
            bmp = dc.createCompatibleBitmap(wndrc[2]-wndrc[0], wndrc[3] - wndrc[1])
            orgbmp = paintdc.selectObject(bmp)
            
            self._paint(paintdc, rc)
            dc.bitBlt(rc, paintdc, (rc[0], rc[1]), srccopy=True)
            paintdc.selectObject(orgbmp)

        finally:
            dc.endPaint()
        
    def _onSetCursor(self, msg):
        if not msg.htclient:
            return self.defWndProc(msg)
            
        try:
            pos = self.getCursorPos()
        except pymfc.Win32Exception:
            return self.defWndProc(msg)

        pos = self._screen.getLocation(pos, self._vpos)

        if pos and self._screen.getRow(pos).getEndPos() != pos[1:]:
            node, style, action = self._screen.getObject(pos)
            if action:
                cursor = gdi.Cursor(hand=True)
                cursor.setCursor()
                return

        cursor = gdi.Cursor(ibeam=True)
        cursor.setCursor()
        
    def _vscroll(self, newpos):
        rc = self.getClientRect()
        height = rc[3]-rc[1]
        lastpage = self._screen.getLastPage(height)
        newpos = max(min(newpos, lastpage), 0)
        if newpos != self._vpos:
            self._vpos = newpos
            self.invalidateRect(None, erase=False)
            self._updateScrollBar()
            self.updateWindow()
        
    def lineDown(self):
        newpos = self._vpos+1
        self._vscroll(newpos)
        
    def lineUp(self):
        newpos = self._vpos-1
        self._vscroll(newpos)
        
    def pageDown(self):
        rc = self.getClientRect()
        height = rc[3]-rc[1]
        newpos = self._screen.getPageBottom(height, self._vpos)
        self._vscroll(newpos)
        
    def pageUp(self):
        rc = self.getClientRect()
        height = rc[3]-rc[1]
        newpos = self._screen.getPrevPage(height, self._vpos)
        self._vscroll(newpos)
        
    def _onVScroll(self, msg):
        if msg.linedown:
            self.lineDown()
        elif msg.lineup:
            self.lineUp()
        elif msg.pagedown:
            self.pageDown()
        elif msg.pageup:
            self.pageUp()
        elif msg.bottom:
            rc = self.getClientRect()
            self._vscroll(self._screen.getLastPage(rc[3]-rc[1]))
        elif msg.top:
            self._vscroll(0)
        elif msg.thumbtrack:
            info = self.getScrollInfo(vert=True)
            newpos = info.trackpos
            if info.page + newpos >= info.max:
                rc = self.getClientRect()
                height = rc[3]-rc[1]
                lastpage = self._screen.getLastPage(height)

                newpos = lastpage
            self._vscroll(newpos)
            
    def _updateScrollBar(self):
        
        if not self.getHwnd():
            return

        if not self._showvbar:
            return
#        print time.clock(), ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
#        if self._screen._rows:
#            print u"".join(d for a, b, c, d in self._screen._rows[0].iterRowText(0,0,1000,1000))
        rc = self.getClientRect()
        height = rc[3]-rc[1]


        if self._screen.getHeight() < height:
            self._vpos = 0
        else:
            self._vpos = min(self._vpos, self._screen.getLastPage(height))

        endpos = self._screen.getPageBottom(height, self._vpos)
        nrows = self._screen.getRowCount()

        if nrows == endpos+1 and self._vpos == 0:
            self.setScrollInfo(vert=True, min=0, max=0, pos=0, redraw=True)
            self.showScrollBar(vert=True, horz=False, show=False)
        else:
            self.showScrollBar(vert=True, horz=False, show=True)
            self._lastScrollPage = endpos-self._vpos+1
            self.setScrollInfo(vert=True, min=0, 
                    max=self._screen.getRowCount()-1, pos=self._vpos, 
                    page=self._lastScrollPage, redraw=True)

    def copySelectedText(self):
        text = self.getSelText()
        if text:
            s = u"\r\n".join(text.splitlines())
            self.openClipboard()
            try:
                self.emptyClipboard()
                self.setClipboardText(s)
            finally:
                self.closeClipboard()
        
    def selectAll(self):
        if self._screen.getRowCount():
            selfrom, selto = self._screen.getAllRange()
            self._selRange = [selfrom, selto]
            self.invalidateRect(None, erase=False)
            
    def _onKeyDown(self, msg):
        shift = wnd.getKeyState(wnd.KEY.SHIFT).down
        ctrl = wnd.getKeyState(wnd.KEY.CONTROL).down
        alt = wnd.getKeyState(wnd.KEY.MENU).down

        if msg.key == wnd.KEY.DOWN:
            self.lineDown()
        elif msg.key == wnd.KEY.UP:
            self.lineUp()
        elif msg.key == wnd.KEY.PGDN:
            self.pageDown()
        elif msg.key == wnd.KEY.PGUP:
            self.pageUp()
        elif msg.key == wnd.KEY.HOME:
            self.showFirstPage()
        elif msg.key == wnd.KEY.END:
            self.showLastPage()
        elif (msg.key == ord('C')) and ctrl and not shift and not alt:
            self.copySelectedText()
        elif (msg.key == ord('A')) and ctrl and not shift and not alt:
            self.selectAll()
        elif (msg.key == ord('F')) and ctrl and not shift and not alt:
            self.searchText(None, None)
        elif msg.key == wnd.KEY.F3:
            self.searchAgain()
            
    def _onLButtonDown(self, msg):
        if self.MOUSEACTIVATE:
            top = self.getTopWnd()
            if top:
                top.setActiveWindow()
            self.setFocus()

        pos = self._screen.getLocation((msg.x, msg.y), self._vpos)
        if not pos:
            return

        if msg.shift:
            # shift key pressed. Extend current selection
            if self._selRange:
                self._selRange = [self._selRange[0], pos]
            else:
                selfrom, selto = self._screen.getAllRange()
                self._selRange = [selfrom, pos]
            self.invalidateRect(None, erase=False)
            return
                
        self._selRange = [pos, None]
        
        self.setCapture()
        self._mouseCheckTimer = wnd.TimerProc(80, self._onMouseCheckTimer, self)
        self._mouseSelecting = True
        self._clickedAt = self.getCursorPos()
        self._mouseMoved = False
        
        if self._screen.getRow(pos).getEndPos() != pos[1:]:
            ret = self._screen.getObject(pos)
            if ret:
                node, style, action = ret
                if action:
                    self._screen.setActiveNode(node)
                    self.invalidateRect(None, erase=False)
                    self.updateWindow()
                    ret = action.onLButtonDown(self, node, style)
                    if not ret:
                        self._onCancelMode(None)
                        self._screen.setActiveNode(None)

                    if not wnd.getKeyState(wnd.KEY.LBUTTON).down:
                        if ret:
                            # action.onLButtonDown()で、Drag&Drop等によりLButtonUpが発生した場合
                            self._onLButtonUp(msg)

    def _onMouseHover(self, msg):
        pos = self._screen.getLocation((msg.x, msg.y), self._vpos)
        if pos and self._screen.getRow(pos).getEndPos() != pos[1:]:
            ret = self._screen.getObject(pos)
            if ret:
                node, style, action = ret
                if action:
                    action.onMouseHovered(self, node, style)
        
    def _onMouseLeave(self, msg):
        if self._screen.getHoveredNode():
            self._screen.setHoveredNode(None)
            self.invalidateRect(None, erase=False)
        

    def _onMouseCheckTimer(self):
        self._onMouseMove(None)
        xpos, ypos = self.getCursorPos()
        
        if self._showvbar:
            if ypos < 0:
                self.lineUp()
            else:
                l, t, r, b = self.getClientRect()
                if ypos >= b:
                    self.lineDown()
                    
            
    def _onMouseMove(self, msg):
        xpos, ypos = self.getCursorPos()
        if self._mouseSelecting:
            if self._clickedAt == (xpos, ypos):
                # Mouse didn't move. This WM_MOUSEMOVE was sent by activated, etc.
                return
            
            # Start text selection if mouse cursor moves more than two pixels.
            if (abs(self._clickedAt[0]-xpos) < 3) and (abs(self._clickedAt[1]-ypos) < 3):
                return
            
            self._mouseMoved = True
            self._screen.setActiveNode(None)
            
            if self._selRange:
                pos = self._screen.getLocation((xpos, ypos), self._vpos)
                if not pos:
                    return
                
                selfrom, selto = self._selRange
                if selto != pos:
                    self._selRange = [selfrom, pos]
                    self.invalidateRect(None, erase=False)

        else:
            # select a node under mouse cursor
            pos = self._screen.getLocation((xpos, ypos), self._vpos)
            if pos and self._screen.getRow(pos).getEndPos() != pos[1:]:
                ret = self._screen.getObject(pos)
                if ret:
                    node, style, action = ret
                    if action:
                        if self._screen.getHoveredNode() != node:
                            self._screen.setHoveredNode(node)
                            self.trackMouseEvent(leave=True, hover=True)
                            self.invalidateRect(None, erase=False)
                        return

            # Mouse cursor doesn't locate on a node.
            if self._screen.getHoveredNode():
                self._screen.setHoveredNode(None)
                self.invalidateRect(None, erase=False)
            
            
    def _onLButtonUp(self, msg):
        self._screen.setActiveNode(None)
        if self._mouseSelecting:
            self._onCancelMode(None)
            if not self._mouseMoved:
                # User clicked a mouse button, not dragging to select text.
                pos = self._screen.getLocation((msg.x, msg.y), self._vpos)
                if pos and self._screen.getRow(pos).getEndPos() != pos[1:]:
                    ret = self._screen.getObject(pos)
                    if ret:
                        node, style, action = ret
                        if action:
                            action.onLButtonClicked(self, node, style)

    def _onLButtonDblClk(self, msg):
        pos = self._screen.getLocation((msg.x, msg.y), self._vpos)
        if not pos:
            return
        nrow, nobj, ncol = pos
        last = None
        for f, t, s in self._screen.iterTextWords(nrow):
            if f <= pos < t:
                self._selRange = [f, t]
                self.invalidateRect(None, erase=False)
                return
            if f[0] > nrow:
                break
            
            last = [f, t]
        if last:
            self._selRange = last
            self.invalidateRect(None, erase=False)
            

    def _onRButtonDown(self, msg):
        if self.MOUSEACTIVATE:
            self.setFocus()
        
    def _showContextMenu(self):
        text = self.getSelText()
        popup = menu.PopupMenu(u"popup")
        popup.append(menu.MenuItem(u"コピー", u"選択したテキストをコピー", grayed=False if text else True))
        popup.create()

        pos = self.getCursorPos()
        pos = self.clientToScreen(pos)
        item = popup.trackPopup(pos, self, nonotify=True, returncmd=True)
        if item:
            self.copySelectedText()
            
    def _onRButtonUp(self, msg):
        pos = self._screen.getLocation((msg.x, msg.y), self._vpos)
        if pos and self._screen.getRow(pos).getEndPos() != pos[1:]:
            ret = self._screen.getObject(pos)
            if ret:
                node, style, action = ret
                if action:
                    action.onRButtonClicked(self, node, style)
                    return
        
        self._showContextMenu()
        
    def _onCancelMode(self, msg):
        if self._mouseSelecting:
            self.releaseCapture()
            self._mouseSelecting = False
            self._mouseCheckTimer.unRegister()
            self._mouseCheckTimer = None

        self.invalidateRect(None, erase=False)
    
    def _onSetFocus(self, msg):
        self.invalidateRect(None, erase=False)
    
    def _onKillFocus(self, msg):
        self.invalidateRect(None, erase=False)

    def _onMouseWheel(self, msg):
        delta = msg.delta//120
        if delta < 0:
            delta = max(3, min(20, delta*-1))
            for d in range(delta):
                self.lineDown()
                self.updateWindow()
        else:
            delta = max(3, min(20, delta))
            for d in range(delta):
                self.lineUp()
                self.updateWindow()
        return 0
        
    def _getNextPage(self):
        rc = self.getClientRect()
        height = rc[3]-rc[1]
        lastpage = self._screen.getLastPage(height)
        newpos = self._screen.getPageBottom(height, self._vpos)
        newpos = max(min(newpos, lastpage), 0)
        return newpos
        

    def _ensureVisible(self, nrow):
        l, t, r, b = self.getClientRect()
        height = b-t
        
        if nrow < self._vpos:
            self._vpos = nrow
            self.invalidateRect(None, erase=False)
            self._updateScrollBar()
        else:
            bottom = self._screen.getPageBottom(height, self._vpos)
            if nrow <= bottom:
                return
            
            self._vpos = self._screen.getPageTop(height, nrow)
            self.invalidateRect(None, erase=False)
            self._updateScrollBar()
            

    def onDragEnter(self, msg):
        return pymfc.DropEffect(move=True, copy=True)

    def _dragOverScreen(self, msg):
        return
        
    def onDragOver(self, msg):
        pos = self._screen.getLocation(msg.pos, self._vpos)
        if pos and self._screen.getRow(pos).getEndPos() != pos[1:]:
            ret = self._screen.getObject(pos)
            if ret:
                node, style, action = ret
                if action:
                    if self._screen.getHoveredNode() != node:
                        self._screen.setHoveredNode(node)
                        self.invalidateRect(None, erase=False)
                    return action.onDragOver(self, node, msg)

        # Mouse cursor doesn't locate on a node.
        if self._screen.getHoveredNode():
            self._screen.setHoveredNode(None)
            self.invalidateRect(None, erase=False)

        return self._dragOverScreen(msg)
            
    def onDragLeave(self, msg):
        if self._screen.getHoveredNode():
            self._screen.setHoveredNode(None)
            self.invalidateRect(None, erase=False)

    def _dropOnScreen(self, msg):
        return
        
    def onDrop(self, msg):
        if self._screen.getHoveredNode():
            self._screen.setHoveredNode(None)
            self.invalidateRect(None, erase=False)

        pos = self._screen.getLocation(msg.pos, self._vpos)
        if pos and self._screen.getRow(pos).getEndPos() != pos[1:]:
            ret = self._screen.getObject(pos)
            if ret:
                node, style, action = ret
                if action:
                    if self._screen.getHoveredNode() != node:
                        self._screen.setHoveredNode(node)
                        self.invalidateRect(None, erase=False)
                    return action.onDrop(self, node, msg)
        
        return self._dropOnScreen(msg)

    def onDropScrollCheck(self, msg):
        if msg.lineup:
            if self._vpos == 0:
                return False
            else:
                return True
        elif msg.linedown:
            if self.isLastPage():
                return False
            else:
                return True
        
    def onDropScroll(self, msg):
        self._onVScroll(msg)
        return 


    def lineUp(self):
        if self._vpos:
            self._vpos -= 1
            self.invalidateRect(None, erase=False)
            self._updateScrollBar()
            self.updateWindow()

    def lineDown(self):
        rc = self.getClientRect()
        height = rc[3]-rc[1]
        lastpage = self._screen.getLastPage(height)
        
        if self._vpos < lastpage:
            self._vpos += 1
            self.invalidateRect(None, erase=False)
            self._updateScrollBar()
            self.updateWindow()
            
    def pageUp(self):
        rc = self.getClientRect()
        height = rc[3]-rc[1]
        newpos = self._screen.getPrevPage(height, self._vpos)

        if newpos != self._vpos:
            self._vpos = newpos
            self.invalidateRect(None, erase=False)
            self._updateScrollBar()
            return True

    def pageDown(self):
        newpos = self._getNextPage()
        if newpos != self._vpos:
            self._vpos = newpos
            self.invalidateRect(None, erase=False)
            self._updateScrollBar()
            return True

    def showFirstPage(self):
        if self._vpos:
            self._vpos = 0
            self.invalidateRect(None, erase=False)
            self._updateScrollBar()
            return True

    def showLastPage(self):
        rc = self.getClientRect()
        height = rc[3]-rc[1]
        newpos = self._screen.getLastPage(height)
        if newpos != self._vpos:
            self._vpos = newpos
            self.invalidateRect(None, erase=False)
            self._updateScrollBar()
            return True

    def searchText(self, s, searchfrom):
        s = SearchTextDlg(doc=self).doModal()
        self.setFocus()

    def searchNext(self, s, searchfrom):
        start = None
        if searchfrom is None:
            if self._selRange:
                searchfrom = self._selRange[0]
        
        if s:
            self._lastSearch = s
        
        range = self._screen.search(s, searchfrom)
        if not range and searchfrom:
            range = self._screen.search(s, None)
        
        if range:
            self._selRange = range
            self._ensureVisible(range[0][0])
            self.invalidateRect(None, erase=False)
            self._updateScrollBar()
            return range[0]
        
    def searchAgain(self):
        if self._lastSearch:

            if self._selRange:
                nrow, nobj, ncol = self._selRange[0]
                searchfrom = (nrow, nobj, ncol+1)
            else:
                searchfrom = None
                
            self.searchNext(self._lastSearch, searchfrom)
            
    def isLastPage(self):
        newpos = self._getNextPage()
        if newpos == self._vpos:
            return True

    def getHeight(self):
        return self._screen.getHeight()
        

class RoundRectHeader(Background):
    PEN_WIDTH = 1
    
    MARGIN_LEFT = 5
    MARGIN_RIGHT = 5
    MARGIN_TOP = 0
    MARGIN_BOTTOM = 0
    RADIAL = 5
    
    HAS_TITLE = True
    COLOR_BORDER = 0xc0c0c0
    BGCOLOR = 0xecf7f7

    def draw(self, row, dc, pos, width, isfirstrow, islastrow):
        l, t, r, b = pos[0], pos[1], pos[0] + width, pos[1]+row.height
        if isfirstrow:
            t += self.MARGIN_TOP
        if islastrow:
            b -= self.MARGIN_BOTTOM
            
        l += self.MARGIN_LEFT
        r -= self.MARGIN_RIGHT
        R = self.RADIAL

        if isfirstrow:
            if self.BGCOLOR is not None:
                pen = gdi.Pen(null=True, endcap_square=True, width=0)
                dc.selectObject(pen)
                dc.beginPath()
                dc.moveTo((l, b))
                dc.lineTo((l, t+R))
                dc.setArcDirection(True)
                dc.arcTo((l, t, l+R*2+1, t+R*2+1), (l, t+R), (l+R, t))
                dc.arcTo((r-R*2, t, r+1, t+R*2), (r-R, t), (r, t+R))
                dc.lineTo((r, b))
                dc.endPath()

                br = gdi.Brush(color=self.BGCOLOR)
                dc.selectObject(br)
                dc.fillPath()

            pen = gdi.Pen(color=self.COLOR_BORDER, solid=True, endcap_square=True, width=self.PEN_WIDTH)
            dc.selectObject(pen)

            dc.beginPath()
            dc.moveTo((l, b))
            dc.lineTo((l, t+R))
            dc.setArcDirection(True)
            dc.arcTo((l, t, l+R*2+1, t+R*2+1), (l, t+R), (l+R, t))
            dc.arcTo((r-R*2, t, r+1, t+R*2), (r-R, t), (r, t+R))
            dc.lineTo((r, b))
            dc.endPath()

            dc.strokePath()

        else:
            if self.BGCOLOR is not None:
                dc.fillSolidRect((l, t, r, b), self.BGCOLOR)
            
            pen = gdi.Pen(color=self.COLOR_BORDER, solid=True, endcap_square=True, width=self.PEN_WIDTH)
            dc.selectObject(pen)

            dc.moveTo((l, t))
            dc.lineTo((l, b))
            dc.moveTo((r, t))
            dc.lineTo((r, b))


class RoundRectFooter(Background):
    PEN_WIDTH = 1
    
    MARGIN_LEFT = 5
    MARGIN_RIGHT = 5
    MARGIN_TOP = 0
    MARGIN_BOTTOM = 0
    RADIAL = 5
    
    HAS_TITLE = True
    COLOR_BORDER = 0xc0c0c0
    BGCOLOR = 0xecf7f7

    def draw(self, row, dc, pos, width, isfirstrow, islastrow):
        l, t, r, b = pos[0], pos[1], pos[0] + width, pos[1]+row.height
        if isfirstrow:
            t += self.MARGIN_TOP
        if islastrow:
            b -= self.MARGIN_BOTTOM
            
        l += self.MARGIN_LEFT
        r -= self.MARGIN_RIGHT
        R = self.RADIAL


        if islastrow:
            if self.BGCOLOR is not None:
                pen = gdi.Pen(null=True, endcap_square=True, width=0)
                dc.selectObject(pen)

                dc.beginPath()
                dc.setArcDirection(False)
                dc.moveTo((l, t))
                dc.lineTo((l, b-R))
                dc.arcTo((l, b-R*2, l+R*2, b), (l, b-R), (l+R, b))
                dc.arcTo((r-R*2, b-R*2, r+1, b), (r-R, b+1), (r, b-R))
                dc.lineTo((r, t))
                dc.endPath()

                br = gdi.Brush(color=self.BGCOLOR)
                dc.selectObject(br)
                dc.fillPath()

            pen = gdi.Pen(color=self.COLOR_BORDER, solid=True, endcap_square=True, width=self.PEN_WIDTH)
            dc.selectObject(pen)

            dc.beginPath()
            dc.setArcDirection(False)
            dc.moveTo((l, t))
            dc.lineTo((l, b-R))
            dc.arcTo((l, b-R*2, l+R*2, b), (l, b-R), (l+R, b))
            dc.arcTo((r-R*2, b-R*2, r+1, b), (r-R, b+1), (r, b-R))
            dc.lineTo((r, t))
            dc.endPath()

            dc.strokePath()

        else:
            if self.BGCOLOR is not None:
                dc.fillSolidRect((l, t, r, b), self.BGCOLOR)

            pen = gdi.Pen(color=self.COLOR_BORDER, solid=True, endcap_square=True, width=self.PEN_WIDTH)
            dc.selectObject(pen)

            dc.moveTo((l, t))
            dc.lineTo((l, b))
            dc.moveTo((r, t))
            dc.lineTo((r, b))

        if isfirstrow:
            pen = gdi.Pen(color=self.COLOR_BORDER, solid=True, endcap_square=True, width=self.PEN_WIDTH)
            dc.selectObject(pen)
            dc.moveTo((l, t))
            dc.lineTo((r, t))

class RoundRectBackground(Background):
    PEN_WIDTH = 1
    
    MARGIN_LEFT = 5
    MARGIN_RIGHT = 5
    MARGIN_TOP = 0
    MARGIN_BOTTOM = 0
    RADIAL = 10
    
    COLOR_BORDER = 0xc0c0c0
    BGCOLOR = 0xecf7f7

    def draw(self, row, dc, pos, width, isfirstrow, islastrow):
        l, t, r, b = pos[0], pos[1], pos[0] + width, pos[1]+row.height
        if isfirstrow:
            t += self.MARGIN_TOP
        if islastrow:
            b -= self.MARGIN_BOTTOM
            
        l += self.MARGIN_LEFT
        r -= self.MARGIN_RIGHT
        R = self.RADIAL
        
        if isfirstrow and islastrow:
            if self.BGCOLOR is not None:
                pen = gdi.Pen(null=True, endcap_square=True, width=0)
                dc.selectObject(pen)
                dc.beginPath()
                dc.moveTo((l, b-R))
                dc.lineTo((l, t+R))
                dc.setArcDirection(True)
                dc.arcTo((l, t, l+R*2+1, t+R*2+1), (l, t+R), (l+R, t))
                dc.arcTo((r-R*2, t, r+1, t+R*2), (r-R, t), (r, t+R))
                dc.arcTo((r-R*2, b-R*2, r+1, b+1), (r, b-R), (r-R, b+R))
                dc.arcTo((l, b-R*2, l+R*2+1, b+1), (l+R, b), (l, b-R))
                dc.endPath()

                br = gdi.Brush(color=self.BGCOLOR)
                dc.selectObject(br)
                dc.fillPath()

            pen = gdi.Pen(color=self.COLOR_BORDER, solid=True, endcap_square=True, width=self.PEN_WIDTH)
            dc.selectObject(pen)

            dc.beginPath()
            dc.moveTo((l, b-R))
            dc.lineTo((l, t+R))
            dc.setArcDirection(True)
            dc.arcTo((l, t, l+R*2+1, t+R*2+1), (l, t+R), (l+R, t))
            dc.arcTo((r-R*2, t, r+1, t+R*2), (r-R, t), (r, t+R))
            dc.arcTo((r-R*2, b-R*2, r+1, b+1), (r, b-R), (r-R, b+R))
            dc.arcTo((l, b-R*2, l+R*2+1, b+1), (l+R, b), (l, b-R))

            dc.endPath()

            dc.strokePath()

        elif isfirstrow:
            if self.BGCOLOR is not None:
                pen = gdi.Pen(null=True, endcap_square=True, width=0)
                dc.selectObject(pen)
                dc.beginPath()
                dc.moveTo((l, b))
                dc.lineTo((l, t+R))
                dc.setArcDirection(True)
                dc.arcTo((l, t, l+R*2+1, t+R*2+1), (l, t+R), (l+R, t))
                dc.arcTo((r-R*2, t, r+1, t+R*2), (r-R, t), (r, t+R))
                dc.lineTo((r, b))
                dc.endPath()

                br = gdi.Brush(color=self.BGCOLOR)
                dc.selectObject(br)
                dc.fillPath()

            pen = gdi.Pen(color=self.COLOR_BORDER, solid=True, endcap_square=True, width=self.PEN_WIDTH)
            dc.selectObject(pen)

            dc.beginPath()
            dc.moveTo((l, b))
            dc.lineTo((l, t+R))
            dc.setArcDirection(True)
            dc.arcTo((l, t, l+R*2+1, t+R*2+1), (l, t+R), (l+R, t))
            dc.arcTo((r-R*2, t, r+1, t+R*2), (r-R, t), (r, t+R))
            dc.lineTo((r, b))
            dc.endPath()

            dc.strokePath()
            
        elif islastrow:
            if self.BGCOLOR is not None:
                pen = gdi.Pen(null=True, endcap_square=True, width=0)
                dc.selectObject(pen)

                dc.beginPath()
                dc.setArcDirection(False)
                dc.moveTo((l, t))
                dc.lineTo((l, b-R))
                dc.arcTo((l, b-R*2, l+R*2, b), (l, b-R), (l+R, b))
                dc.arcTo((r-R*2, b-R*2, r+1, b), (r-R, b+1), (r, b-R))
                dc.lineTo((r, t))
                dc.endPath()

                br = gdi.Brush(color=self.BGCOLOR)
                dc.selectObject(br)
                dc.fillPath()

            pen = gdi.Pen(color=self.COLOR_BORDER, solid=True, endcap_square=True, width=self.PEN_WIDTH)
            dc.selectObject(pen)

            dc.beginPath()
            dc.setArcDirection(False)
            dc.moveTo((l, t))
            dc.lineTo((l, b-R))
            dc.arcTo((l, b-R*2, l+R*2, b), (l, b-R), (l+R, b))
            dc.arcTo((r-R*2, b-R*2, r+1, b), (r-R, b+1), (r, b-R))
            dc.lineTo((r, t))
            dc.endPath()

            dc.strokePath()
        
        else:
            if self.BGCOLOR is not None:
                dc.fillSolidRect((l, t, r, b), self.BGCOLOR)
            
            pen = gdi.Pen(color=self.COLOR_BORDER, solid=True, endcap_square=True, width=self.PEN_WIDTH)
            dc.selectObject(pen)

            dc.moveTo((l, t))
            dc.lineTo((l, b))
            dc.moveTo((r, t))
            dc.lineTo((r, b))


class RectBackground(Background):
    PEN_WIDTH = 1
    
    MARGIN_LEFT = 5
    MARGIN_RIGHT = 5
    MARGIN_TOP = 0
    MARGIN_BOTTOM = 1
    RADIAL = 10
    
    COLOR_BORDER = 0xc0c0c0
    BGCOLOR = 0xecf7f7
    
    def draw(self, row, dc, pos, width, isfirstrow, islastrow):
        l, t, r, b = pos[0], pos[1], pos[0] + width-1, pos[1]+row.height-1
        if isfirstrow:
            t += self.MARGIN_TOP
        if islastrow:
            b -= self.MARGIN_BOTTOM
            
        l += self.MARGIN_LEFT
        r -= self.MARGIN_RIGHT
        
        if isfirstrow and islastrow:
            if self.BGCOLOR is not None:
                pen = gdi.Pen(null=True, endcap_square=True, width=0)
                dc.selectObject(pen)
                dc.beginPath()
                dc.moveTo((l, b))
                dc.lineTo((l, t))
                dc.lineTo((r, t))
                dc.lineTo((r, b))
                dc.lineTo((l, b))
                dc.endPath()

                br = gdi.Brush(color=self.BGCOLOR)
                dc.selectObject(br)
                dc.fillPath()

            pen = gdi.Pen(color=self.COLOR_BORDER, solid=True, endcap_square=True, width=self.PEN_WIDTH)
            dc.selectObject(pen)

            dc.beginPath()
            dc.moveTo((l, b))
            dc.lineTo((l, t))
            dc.lineTo((r, t))
            dc.lineTo((r, b))
            dc.lineTo((l, b))
            dc.endPath()

            dc.strokePath()

        elif isfirstrow:
            if self.BGCOLOR is not None:
                pen = gdi.Pen(null=True, endcap_square=True, width=0)
                dc.selectObject(pen)
                dc.beginPath()
                dc.moveTo((l, b))
                dc.lineTo((l, t))
                dc.lineTo((r, t))
                dc.lineTo((r, b))
                dc.endPath()

                br = gdi.Brush(color=self.BGCOLOR)
                dc.selectObject(br)
                dc.fillPath()

            pen = gdi.Pen(color=self.COLOR_BORDER, solid=True, endcap_square=True, width=self.PEN_WIDTH)
            dc.selectObject(pen)

            dc.beginPath()
            dc.moveTo((l, b))
            dc.lineTo((l, t))
            dc.lineTo((r, t))
            dc.lineTo((r, b))
            dc.endPath()

            dc.strokePath()
            
        elif islastrow:
            if self.BGCOLOR is not None:
                pen = gdi.Pen(null=True, endcap_square=True, width=0)
                dc.selectObject(pen)

                dc.beginPath()
                dc.moveTo((l, t))
                dc.lineTo((l, b))
                dc.lineTo((r, b))
                dc.lineTo((r, t))
                dc.endPath()

                br = gdi.Brush(color=self.BGCOLOR)
                dc.selectObject(br)
                dc.fillPath()

            pen = gdi.Pen(color=self.COLOR_BORDER, solid=True, endcap_square=True, width=self.PEN_WIDTH)
            dc.selectObject(pen)

            dc.beginPath()
            dc.moveTo((l, t))
            dc.lineTo((l, b))
            dc.lineTo((r, b))
            dc.lineTo((r, t))
            dc.endPath()

            dc.strokePath()
        
        else:
            if self.BGCOLOR is not None:
                dc.fillSolidRect((l, t, r, b), self.BGCOLOR)
            
            pen = gdi.Pen(color=self.COLOR_BORDER, solid=True, endcap_square=True, width=self.PEN_WIDTH)
            dc.selectObject(pen)

            dc.moveTo((l, t))
            dc.lineTo((l, b))
            dc.moveTo((r, t))
            dc.lineTo((r, b))
