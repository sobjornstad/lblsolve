from __future__ import annotations

import collections
import random
from typing import Deque, Iterable, Iterator, Optional

SUITS = ('C', 'D', 'H', 'S')
NUMS = list(range(1,14))
NAMES = ['A'] + [str(i) for i in range(2, 11)] + ['J', 'Q', 'K']
SUIT_GLYPHS = {'C': '♣', 'D': '♦', 'H': '♥', 'S': '♠'}


class Card:
    """
    Represents a single playing card from a standard 52-card deck. It has a
    suit and a number. Cards are immutable once created.
    """
    def __init__(self, num: int, suit: str) -> None:
        assert suit in SUITS
        assert num in NUMS
        self._suit = suit
        self._num = num

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Card):
            return NotImplemented
        return self._suit == other._suit and self._num == other._num

    def __repr__(self) -> str:
        return f"{self.name}{self.suit_glyph}"

    @property
    def name(self) -> str:
        """
        The friendly name of the card. This is the card's number for 2-10,
        'A' for a number of 1, 'J' for 11, 'Q' for 12, and 'K' for 13.

        >>> Card(13, 'S').name
        'K'
        """
        return NAMES[self._num - 1]

    @property
    def num(self) -> int:
        """
        The raw number of the card, 1-13.

        >>> Card(13, 'S').num
        13
        """
        return self._num

    @property
    def suit(self) -> str:
        """
        The raw suit of the card, C, D, H, or S.

        >>> Card(5, 'S').suit
        'S'
        """
        return self._suit

    @property
    def suit_glyph(self) -> str:
        """
        The Unicode suit glyph corresponding to the card's raw suit.

        >>> Card(5, 'S').suit_glyph
        '♠'
        """
        return SUIT_GLYPHS[self._suit]

    def after(self) -> Optional[Card]:
        """
        Create and return the card after this one (that is, the one with the
        same suit and the next number in sequence). Aces are low. Calling
        after() on a king yields None.

        >>> c = Card(5, 'D')
        >>> c.after()
        6♦

        >>> c = Card(13, 'H')
        >>> c.after() is None
        True
        """
        if self.num == 13:
            return None
        return Card(self.num + 1, self.suit)

    def before(self) -> Optional[Card]:
        """
        Create and return the card before this one (that is, the one with the
        same suit and the previous number in sequence). Aces are low; calling
        before() on one yields None.

        >>> c = Card(5, 'D')
        >>> c.before()
        4♦

        >>> c = Card(1, 'H')
        >>> c.before() is None
        True
        """
        if self.num == 1:
            return None
        return Card(self.num - 1, self.suit)


class Stack:
    """
    A pile of Cards with a top and a bottom. The bottom is the
    "right" of the deque.
    """
    def __init__(self) -> None:
        self._cards: Deque[Card] = collections.deque()

    def __len__(self) -> int:
        return len(self._cards)

    def __iter__(self) -> Iterator[Card]:
        for i in self._cards:
            yield i

    def __bool__(self) -> bool:
        return len(self._cards) > 0

    def add(self, card: Card) -> None:
        "Place a card on the bottom of the stack."
        self._cards.append(card)

    def add_many(self, cards: Iterable[Card]) -> None:
        """
        Place a series of cards on the bottom of the stack in sequence,
        maintaining their order.
        """
        for i in cards:
            self._cards.append(i)

    def draw(self) -> Card:
        "Remove and return the top card on the stack."
        return self._cards.popleft()

    def draw_bottom(self) -> Card:
        "Remove and return the bottom card of the stack."
        return self._cards.pop()


class Deck(Stack):
    """
    A Stack that can be used to shuffle and deal cards to players.
    """
    def __init__(self):
        super(Deck, self).__init__()

    def fill(self):
        """
        Add one of each distinct card in the standard 52-card set to the
        deck. This is done in order, so you most likely want to shuffle()
        afterwards.
        """
        for suit in SUITS:
            for num in NUMS:
                self.add(Card(num, suit))

    def shuffle(self):
        "Shuffle all cards currently in the deck."
        random.shuffle(self._cards)
