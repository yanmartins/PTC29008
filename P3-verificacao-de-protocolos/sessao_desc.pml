/*
   SESSÃO DESCONEXÃO
   Verificação do modelo para duas entidades alcancem, 
   onde o término de sessão eventualmente será concluído 
   para ambas as partes.
*/

// Os tipos de mensagens
mtype = {data, dr, dc, kr};
/*
    data = mensagem com payload
    dr = disconnect request
    dc = disconnect confirm
    kr = keep-alive request
*/

// Mensagens que serão transmitidas pelos canais
chan    c1 = [1] of {mtype};
chan    c2 = [1] of {mtype};

// Entidades iniciam conectadas.
bool desconectado1 = false
bool desconectado2 = false

active proctype entidade1() {
    conectado:
        do
        :: c1!dr ->   // tomou a iniciativa da desconexão
           printf("Iniciativa %d\n", _pid)
           goto half1

        :: c2?dr -> c1!dr   // recebeu solicitação de desconexão
           printf("Solicitação %d\n", _pid)
           goto half2
        od

    half1:
        do
        :: c2?data -> printf("Mensagem")
        :: c2?kr -> c1!dr
        :: c2?dr -> c1!dc
           goto desconectado
        :: timeout -> goto desconectado  // erro notificado por ARQ
        od

    half2:
        do
        :: c2?dr -> c1!dr
        :: c2?dc -> goto desconectado
        :: timeout -> goto desconectado
        od

    desconectado:
        desconectado1 = true
        printf("Entidade %d se desconectou\n", _pid)
}

active proctype entidade2() {
    conectado:
        do
        :: c1!dr ->   // tomou a iniciativa da desconexão
           printf("Iniciativa %d\n", _pid)
           goto half1

        :: c1?dr -> c2!dr   // recebeu solicitação de desconexão
           printf("Solicitação %d\n", _pid)
           goto half2
        od

    half1:
        do
        :: c1?data -> printf("Mensagem")
        :: c1?kr  -> c2!dr
        :: c1?dr -> c2!dc
           goto desconectado
        :: timeout -> goto desconectado  // erro notificado por ARQ
        od

    half2:
        do
        :: c1?dr -> c2!dr
        :: c1?dc -> goto desconectado
        :: timeout -> goto desconectado
        od

    desconectado:
        printf("Entidade %d se desconectou\n", _pid)
        desconectado2 = true
}

// A partir de algum momento, ambas entidades permanecerão sempre desconectadas.
ltl desc { <>[](desconectado1 && desconectado2) }