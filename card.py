SUITS = ('♣', '♦', '♥', '♠')
NUMS = list(range(1,14))
NAMES = ['A'] + [str(i) for i in range(2, 11)] + ['J', 'Q', 'K']

import collections
import random


class Card:
    def __init__(self, num, suit):
        assert suit in SUITS
        assert num in NUMS
        self._suit = suit
        self._num = num

    def __repr__(self):
        return self.pp()

    def after(self):
        if self.num == 13:
            return None
        return Card(self.num + 1, self.suit)

    def before(self):
        if self.num == 1:
            return None
        return Card(self.num - 1, self.suit)

    # Using named methods rather than < and >,
    # because those are kind of weirdly defined with SUITS.
    def precedes(self, other):
        return self.suit == other.suit and self.num < other.num
    
    def succeeds(self, other):
        return self.suit == other.suit and self.num > other.num

    @property
    def suit(self):
        return self._suit

    @property
    def num(self):
        return self._num

    def suitEq(self, other):
        return self._suit == other._suit
    def numEq(self, other):
        return self._num == other._num
    def __eq__(self, other):
        return self.suitEq(other) and self.numEq(other)
    def __ne__(self, other):
        return not self.__eq__(other)

    def pp(self):
        return "%s%s" % (NAMES[self._num - 1], self._suit)
    # Cards are immutable.


class Stack:
    """
    Left side is the "top" of the card stack.
    """
    def __init__(self):
        self._cards = collections.deque()

    def __len__(self):
        return len(self._cards)

    def __iter__(self):
        for i in self._cards:
            yield i

    def __bool__(self):
        return self.has_cards()

    def add(self, card):
        self._cards.append(card)

    def add_many(self, card_list):
        for i in card_list:
            self._cards.append(i)

    def draw(self):
        return self._cards.popleft()

    def draw_bottom(self):
        return self._cards.pop()

    def has_cards(self):
        return len(self._cards) > 0


class Deck(Stack):
    def __init__(self):
        super(Deck, self).__init__()

    def fill(self):
        for suit in SUITS:
            for num in NUMS:
                self.add(Card(num, suit))

    def shuffle(self):
        random.shuffle(self._cards)