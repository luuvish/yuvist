PYTHON = python
CHECKSCRIPT = kivy/tools/pep8checker/pep8kivy.py
YUVIST_DIR = yuvist/
NOSETESTS = nosetests

.PHONY: build force mesabuild pdf style stylereport hook test batchtest cover clean distclean theming

build:
	$(PYTHON) setup.py build_ext --inplace

force:
	$(PYTHON) setup.py build_ext --inplace -f

mesabuild:
	/usr/bin/env USE_MESAGL=1 $(PYTHON) setup.py build_ext --inplace

pdf:
	$(MAKE) -C doc latex && make -C doc/build/latex all-pdf

html:
	env USE_EMBEDSIGNATURE=1 $(MAKE) force
	$(MAKE) -C doc html

style:
	$(PYTHON) $(CHECKSCRIPT) $(YUVIST_DIR)

stylereport:
	$(PYTHON) $(CHECKSCRIPT) -html $(YUVIST_DIR)

hook:
	# Install pre-commit git hook to check your changes for styleguide
	# consistency.
	cp yuvist/tools/pep8checker/pre-commit.githook .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit

test:
	-rm -rf yuvist/tests/build
	$(NOSETESTS) yuvist/tests

cover:
	coverage html --include='$(YUVIST_DIR)*' --omit '$(YUVIST_DIR)data/*,$(YUVIST_DIR)tools/*,$(YUVIST_DIR)tests/*'

install:
	python setup.py install

clean:
	-rm -rf doc/build
	-rm -rf build
	-rm -rf htmlcov
	-rm .coverage
	-rm .noseids
	-rm -rf yuvist/tests/build
	-find yuvist -iname '*.so' -exec rm {} \;
	-find yuvist -iname '*.pyc' -exec rm {} \;
	-find yuvist -iname '*.pyo' -exec rm {} \;

distclean: clean
	-git clean -dxf

theming:
	$(PYTHON) -m kivy.atlas yuvist/data/images/defaulttheme 512 yuvist/tools/theming/defaulttheme/*.png
