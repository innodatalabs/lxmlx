import re
import itertools

__TEXT_ESCAPE = {
    '\u000d': '&#13;',
    '<'     : '&lt;',
    '>'     : '&gt;',
    '&'     : '&amp;'
}
__TEXT_ESCAPE_PATTERN = re.compile('|'.join(re.escape(x) for x in __TEXT_ESCAPE.keys()))

def xml_escape_text(text):
    """escapes XML text"""
    return __TEXT_ESCAPE_PATTERN.sub(lambda mtc: __TEXT_ESCAPE[mtc.group()], text)

__ATTR_ESCAPE = {
    '\u0009': '&#9;',
    '\u000a': '&#10;',
    '\u000d': '&#13;',
    '"'     : '&quot;',
    '<'     : '&lt;',
    '>'     : '&gt;',
    '&'     : '&amp;'
}
__ATTR_ESCAPE_PATTERN = re.compile('|'.join(re.escape(x) for x in __ATTR_ESCAPE.keys()))

def xml_escape_attr(text):
    """escapes XML attribute value"""
    return __ATTR_ESCAPE_PATTERN.sub(lambda mtc: __ATTR_ESCAPE[mtc.group()], text)

__PI_TEXT_CHECK_PATTERN = re.compile(r'\?>')
def validate_pi_text(text):
    """validates XML Processing Instruction text"""
    if __PI_TEXT_CHECK_PATTERN.search(text):
        raise RuntimeError('Processing instruction text can not contain "?>"')

__COMMENT_TEXT_CHECK_PATTERN = re.compile(r'--|-$')
def validate_comment_text(text):
    """validates XML comment text"""
    if __COMMENT_TEXT_CHECK_PATTERN.search(text):
        raise RuntimeError('Comment text can not contain "--", nor end with a dash "-"')

__INVALID_XML_CHARS = set(chr(x) for x in itertools.chain(
    range(0x0, 0x8+1),
    range(0xb, 0xc+1),
    range(0xe, 0x1f+1),
    range(0xd800, 0xdfff+1),
    range(0xfffe, 0xffff+1)
))

def validate_xml_text(text):
    """validates XML text"""
    bad_chars = __INVALID_XML_CHARS & set(text)
    if bad_chars:
        for offset,c in enumerate(text):
            if c in bad_chars:
                raise RuntimeError('invalid XML character: ' + repr(c) + ' at offset ' + str(offset))

__INVALID_NAME_CHARS = set(chr(x) for x in itertools.chain(
    range(0x0, 0x2c+1),
    range(0x2f, 0x2f+1),
    range(0x3b, 0x40+1),
    range(0x5b, 0x5e+1),
    range(0x60, 0x60+1),
    range(0x7b, 0xb6+1),
    range(0xb8, 0xbf+1),
    range(0xd7, 0xd7+1),
    range(0xf7, 0xf7+1),
    range(0x37e, 0x37e+1),
    range(0x2000, 0x200b+1),
    range(0x200e, 0x203e+1),
    range(0x2041, 0x206f+1),
    range(0x2190, 0x2bff+1),
    range(0x2ff0, 0x3000+1),
    range(0xd800, 0xf8ff+1),
    range(0xfdd0, 0xfdef+1),
    range(0xfffe, 0xffff+1)
))

__INVALID_NAME_START_CHARS = set(chr(x) for x in itertools.chain(
    range(0x2d, 0x2e+1),
    range(0x30, 0x39+1),
    range(0xb7, 0xb7+1),
    range(0x300, 0x36f+1),
    range(0x203f, 0x2040+1)
))

def validate_xml_name(name):
    """validates XML name"""
    if len(name) == 0:
        raise RuntimeError('empty XML name')

    if __INVALID_NAME_CHARS & set(name):
        raise RuntimeError('XML name contains invalid character')

    if name[0] in __INVALID_NAME_START_CHARS:
        raise RuntimeError('XML name starts with invalid character')

if __name__ == '__main__':

    def strip_prefix(s, prefix):
        assert s.startswith(prefix), s[:100]
        return s[len(prefix):]

    def strip_suffix(s, suffix):
        assert s.startswith(suffix), s[-100:]
        return s[-len(suffix):]

    def to_ranges(values):

        end = None
        start = None
        for x in sorted(values):
            if start is None:
                start = end = x
            elif x == end + 1:
                end = x
            else:
                yield start, end
                start = end = x

        if start is not None:
            yield start, end

    def detect_what_lxml_encodes_in_text():
        root = et.Element('root')
        #root.append(et.Comment('-hel<b>l\no- '))
        #root.append(et.PI('a', '\n>\n\tx'))
        #root.append(et.Element('z', {'aa': '\u000a\u000d\u0085'}))

        root.text = ''.join(chr(x) for x in valid_xml_characters())
        text = et.tostring(root, encoding='utf-8', xml_declaration=True)
        text = text.decode('utf-8')
        for mtc in re.finditer(r'&(.*?);', text):
            yield mtc.group(1)

    def detect_what_lxml_encodes_in_attrib():
        root = et.Element('root')
        #root.append(et.Comment('-hel<b>l\no- '))
        #root.append(et.PI('a', '\n>\n\tx'))
        #root.append(et.Element('z', {'aa': '\u000a\u000d\u0085'}))
        root.attrib['test'] = ''.join(chr(x) for x in valid_xml_characters())
        text = et.tostring(root, encoding='utf-8', xml_declaration=True)
        text = text.decode('utf-8')
        for mtc in re.finditer(r'&(.*?);', text):
            yield mtc.group(1)

    def write_stream(writer, events):

        for event, obj in events:
            if event == 'enter':
                if obj.tag is et.Comment:
                    writer.write_comment(obj.text)
                elif obj.tag is et.PI:
                    print(obj.target)
                    writer.write_pi(obj.target, obj.text)
                else:
                    writer.write_enter(obj.tag, attrib=obj.attrib, nsmap=obj.nsmap)
            elif event == 'exit':
                if obj.tag not in (et.Comment, et.PI):
                    writer.write_exit(obj.tag)
            else:
                assert event == 'text'
                writer.write_text(obj)

    #scan_parse_xml('ECFR-title11_new.innod.xml')
    print('Text:')
    for val in detect_what_lxml_encodes_in_text():
        print(val)

    print()
    print('Attr:')
    for val in detect_what_lxml_encodes_in_attrib():
        print(val)

    test_nsmap_handling()

    nc = set(valid_xml_name_char())
    ncs = set(valid_xml_name_char_start())
    unicode_all = set(range(0, 0xf0000))
    print(len(nc))
    print(len(ncs))
    print(len(nc-ncs))
    print(len(unicode_all-nc))
    print(len(unicode_all-ncs))

    print(len(__INVALID_XML_CHARS))
    print(len(__INVALID_NAME_CHARS))
    print(len(__INVALID_NAME_START_CHARS))

    print('invalid_xml_chars')
    for s,e in to_ranges(__INVALID_XML_CHARS):
        print('range('+hex(s)+',', hex(e)+'+1)')

    print('invalid_name_chars')
    for s,e in to_ranges(__INVALID_NAME_CHARS):
        print('range('+hex(s)+',', hex(e)+'+1)')

    print('invalid_name_start_chars')
    for s,e in to_ranges(__INVALID_NAME_START_CHARS):
        print('range('+hex(s)+',', hex(e)+'+1)')
