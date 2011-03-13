#
# Makefile for pymnl
#

SHELL = /bin/sh

package = pymnl

srcdir = .

VERSION = $(shell cat $(srcdir)/docs/VERSION)

BRANCH = "master"

TOPDIR := $(CURDIR)

.PHONY: all install test sdist tarball clean distclean

all:
	PYTHONPATH=. python ./setup.py build

install:
	PYTHONPATH=. python ./setup.py install

test:	test2 test3

test2:
	PYTHONPATH=. python ./setup.py test --test-list \
		pymnl.tests.nlsocket,pymnl.tests.attributes,pymnl.tests.message,pymnl.tests.genl \
		--test-verbose

test3:
	PYTHONPATH=. python3.1 ./setup.py test --test-list \
		pymnl.tests.nlsocket,pymnl.tests.attributes,pymnl.tests.message,pymnl.tests.genl \
		--test-verbose

sdist:
	PYTHONPATH=. python ./setup.py sdist --force-manifest --formats=bztar


clean:
	PYTHONPATH=. python ./setup.py clean
	rm -fr tmp/ dist/ build/

distclean:	clean
	find $(TOPDIR) -name "*.pyc" -exec rm -f {} \;
	rm -f MANIFEST

