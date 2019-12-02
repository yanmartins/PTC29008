// Escreva um modelo para um protocolo do tipo pare-e-espere
// em um ambiente de execução em que erros são possíveis.
// Seu modelo deve prever a perda de mensagens, retransmissões 
// e descarte de mensagens duplicadas.

// Os tipos de mensagens
mtype = {data, ack};

// Mensagens que possuem tipo (data ou ack) e um bit para 
// o número de sequência
chan    c1 = [1] of {mtype, bit};
chan    c2 = [1] of {mtype, bit};
 
active proctype tx() {
    bit seq = 0
    estado0:
      c1!data,seq

    estado1:
      do
      :: c2?ack -> // simula erro, que causa, fatalmente, um timeout
         skip
      :: c2?ack,eval(seq) ->  // ack com sequência correta
         printf("TX: recebeu ack = %d\n", seq)
         seq = !seq           // inverte sequência...
         goto estado0         // ... e volta pro estado0
      :: c2?ack,eval(!seq) -> // ack com sequência errada
         printf("TX: recebeu ack = %d\n", seq)
         skip                 // não faz nada
      :: timeout ->           // não recebeu ack (mesmo!)
         printf("TX: erro ... retransmitindo com seq = %d\n", seq)
         c1!data,seq
      od
}
 
active proctype rx() {
    bit seq = 0
    do
    :: c1?data -> printf("erro ...\n")
    :: c1?data,eval(seq) -> 
       printf("RX: recebeu data = %d (correto)\n", seq)
       c2!ack,seq
       seq = !seq
    :: c1?data,eval(!seq) -> 
       printf("RX: recebeu data = %d (esperado = %d)\n", !seq, seq)
       c2!ack,!seq
    od
}