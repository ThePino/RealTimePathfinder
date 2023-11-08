% Define some facts
father(john, jim).
father(john, alice).
mother(jane, jim).
mother(jane, alice).

% Define a rule
parent(X, Y) :- father(X, Y).
parent(X, Y) :- mother(X, Y).