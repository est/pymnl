#
# Makefile for pymnl
#

SHELL = /bin/sh

package = pymnl

srcdir = .

VERSION = $(shell cat $(srcdir)/docs/VERSION)

BRANCH = "master"

TOPDIR := $(CURDIR)

TESTCASES = pymnl.tests.nlsocket,pymnl.tests.attributes,pymnl.tests.message,pymnl.tests.genl

COVERAGE2=coverage-py2.6

COVERAGE3=coverage-py3.1

.PHONY: all install test sdist tarball clean distclean

all:
	PYTHONPATH=. python ./setup.py build

install:
	PYTHONPATH=. python ./setup.py install

test:	test2 test3

test2:
	PYTHONPATH=. python ./setup.py test \
		--test-list $(TESTCASES) --test-verbose

test3:
	PYTHONPATH=. python3.1 ./setup.py test \
		--test-list $(TESTCASES) --test-verbose

testcoverage:	testcoverage2 testcoverage3
	$(COVERAGE3) combine
	$(COVERAGE3) html

testcoverage2:
	@which $(COVERAGE2) > /dev/null 2>&1 || \
		(echo "Code coverage for Python 2 not found" && exit 1)
	PYTHONPATH=. $(COVERAGE2) run --parallel-mode --branch \
		--omit="*testcommand*" \
		./setup.py test --test-list $(TESTCASES) --test-verbose

testcoverage3:
	@which $(COVERAGE3) > /dev/null 2>&1 || \
		(echo "Code coverage for Python 3 not found" && exit 1)
	PYTHONPATH=. $(COVERAGE3) run --parallel-mode --branch \
		--omit="*testcommand*" \
		./setup.py test --test-list $(TESTCASES) --test-verbose

sdist:	$(TOPDIR)/dist/${package}-$(VERSION).tar.bz2.sha256 $(TOPDIR)/dist/${package}-$(VERSION).tar.bz2.sign

$(TOPDIR)/dist/${package}-$(VERSION).tar.bz2:
	PYTHONPATH=. python ./setup.py sdist --force-manifest --formats=bztar

$(TOPDIR)/dist/${package}-$(VERSION).tar.bz2.sha256: $(TOPDIR)/dist/${package}-$(VERSION).tar.bz2
	cd $(TOPDIR)/dist && \
		sha256sum ${package}-$(VERSION).tar.bz2 \
			> ${package}-$(VERSION).tar.bz2.sha256

$(TOPDIR)/dist/${package}-$(VERSION).tar.bz2.sign: $(TOPDIR)/dist/${package}-$(VERSION).tar.bz2
	cd $(TOPDIR)/dist && \
		gpg --detach-sign -a --output \
			${package}-$(VERSION).tar.bz2.asc \
			${package}-$(VERSION).tar.bz2
	cd $(TOPDIR)/dist && \
		chmod 644 $(TOPDIR)/dist/${package}-$(VERSION).tar.bz2.asc
	cd $(TOPDIR)/dist && \
		gpg --verify $(TOPDIR)/dist/${package}-$(VERSION).tar.bz2.asc

clean:
	PYTHONPATH=. python ./setup.py clean
	rm -fr tmp/ dist/ build/ htmlcov/
	@which $(COVERAGE2) > /dev/null 2>&1 && $(COVERAGE2) erase
	@which $(COVERAGE3) > /dev/null 2>&1 && $(COVERAGE3) erase

distclean:	clean
	find $(TOPDIR) -name "*.pyc" -exec rm -f {} \;
	rm -f MANIFEST

