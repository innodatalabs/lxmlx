from __future__ import unicode_literals
from __future__ import print_function
import unittest
from lxmlx.xml_writer import xml_escape_attr, xml_escape_text, \
    validate_xml_name, validate_xml_text
import io
import lxml.etree as et
import itertools
from builtins import ord, chr

def valid_xml_characters():
    """ only those can be used in an XML document"""
    return itertools.chain(
        [0x9, 0xa, 0xd],
        range(0x20, 0xd7ff+1),
        range(0xe000, 0xfffd+1),
        range(0x10000, 0xf0000)
    )

def valid_xml_name_char_start():
    """ XML name can start with this chars """

    def rng(s, e):
        return range(ord(s), ord(e)+1)

    return itertools.chain(
        [ord(':')],
        rng('A', 'Z'),
        [ord('_')],
        rng('a', 'z'),
        rng('\u00c0', '\u00d6'),
        rng('\u00d8', '\u00f6'),
        rng('\u00f8', '\u02ff'),
        rng('\u0370', '\u037d'),
        rng('\u037f', '\u1fff'),
        rng('\u200c', '\u200d'),
        rng('\u2070', '\u218f'),
        rng('\u2c00', '\u2fef'),
        rng('\u3001', '\ud7ff'),
        rng('\uf900', '\ufdcf'),
        rng('\ufdf0', '\ufffd'),
        rng('\U00010000', '\U000effff')
    )

def valid_xml_name_char():
    """ XML name can contain any of these chars """

    def rng(s, e):
        return range(ord(s), ord(e)+1)

    return itertools.chain(
        valid_xml_name_char_start(),
        [ord('-')],
        [ord('.')],
        rng('0', '9'),
        [ord('\u00b7')],
        rng('\u0300', '\u036f'),
        rng('\u203f', '\u2040')
    )

def unicode_range():
    """ internal: all reasonable Unicode range """
    for x in range(1, 0xf0000): yield x

class TestXmlEncode(unittest.TestCase):

    def test00(self):
        for x in valid_xml_name_char():
            assert type(x) == int, x

    def test01(self):
        s = xml_escape_attr('"&<')
        self.assertEqual(s, '&quot;&amp;&lt;')

    def test02(self):
        s = xml_escape_attr('\n')
        self.assertEqual(s, '&#10;')

    def test03(self):

        with self.assertRaisesRegexp(RuntimeError, 'empty XML name'):
            validate_xml_name('')

        with self.assertRaisesRegexp(RuntimeError, 'XML name contains invalid character'):
            validate_xml_name(' ')

        with self.assertRaisesRegexp(RuntimeError, 'XML name starts with invalid character'):
            validate_xml_name('-a')

    def test03a(self):
        for x in valid_xml_name_char():
            print(x)
            validate_xml_name('a' + chr(x))

    def test03b(self):
        for x in valid_xml_name_char_start():
            validate_xml_name(chr(x) + 'a')

    def test03c(self):

        invalid_name_chars = set(unicode_range()) - set(valid_xml_name_char())
        invalid_name_start_chars = set(unicode_range()) - set(valid_xml_name_char_start()) - invalid_name_chars

        for x in invalid_name_chars:
            with self.assertRaisesRegexp(RuntimeError, 'contains invalid character'):
                validate_xml_name('a' + chr(x))

        for x in invalid_name_start_chars:
            with self.assertRaisesRegexp(RuntimeError, 'starts with invalid character'):
                validate_xml_name(chr(x) + 'a')

    def test04(self):

        s = ''.join(chr(x) for x in valid_xml_characters())
        validate_xml_text(s)

    def test04a(self):

        invalid_chars = set(unicode_range()) - set(valid_xml_characters())

        for x in invalid_chars:
            with self.assertRaisesRegexp(RuntimeError, 'invalid XML character: .* at offset 5'):
                print(x)
                validate_xml_text('text ' + chr(x))
