chan canal1 = [1] of {int}
chan canal2 = [1] of {int}
 
active proctype p1() {
  int msg1, msg2
 
Repetir:
  // :: condição -> execução
  // Se uma condição for verdadeira ele a executa.
  // Se mais de uma condições forem verdadeiras, uma é sorteada e executada.
  if
  :: canal1?msg1 -> printf("erro ...\n") // Simula um erro (possibilidade, não probabilidade)
  :: canal1?msg1 -> printf("Recebeu msg1=%d\n", msg1)
  :: canal2?msg2 -> printf("Recebeu msg2=%d\n", msg2)
  :: else -> printf("Canais vazios") // Ocorre quando todas as outras condições são falsas
  fi
 
  goto Repetir
}
 
active proctype p2() {
  do
  :: canal1!111 -> printf("enviei pelo canal1\n")
  :: canal2!222 -> printf("enviei pelo canal2\n")
  od
}
