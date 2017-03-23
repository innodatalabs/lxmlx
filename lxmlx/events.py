"""
XML can be represented as a series of events (similar to SAX).

We use simplified event model, consisting of three events:
- tag enter
- tag exit
- text

"""
import lxml.etree as et

ENTER = 'enter'
EXIT  = 'exit'
TEXT  = 'text'

def scan(xml):
    """Converts XML tree to events generater"""

    yield ENTER, xml

    if type(xml.tag) is str and xml.text:
        yield TEXT, xml.text

    for c in xml:
        yield from scan(c)
        if c.tail:
            yield TEXT, c.tail

    yield EXIT, xml

def unscan(events):
    """Converts events stream into lXML tree"""

    root = None
    last_closed_elt = None
    stack = []
    for event, obj in events:

        if event == ENTER:
            out = clone(obj)
            if stack:
                stack[-1].append(out)
            elif root is not None:
                raise RuntimeError('Event stream tried to create second XML tree')
            else:
                root = out
            stack.append(out)
            last_closed_elt = None

        elif event == EXIT:
            last_closed_elt = stack.pop()

        elif event == TEXT:
            if obj:
                if last_closed_elt is None:
                    stack[-1].text = (stack[-1].text or '') + obj
                else:
                    last_closed_elt.tail = (last_closed_elt.tail or '') + obj
        else:
            assert False

    if root is None:
        raise RuntimeError('Empty XML event stream')

    return root

def clone(elt):
    """Clones lXML tree node (can be either Element, ProcessingInstruction, or Comment)"""

    if elt.tag is et.Comment:
        out = et.Comment(elt.text.strip('-'))  # workaround for LXML not being able to create comment with dashes
    elif elt.tag is et.ProcessingInstruction:
        out = et.ProcessingInstruction(elt.target, elt.text)
    else:
        out = et.Element(elt.tag, elt.attrib, elt.nsmap)

    return out

def parse(filename):
    """Parses file content into events stream"""
    for event, elt in et.iterparse(filename, events= ('start', 'end', 'comment', 'pi'), huge_tree=True):
        if event == 'start':
            yield ENTER, elt
            if elt.text:
                yield TEXT, elt.text
        elif event == 'end':
            yield EXIT, elt
            if elt.tail:
                yield TEXT, elt.tail
            elt.clear()
        elif event == 'comment':
            yield ENTER, elt
            yield EXIT, elt
        elif event == 'pi':
            yield ENTER, elt
            yield EXIT, elt
        else:
            assert False, (event, elt)

def subtree(events):
    """selects sub-tree events"""
    stack = 0
    for event, obj in events:
        if event == ENTER:
            stack += 1
        elif event == EXIT:
            if stack == 0:
                break
            stack -= 1
        yield event, obj

def merge_text(events):
    """merges each run of successive text events into one text event"""
    text = []
    for event, obj in events:
        if event == TEXT:
            text.append(obj)
        else:
            if text:
                yield TEXT, ''.join(text)
                text.clear()
            yield event, obj
    if text:
        yield TEXT, ''.join(text)
