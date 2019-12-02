mtype = {ack, nak, err} /* Equivalente a um enum */
 
active proctype hello() {
  int x;
  pid p;
  mtype m = ack
 
  p = _pid;
  x = x + 1;
  printf("hello world: meu id é %d e x=%d\n", p, x)
  printf("... e m=")
  printm(m) /* Exibe o valor simbólico */
  printf("\n")
}
