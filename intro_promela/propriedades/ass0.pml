chan canal1 = [1] of {int}
chan canal2 = [1] of {int}
 
active proctype p1() {
  int msg
  int n1 = 0
  int n2 = 0
 
  do
  :: canal1?msg -> n1++; assert(n1 < 10)
  :: canal1?msg -> n1--; assert(n1 < 10)
  :: canal2?msg -> n2++; assert(n2 < 15)
  :: canal2?msg -> n2--; assert(n2 < 15)
  od
}
 
active proctype p2() {
  do
  :: canal1!1
  :: canal2!1
  od
}