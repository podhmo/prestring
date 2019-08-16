test:
	python setup.py test
example:
	make -C examples/python clean default
	make -C examples/go clean default
