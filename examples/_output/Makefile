default: 00

00:
	rm -rf dst/$@
	mkdir -p dst/$@

	python src/$@/main.py dst/$@/create

	cp -r dst/$@/create dst/$@/update
	python src/$@/main.py dst/$@/update
	VERBOSE=1 python src/$@/main.py dst/$@/update

.PHONY: 00
clean:
	rm -rf dst

