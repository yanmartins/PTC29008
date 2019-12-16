int count;
bool incr;
 
active proctype counter() {
  do
  :: incr && count < 10 -> 
    count++
    incr = false
  :: count == 10 -> count = 0
  od
}
 
active proctype env() {
  do
  :: !incr -> incr = true
  od
}

// verifique se é garantido que o contador atinja o valor 10
ltl f1 { <>(count == 10) }

// verifique se o valor do contador cont assume o valor 10 de forma cíclica
ltl f2 { []<>(count == 10) }

// verifique se a execução dos processos possui a propriedade da justiça
