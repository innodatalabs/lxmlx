# lxmlx
[![Build Status](https://travis-ci.org/innodatalabs/lxmlx.svg?branch=master)](https://travis-ci.org/innodatalabs/lxmlx)
[![PyPI version](https://badge.fury.io/py/lxmlx.svg)](https://badge.fury.io/py/lxmlx)

Helpers and utilities for streaming processing of XML documents. Intended to be used with [lxml](http://lxml.de)

## Installation

Attention: this package no longer supports Python 2.

If you install using `pip`, all dependencies are automatically fetched and installed:

```
pip install lxmlx
```

If you want to build from sources, follow these steps:

### Building and testing (Python 3):
```
virtualenv .venv -p python3
. .venv/bin/activate
pip install -r requirements.txt
pip install pytest
pytest lxmlx
```

## Event stream
Event stream is XML representation which is equivalent to the in-memory tree.

It is similar to SAX parsing events, except:

1. we use simplified set of events (ENTER, EXIT, TEXT, COMMENT and PI)
2. events are represented natively as Python streams (generators)
3. event objects are JSON-serializable
3. we use events for complete XML processing: parsing, transformation, writing

Each event in the stream is a dict containing at least `type` key

## ENTER event
`ENTER` event is fired to indicate the opening of an XML tag. Payload:

* `type` must be string `"enter"` (or constant `lxmlx.event.ENTER`)
* `tag` element tag
* `attrib` optional - a dictionary of attributes

Example:
```python
{
  'type'  : 'enter',
  'tag'   : 'font',
  'attrib': {
    'name' : 'Times',
    'style': 'bold'
  }
}
```

## EXIT event
`EXIT` event is fired to indicate closing of an XML tag. No payload is
expected, because it implicitly corresponds to the opening tag from `ENTER`
event.

* `type` must be string `"exit"` (or constant `lxmlx.event.EXIT`)

Example:
```python
{
  "type": "exit"
}
```

## TEXT event
`TEXT` event is fired to indicate XML `CTEXT` value. Payload is:

* `type` must be string `"text"` (or constant `lxmlx.event.TEXT`)
* `text` - required

Example:
```python
{
  "type": "text",
  "text": "Hello!"
}
```

## COMMENT

Payload is:
* `type` must be string `"comment"` (or constant `lxmlx.event.COMMENT`)
* `text` - required

Example:
```python
{
  "type": "comment",
  "text": "Hello!"
}
```

## PI
`PI` - processing instruction. Payload:

* `type` must be string `"pi"` (or constant `lxmlx.event.PI`)
* `target` - required PI target (aka tag)
* `text` - optional PI text content

Example:
```python
{
  "type"  : "pi",
  "target": "myPI",
  "text"  : "my cool text here"
}
```

Our definition of event stream is consistent with depth-first left-to-right
traversal of XML tree.

## Example
XML document below
```xml
<book>
   <chapter id="1">Introduction</chapter>
   <chapter id="2">Preface</chapter>
   <chapter id="3">Title</chapter>
</book>
```

can equivalently be represented by the following event stream:
```json
[
  {"type": "enter", "tag": "book"},

  {"type": "enter", "tag": "chapter", "attrib": {"id": "1"}},
  {"type": "text", "text": "Introduction"},
  {"type": "exit"},

  {"type": "enter", "tag": "chapter", "attrib": {"id": "2"}},
  {"type": "text", "text": "Preface"},
  {"type": "exit"},

  {"type": "enter", "tag": "chapter", "attrib": {"id": "3"}},
  {"type": "text", "text": "Title"},
  {"type": "exit"},

  {"type": "exit"}
]
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
   ''.join(evt['text'] for evt in events if evt['type']==TEXT)
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
