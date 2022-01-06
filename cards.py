#!/usr/bin/python3

import re
import sys
from typing import NoReturn, Optional

import argparse

from card import Card, Deck
from instrument import Stopwatch
from lucie import Fan, Foundations, Tableau
from solve import play_deal



def check_won(tableau: Tableau, deals: int, watch: Stopwatch) -> None:
    if not tableau:
        print("")
        watch.checkpoint()
        print(f"Game solved in {watch.running_time * 1000:.2f}ms on deal {deals}.")
        sys.exit(0)


def parse_position() -> Deck:
    cards = []
    for line in sys.stdin:
        for card_text in re.finditer("(?:[0-9]{1,2}|[AKQJ])[cCdDhHsS♣♦♥♠]", line):
            print("Read: ", card_text)
            # TODO: Better error checking in from_text
            card = Card.from_text(card_text.group(0))
            if card is None:
                # TODO: This should happen if nonsense was found on the line, too
                sys.stderr.write("Oops! That doesn't appear to be a valid format.\n")
                sys.stderr.write("Enter 'A', 'J', 'Q', 'K', or 2-10, plus a suit ")
                sys.stderr.write("(C, D, H, or S, or the filled Unicode glyphs)\n")
                sys.stderr.write("for each card. Three cards (one fan) per line, ")
                sys.stderr.write("separated by spaces.\n")
                sys.exit(255)
            cards.append(card)

    deck = Deck()
    deck.add_many(cards)
    return deck


def play_game(args, deck: Optional[Deck], tableau: Optional[Tableau] = None,
             found: Optional[Foundations] = None) -> NoReturn:
    """
    Play a game of LBS, beginning from either a shuffled /deck/
    or an initial position with a /tableau/ and a /found/ation.
    """
    assert deck is not None or (tableau is not None and found is not None)

    watch = Stopwatch()
    if deck is not None:
        tableau = Tableau()
        found = Foundations()
        tableau.deal(deck)

    if not args.redeal:
        iterator = range(args.deal, args.deal+1)
    else:
        iterator = range(args.deal, args.max_deal+1)

    first_managed_deal = True
    for deal_num in iterator:
        if not first_managed_deal:
            # If this isn't the first deal the solver has worked on,
            # it should gather, shuffle, and redeal the tableau.
            deck.add_many(tableau.gather())
            deck.shuffle()
            tableau.deal(deck)
        first_managed_deal = False

        if args.merci and (deal_num == args.max_deal or not args.redeal):
            tableau, found = play_deal(tableau, found, deal_num, merci=True)
        else:
            tableau, found = play_deal(tableau, found, deal_num)
        check_won(tableau, deal_num, watch)

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
        #TODO: This isn't going to work for a mid-game position:
        # we should parse to a tableau rather than to a deck.
        deck = parse_position()

    play_game(args, deck)


# TODO: Is there a way to early break when it finds a complete solution? Not really any reason to continue searching at that point.