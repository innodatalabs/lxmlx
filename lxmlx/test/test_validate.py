import unittest
from lxmlx.xml_writer import xml_escape_attr, xml_escape_text, \
    validate_xml_name, validate_xml_text
import io
import lxml.etree as et
from lxmlx.events import scan

def valid_xml_characters():
    """ only those can be used in an XML document"""
    yield from [0x9, 0xa, 0xd]
    yield from range(0x20, 0xd7ff+1)
    yield from range(0xe000, 0xfffd+1)
    yield from range(0x10000, 0xf0000)

def valid_xml_name_char_start():
    """ XML name can start with this chars """

    def rng(s, e):
        yield from range(ord(s), ord(e)+1)

    yield ord(':')
    yield from rng('A', 'Z')
    yield ord('_')
    yield from rng('a', 'z')
    yield from rng('\u00c0', '\u00d6')
    yield from rng('\u00d8', '\u00f6')
    yield from rng('\u00f8', '\u02ff')
    yield from rng('\u0370', '\u037d')
    yield from rng('\u037f', '\u1fff')
    yield from rng('\u200c', '\u200d')
    yield from rng('\u2070', '\u218f')
    yield from rng('\u2c00', '\u2fef')
    yield from rng('\u3001', '\ud7ff')
    yield from rng('\uf900', '\ufdcf')
    yield from rng('\ufdf0', '\ufffd')
    yield from rng('\U00010000', '\U000effff')

def valid_xml_name_char():
    """ XML name can contain any of these chars """

    def rng(s, e):
        yield from range(ord(s), ord(e)+1)

    yield from valid_xml_name_char_start()

    yield ord('-')
    yield ord('.')
    yield from rng('0', '9')
    yield ord('\u00b7')
    yield from rng('\u0300', '\u036f')
    yield from rng('\u203f', '\u2040')

def unicode_range():
    """ internal: all reasonable Unicode range """
    yield from range(1, 0xf0000)

class TestXmlEncode(unittest.TestCase):

    def test01(self):
        s = xml_escape_attr('"&<')
        self.assertEqual(s, '&quot;&amp;&lt;')

    def test02(self):
        s = xml_escape_attr('\n')
        self.assertEqual(s, '&#10;')

    def test03(self):

        with self.assertRaisesRegex(RuntimeError, 'empty XML name'):
            validate_xml_name('')

        with self.assertRaisesRegex(RuntimeError, 'XML name contains invalid character'):
            validate_xml_name(' ')

        with self.assertRaisesRegex(RuntimeError, 'XML name starts with invalid character'):
            validate_xml_name('-a')

    def test03a(self):
        for x in valid_xml_name_char():
            validate_xml_name('a' + chr(x))

    def test03b(self):
        for x in valid_xml_name_char_start():
            validate_xml_name(chr(x) + 'a')

    def test03c(self):

        invalid_name_chars = set(unicode_range()) - set(valid_xml_name_char())
        invalid_name_start_chars = set(unicode_range()) - set(valid_xml_name_char_start()) - invalid_name_chars

        for x in invalid_name_chars:
            with self.assertRaisesRegex(RuntimeError, 'contains invalid character'):
                validate_xml_name('a' + chr(x))

        for x in invalid_name_start_chars:
            with self.assertRaisesRegex(RuntimeError, 'starts with invalid character'):
                validate_xml_name(chr(x) + 'a')

    def test04(self):

        s = ''.join(chr(x) for x in valid_xml_characters())
        validate_xml_text(s)

    def test04a(self):

        invalid_chars = set(unicode_range()) - set(valid_xml_characters())

        for x in invalid_chars:
            with self.assertRaisesRegex(RuntimeError, 'invalid XML character: .* at offset 5'):
                print(x)
                validate_xml_text('text ' + chr(x))
