import unittest
import lxml.etree as et
from lxmlx.events_json import scan, unscan


class TestEventsJson(unittest.TestCase):

    def test_scan(self):

        xml = et.fromstring(b'<a>Hello! <b>World</b>!</a>')
        events = list(scan(xml))

        self.assertEqual(len(events), 7)
        self.assertEqual([x['type'] for x in events],
                ['enter', 'text', 'enter', 'text', 'exit', 'text', 'exit'])
        self.assertEqual(events[0]['tag'], 'a')
        self.assertEqual(events[2]['tag'], 'b')
        self.assertEqual(events[1]['text'], 'Hello! ')

    def test_roundtrip(self):

        def _roundtrip(text, model=None, nsmap=None):
            xml = et.fromstring(text)
            result = et.tostring(
                unscan(scan(xml), nsmap=nsmap)
            )
            if model is None:
                model = text

            if model != result:
                print(model)
                print(result)
                self.fail('Strings not equal')

        _roundtrip(b'<root/>')
        _roundtrip(b'<root a="A" b="B" c="C"/>')
        _roundtrip(b'<a:root xmlns:a="a">Test <a>bold</a></a:root>', nsmap={'a':'a'})
        _roundtrip(b'<root><!-- comment --></root>')
        _roundtrip(b'<root><?pi1 pi text?></root>')

if __name__ == '__main__':
    unittest.main()
