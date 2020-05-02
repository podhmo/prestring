default: 00 01 02 03 04

00:
	mkdir -p dst/$@
	python src/$@/hello.py > dst/$@/hello.go

01:
	mkdir -p dst/$@/
	python src/$@/person.py > dst/$@/person.go

02:
	mkdir -p dst/$@/
	python src/$@/go-routine.py > dst/$@/goroutine.go

03:
	mkdir -p dst/$@/
	python src/$@/models.py > dst/$@/models.go

04:
	mkdir -p dst/$@/
	python src/$@/empty.py > dst/$@/models.go


clean:
	rm -rf dst
