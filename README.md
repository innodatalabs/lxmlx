# lxmlx
[![Build Status](https://travis-ci.org/innodatalabs/lxmlx.svg?branch=master)](https://travis-ci.org/innodatalabs/lxmlx)
[![PyPI version](https://badge.fury.io/py/lxmlx.svg)](https://badge.fury.io/py/lxmlx)

Helpers and utilities to be used with lxml

## Requirements

1. Python 3.3 or better (for `yield from` support)
2. `lxml` (obviously)

## Event stream
Event stream is XML representation which is equivalent to the in-memory tree.

It is similar to SAX parsing events, except:

1. we use simplified set of events (three events, actually - ENTER, EXIT, and TEXT)
2. events are represented natively as Python streams (generators)
3. we use events for complete XML processing: parsing, transformation, writing

Each event in the stream is a tuple, containing:
* event type
* event object

Events types:
1. `ENTER` event is fired to indicate the opening of an XML tag. Event object is
   `lxml.etree.Element` where value for `tag` and `attrib` attributes are
   guaranteed to be set. Children and text/tail attributes should not be used.
2. `EXIT` event is fired to indicate closing of an XML tag. Event object is
   `lxml.etree.Element` object, same as in the matching `ENTER`.
3. `TEXT` event is fired to indicate XML `CTEXT` value.

Our definition of event stream is consisten with depth-first left-to-right
traversal of XML tree.

Example:
```
<book>
   <chapter id="1">Introduction</chapter>
   <chapter id="2">Preface</chapter>
   <chapter id="3">Title</chapter>
</book>
```

can equivalently be represented by the following event stream:
```
ENTER, lxml.etree.Element('book')
ENTER, lxml.etree.Element('chapter', {'id': '1'})
TEXT , "Introduction"
EXIT , lxml.etree.Element('chapter', {'id': '1'})
ENTER, lxml.etree.Element('chapter', {'id': '2'})
TEXT , "Preface"
EXIT , lxml.etree.Element('chapter', {'id': '2'})
ENTER, lxml.etree.Element('chapter', {'id': '3'})
TEXT , "title"
EXIT , lxml.etree.Element('chapter', {'id': '3'})
EXIT , lxml.etree.Element('book')
```

### Why do we need event stream representation of XML?
Some tasks are easier done using tree representation, but other
tasks are better done on event stream representation.

1. Stripping some XML tags. Remove some tags from XML document, leaving
   text and other tags intact. In terms of XML tree this requires
   carefully taking care of the children and contained text, and is
   pretty difficult to get it right. Especially if you need to
   remove many tags from a single tree - mutating the tree for each
   one.

   Using event stream representation this is as easy as suppressing
   matching `ENTER` and `EXIT` events.

2. Extracting text content from an XML fragment. Using traditional
   tree representation this is not a difficult task. But using event stream
   representation this becomes quite trivial: accept only `TEXT` events and
   join the resulting text pieces together:
   ```
   ''.join(txt for evt,txt in events if evt==TEXT)
   ```

3. Wrapping XML elements. Daunting task using XML tree representation. Very
   easy using events stream - just inject wrappers each time you detect
   `ENTER` or `EXIT` of a wrapee.

4. When implemented right, event stream uses limited memory, independent of
   the size of the XML document. Even huge XML documents can be transformed
   quickly using small amount of RAM.

## Well-formed event stream

Not every sequence of events is a valid event stream. The requirement of
well-formedness asserts that stream corresponds to left-to-right depth-first
traversal of some tree.
