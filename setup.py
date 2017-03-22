from setuptools import setup, find_packages
import io
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with io.open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='lxmlx',
    version='0.1.0',
    description='Helpers and utilities to be used with lxml',
    long_description=long_description,
    url='https://github.com/innodatalabs/lxmlx',
    author='Mike Kroutikov',
    author_email='mkroutikov@innodata.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='lxml xml events sax',
    packages=['lxmlx'],
    install_requires=['lxml'],
)
