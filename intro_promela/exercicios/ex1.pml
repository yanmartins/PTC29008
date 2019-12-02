// Escreva um modelo para o problema do produtor e consumidor. 
// Suponha que o produtor produza 10 mensagens e depois termine, 
// e o buffer intermediário tenha capacidade para 4 mensagens.

 chan buffer = [4] of {int,bool}

active proctype produtor() {
    int msg = 1
    do
    :: msg <= 10 ->
       printf("Enviou %d\n", msg)
       buffer!msg,false
       msg++
    :: msg > 10  ->
       buffer!msg,true
       break
    od
}
 
active proctype consumidor() {
    int msg
    bool last = false
    do
    :: !last ->
       buffer?msg,last
       printf("Recebeu %d\n", msg)
    :: last -> 
       break
    od
}

// chan buffer = [4] of {int,bool}

// active proctype produtor() {
//     int msg = 1
//     do
//     :: buffer!msg,false ->
//        msg++
//     :: buffer!msg,true  ->
//        break
//     od
// }
 
// active proctype consumidor() {
//     int msg = 0
//     bool last = false
//     do
//     :: !last ->
//     :: buffer?msg,last
//        printf("Recebeu %d\n", msg)
//     :: timeout -> break
//     od
// }