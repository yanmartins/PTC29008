mtype = {delimitador, esc, dados}
chan    c1 = [1] of {mtype, bit};

active proctype tx() {
   do
   :: c1!delimitador // Quadro correto com escape
      c1!dados
      c1!dados
      c1!esc
      c1!dados
      c1!delimitador

   :: c1!delimitador // Quadro correto sem escape
      c1!dados
      c1!dados
      c1!dados
      c1!delimitador

   :: c1!delimitador // Quadro com erro escape
      c1!dados
      c1!dados
      c1!esc
      c1!esc
      c1!delimitador
   
   :: c1!delimitador // Quadro com overflow
      c1!dados
      c1!dados
      c1!dados
      c1!dados
      c1!esc
      c1!dados
      c1!delimitador

   :: c1!delimitador // Quadro vazio
      c1!delimitador
   od
}

active proctype rx() {
    int max = 3
    int n = 0
    ocioso:
        do
        :: c1?delimitador ->
           printf("Delimitador\n")
           n = 0
           goto recepcao
        :: c1?dados -> goto ocioso
        :: c1?esc -> goto ocioso
        od

    recepcao:
        do
        :: c1?dados -> 
           if
           :: n < max -> 
              printf("Byte: %d\n", dados)
              n++
           :: else -> 
              printf("overflow\n")
              goto ocioso
           fi
        :: c1?esc -> 
           goto escape
        :: c1?delimitador ->
           if
           :: n == 0 -> 
              printf("Delimitador (Vazio)\n"); 
              goto recepcao;
           :: n > 0 -> 
              printf("Delimitador\n")
              goto ocioso
           fi
        :: timeout -> 
           goto ocioso
        od

    escape:
        do
        :: c1?dados -> 
           printf("Byte Escape: %d\n", dados)
           n++
           goto recepcao
        :: c1?esc -> 
           printf("Erro escape...\n")
           goto ocioso
        :: c1?delimitador -> 
           printf("Erro escape...\n")
           goto ocioso
        :: timeout -> 
           goto ocioso
        od
}

ltl enviada { <>(rx@ocioso)}