// Modifique seu modelo da questão anterior para que 
// existam 2 produtores.

 chan buffer = [4] of {int,bool}

proctype produtor() {
    int msg = 1
    do
    :: msg <= 10 ->
       printf("%d: Enviou %d\n", _pid, msg)
       buffer!msg,false
       msg++
    :: msg > 10  ->
       buffer!msg,true
       break
    od
}

// Neste caso, o consumidor não está fazendo uso da flag
// para o fim de uma transmissão :(
active proctype consumidor() {
    int msg
    do
    :: buffer?msg,last ->
       printf("%d: Recebeu %d\n", _pid, msg)
    :: timeout -> 
       break
    od
}

active proctype inicio(){
    run produtor()
    run produtor()
}