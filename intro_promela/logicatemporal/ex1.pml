int n=7
 
active proctype teste() {
  do
  :: n > 0 -> n--
  :: n < 5 -> n++
  od
}

// Está acontecendo?
ltl formula1 { n == 7 }
ltl formula2 { n == 5 }

// Sempre acontece?
ltl formula3 { [](n == 7) } // Falso
ltl formula4 { [](n >= 0) } // Verdade

// Com certeza em algum momento acontece?
ltl formula5 { <>(n == 7) } // Verdade
ltl formula6 { <>(n == 5) } // Verdade
ltl formula7 { <>(n == 0) } // Falso

// Sempre irá acontecer em algum momento futuro
ltl formula8 { []<>(n != 5) } // Verdade
ltl formula9 { []<>(n == 5) } // Falso

// A partir de um momento irá acontecer sempre
ltl formula10 { <>[](n < 5) } // Falso
ltl formula11 { <>[](n < 6) } // Verdade

ltl f1 { (n > 5) U (n <= 5) } // Verdade
ltl f2 { (n > 5) U (n == 5) } // Verdade
ltl f3 { (n == 6) U (n <= 5) } // Falso
ltl f4 { <>((n == 6) U (n <= 5)) }  // Verdade