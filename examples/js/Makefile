default: 00 01 02 03
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
	node dst/02/arraylike.js
.PHONY: 02

03:
	mkdir -p dst/03/
	python src/03/gen.py > dst/03/exc.js
03-use:
	node dst/03/exc.js
.PHONY: 03
