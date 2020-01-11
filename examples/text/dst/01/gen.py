from prestring.text import Module


def gen(*, m=None, indent='    '):
    m = m or Module(indent=indent)

    m.stmt('package main')
    m.sep()
    m.stmt('import (')
    m.stmt('\t"fmt"')
    m.stmt('\t"time"')
    m.stmt(')')
    m.sep()
    m.stmt('func worker(id int, jobs <-chan int, results chan<- int) {')
    m.stmt('\tfor j := range jobs {')
    m.stmt('\t\tfmt.Println("worker", id, "started  job", j)')
    m.stmt('\t\ttime.Sleep(time.Second)')
    m.stmt('\t\tfmt.Println("worker", id, "finished job", j)')
    m.stmt('\t\tresults <- j * 2')
    m.stmt('\t}')
    m.stmt('}')
    m.sep()
    m.stmt('func main() {')
    m.sep()
    m.stmt('\tconst numJobs = 5')
    m.stmt('\tjobs := make(chan int, numJobs)')
    m.stmt('\tresults := make(chan int, numJobs)')
    m.sep()
    m.stmt('\tfor w := 1; w <= 3; w++ {')
    m.stmt('\t\tgo worker(w, jobs, results)')
    m.stmt('\t}')
    m.sep()
    m.stmt('\tfor j := 1; j <= numJobs; j++ {')
    m.stmt('\t\tjobs <- j')
    m.stmt('\t}')
    m.stmt('\tclose(jobs)')
    m.sep()
    m.stmt('\tfor a := 1; a <= numJobs; a++ {')
    m.stmt('\t\t<-results')
    m.stmt('\t}')
    m.stmt('}')
    return m


if __name__ == "__main__":
    m = gen(indent='    ')
    print(m)
