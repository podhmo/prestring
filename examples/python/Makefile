default: 00 01 02 03 04 05 06 07

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
	python src/$@/genpkg.py dst/$@
06:
	mkdir -p dst/$@
	python src/$@/typed.py > dst/$@/typed.py
07:
	mkdir -p dst/$@
	@echo ---------------------------------------- > /dev/stderr
	python -m prestring.python.transform src/$@/hello.py | tee dst/$@/hello.template.py
	@echo ---------------------------------------- > /dev/stderr
	python dst/$@/hello.template.py | tee dst/$@/hello.py
	@echo ---------------------------------------- > /dev/stderr
	python dst/$@/hello.py foo
	python src/$@/hello.py foo
	diff -u src/$@/hello.py dst/$@/hello.py
08:
	python src/$@/gen.py -o dst

clean:
	rm -rf dst
