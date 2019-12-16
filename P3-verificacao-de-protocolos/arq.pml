// Os tipos de mensagens
mtype = {data, ack};

// Mensagens que possuem tipo (data ou ack) e um bit para 
// o número de sequência
chan    c1 = [1] of {mtype, bit};
chan    c2 = [1] of {mtype, bit};
 
active proctype tx() {
    bit seq = 0
    int max_retries = 3
    int retries = 0

    estado0:
      c1!data,seq
      retries = 0
      /*
      int boff = 0
      do
      :: c1!data,seq
         retries = 0
      :: boff < 7 -> boff++
      */
    estado1:
      do
      :: c2?ack -> // simula erro, que causa, fatalmente, um timeout
         skip

      :: c2?ack,eval(seq) ->  // ack com sequência correta
         printf("TX: recebeu ack = %d\n", seq)
         seq = !seq           // inverte sequência...
         goto estado0         // ... e volta pro estado0

      :: c2?ack,eval(!seq) -> // ack com sequência errada
         if
         :: (retries < max_retries) ->
            printf("TX: erro ACK... retransmitindo com seq = %d\n", seq)
            c1!data,seq   // retransmite
            retries++
         :: else -> goto estado0
         fi

      :: timeout ->           // não recebeu ack (mesmo!)
         if
         :: (retries < max_retries) ->
            printf("TX: erro TIMEOUT... retransmitindo com seq = %d\n", seq)
            c1!data,seq   // retransmite
            retries++
         :: else -> goto estado0
         fi
      od
}
 
active proctype rx() {
    bit seq = 0

    // Este comportamento é o mesmo para os quatro estados da FSM.
    do
    :: c1?data -> // Simula erro, perda de msg
       skip
    :: c1?data,eval(seq) -> 
        printf("RX: recebeu data = %d (correto)\n", seq)
        c2!ack,seq
        seq = !seq

    :: c1?data,eval(!seq) -> 
        printf("RX: recebeu data = %d (esperado = %d)\n", !seq, seq)
        c2!ack,!seq
    od
}

// Verifica se uma entrega eventualmente terá sucesso.
ltl recebeu { <>(tx@estado0)}