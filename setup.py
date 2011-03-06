#!/usr/bin/python

from distutils.core import setup

from pymnl.tests.testcommand import test

def get_version():
    version_file = open("docs/VERSION")
    try:
        version = version_file.readline()
    finally:
        version_file.close()
    return version[:-1]

setup(
    name = "pymnl",
    version = get_version(),
    author = "Sean Robinson",
    author_email = "seankrobinson@gmail.com",
    maintainer_email = "pymnl-dev@lists.tuxfamily.org",
    description = """pymnl (rhymes with hymnal) is a pure Python
re-implmentation of libmnl and provides a minimal interface to Linux
Netlink.""",
    url = "http://pymnl.wikispot.org/",
    packages = ['pymnl', 'pymnl.tests'],
    provides = ['pymnl'],
    scripts = ['examples/genl/genl-family-get.py'],

    data_files=[('', ['README',]),
                ('docs', ['docs/AUTHORS', 'docs/BUGS', 'docs/LICENSE.GPL',
                          'docs/LICENSE.LGPL', 'docs/NEWS', 'docs/ROADMAP',
                          'docs/TODO', 'docs/VERSION',
                          'docs/api-checklist.txt', 'docs/python2-dev.txt',
                          'docs/python3-dev.txt',
                          ]),
               ],

    platforms = "Linux",
    license = "LGPL for module; GPL for example apps",
    keywords = "Netlink genl socket",
    download_url = "https://pymnl.tuxfamily.org",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: Lesser General Public License (LGPL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: System',
    ],
    cmdclass={'test': test},
)

