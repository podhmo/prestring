default: 00

00:
	mkdir -p dst/$@
	python -m prestring.text.transform src/$@/index.html --indent=2 > dst/$@/gen.py
	python dst/$@/gen.py > dst/$@/index.html
	diff -u src/$@/index.html dst/$@/index.html
