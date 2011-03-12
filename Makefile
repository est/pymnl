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

test2:
	PYTHONPATH=. python ./setup.py test --test-list \
		pymnl.tests.nlsocket,pymnl.tests.attributes,pymnl.tests.message,pymnl.tests.genl \
		--test-verbose

sdist:
	PYTHONPATH=. python ./setup.py sdist --force-manifest --formats=bztar

tarball: $(TOPDIR)/tmp/${package}-$(VERSION).tar.bz2.sha256 $(TOPDIR)/tmp/${package}-$(VERSION).tar.bz2.sign

$(TOPDIR)/tmp/${package}-$(VERSION).tar.bz2.sign: $(TOPDIR)/tmp/${package}-$(VERSION).tar.bz2
	cd $(TOPDIR)/tmp && gpg --detach-sign -a --output ${package}-$(VERSION).tar.bz2.asc ${package}-$(VERSION).tar.bz2
	cd $(TOPDIR)/tmp && chmod 644 ${package}-$(VERSION).tar.bz2.asc
	cd $(TOPDIR)/tmp && gpg --verify ${package}-$(VERSION).tar.bz2.asc

$(TOPDIR)/tmp/${package}-$(VERSION).tar.bz2.sha256: $(TOPDIR)/tmp/${package}-$(VERSION).tar.bz2
	cd $(TOPDIR)/tmp && sha256sum ${package}-$(VERSION).tar.bz2 > ${package}-$(VERSION).tar.bz2.sha256

$(TOPDIR)/tmp/${package}-$(VERSION).tar.bz2:
	rm -fr $(TOPDIR)/tmp
	mkdir -p $(TOPDIR)/tmp/
	git archive --format=tar --prefix=${package}-$(VERSION)/ $(BRANCH) | (cd $(TOPDIR)/tmp/ && tar xf -)
	find $(TOPDIR)/tmp/${package}-$(VERSION) -type f -exec chmod ug+r  {} \;
	find $(TOPDIR)/tmp/${package}-$(VERSION) -type d -exec chmod ug+rx {} \;
	chmod 755 $(TOPDIR)/tmp/${package}-$(VERSION)/examples/*/*.py
	cd $(TOPDIR)/tmp && tar -ch ${package}-$(VERSION) | bzip2 > ${package}-$(VERSION).tar.bz2
	cd $(TOPDIR)/tmp && chmod 644 ${package}-$(VERSION).tar.bz2
	ls -l $(TOPDIR)/tmp/

clean:
	PYTHONPATH=. python ./setup.py clean
	rm -fr tmp/ dist/ build/

distclean:	clean
	find $(TOPDIR) -name "*.pyc" -exec rm -f {} \;
	rm -f MANIFEST

