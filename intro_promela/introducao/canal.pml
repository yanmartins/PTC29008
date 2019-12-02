chan canal1 = [1] of {int}
chan canal2 = [1] of {int, byte}
 
active proctype p1() {
  int msg
  byte codigo
 
  // envia uma mensagem pelo canal1
  canal1!9
 
  // aguarda uma mensagem pelo canal2
  canal2?msg,codigo
 
  printf("Recebeu %d,%d\n", msg, codigo)
}
 
 
active proctype p2() {
  int msg
 
  // envia uma mensagem pelo canal2
  canal2!2,125
 
  // aguarda uma mensagem pelo canal1
  canal1?msg
 
  printf("Recebeu %d\n", msg)
}