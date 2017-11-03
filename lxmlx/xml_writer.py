# coding: utf-8
import io
import lxml.etree as et
import re
import itertools
import contextlib
from lxmlx.events_json import ENTER, EXIT, TEXT, COMMENT, PI
from lxmlx.validate import validate_xml_text, validate_xml_name, \
    validate_pi_text, validate_comment_text, xml_escape_text, \
    xml_escape_attr

_QUAL_NAME = re.compile(r'{(.*?)}(.*)$')

class XmlWriter:
    """Incremental writer"""

    def __init__(self, target=None, xml_declaration=False):
        self._target = target
        self._tags = []
        self._empty = False
        self._active_rmap = [{}]
        if xml_declaration:
            target.write(b"<?xml version='1.0' encoding='utf-8'?>\n")

    def __push(self, tag, nsmap):
        self._tags.append(tag)
        self._nsmap.append(nsmap)

    def __pop(self):
        return self._tags.pop(), self._nsmap.pop()

    def __write(self, s):
        self._target.write(s.encode('utf-8'))

    @property
    def _rmap(self):
        return self._active_rmap[-1]

    @contextlib.contextmanager
    def _ns_resolver(self, nsmap):

        # which namespaces we need to declare?
        rmap = {b:a for a,b in nsmap.items()} if nsmap is not None else {}

        def resolve_namespace(ns, name):
            if ns in rmap:
                prefix = rmap[ns]
            elif ns in self._rmap:
                prefix = self._rmap[ns]
            else:
                prefix = self._generate_prefix()
                rmap[ns] = prefix

            if prefix is None:
                return name
            else:
                return prefix + ':' + name

        def namespaces_to_declare():
            if not rmap:
                return []

            for n,p in self._rmap.items():
                if n in rmap and rmap[n] == p:
                    del rmap[n]

            if not rmap:
                return []

            return sorted( rmap.items(), key=lambda x: x[1] if x[1] is not None else '' )

        def resolve(name=None):
            if name is None:
                return namespaces_to_declare()
            else:
                mtc = _QUAL_NAME.match(name)
                if mtc is None:
                    validate_xml_name(name)
                    return name
                ns = mtc.group(1)
                name = mtc.group(2)
                validate_xml_name(name)
                return resolve_namespace(ns, name)

        yield resolve

        if len(self._rmap) == 0:
            self._active_rmap.append(rmap)
        else:
            d = dict(self._rmap)
            d.update(rmap)
            self._active_rmap.append(d)

    def write_enter(self, tag, attrib=None, nsmap=None):
        if self._empty:
            self.__write('>')
            self._empty = False

        with self._ns_resolver(nsmap) as resolver:
            tagname = resolver(tag)

            self.__write('<' + tagname)
            self._tags.append( (tag, tagname) )

            if attrib:
                attrib = sorted( (resolver(x), xml_escape_attr(y)) for x,y in attrib.items() )

            # first, declare all namaspaces
            for ns, prefix in resolver():  # FIXME: hackish?
                if prefix is None:
                    self.__write(' xmlns="' + xml_escape_attr(ns) + '"')
                else:
                    self.__write(' xmlns:' + prefix + '="' + xml_escape_attr(ns) + '"')

        if attrib:
            for n,v in attrib:
                validate_xml_name(n)
                self.__write(' ' + n + '="' + v + '"')

        self._empty = True

    def write_exit(self, tag=None):
        old_tag, value = self._tags.pop()
        if tag is not None and old_tag != tag:
            raise RuntimeError('unbalanced XML tags: ' + tag + ' (expected ' + old_tag + ')')

        if self._empty:
            self.__write('/>')
            self._empty = False
        else:
            self.__write('</' + value + '>')

    def write_comment(self, text):
        if self._empty:
            self.__write('>')
            self._empty = False
        validate_comment_text(text)
        self.__write('<!--')
        self.__write(text)
        self.__write('-->')

    def write_pi(self, target, content=None):
        if self._empty:
            self.__write('>')
            self._empty = False
        validate_xml_name(target)
        self.__write('<?' + target)
        if content:
            validate_pi_text(content)
            self.__write(' ' + content)
        self.__write('?>')

    def write_text(self, text):
        if self._empty:
            self.__write('>')
            self._empty = False
        validate_xml_text(text)
        self.__write(xml_escape_text(text))

    def write_events(self, events):

        for event, obj in events:
            if event == ENTER:
                if obj.tag is et.Comment:
                    self.write_comment(obj.text)
                elif obj.tag is et.PI:
                    self.write_pi(obj.target, obj.text)
                else:
                    self.write_enter(obj.tag, attrib=obj.attrib, nsmap=obj.nsmap)
            elif event == EXIT:
                if obj.tag not in (et.Comment, et.PI):
                    self.write_exit(obj.tag)
            else:
                assert event == TEXT
                self.write_text(obj)

    def write_events_json(self, events, nsmap=None):

        for obj in events:
            if obj['type'] == ENTER:
                self.write_enter(obj['tag'], attrib=obj.get('attrib'), nsmap=nsmap)
            elif obj['type'] == EXIT:
                self.write_exit()
            elif obj['type'] == TEXT:
                self.write_text(obj['text'])
            elif obj['type'] == COMMENT:
                self.write_comment(obj['text'])
            elif obj['type'] == PI:
                self.write_pi(obj['target'], obj.get('text'))
            else:
                assert False, obj
