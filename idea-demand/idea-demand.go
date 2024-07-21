package main

import (
	"fmt"
)

type Saiyan struct{
	Name string
	Power int
	Father *Saiyan
}

func main() {
	goku := &Saiyan{
		Name: "Goku", 
		Power: 9000,
		Father: nil} 
	Super(goku) 
	fmt.Println(goku.Father)
}

func Super(s *Saiyan) { 
	s.Power += 10000
}