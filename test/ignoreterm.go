package main

import "fmt"
import "os"
import "os/signal"
import "time"

func main() {
  sig := make(chan os.Signal)
  quit := make(chan int)
  signal.Notify(sig) // Catch everything...     

  go func() {
    for {
      caught := <- sig
      fmt.Printf("Caught %v\n", caught)
    }
  }()

  go func() {
    for {
      time.Sleep(1 * time.Second)
      fmt.Println("Still here")
    }
  }()

  <- quit
}