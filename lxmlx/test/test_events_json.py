import unittest
import lxml.etree as et
from lxmlx.events_json import scan, unscan, with_peer


class TestEventsJson(unittest.TestCase):

    def test_scan(self):

        xml = et.fromstring(b'<a>Hello! <b>World</b>!</a>')
        events = list(scan(xml))

        self.assertEqual(events, [
            dict(type='enter', tag='a'),
            dict(type='text',  text='Hello! '),
            dict(type='enter', tag='b'),
            dict(type='text',  text='World'),
            dict(type='exit'),
            dict(type='text',  text='!'),
            dict(type='exit'),
        ])

    def test_unscan(self):

        events = [
            dict(type='enter', tag='a'),
            dict(type='text',  text='Hello! '),
            dict(type='enter', tag='b'),
            dict(type='text',  text='World'),
            dict(type='exit'),
            dict(type='text',  text='!'),
            dict(type='exit'),
        ]
        xml = unscan(events)

        result = et.tostring(xml)
        model = b'<a>Hello! <b>World</b>!</a>'
        if model != result:
            print(model)
            print(result)
            self.fail()

    def test_with_peer(self):

        events = [
            dict(type='enter', tag='a'),
            dict(type='text',  text='Hello! '),
            dict(type='enter', tag='b'),
            dict(type='text',  text='World'),
            dict(type='exit'),
            dict(type='text',  text='!'),
            dict(type='exit'),
        ]

        result = list(with_peer(events))
        self.assertEqual(result, [
            (dict(type='enter', tag='a'),        None),
            (dict(type='text',  text='Hello! '), None),
            (dict(type='enter', tag='b'),        None),
            (dict(type='text',  text='World'),   None),
            (dict(type='exit'), dict(type='enter', tag='b')),
            (dict(type='text',  text='!'),       None),
            (dict(type='exit'), dict(type='enter', tag='a')),
        ])

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
