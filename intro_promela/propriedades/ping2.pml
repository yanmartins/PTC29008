chan c1 = [1] of {int}
chan c2 = [1] of {int}
 
active proctype ping() {
  int x,y
 
loop:
    c1!x
    printf("%d enviou %d\n", _pid, x)
    progress: x = !x
    c2?y
    printf("%d recebeu resposta: %d\n", _pid, y)
 
    goto loop
}
 
 
active proctype pong() {
  int x
 
loop:
 
  c1?x
  printf("%d recebeu %d\n", _pid, x)
  c2!x
  printf("%d devolveu: %d\n", _pid, x)
 
  goto loop
}