#!/usr/bin/python3

import sys

import argparse

from card import Card, Deck
from instrument import Stopwatch
from lucie import Fan, Foundations, Tableau
from solve import play_deal



def check_won(foundation, deals, watch) -> None:
    if len(foundation) == 52:
        print("")
        watch.checkpoint()
        print(f"Game solved in {watch.running_time * 1000:.2f}ms using {deals} deal(s).")
        sys.exit(0)


def play_game(args, deck):
    tableau = Tableau()
    found = Foundations()
    watch = Stopwatch()

    if not args.redeal:
        iterator = range(args.deal, args.deal+1)
    else:
        iterator = range(args.deal, args.max_deal+1)

    for deal_num in iterator:
        assert deck or tableau, "Either the deck or the tableau must contain cards."
        if not deck:
            deck.add_many(tableau.gather())
        tableau.deal(deck)

        if deal_num == args.max_deal and args.merci:
            tableau, found = play_deal(tableau, found, deal_num, merci=True)
        else:
            tableau, found = play_deal(tableau, found, deal_num)
        check_won(found, deal_num, watch)

    print("")
    watch.checkpoint()
    print(f"Solution space exhausted in {watch.running_time * 1000:.2f}ms.")
    print("Unfortunately, no solutions were found.")
    sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Solve La Belle Lucie solitaire games.')
    parser.add_argument("--deal", metavar='N', type=int, default=1,
        help='Numbered deal to begin on. The base rules have 3 deals.')
    parser.add_argument("--redeal", action='store_true', default=False,
        help='If the game is not solved, automatically shuffle, redeal, and '
             'continue solving, up to (--max-deal - --deal)  times.')
    parser.add_argument("--max-deal", metavar='N', type=int, default=3,
        help='Number of total deals.')
    parser.add_argument("--merci", action='store_true', default=False,
        help='On the final deal, allow one card not on the top of its pile to be '
             'retrieved and played on the foundation or tableau.')
    parser.add_argument("--shuffle", action='store_true', default=False,
        help='Rather than taking an initial position on stdin, generate a random one.')

    args = parser.parse_args()

    deck = Deck()
    if args.shuffle:
        deck.fill()
        deck.shuffle()
    else:
        raise NotImplementedError("Not implemented, dummy")

    play_game(args, deck)


# TODO: Allow user to input stuff
# TODO: Is there a way to early break when it finds a complete solution? Not really any reason to continue searching at that point.