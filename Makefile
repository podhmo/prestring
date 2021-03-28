test:
	python setup.py test

example:
	$(MAKE) -C examples

ci:
	$(MAKE) lint typing test example
	git diff

format:
#	pip install -e .[dev]
	black prestring setup.py

lint:
#	pip install -e .[dev]
	# stop the build if there are Python syntax errors or undefined names
	flake8 prestring --count --select=E9,F63,F7,F82 --show-source --statistics
	# exit-zero treats all errors as warnings. The GitHub editor is 127 chars wide
	flake8 prestring --count --ignore W503,E203,E501 --exit-zero --max-complexity=10 --max-line-length=127 --statistics

typing:
#	pip install -e .[dev]
	mypy --strict --ignore-missing-imports prestring

build:
#	pip install wheel
	python setup.py sdist bdist_wheel

upload:
#	pip install twine
	twine check dist/prestring-$(shell cat VERSION)*
	twine upload dist/prestring-$(shell cat VERSION)*

.PHONY: test format lint build upload examples
