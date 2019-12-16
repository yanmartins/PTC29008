/*
   SESSÃO CONEXÃO
   Verificação do modelo para que duas entidades sejam 
   capazes de estabelecerem uma sessão, independente 
   de qual delas iniciar a sessão.
*/

// Os tipos de mensagens
mtype = {data, cr, cc, kr, kc};
/*
   data = mensagem com payload
   cr = connect request
   cc = connect confirm
   kr = keep-alive request
   kc = keep-alive confirm
*/

// Mensagens que serão transmitidas pelos canais
chan    c1 = [1] of {mtype};
chan    c2 = [1] of {mtype};

// Entidades iniciam desconectadas.
bool conectado1 = false
bool conectado2 = false

active proctype entidade1() {
   desconectado:
      c1!cr    // Uma entidade sempre tenta tomar a iniciativa
      goto hand1

   hand1:
      printf("Hand1 %d\n", _pid)
      do
      :: c2?cr ->
         c1!cc
         goto hand2
      :: c2?cc ->
         goto hand3
      :: timeout -> // erro notificado por ARQ ou a outra entidade parou de se comunicar.
         c1!cr
         goto hand1
      od

   hand2:
      printf("Hand2 %d\n", _pid)
      do
      :: c2?cc ->
         goto conectado
      :: timeout ->  // erro notificado por ARQ ou a outra entidade parou de se comunicar.
         c1!cr
         goto hand1
      od

   hand3:
      printf("Hand3 %d\n", _pid)
      do
      :: c2?cr ->
         c1!cc
         goto conectado
      :: timeout ->  // erro notificado por ARQ
         c1!cr
         goto hand1
      od

   conectado:
      printf("Entidade %d se conectou\n", _pid)
      conectado1 = true
}

active proctype entidade2() {
   desconectado:
      c2!cr
      goto hand1

   hand1:
      printf("Hand1 %d\n", _pid)
      do
      :: c1?cr ->
         c2!cc
         goto hand2
      :: c1?cc -> 
         goto hand3
      :: timeout -> 
         c2!cr
         goto hand1
      od

   hand2:
      printf("Hand2 %d\n", _pid)
      do
      :: c1?cc ->
         goto conectado
      :: timeout -> 
         c2!cr
         goto hand1
      od

   hand3:
      printf("Hand3 %d\n", _pid)
      do
      :: c1?cr ->
         c2!cc
         goto conectado
      :: timeout -> 
         c2!cr
         goto hand1
      od

   conectado:
      printf("Entidade %d se conectou\n", _pid)
      conectado2 = true
}

// A partir de algum momento, ambas entidades permanecerão sempre conectadas.
ltl conectados { <>[] (conectado1 && conectado2) }