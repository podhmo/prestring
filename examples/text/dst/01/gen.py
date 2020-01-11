from prestring.text import Module


def gen(*, m=None, indent='\t'):
    m = m or Module(indent=indent)

    m.stmt('package main')
    m.sep()
    m.stmt('import (')
    with m.scope():
        m.stmt('"fmt"')
        m.stmt('"time"')
    m.stmt(')')
    m.sep()
    m.stmt('func worker(id int, jobs <-chan int, results chan<- int) {')
    with m.scope():
        m.stmt('for j := range jobs {')
        with m.scope():
            m.stmt('fmt.Println("worker", id, "started  job", j)')
            m.stmt('time.Sleep(time.Second)')
            m.stmt('fmt.Println("worker", id, "finished job", j)')
            m.stmt('results <- j * 2')
        m.stmt('}')
    m.stmt('}')
    m.sep()
    m.stmt('func main() {')
    m.sep()
    with m.scope():
        m.stmt('const numJobs = 5')
        m.stmt('jobs := make(chan int, numJobs)')
        m.stmt('results := make(chan int, numJobs)')
        m.sep()
        m.stmt('for w := 1; w <= 3; w++ {')
        with m.scope():
            m.stmt('go worker(w, jobs, results)')
        m.stmt('}')
        m.sep()
        m.stmt('for j := 1; j <= numJobs; j++ {')
        with m.scope():
            m.stmt('jobs <- j')
        m.stmt('}')
        m.stmt('close(jobs)')
        m.sep()
        m.stmt('for a := 1; a <= numJobs; a++ {')
        with m.scope():
            m.stmt('<-results')
        m.stmt('}')
    m.stmt('}')
    return m


if __name__ == "__main__":
    m = gen(indent='\t')
    print(m)
