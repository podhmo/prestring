00:
	mkdir -p output
	@echo ---------------------------------------- > /dev/stderr
	python -m prestring.python.transform 00hello.py | tee output/00hello.template.py
	@echo ---------------------------------------- > /dev/stderr
	python output/00hello.template.py | tee output/00hello.py
	@echo ---------------------------------------- > /dev/stderr
	handofcats "output/00hello.py:hello" foo

# self
01:
	mkdir -p output
	@echo ---------------------------------------- > /dev/stderr
	python -m prestring.python.transform `pyinspect resolve prestring.python.transform` | tee output/01transform.template.py
	@echo ---------------------------------------- > /dev/stderr
	python output/01transform.template.py | tee output/01transform.py
	@echo ---------------------------------------- > /dev/stderr
	diff -u `pyinspect resolve prestring.python.transform` output/01transform.py | sed "s@$$HOME@HOME@g" > output/01transform.diff
