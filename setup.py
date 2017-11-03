from setuptools import setup
from lxmlx import __version__, __description__, __url__, __author__, \
    __author_email__, __keywords__

NAME = 'lxmlx'

setup(
    name=NAME,
    version=__version__,
    description=__description__,
    url=__url__,
    author=__author__,
    author_email=__author_email__,
    keywords=__keywords__,

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
