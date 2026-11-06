% Royal Archive Access Verification
% Step 1: Predicate logic representation
% archivist(X), verifies(X,R), trusted(X), access(X,R),
% permitted(X,R), inspects(X,R), hidden_mark(R), stored(R),
% sealed(R), royal_archive(R).

% Step 2: Negation of goal
% Goal: trusted(mira). Negated goal: not trusted(mira).

% Step 3: Implication removal (representative clauses)
% (archivist(X) AND verifies(X,R)) -> trusted(X)
% becomes: not archivist(X) OR not verifies(X,R) OR trusted(X).
% (trusted(X) AND access(X,R)) -> permitted(X,R)
% becomes: not trusted(X) OR not access(X,R) OR permitted(X,R).
% (inspects(X,R) AND hidden_mark(R)) -> verifies(X,R)
% becomes: not inspects(X,R) OR not hidden_mark(R) OR verifies(X,R).
% stored(R) -> sealed(R) becomes: not stored(R) OR sealed(R).

% Step 4-7: Standardized, Skolem-free CNF clauses.
% C1: ~archivist(X) v ~verifies(X,R) v trusted(X)
% C2: ~trusted(X) v ~access(X,R) v permitted(X,R)
% C3: ~inspects(X,R) v ~hidden_mark(R) v verifies(X,R)
% C4: ~stored(R) v sealed(R)
% Facts are unit clauses.

archivist(mira).
access(mira, scroll_7).
inspects(mira, scroll_7).
hidden_mark(scroll_7).
stored(scroll_7).
royal_archive(scroll_7).

% Clause-form facts and rules as executable Prolog predicates.
trusted(X) :- archivist(X), verifies(X, _).
permitted(X,R) :- trusted(X), access(X,R).
verifies(X,R) :- inspects(X,R), hidden_mark(R).
sealed(R) :- stored(R).

% Step 8: Resolution-refutation trace.
% From inspects(mira,scroll_7) and hidden_mark(scroll_7),
% resolve C3 to obtain verifies(mira,scroll_7).
% From archivist(mira) and verifies(mira,scroll_7),
% resolve C1 to obtain trusted(mira).
%
% Add negated goal: ~trusted(mira).
% Resolve trusted(mira) with ~trusted(mira) to derive [].
%
% The following predicate prints the ordered resolvent sequence.
resolution_trace :-
    writeln('Initial facts:'),
    writeln('  archivist(mira)'),
    writeln('  inspects(mira,scroll_7)'),
    writeln('  hidden_mark(scroll_7)'),
    writeln('Negated goal: not trusted(mira)'),
    writeln('Resolvent 1: verifies(mira,scroll_7)'),
    writeln('Resolvent 2: trusted(mira)'),
    writeln('Resolvent 3: []  (contradiction)'),
    writeln('Therefore Mira is trusted.').

% Run: ?- resolution_trace.
% Verify: ?- trusted(mira).
