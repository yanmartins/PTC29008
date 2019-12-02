// Escreva um modelo para um protocolo do tipo pare-e-espere
// em um ambiente de execução livre de erros.

// Os tipos de mensagens
mtype = {data, ack};

// Mensagens que possuem tipo (data ou ack) e um bit para 
// o número de sequência
chan    c1 = [1] of {mtype, bit};
chan    c2 = [1] of {mtype, bit};
 
active proctype sender() {
    bit seq = 0
    inicio:
        c1!data,seq
        c2?ack,eval(seq)    // Aguarda a sequência desejada
        printf("TX: recebeu ack = %d\n", seq)
        seq = !seq
        goto inicio
}
 
active proctype receiver() {
    bit seq = 0
    do
    :: c1?data,eval(seq) -> 
       c2!ack,seq
       printf("RX: recebeu data = %d\n", seq)
       seq = !seq
    od
}