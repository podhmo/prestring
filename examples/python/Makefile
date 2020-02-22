default: 00 01 02 03 04 05 06 07 08 09

00:
	mkdir -p dst/$@
	python src/$@/readme.py > dst/$@/readme.py
01:
	mkdir -p dst/$@
	python src/$@/submodule_sample.py > dst/$@/submodule_sample.py
02:
	mkdir -p dst/$@
	python src/$@/batch_mail.py > dst/$@/batch_mail.output
03:
	mkdir -p dst/$@
	python src/$@/cross_product.py > dst/$@/cross_product.py
04:
	mkdir -p dst/$@
	python src/$@/poormans_fizzbuzz.py > dst/$@/fizzbuzz.py
05:
	mkdir -p dst/$@
	python src/$@/genpkg.py --config=src/$@/config.json dst/$@
06:
	mkdir -p dst/$@
	python src/$@/typed.py > dst/$@/typed.py
07:
	mkdir -p dst/$@
	@echo ---------------------------------------- > /dev/stderr
	python -m prestring.python src/$@/hello.py | tee dst/$@/gen.py
	@echo ---------------------------------------- > /dev/stderr
	python dst/$@/gen.py | tee dst/$@/hello.py
	@echo ---------------------------------------- > /dev/stderr
	python dst/$@/hello.py foo
	python src/$@/hello.py foo
	black src/$@/hello.py dst/$@/hello.py
	diff -u src/$@/hello.py dst/$@/hello.py
08:
	mkdir -p dst/$@
	python src/$@/gen.py -o dst/$@
09:
	mkdir -p dst/$@
	python -m prestring.python src/$@/hello.py > dst/$@/hello.gen.py 2>&1
	python -m prestring.python src/$@/hello-with-type.py > dst/$@/hello-with-type.gen.py 2>&1

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


clean:
	rm -rf dst
