default: 00 01 02
00:
	mkdir -p dst/00/
	python src/00/gen.py > dst/00/cat.js
00-use:
	node dst/00/cat.js dst/00/cat.js
.PHONY: 00

01:
	mkdir -p dst/01/
	python src/01/gen.py > dst/01/marked.js
01-use:
	node dst/01/marked.js src/01/sample.md > dst/01/sample.html
.PHONY: 01

02:
	mkdir -p dst/02/
	python src/02/gen.py > dst/02/arraylike.js
02-use:
	node dst/02/arraylike.js src/02/sample.md > dst/02/sample.html
.PHONY: 02
