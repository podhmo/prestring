default: 00 01 02 03 04 05 06 07 08 09

# readme (class)
00:
	mkdir -p dst/$(notdir $(shell echo src/$@*))
	python $(shell echo src/$@*)/readme.py > dst/$(notdir $(shell echo src/$@*))/readme.py

# readme (submodule)
01:
	mkdir -p dst/$(notdir $(shell echo src/$@*))
	python $(shell echo src/$@*)/readme.py > dst/$(notdir $(shell echo src/$@*))/readme.py

# batch mail
02:
	mkdir -p dst/$(notdir $(shell echo src/$@*))
	python $(shell echo src/$@*)/main.py > dst/$(notdir $(shell echo src/$@*))/main.py

# cross product
03:
	mkdir -p dst/$(notdir $(shell echo src/$@*))
	python $(shell echo src/$@*)/main.py > dst/$(notdir $(shell echo src/$@*))/main.py

# poorman's fizzbuzz
04:
	mkdir -p dst/$(notdir $(shell echo src/$@*))
	python $(shell echo src/$@*)/main.py > dst/$(notdir $(shell echo src/$@*))/main.py

# genpkg
05:
	mkdir -p dst/$(notdir $(shell echo src/$@*))
	python $(shell echo src/$@*)/main.py --config=$(shell echo src/$@*)/config.json dst/$(notdir $(shell echo src/$@*))

# typed codegen
06:
	mkdir -p dst/$(notdir $(shell echo src/$@*))
	python $(shell echo src/$@*)/main.py > dst/$(notdir $(shell echo src/$@*))/main.py

# transform by python -m prestring.python
07:
	mkdir -p dst/$(notdir $(shell echo src/$@*))
	@echo ---------------------------------------- > /dev/stderr
	python -m prestring.python $(shell echo src/$@*)/main.py | tee dst/$(notdir $(shell echo src/$@*))/gen.py
	@echo ---------------------------------------- > /dev/stderr
	python dst/$(notdir $(shell echo src/$@*))/gen.py | tee dst/$(notdir $(shell echo src/$@*))/main.py
	@echo ---------------------------------------- > /dev/stderr
	python dst/$(notdir $(shell echo $(shell echo src/$@*)*))/main.py foo
	python $(shell echo src/$@*)/main.py foo
	black $(shell echo src/$@*)/main.py dst/$(notdir $(shell echo $(shell echo src/$@*)*))/main.py
	diff -u $(shell echo src/$@*)/main.py dst/$(notdir $(shell echo $(shell echo src/$@*)*))/main.py

# prestring.output
08:
	mkdir -p dst/$(notdir $(shell echo src/$@*))
	python $(shell echo src/$@*)/main.py -o dst/$(notdir $(shell echo src/$@*))

# prestring.python
09:
	mkdir -p dst/$(notdir $(shell echo src/$@*))
	python -m prestring.python $(shell echo src/$@*)/hello.py > dst/$(notdir $(shell echo src/$@*))/hello.gen.py 2>&1
	python -m prestring.python $(shell echo src/$@*)/hello-with-type.py > dst/$(notdir $(shell echo src/$@*))/hello-with-type.gen.py 2>&1

# async support
10:
	mkdir -p dst/$(notdir $(shell echo src/$@*))
	python $(shell echo src/$@*/main.py) | tee dst/$(notdir $(shell echo src/$@*))/main.gen.py
	python dst/$(notdir $(shell echo src/$@*))/main.gen.py 2>&1 | tee dst/$(notdir $(shell echo src/$@*))/output.txt
	# transform
	python -m prestring.python dst/$(notdir $(shell echo src/$@*))/main.gen.py | tee dst/$(notdir $(shell echo src/$@*))/main.transform.py
	# run transform
	python dst/$(notdir $(shell echo src/$@*))/main.transform.py | tee dst/$(notdir $(shell echo src/$@*))/main.transform.gen.py
	diff -u dst/$(notdir $(shell echo src/$@*))/main.gen.py dst/$(notdir $(shell echo src/$@*))/main.transform.gen.py


# async support (for, with)
11:
	mkdir -p dst/$(notdir $(shell echo src/$@*))
	python $(shell echo src/$@*/main.py) | tee dst/$(notdir $(shell echo src/$@*))/main.gen.py
	python dst/$(notdir $(shell echo src/$@*))/main.gen.py 2>&1 | tee dst/$(notdir $(shell echo src/$@*))/output.txt
	# transform
	python -m prestring.python dst/$(notdir $(shell echo src/$@*))/main.gen.py | tee dst/$(notdir $(shell echo src/$@*))/main.transform.py
	# run transform
	python dst/$(notdir $(shell echo src/$@*))/main.transform.py | tee dst/$(notdir $(shell echo src/$@*))/main.transform.gen.py
	diff -u dst/$(notdir $(shell echo src/$@*))/main.gen.py dst/$(notdir $(shell echo src/$@*))/main.transform.gen.py


clean:
	rm -rf dst
