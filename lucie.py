from copy import deepcopy
from itertools import zip_longest
from typing import Dict, List, Iterable, Iterator, Optional

from card import Card, Deck, SUIT_GLYPHS



class Fan:
    """
    The tableau of La Belle Lucie is composed of a series of fans, which deal
    out containing three cards but may in theory contain anywhere from zero
    to fifteen cards (if a king was on top of the three dealt cards and you
    built an additional twelve down in suit from there).

    Ordinarily, you may work only with the top card. A card that is the same
    suit and comes before the top card may be built onto the fan, and the top
    card may be removed and built onto another fan in this way, or placed on
    a foundation pile if it comes after that card.

    During the third deal, many rulesets allow a /merci/, in which a single
    blocked (not on top) card may be removed from any fan and placed on an
    existing fan or foundation pile.

    If a fan becomes empty, no more interactions with it are possible and it
    becomes boolean false. Users of the fan are expected to check this after
    removing cards and delete their references to the fan if it has become
    empty.
    """
    def __init__(self, cards: List[Card]) -> None:
        """
        Deal a new fan from a list of cards. No more than three cards may be
        dealt into a fan, so an AssertionError is raised if more are provided
        to the constructor.
        """
        assert len(cards) <= 3, "No more than three cards may be dealt into a fan."
        self.cards = cards

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Fan):
            return NotImplemented
        return all(i == j for i, j in zip_longest(self.cards, other.cards))

    def __iter__(self) -> Iterator[Card]:
        for i in self.cards:
            yield i

    def __repr__(self) -> str:
        return '  '.join(repr(c) for c in self.cards)

    def __bool__(self) -> bool:
        return bool(self.cards)

    def __contains__(self, item: Card) -> bool:
        return item in self.cards

    def __getitem__(self, index) -> 'Fan':
        return self.cards[index]

    def __len__(self) -> int:
        return len(self.cards)

    def pprint(self):
        "Pretty-print this fan with spacing, to be used in a tableau print."
        return '  '.join(('' if len(repr(c)) > 2 else ' ') + repr(c)
                         for c in self.cards)

    def top(self) -> Card:
        "Glimpse the top item of the fan in place."
        assert self.cards, "Calling top() on an empty fan is invalid."
        return self.cards[-1]

    def pop(self, card: Card = None) -> Card:
        """
        Remove and return the top item from the fan, or alternatively if a
        Card object is provided, that card. In the latter case, the caller
        must ensure the specified card actually exists in the fan.
        """
        if card:
            return self.cards.pop(self.cards.index(card))
        else:
            return self.cards.pop()

    def can_push(self, card: Card) -> bool:
        """
        A card can be pushed onto this fan if it comes just before the
        current top item.
        """
        if not self:
            # We can never build on an empty fan.
            return False
        if not card.after():
            # We can never build a king on anything.
            return False
        return self.top() == card.after()

    def push(self, card: Card) -> None:
        """
        Push a card onto this fan. The caller should LBYL and ensure the card
        is pushable.
        """
        assert self.can_push(card), f"{card} {card.after()} {self.top()} {self}"
        self.cards.append(card)

    def safe_build(self, card: Card) -> bool:
        """
        A card may be *safely built* on a fan if doing so does not remove any
        possible moves from the move tree. In general, this occurs when a
        card or series of cards that cannot be moved together sits on top of
        the fan, or when no cards are blocked by the fan (e.g., there's only one
        card).

        Because safe builds will never make the situation worse, a human or
        computer solver may evaluate and perform all safe builds after every
        potential blocking move, along with all foundation builds.

        This method uses a conservative definition of "safe build": there are
        some edge cases where moves not defined here can be safe. This is of
        little consequence for this method's intended use -- quickly making
        moves that are known to be an improvement -- as the complete DFS will
        catch any safe moves that are needed to make progress, just more slowly.
        """
        if not self.can_push(card):
            # We can't safely build if we can't build at all.
            return False
        elif len(self) == 1:
            # We can safely build if there is only one card (there's nothing to block).
            return True
        elif self.cards[-1].num == 13:
            # We can safely build if the top card is a king
            # (it can only be moved onto foundation anyway).
            return True
        elif self.cards[-1].after() == self.cards[-2]:
            # We can safely build if a descending run sits atop the stack
            # (the stack can only be moved onto foundation anyway).
            return True
        else:
            return False


class Foundations:
    """
    The Foundations are a set of stacks built up from ace to king. You win the game
    by moving all cards on the tableau onto such stacks.
    """
    def __init__(self):
        self.founds: Dict[List[Card]] = {}

    def __repr__(self) -> str:
        result = []
        for k, v in self.founds.items():
            result.append(f"[{SUIT_GLYPHS[k]}] " + (" ".join(repr(i) for i in v)))
        return '\n'.join(result)

    def __len__(self) -> int:
        return sum(len(v) for v in self.founds.values())

    def can_insert(self, card: Card) -> bool:
        """
        A card can be inserted into the foundations if either:

        * It is an ace (aces start new foundation piles when moved).
        * One of the foundation piles contains the card immediately before it.
        """
        if card.suit not in self.founds and card.num == 1:
            return True
        elif card.suit in self.founds and self.founds[card.suit][-1] == card.before():
            return True
        else:
            return False
    
    def insert(self, card: Card) -> bool:
        """
        Try to insert a card into the foundations. Return True if successful,
        False if it was not possible to insert.
        """
        if not self.can_insert(card):
            return False
        if card.suit not in self.founds:
            self.founds[card.suit] = [card]
        else:
            self.founds[card.suit].append(card)
        return True


class Tableau:
    """
    The tableau for La Belle Lucie consists of a series of Fans. See that class
    for details on the allowable moves, etc.
    """
    def __init__(self):
        self.fans: List[Fan] = []

    def __repr__(self) -> str:
        result = []
        for idx, fan in enumerate(self.fans):
            result.append(f"[{idx:2}] " + fan.pprint())
        return '\n'.join(result)

    def __len__(self) -> int:
        return sum(len(v) for v in self.fans)

    def teardown_empty_fans(self):
        # Remove any fans that no longer contain any cards.
        self.fans = [i for i in self.fans if i]

    def deal(self, deck: Deck) -> None:
        """
        Deal the contents of a Deck onto the tableau, creating fans of three cards
        (with three, two, or one in the final fan, depending on parity).
        """
        while deck:
            next_fan_cards = []
            for _ in range(3):
                if deck:
                    next_fan_cards.append(deck.draw())
            self.fans.append(Fan(next_fan_cards))

    def fan(self, index: int) -> Fan:
        "Return the Fan at the specified index."
        return self.fans[index]

    def fan_of(self, card: Card) -> Optional[Fan]:
        """
        Find and return the Fan that contains the specified Card,
        or None in the card isn't in the tableau.
        """
        for fan in self.fans:
            if card in fan:
                return fan
        return None

    def gather(self) -> List[Card]:
        """
        Remove and return all cards from the tableau, typically used when
        redealing. The resulting order is undefined.
        """
        L = [i for fan in self.fans for i in fan]
        self.fans.clear()
        return L

    def movable_cards(self) -> Iterable[Card]:
        "Iterate over the cards in the tableau that can currently be manipulated."
        return (i.top() for i in self.fans)

    def immovable_cards(self) -> Iterable[Card]:
        "Iterate over the cards in the tableau that *cannot* currently be manipulated."
        for fan in self.fans:
            for card in fan[:-1]:
                yield card

    def moves(self, merci: bool = False, foundation: Foundations = None):
        """
        Return a list of all legal moves on the current tableau.

        If /merci/ is set, mercis (moves of immovable cards to another
        location on the tableau or to the foundation) will be included in the
        list. If /merci/ is unset, moves to the foundation are not included
        in this list and the foundation parameter is ignored entirely, as it
        is assumed that you have already completed all foundation moves and
        safe builds prior to using this method to search for good blocking
        moves.
        """
        legal_moves = []
        for card in self.movable_cards():
            for idx, target_fan in enumerate(self.fans):
                if target_fan.can_push(card):
                    legal_moves.append(Move(card, target_fan, idx))

        if merci:
            assert foundation is not None  # only required for merci moves
            for card in self.immovable_cards():
                if foundation.can_insert(card):
                    legal_moves.append(Move(card, is_merci=True))

                for idx, target_fan in enumerate(self.fans):
                    if target_fan.can_push(card):
                        legal_moves.append(Move(card, target_fan, idx, is_merci=True))

        return legal_moves


class Move:
    def __init__(self,
                 card: Card,
                 target_fan: Optional[Fan] = None,
                 target_fan_index: Optional[int] = None,
                 is_merci: bool = False,
                 is_safe: bool = False) -> None:
        self.card = card
        if target_fan is not None:  # None = foundation move
            self.target_fan = deepcopy(target_fan)
        else:
            self.target_fan = None
        self.target_fan_index = target_fan_index
        self.is_merci = is_merci
        self.is_safe = is_safe

    @property
    def is_foundation_move(self):
        return self.target_fan is None

    def __str__(self) -> str:
        if self.is_merci and self.is_foundation_move:
            return f"[Merci          ] {self.card} => foundation"
        elif self.is_merci:
            return f"[Merci          ] {self.card} => {self.target_fan}"
        elif self.is_foundation_move:
            return f"[Foundation move] {self.card}"
        elif self.is_safe:
            return f"[Safe build     ] {self.card} => {self.target_fan}"
        else:
            return f"[Blocking move  ] {self.card} => {self.target_fan}"

    def apply(self, tableau: Tableau, foundation: Foundations) -> None:
        """
        Perform the move identified in the stack on the given tableau and foundation.
        """
        if self.is_foundation_move:
            foundation.insert(self.card)
        else:
            tableau.fan(self.target_fan_index).push(self.card)
