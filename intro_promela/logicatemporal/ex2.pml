int n = 5
bool down = true
 
active proctype ex2() {
  do
  :: down ->
    n--
    down = (n > 0)
  :: else ->
    n++
    down = (n == 5)
  od
}

ltl f1 { [](down -> <> !down) }
ltl f2 { [](down -> <> !down) && [](!down -> <>down) }
ltl f3 { []<>(!down -> <> (n == 5)) }
ltl f4 { []<>(down -> <> (n == 0)) }
//ltl f5 { <>((n == 0) && (!down)) }