import unittest
import lxml.etree as et
from lxmlx.events import scan, unscan


class TestEvents(unittest.TestCase):

    def test_scan(self):

        xml = et.fromstring(b'<a>Hello! <b>World</b>!</a>')
        events = list(scan(xml))

        self.assertEqual(len(events), 7)
        self.assertEqual([x[0] for x in events],
                ['enter', 'text', 'enter', 'text', 'exit', 'text', 'exit'])
        self.assertEqual(events[0][1].tag, 'a')
        self.assertEqual(events[2][1].tag, 'b')
        self.assertEqual(events[1][1], 'Hello! ')

    def test_roundtrip(self):

        def _roundtrip(text, model=None):
            result = et.tostring(unscan(scan(et.fromstring(text))))
            if model is None:
                model = text

            if model != result:
                print(model)
                print(result)
                self.fail('Strings not equal')

        _roundtrip(b'<root/>')
        _roundtrip(b'<root a="A" b="B" c="C"/>')
        _roundtrip(b'<a:root xmlns:a="a">Test <a>bold</a></a:root>')
        _roundtrip(b'<root><!-- comment --></root>')
        _roundtrip(b'<root><?pi1 pi text?></root>')
