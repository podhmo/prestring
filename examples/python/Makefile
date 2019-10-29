default: 00 01 03 04 06 07  # skip 02 05

00:
	mkdir -p dst/00
	python src/00/readme.py > dst/00/readme.py
01:
	mkdir -p dst/01
	python src/01/submodule_sample.py > dst/01/submodule_sample.py
02:
	mkdir -p dst/02
	python src/02/batch_mail.py > dst/02/batch_mail.output
03:
	mkdir -p dst/03
	python src/03/cross_product.py > dst/03/cross_product.py
04:
	mkdir -p dst/04
	python src/04/poormans_fizzbuzz.py > dst/04/fizzbuzz.py
05:
	mkdir -p dst/05
	python src/05/genpkg.py dst/05
06:
	mkdir -p dst/06
	python src/06/typed.py > dst/06/typed.py
07:
	mkdir -p dst/07
	@echo ---------------------------------------- > /dev/stderr
	python -m prestring.python.transform src/07/hello.py | tee dst/07/hello.template.py
	@echo ---------------------------------------- > /dev/stderr
	python dst/07/hello.template.py | tee dst/07/hello.py
	@echo ---------------------------------------- > /dev/stderr
	python dst/07/hello.py foo
	python src/07/hello.py foo
	diff -u src/07/hello.py dst/07/hello.py
clean:
	rm -rf dst
