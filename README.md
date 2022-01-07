# La Belle Lucie Solver

This is an automatic solver for the solitaire game
[La Belle Lucie](https://en.wikipedia.org/wiki/La_Belle_Lucie)
(including, optionally, the merci rule).


## Installation

This solver has no dependencies outside the standard library
(all dependencies in `requirements.txt` are needed for development only).
You can install it directly via PyPi:

```
pip install lblsolve
```

Or, if you'd like to play with the code,
you can clone this repository and install the package in editable mode:

```
pip install -r requirements.txt
```

Either way, the `lbl` command and the `lblsolve` Python package
will be available on your system.


## Use

The solver accepts a text representation of your tableau on standard input.
Each line represents a fan, while cards in each fan are separated with spaces.
Here's a typical input that's solvable with 3 deals and a *merci*:

```
KH 2S 8S
3S 5S QH
JH 4H 10D
3D 8C 8D
4C JS 7D
AH AS 5H
7C 2D 5D
AC 8H 10C
2H QD 7H
3H AD KD
4S 9S 6H
9D QC 10H
6C KS JD
6D 6S 9C
KC 9H 10S
5C 4D 7S
2C 3C JC
QS
```

You don't have to enter cards on the foundations --
they're assumed to contain all cards that aren't on the tableau.

If standard input is connected to your terminal,
you'll receive a small help message before being prompted to enter the tableau.

Alternatively, you can use the `--shuffle` option
to generate a random tableau and attempt to solve that.

There is currently minimal error-checking on inputs.
Be warned that you may get very odd results
if you input a tableau that can't have occurred by making legal moves
(for instance, if you include a 2♦ and a 4♦ but no 3♦,
 so that the foundation contains A♦ 3♦).

You can control whether the solver automatically redeals
and whether it applies the *merci* rule
with additional command-line options;
check `lbl --help` for these.

Here's what the output looks like:

```
La Belle Lucie solver
Copyright (c) 2022 Soren Bjornstad.
Use the --help switch for full command-line options.

Awaiting the tableau to solve on standard input.
Cards look like '5H', where 5 is the number of the card or 'A', 'J', 'Q', or 'K', 
and H the suit of the card, 'C', 'D', 'H', or 'S' (lowercase letters or Unicode suit glyphs also accepted).
Enter horizontal whitespace between cards of a fan and Return between fans.
To finish entering fans, press ^D. The foundations will consist of any cards not on your tableau.

KH 2S 8S
3S 5S QH
JH 4H 10D
3D 8C 8D
4C JS 7D
AH AS 5H
7C 2D 5D
AC 8H 10C
2H QD 7H
3H AD KD
4S 9S 6H
9D QC 10H
6C KS JD
6D 6S 9C
KC 9H 10S
5C 4D 7S
2C 3C JC
QS
[Read fan  0] K♥  2♠  8♠
[Read fan  1] 3♠  5♠  Q♥
[Read fan  2] J♥  4♥  10♦
[Read fan  3] 3♦  8♣  8♦
[Read fan  4] 4♣  J♠  7♦
[Read fan  5] A♥  A♠  5♥
[Read fan  6] 7♣  2♦  5♦
[Read fan  7] A♣  8♥  10♣
[Read fan  8] 2♥  Q♦  7♥
[Read fan  9] 3♥  A♦  K♦
[Read fan 10] 4♠  9♠  6♥
[Read fan 11] 9♦  Q♣  10♥
[Read fan 12] 6♣  K♠  J♦
[Read fan 13] 6♦  6♠  9♣
[Read fan 14] K♣  9♥  10♠
[Read fan 15] 5♣  4♦  7♠
[Read fan 16] 2♣  3♣  J♣
[Read fan 17] Q♠
^D

========== Deal 1 ==========
Starting tableau:
[ 0]  K♥   2♠   8♠
[ 1]  3♠   5♠   Q♥
[ 2]  J♥   4♥  10♦
[ 3]  3♦   8♣   8♦
[ 4]  4♣   J♠   7♦
[ 5]  A♥   A♠   5♥
[ 6]  7♣   2♦   5♦
[ 7]  A♣   8♥  10♣
[ 8]  2♥   Q♦   7♥
[ 9]  3♥   A♦   K♦
[10]  4♠   9♠   6♥
[11]  9♦   Q♣  10♥
[12]  6♣   K♠   J♦
[13]  6♦   6♠   9♣
[14]  K♣   9♥  10♠
[15]  5♣   4♦   7♠
[16]  2♣   3♣   J♣
[17]  Q♠

DFS for best blocking moves using 7 thread(s):
  Found 17702 total legal permutation(s) of blocking moves.   
Best sequence has 39 moves, transferring 18 cards to the foundation and leaving 34 on the tableau.

Move sequence:
  [Blocking move  ] 10♦ => 6♣  K♠  J♦
  [Blocking move  ] 6♥ => 2♥  Q♦  7♥
  [Safe build     ] 5♥ => 2♥  Q♦  7♥  6♥
  [Safe build     ] 4♥ => 2♥  Q♦  7♥  6♥  5♥
  [Safe build     ] 10♥ => J♥
  [Foundation move] A♠
  [Foundation move] A♥
  [Blocking move  ] J♣ => 9♦  Q♣
  [Safe build     ] 10♣ => 9♦  Q♣  J♣
  [Safe build     ] 9♣ => 9♦  Q♣  J♣  10♣
  [Blocking move  ] 6♠ => 5♣  4♦  7♠
  [Safe build     ] 5♦ => 6♦
  [Blocking move  ] 9♠ => K♣  9♥  10♠
  [Safe build     ] 8♠ => K♣  9♥  10♠  9♠
  [Foundation move] 2♠
  [Safe build     ] Q♥ => K♥
  [Safe build     ] 5♠ => 5♣  4♦  7♠  6♠
  [Safe build     ] 3♠ => 4♠
  [Foundation move] 3♠
  [Foundation move] 4♠
  [Foundation move] 5♠
  [Foundation move] 6♠
  [Foundation move] 7♠
  [Foundation move] 8♠
  [Foundation move] 9♠
  [Foundation move] 10♠
  [Safe build     ] 9♥ => J♥  10♥
  [Safe build     ] 8♥ => J♥  10♥  9♥
  [Safe build     ] 4♦ => 6♦  5♦
  [Foundation move] A♣
  [Blocking move  ] 7♦ => 3♦  8♣  8♦
  [Foundation move] J♠
  [Foundation move] Q♠
  [Safe build     ] 3♣ => 4♣
  [Safe build     ] 2♣ => 4♣  3♣
  [Foundation move] 2♣
  [Foundation move] 3♣
  [Foundation move] 4♣
  [Foundation move] 5♣

Final table state after deal 1:
[ 0]  K♥   Q♥
[ 1]  J♥  10♥   9♥   8♥
[ 2]  3♦   8♣   8♦   7♦
[ 3]  7♣   2♦
[ 4]  2♥   Q♦   7♥   6♥   5♥   4♥
[ 5]  3♥   A♦   K♦
[ 6]  9♦   Q♣   J♣  10♣   9♣
[ 7]  6♣   K♠   J♦  10♦
[ 8]  6♦   5♦   4♦
[ 9]  K♣

[♠] A♠ 2♠ 3♠ 4♠ 5♠ 6♠ 7♠ 8♠ 9♠ 10♠ J♠ Q♠
[♥] A♥
[♣] A♣ 2♣ 3♣ 4♣ 5♣

========== Deal 2 ==========
Starting tableau:
[ 0]  6♥   7♣   5♦
[ 1]  5♥   K♦   2♦
[ 2]  K♠   K♥   3♥
[ 3]  2♥   6♣   7♥
[ 4]  8♥   6♦   7♦
[ 5] 10♥   4♥   8♣
[ 6]  8♦   9♦   J♣
[ 7] 10♣   9♣   Q♣
[ 8]  K♣   9♥   Q♦
[ 9]  A♦   4♦   Q♥
[10]  J♥   3♦   J♦
[11] 10♦

Starting foundation:
[♠] A♠ 2♠ 3♠ 4♠ 5♠ 6♠ 7♠ 8♠ 9♠ 10♠ J♠ Q♠
[♥] A♥
[♣] A♣ 2♣ 3♣ 4♣ 5♣

DFS for best blocking moves using 3 thread(s):
  Found 7 total legal permutation(s) of blocking moves.   
Best sequence has 45 moves, transferring 29 cards to the foundation and leaving 5 on the tableau.

Move sequence:
  [Blocking move  ] J♦ => K♣  9♥  Q♦
  [Safe build     ] 10♦ => K♣  9♥  Q♦  J♦
  [Blocking move  ] J♣ => 10♣  9♣  Q♣
  [Safe build     ] 9♦ => K♣  9♥  Q♦  J♦  10♦
  [Safe build     ] 7♦ => 8♦
  [Safe build     ] 6♦ => 8♦  7♦
  [Safe build     ] 7♥ => 8♥
  [Safe build     ] 5♦ => 8♦  7♦  6♦
  [Foundation move] 6♣
  [Foundation move] 2♥
  [Foundation move] 7♣
  [Foundation move] 3♥
  [Foundation move] 8♣
  [Foundation move] 4♥
  [Safe build     ] Q♥ => K♠  K♥
  [Safe build     ] 6♥ => 8♥  7♥
  [Safe build     ] 4♦ => 8♦  7♦  6♦  5♦
  [Safe build     ] 3♦ => 8♦  7♦  6♦  5♦  4♦
  [Safe build     ] J♥ => K♠  K♥  Q♥
  [Safe build     ] 10♥ => K♠  K♥  Q♥  J♥
  [Safe build     ] 2♦ => 8♦  7♦  6♦  5♦  4♦  3♦
  [Safe build     ] A♦ => 8♦  7♦  6♦  5♦  4♦  3♦  2♦
  [Foundation move] A♦
  [Foundation move] 2♦
  [Foundation move] 3♦
  [Foundation move] 4♦
  [Foundation move] 5♦
  [Foundation move] 6♦
  [Foundation move] 7♦
  [Foundation move] 8♦
  [Foundation move] 9♦
  [Foundation move] 10♦
  [Foundation move] J♦
  [Foundation move] Q♦
  [Foundation move] K♦
  [Foundation move] 5♥
  [Foundation move] 6♥
  [Foundation move] 7♥
  [Foundation move] 8♥
  [Foundation move] 9♥
  [Foundation move] 10♥
  [Foundation move] J♥
  [Foundation move] Q♥
  [Foundation move] K♥
  [Foundation move] K♠

Final table state after deal 2:
[ 0] 10♣   9♣   Q♣   J♣
[ 1]  K♣

[♠] A♠ 2♠ 3♠ 4♠ 5♠ 6♠ 7♠ 8♠ 9♠ 10♠ J♠ Q♠ K♠
[♥] A♥ 2♥ 3♥ 4♥ 5♥ 6♥ 7♥ 8♥ 9♥ 10♥ J♥ Q♥ K♥
[♣] A♣ 2♣ 3♣ 4♣ 5♣ 6♣ 7♣ 8♣
[♦] A♦ 2♦ 3♦ 4♦ 5♦ 6♦ 7♦ 8♦ 9♦ 10♦ J♦ Q♦ K♦

========== Deal 3 ==========
Starting tableau:
[ 0] 10♣   Q♣   9♣
[ 1]  J♣   K♣

Starting foundation:
[♠] A♠ 2♠ 3♠ 4♠ 5♠ 6♠ 7♠ 8♠ 9♠ 10♠ J♠ Q♠ K♠
[♥] A♥ 2♥ 3♥ 4♥ 5♥ 6♥ 7♥ 8♥ 9♥ 10♥ J♥ Q♥ K♥
[♣] A♣ 2♣ 3♣ 4♣ 5♣ 6♣ 7♣ 8♣
[♦] A♦ 2♦ 3♦ 4♦ 5♦ 6♦ 7♦ 8♦ 9♦ 10♦ J♦ Q♦ K♦

DFS for best blocking moves using 2 thread(s):
  Found 2 total legal permutation(s) of blocking moves.   
Best sequence has 7 moves, transferring 5 cards to the foundation and leaving 0 on the tableau.

Move sequence:
  [Foundation move] 9♣
  [Safe build     ] Q♣ => J♣  K♣
  [Foundation move] 10♣
  [Merci          ] J♣ => J♣  K♣  Q♣
  [Foundation move] J♣
  [Foundation move] Q♣
  [Foundation move] K♣

Final table state after deal 3:


[♠] A♠ 2♠ 3♠ 4♠ 5♠ 6♠ 7♠ 8♠ 9♠ 10♠ J♠ Q♠ K♠
[♥] A♥ 2♥ 3♥ 4♥ 5♥ 6♥ 7♥ 8♥ 9♥ 10♥ J♥ Q♥ K♥
[♣] A♣ 2♣ 3♣ 4♣ 5♣ 6♣ 7♣ 8♣ 9♣ 10♣ J♣ Q♣ K♣
[♦] A♦ 2♦ 3♦ 4♦ 5♦ 6♦ 7♦ 8♦ 9♦ 10♦ J♦ Q♦ K♦

Game solved in 9842.60ms on deal 3.
```

If the game isn't solvable,
the sequence of moves yielding the smallest possible number
of remaining cards on the tableau is shown.

The exit status is 0 if the game was solved,
1 if it was unsolvable,
and 255 if the input was invalid.


## Computational approach

The solver categorizes all possible moves
into *safe builds*, *foundation moves*, *blocking moves*, and *mercis*.

* **Safe builds**: Cards that can be moved to another location on the tableau
  without removing any moves from the set of possible future moves
  (except, of course, the safe build itself).
  These include moving a card onto a king,
  moving a card onto a fan with only one card,
  and moving a card onto a sequence of two or more descending cards of the same suit.

  There are other edge cases that are safe builds,
  but the only consequence of leaving them out of the solver's definition
  is that the search might take a bit longer,
  so they're ignored for simplicity.

* **Foundation moves**: Cards that can be moved directly onto a foundation.
  These are also safe in the sense that they don't remove any possible future moves.

* **Blocking moves**: Other moves of cards onto other cards in the tableau.
  While these moves can allow further safe builds or foundation moves
  that wouldn't otherwise be possible,
  they can also prevent other cards from being moved to useful places,
  and they cannot ever be undone or the card moved again to anywhere other than the foundation,
  so these moves need to be considered carefully.

* **Mercis**: In the ruleset including a *merci*,
  at some point during the third deal,
  you can pick up one card that's not at the top of its fan
  and place it somewhere on the tableau or foundation.
  The solver weights these equally with blocking moves
  and considers them at the same time,
  when mercis are enabled, the current deal is the last deal,
  and no merci has yet happened this deal.
  Otherwise, it skips looking for them entirely.

We benefit from doing safe builds and foundation moves
as soon as they're available,
while blocking moves and mercis should be done
only when these possibilities are exhausted.
Completing safe builds and foundation moves as soon as they're available
removes enough computational complexity that a brute-force depth-first search
on blocking moves and mercis
becomes practical;
optimally solved games typically use a single-digit number of blocking moves.

The general structure of the solver algorithm is as follows:

1. Starting from the initial position,
   the solver builds an implicit tree (via recursion)
   of all possible sequences of blocking moves or mercis
   (if enabled and allowed on the current deal).
2. After every blocking move/merci,
   it applies all possible safe builds and foundation moves
   (alternating between doing all the safe builds possible
    and all the foundation moves possible
    until there are no more of either).
   Then it tries another blocking move or merci.
3. Recursion continues until the tableau is empty
   or there are no more legal moves.
4. At every branch,
   the child candidate sequence of moves that results in
   the most cards transferred to the foundation
   is passed back up to the parent.
   Since the tableau will be reshuffled (or useless, on the last deal)
   after all foundation moves are made,
   nothing else matters.
   (If at any point there are multiple possible sequences
    with the same number of foundations transfers,
    the one chosen is the one tried first.)
5. Back at the top level,
   the best possible sequence and the resulting tableau and foundations
   are displayed to the user.
6. If the tableau isn't empty,
   redeals were requested,
   and this wasn't the last deal,
   the tableau is gathered up, reshuffled, and redealt,
   and the process begins again from step 1.

The first level of the recursive tree is split into threads
to speed up the process.
This is often suboptimal
depending on how many possible moves there are in the initial state,
but it's a very quick and easy way to get a usually reasonable number,
and the solver almost always finishes in under a minute
(often seconds or milliseconds -- the complexity of deals seems to have high variance)
anyway.
