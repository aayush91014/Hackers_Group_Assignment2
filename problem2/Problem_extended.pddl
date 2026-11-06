(define (problem mars-rover-extended)
  (:domain mars-rover)
  (:objects curiosity - rover base sitea siteb sitec sited sitee sitef - location rock1 rock2 rock3 rock4 rock5 rock6 rock7 - sample
            bay1 bay2 - bay drill1 - equipment)
  (:init (at-rover curiosity base) (at-equipment drill1 sitee) (empty bay1) (empty bay2) (soft rock1) (at-sample rock1 sitea) (soft rock2) (at-sample rock2 siteb) (hard rock3) (at-sample rock3 sitec) (soft rock4) (at-sample rock4 sited) (hard rock5) (at-sample rock5 sitef) (soft rock6) (at-sample rock6 sitee) (hard rock7) (at-sample rock7 sitef) (connected base sitea) (connected sitea base) (connected sitea sitec) (connected sitec sitea) (connected siteb sited) (connected sited siteb) (connected sitec sitee) (connected sitee sitec) (connected sited sitee) (connected sitee sited) (connected sitee sitef) (connected sitef sitee) (connected sitec sited))
  (:goal (and (delivered rock1) (delivered rock2) (delivered rock3) (delivered rock4) (delivered rock5) (delivered rock6) (delivered rock7) (empty bay1) (empty bay2) (at-rover curiosity base))))
