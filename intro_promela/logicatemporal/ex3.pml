mtype { p, v };
 
chan sema = [0] of { mtype };
 
active proctype Dijkstra()
{       byte count = 1;
end:    do
        :: (count == 1) ->
                sema!p; count = 0
        :: (count == 0) ->
                sema?v; count = 1
        od
}
 
active proctype p1()
{       do
        :: sema?p;        /* enter */
critical: skip;           /* leave */
          sema!v;
        od
}
 
active proctype p2()
{       do
        :: sema?p;        /* enter */
critical: skip;           /* leave */
          sema!v;
        od
}
 
// Apenas um processo está em sua seção crítica por vez
ltl crit { [] (! p1@critical || ! p2@critical)}
 
// Nenhum processo monopoliza a seção crítica
ltl justica { [] (p1@critical -> <> ! p1@critical) && [] (p2@critical -> <> ! p2@critical)}