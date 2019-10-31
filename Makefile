test:
	python setup.py test

example:
	make -C examples/python default
	make -C examples/go clean default
	make -C examples/js default

ci:
	$(MAKE) test example
	git diff

format:
#	pip install -e .[dev]
	black prestring setup.py

lint:
#	pip install -e .[dev]
	flake8 prestring --ignore W503,E203,E501

typing:
#	pip install -e .[dev]
	mypy --strict --ignore-missing-imports prestring

build:
#	pip install wheel
	python setup.py bdist_wheel

upload:
#	pip install twine
	twine check dist/prestring-$(shell cat VERSION)*
	twine upload dist/prestring-$(shell cat VERSION)*

.PHONY: test format lint build upload examples
