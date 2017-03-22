import unittest
from lxmlx.xml_writer import XmlWriter
import io
import lxml.etree as et
from lxmlx.events import scan


class XmlWriterHelper(XmlWriter):

    def __init__(self, xml_declaration=False):
        self.__io = io.BytesIO()
        XmlWriter.__init__(self, self.__io, xml_declaration=xml_declaration)

    @property
    def data(self):
        return self.__io.getvalue()


class TestXmlWriter(unittest.TestCase):

    def _test_roundtrip(self, text, model=None):
        xml = et.fromstring(text)

        w = XmlWriterHelper()
        w.write_events(scan(xml))

        if model is None:
            model = text
        if w.data != model:
            print(model)
            print(et.tostring(xml))
            print(w.data)
            self.fail('Not equal')

    def test01(self):

        w = XmlWriterHelper()
        w.write_enter('root')
        w.write_exit('root')

        model = b'<root/>'
        if model != w.data:
            print(model)
            print(w.data)
            self.fail('Not equal')

    def test02(self):

        w = XmlWriterHelper(xml_declaration=True)
        w.write_enter('root')
        w.write_exit('root')

        model = b"<?xml version='1.0' encoding='utf-8'?>\n<root/>"
        if model != w.data:
            print(model)
            print(w.data)
            self.fail('Not equal')

    def test03(self):
        self._test_roundtrip(b'<root/>')
        self._test_roundtrip(b'<root>Hello</root>')
        self._test_roundtrip(b'<root>Hello&amp;</root>')
        self._test_roundtrip(b'<root>H&#65;ello&amp;</root>', model=b'<root>HAello&amp;</root>')

    def test04(self):
        self._test_roundtrip(b'<root lang="en"/>')
        self._test_roundtrip(b'<root text="hello&apos;&#10;here"/>', model=b'<root text="hello\'&#10;here"/>')

    def test05(self):
        self._test_roundtrip(b'<root><!-- this is a comment --></root>')

    def test06(self):
        self._test_roundtrip(b'<root><?pi1 this is a pi?></root>')

    def test07(self):
        self._test_roundtrip(b'<root xmlns:a="ns-a"/>')

    def test08(self):
        self._test_roundtrip(b'<root xmlns:a="ns-a"><child xmlns:b="ns-a"/></root>')

    def test08(self):
        self._test_roundtrip(b'<root xmlns:a="ns-a"><a:child a:lang="en"/></root>')
