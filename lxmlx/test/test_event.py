import unittest
import lxml.etree as et
from lxmlx.event import scan, unscan, with_peer, text_of


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

    def test_unscan(self):

        events = [
            dict(type='enter', tag='{ns_a}a'),
            dict(type='text',  text='Hello! '),
            dict(type='enter', tag='{ns_b}b'),
            dict(type='text',  text='World'),
            dict(type='exit'),
            dict(type='text',  text='!'),
            dict(type='exit'),
        ]
        xml = unscan(events, nsmap={'a': 'ns_a', 'b': 'ns_b'})

        result = et.tostring(xml)
        model = b'<a:a xmlns:a="ns_a" xmlns:b="ns_b">Hello! <b:b>World</b:b>!</a:a>'
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
        _roundtrip(b'<root>Hello<!-- comment -->world</root>')
        _roundtrip(b'<root><?pi1 pi text?></root>')
        _roundtrip(b'<root>Hello<?pi1 pi text?>world</root>')

    def test_text_of(self):
        xml = et.fromstring(b'<a>Hello! <b>World</b>!</a>')
        text = text_of(scan(xml))
        self.assertEqual(text, 'Hello! World!')

        xml = et.fromstring(b'<a>Hello! <b>Wor<?mypy?>ld</b>!</a>')
        text = text_of(scan(xml))
        self.assertEqual(text, 'Hello! World!')


if __name__ == '__main__':
    unittest.main()
