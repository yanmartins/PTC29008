proctype hello1() {
  printf("hello world1: meu id é %d\n", _pid)
}

active proctype hello2() {
  printf("hello world2: meu id é %d\n", _pid)
  run hello1() /* Não é uma chamada de função */
}
