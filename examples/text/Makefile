default: 00 01

00:
	mkdir -p dst/$@
	python -m prestring.text src/$@/index.html --indent=2 > dst/$@/gen.py
	python dst/$@/gen.py > dst/$@/index.html
	diff -u src/$@/index.html dst/$@/index.html

01:
	mkdir -p dst/$@
	python -m prestring.text --tab src/$@/workers.go > dst/$@/gen.py
	python dst/$@/gen.py > dst/$@/workers.go
	diff -u src/$@/workers.go dst/$@/workers.go
