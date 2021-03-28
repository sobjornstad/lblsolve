#!/usr/bin/python3

import sys

from card import Card, Deck
from instrument import Stopwatch
from lucie import Fan, Foundations, Tableau, MERCI_TO_FOUNDATION_FAN
from solve import play_deal



def check_won(foundation, deals, watch) -> None:
    if len(foundation) == 52:
        print("")
        watch.checkpoint()
        print(f"Game solved in {watch.running_time * 1000:.2f}ms using {deals} deal(s).")
        sys.exit(0)


def play_game():
    deck = Deck()
    tableau = Tableau()
    found = Foundations()
    watch = Stopwatch()

    # first deal: fill deck with 52 cards
    deck.fill()
    deck.shuffle()
    tableau.deal(deck)
    tableau, found = play_deal(tableau, found, 1)
    check_won(found, 1, watch)

    # second deal: fill deck with tableau contents
    assert not deck
    deck.add_many(tableau.gather())
    deck.shuffle()
    tableau.deal(deck)
    tableau, found = play_deal(tableau, found, 2)
    check_won(found, 2, watch)

    # third deal: fill deck with tableau contents and allow merci
    assert not deck
    deck.add_many(tableau.gather())
    deck.shuffle()
    tableau.deal(deck)
    tableau, found = play_deal(tableau, found, 3, merci=True)
    check_won(found, 3, watch)

    print("")
    watch.checkpoint()
    print(f"Solution space exhausted in {watch.running_time * 1000:.2f}ms.")
    print("Unfortunately, this game was not solvable.")


play_game()