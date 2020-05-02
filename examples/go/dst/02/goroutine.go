package main

import (
	"golang.org/x/net/context"
	"log"
	"sync"
)

func gen(nums ...int) <-chan int {
	out := make(chan int)
	go func() {
		for _,  n := range nums  {
			out <- n
		}
		close(out)
	}()
	return out
}

func sq(ctx context.Context, in <-chan int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for n := range in  {
			select {
			case <-ctx.Done():
				return 
			case out <- n*n:

			}

		}
	}()
	return out
}

func merge(ctx context.Context, cs ...<-chan int) <-chan int {
	var wg sync.WaitGroup
	out := make(chan int)

	output := func(c <- chan int) {
		defer wg.Done()
		for n := range c  {
			select {
			case out <- n:

			case <-ctx.Done():
				return 
			}

		}
	}

	wg.Add(len(cs))
	for _, c := range cs  {
		go output(c)
	}
	go func() {
		wg.Wait()
		close(out)
	}()
	return out
}

func main() {
	ctx := context.Background()
	ctx, cancel := context.WithCancel(ctx)

	in := gen(1, 2, 3, 4, 5)
	c1 := sq(ctx, in)
	c2 := sq(ctx, in)

	out := merge(ctx, c1, c2)

	log.Printf("%d\n", <-out) // 1
	log.Printf("%d\n", <-out) // 4
	for n := range out  {
		log.Printf("%d\n", n)
	}

	cancel()
}
