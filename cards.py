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
    fans = []
    help_msg = ("La Belle Lucie solver\n"
                "Copyright (c) 2022 Soren Bjornstad.\n"
                "Use the --help switch for full command-line options.\n\n"
                "Awaiting the tableau to solve on standard input.\n"
                "Cards look like '5H', where 5 is the number of the card "
                "or 'A', 'J', 'Q', or 'K', \n"
                "and H the suit of the card, 'C', 'D', 'H', or 'S' "
                "(lowercase letters or Unicode suit glyphs also accepted).\n"
                "Enter horizontal whitespace between cards of a fan "
                "and Return between fans.\n"
                "To finish entering fans, press ^D. "
                "The foundations will consist of any cards not on your tableau.\n\n")
    if sys.stdin.isatty():
        sys.stderr.write(help_msg)

    for line in sys.stdin:
        fan_cards = []
        for card_text in re.finditer("(?:[0-9]{1,2}|[AKQJakqj])[cCdDhHsS♣♦♥♠]", line):
            # TODO: Better error checking in from_text
            card = Card.from_text(card_text.group(0))
            if card is None:
                # TODO: This should happen if nonsense was found on the line, too
                sys.stderr.write("Oops! That doesn't appear to be a valid card.")
                sys.exit(255)
            fan_cards.append(card)

        fan = Fan(fan_cards)
        fans.append(fan)
        fan_cards.clear()
        print(f"[Read fan {len(fans)-1:2d}]", fan)


    tableau = Tableau()
    tableau.fans.extend(fans)
    all_cards = [c for fan in tableau.fans for c in fan]

    if not all_cards:
        print("No cards were entered on the tableau. Exiting.")
        sys.exit(255)
    assert len(all_cards) == len(set(all_cards)), \
        "There appear to be duplicate cards in this tableau. Please check the tableau."

    found = Foundations.infer(tableau)

    return tableau, found


def play_game(args, deck: Optional[Deck] = None, tableau: Optional[Tableau] = None,
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
        tableau, found = parse_position()

    play_game(args, tableau=tableau, found=found)


# TODO: Is there a way to early break when it finds a complete solution? Not really any reason to continue searching at that point.