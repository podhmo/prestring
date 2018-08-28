package main

import (
	"encoding/json"
	logging "log"
)

type PersonStatus string

const (
	PersonHungry = PersonStatus("hungry")
	PersonAngry = PersonStatus("angry")
)

type Person struct {
	Name string `json:"name"`
	Age int `json:"age"`
	Status PersonStatus `json:"status"`
}

func main()  {
	person := &Person{Name: "foo", Age: 20, Status: PersonHungry}
	b, err := json.Marshal(person)
	if err != nil  {
		logging.Fatal(err)
	}
	logging.Println(string(b))
}
