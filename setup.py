from setuptools import setup
import io
import os
import re

NAME = 'lxmlx'

def meta(name, default='__raise__'):
    with io.open(os.path.join(NAME, '__init__.py'), encoding='utf-8') as f:
        text = f.read()
    pattern = r'''__{meta}__\s*=\s*(\'\'\'|\"\"\"|\"|\')(.*?)\1'''.format(meta=name)
    mtc = re.search(pattern, text, re.MULTILINE|re.DOTALL)
    if mtc is not None:
        return mtc.group(2)
    if default != '__raise__':
        return default
    raise RuntimeError('Could not find __{meta}__ in {name}/__init__.py'.format(meta=meta, name=NAME))

setup(
    name=NAME,
    version=meta('version'),
    description=meta('description'),
    long_description=meta('long_description', 'See ' + meta('url')),
    url=meta('url'),
    author=meta('author'),
    author_email=meta('author_email'),
    keywords=meta('keywords'),

    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=[NAME],
    install_requires=['lxml'],
)
