default: 00 01
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
