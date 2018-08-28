package main

import (
	"fmt"
	"os"
)

// Hello is print Hello
func Hello(name string)  {
	fmt.Printf("%s: Hello", name)
}

func main()  {
	var name string
	if len(os.Args) > 1  {
		name = os.Args[1]
	} else  {
		name = "foo"
	}
	// with block
	{
		Hello(name)
	}
}
