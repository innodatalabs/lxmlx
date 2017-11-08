"""
XML can be represented as a series of events (similar to SAX).

We use simplified event model, consisting of three events:
- enter
- exit
- text

Events representation is intentionally very portable. Lists of events
can are JSON-serializable. This provides an alrernative way to serialize
XMl documents.
"""
import lxml.etree as et

ENTER   = 'enter'
EXIT    = 'exit'
TEXT    = 'text'
COMMENT = 'comment'
PI      = 'pi'

def _obj2elt(obj, nsmap=None):
    return et.Element(obj['tag'], attrib=obj.get('attrib'), nsmap=nsmap)

def _elt2obj(elt):
    obj = {'tag': elt.tag}
    if elt.attrib:
        obj['attrib'] = dict(elt.attrib)
    return obj

def scan(xml):
    """Converts XML tree to event generator"""

    if xml.tag is et.Comment:
        yield {'type': COMMENT, 'text': xml.text}
        return

    if xml.tag is et.PI:
        if xml.text:
            yield {'type': PI, 'target': xml.target, 'text': xml.text}
        else:
            yield {'type': PI, 'target': xml.target}
        return

    obj = _elt2obj(xml)
    obj['type'] = ENTER
    yield obj

    assert type(xml.tag) is str, xml
    if xml.text:
        yield {'type': TEXT, 'text': xml.text}

    for c in xml:
        yield from scan(c)
        if c.tail:
            yield {'type': TEXT, 'text': c.tail}

    yield {'type': EXIT}

def unscan(events, nsmap=None):
    """Converts events stream into lXML tree"""

    root = None
    last_closed_elt = None
    stack = []
    for obj in events:

        if obj['type'] == ENTER:
            elt = _obj2elt(obj, nsmap=nsmap)
            if stack:
                stack[-1].append(elt)
            elif root is not None:
                raise RuntimeError('Event stream tried to create second XML tree')
            else:
                root = elt
            stack.append(elt)
            last_closed_elt = None

        elif obj['type'] == EXIT:
            last_closed_elt = stack.pop()

        elif obj['type'] == COMMENT:
            elt = et.Comment(obj['text'])
            stack[-1].append(elt)

        elif obj['type'] == PI:
            elt = et.PI(obj['target'])
            if obj.get('text'):
                elt.text = obj['text']
            stack[-1].append(elt)

        elif obj['type'] == TEXT:
            text = obj['text']
            if text:
                if last_closed_elt is None:
                    stack[-1].text = (stack[-1].text or '') + text
                else:
                    last_closed_elt.tail = (last_closed_elt.tail or '') + text
        else:
            assert False, obj

    if root is None:
        raise RuntimeError('Empty XML event stream')

    return root


def parse(filename):
    """Parses file content into events stream"""
    for event, elt in et.iterparse(filename, events= ('start', 'end', 'comment', 'pi'), huge_tree=True):
        if event == 'start':
            obj = _elt2obj(elt)
            obj['type'] = ENTER
            yield obj
            if elt.text:
                yield {'type': TEXT, 'text': elt.text}
        elif event == 'end':
            yield {'type': EXIT}
            if elt.tail:
                yield {'type': TEXT, 'text': elt.tail}
            elt.clear()
        elif event == 'comment':
            yield {'type': COMMENT, 'text': elt.text}
        elif event == 'pi':
            yield {'type': PI, 'text': elt.text}
        else:
            assert False, (event, elt)

def subtree(events):
    """selects sub-tree events"""
    stack = 0
    for obj in events:
        if obj['type'] == ENTER:
            stack += 1
        elif obj['type'] == EXIT:
            if stack == 0:
                break
            stack -= 1
        yield obj


def merge_text(events):
    """merges each run of successive text events into one text event"""
    text = []
    for obj in events:
        if obj['type'] == TEXT:
            text.append(obj['text'])
        else:
            if text:
                yield {'type': TEXT, 'text': ''.join(text)}
                text.clear()
            yield obj
    if text:
        yield {'type': TEXT, 'text': ''.join(text)}


def with_peer(events):
    """locates ENTER peer for each EXIT object. Convenient when selectively
    filtering out XML markup"""

    stack = []
    for obj in events:
        if obj['type'] == ENTER:
            stack.append(obj)
            yield obj, None
        elif obj['type'] == EXIT:
            yield obj, stack.pop()
        else:
            yield obj, None
