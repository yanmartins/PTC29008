chan c1 = [1] of {int}
chan c2 = [1] of {int}
 
active proctype ping() {
  int x,y
 
  do
  :: x < 10 ->
    c1!x
    printf("%d enviou %d\n", _pid, x)
    x++
    c2?y
    printf("%d recebeu resposta: %d\n", _pid, y)
  :: else -> break
  od
}
 
 
active proctype pong() {
  int x
 
loop:
 
  end: c1?x
  printf("%d recebeu %d\n", _pid, x)
  c2!x
  printf("%d devolveu: %d\n", _pid, x)
 
  goto loop
}