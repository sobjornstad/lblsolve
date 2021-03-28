#!/usr/bin/python3

import collections
from copy import deepcopy
import logging
import random
from typing import List, Iterable

suits = ('♣', '♦', '♥', '♠')
nums = list(range(1,14))
names = ['A'] + [str(i) for i in range(2, 11)] + ['J', 'Q', 'K']


class Card:
    def __init__(self, num, suit):
        assert suit in suits
        assert num in nums
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
    # because those are kind of weirdly defined with suits.
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
        return not __eq__(other)

    def pp(self):
        return "%s%s" % (names[self._num - 1], self._suit)
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
        for suit in suits:
            for num in nums:
                self.add(Card(num, suit))

    def shuffle(self):
        random.shuffle(self._cards)


class Fan:
    def __init__(self, cards: List[Card]) -> None:
        assert len(cards) <= 3
        self.cards = cards

    def __iter__(self):
        for i in self.cards:
            yield i

    def __repr__(self) -> str:
        return '  '.join(repr(c) for c in self.cards)

    def __bool__(self):
        return bool(self.cards)

    def __contains__(self, item: Card) -> None:
        return item in self.cards

    def __len__(self):
        return len(self.cards)

    def top(self):
        assert self.cards  # invalid to call an empty fan
        return self.cards[-1]

    def pop(self) -> Card:
        return self.cards.pop()

    def can_push(self, card) -> bool:
        if not self:
            # We can never build on an empty fan.
            return False
        if not card.after():
            # We can never build a king on anything.
            return False
        return self.top() == card.after()

    def pprint(self):
        return '  '.join(('' if len(repr(c)) > 2 else ' ') + repr(c)
                         for c in self.cards)

    def push(self, card) -> None:
        assert self.can_push(card)
        self.cards.append(card)

    def is_hard_blocked(self) -> bool:
        """
        A fan is hard-blocked if its top card is a king and a lower card of
        the same suit (if any lower card) is below it. No progress can ever
        be made on such a fan except through a /merci/, and the cards in it
        are guaranteed trapped until a redeal (if any).
        """
        if len(self) < 2:
            return False

        for under_card in self[:-1]:
            if self.top().succeeds(under_card):
                return True
        return False

    def safe_build(self, card) -> bool:
        if not self.can_push(card):
            # We can't safely build if we can't build at all.
            return False
        if len(self) == 1:
            # We can safely build if there is only one card.
            return True
        if self.cards[-1].num == 13:
            # We can safely build if the top card is a king.
            return True
        if self.cards[-1].after() == self.cards[-2]:
            # We can safely build if a descending run sits atop the stack.
            return True
        
        return False



class Foundations:
    def __init__(self):
        self.founds = {}

    def __repr__(self) -> str:
        result = []
        for k, v in self.founds.items():
            result.append(f"[{k}] " + (" ".join(repr(i) for i in v)))
        return '\n'.join(result)

    def __len__(self) -> int:
        return sum(len(v) for v in self.founds.values())

    def can_insert(self, card: Card) -> bool:
        if card.suit not in self.founds and card.num == 1:
            return True
        elif card.suit in self.founds and self.founds[card.suit][-1] == card.before():
            return True
        else:
            return False
    
    def insert(self, card: Card) -> bool:
        if not self.can_insert(card):
            return False
        if card.suit not in self.founds:
            self.founds[card.suit] = [card]
        else:
            self.founds[card.suit].append(card)
        return True


class Tableau:
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

    def deal(self, deck):
        while deck:
            next_fan_cards = []
            for _ in range(3):
                if deck:
                    next_fan_cards.append(deck.draw())
            self.fans.append(Fan(next_fan_cards))

    def fan(self, index) -> Fan:
        return self.fans[index]

    def fan_of(self, card):
        for fan in self.fans:
            if card in fan:
                return fan
        return None

    def gather(self) -> List[Card]:
        """
        Remove and return all cards from the tableau. Order is undefined.
        """
        L = [i for fan in self.fans for i in fan]
        self.fans.clear()
        return L

    def movable_cards(self) -> Iterable[Fan]:
        return (i.top() for i in self.fans)

    def moves(self):
        legal_moves = []
        for card in self.movable_cards():
            for idx, target_fan in enumerate(self.fans):
                if target_fan.can_push(card):
                    legal_moves.append((card, idx))
        return legal_moves

    def move_players(self, found: Foundations, move_stack: List) -> bool:
        """
        Scan all fans and move all possible cards to the foundations. Repeat
        until a complete scan of all fans has been made and no plays were
        possible.
        """
        function_success = False
        any_success = True  # to pass the loop the first time
        while any_success:
            any_success = False
            for fan in self.fans:
                while fan and found.insert(fan.top()):
                    move_stack.append(f"[Foundation move] {fan.top()}")
                    function_success = any_success = True
                    fan.pop()
            self.teardown_empty_fans()
        return function_success

    def safe_builds(self, move_stack: List) -> None:
        """
        Scan all fans and perform all safe builds. Repeat until a complete
        scan of all fans has been made and no plays were possible.

        TODO: Probably we should do foundation moves after *each* safe build?
        Either that or we need to prove that this can't yield a wrong result
        (building on top of a card that was playable on the foundation).
        And e.g., this is a little silly:

        [Safe build     ] A♣ => 7♠  5♦  3♣  2♣
        """
        function_success = False
        any_success = True  # to pass the loop the first time
        while any_success:
            any_success = False
            break_out = False
            for target_fan in self.fans:
                for source_fan in self.fans:
                    if target_fan.safe_build(source_fan.top()):
                        move_stack.append(f"[Safe build     ] {source_fan.top()} => {target_fan}")
                        target_fan.push(source_fan.pop())
                        function_success = any_success = True
                        if not source_fan:
                            break_out = True
                            break  # must tear down empty fans now
                if break_out:
                    break
            self.teardown_empty_fans()
        return function_success


def run_automatic_actions(tableau, foundation, move_stack) -> None:
    """
    Perform all actions that are always safe.
    """
    while tableau.move_players(foundation, move_stack) or tableau.safe_builds(move_stack):
        pass


def recursive_hypothetical(tableau, foundation, move_stack, reclvl=0) -> None:
    """
    Perform a complete tree search for the best possible series of blocking
    moves. Between each blocking move, all automatic moves are applied. The
    "best" series of blocking moves is the one that ends (reaches a state
    with no more legal moves) with the largest number of cards on the
    foundation. (Nothing else matters because we reshuffle the tableau once
    we reach that end state anyway.)
    """
    global tot_searches
    tot_searches += 1
    print(f"\rDFS for best blocking moves: {tot_searches} legal permutations...", end='')
    legal_moves = tableau.moves()

    # Base case: There are no legal moves in this state. Return the number of
    # cards on the foundation.
    if not legal_moves:
        #print(" " * 2 * reclvl + f"No legal moves at level {reclvl}.")
        return len(foundation), (tableau, foundation, move_stack)

    # Recursive case: find the sequence of moves following on from this one.
    best_foundation = 0
    best_state = None
    for card, target_fan_index in legal_moves:
        # Take a copy of the tableau and foundation.
        t = deepcopy(tableau)
        f = deepcopy(foundation)
        ms = deepcopy(move_stack)

        # Log move.
        ms.append(f"[Blocking move  ] {card} => {tableau.fan(target_fan_index)}")

        # For each candidate move, make the move and run any follow-on
        # automatic actions.
        cur_fan = t.fan_of(card)
        assert cur_fan is not None
        assert cur_fan.top() == card  # the card is on top -- or it wouldn't be a legal move
        cur_fan.pop()
        t.fan(target_fan_index).push(card)
        run_automatic_actions(t, f, ms)

        # And recursively repeat this process, recording the best state of any
        # of this state's children.
        #print(" " * 2 * reclvl + f"Foundation size after this move: {len(foundation)}")
        child_foundation, child_state = recursive_hypothetical(t, f, ms, reclvl+1)
        if child_foundation > best_foundation:
            best_foundation = child_foundation
            best_state = child_state

    #print(" " * 2 * reclvl + f"Return foundation size {best_foundation}")
    return best_foundation, best_state


def play_deal(tableau, found, deal):
    print("")
    print(f"Starting tableau for deal {deal}:")
    print(tableau)
    print("")
    orig_tableau_length = len(tableau)

    # search progress indicator
    global tot_searches
    tot_searches = 0

    move_stack = []
    run_automatic_actions(tableau, found, move_stack)
    _, state = recursive_hypothetical(tableau, found, move_stack)
    if state is None:
        pass  # there were no legal moves at all
    else:
        tableau, found, move_stack = state
    
    # Figure out where to stop listing moves, seeing as any moves after
    # the final foundation move are pointless.
    last_foundation = -1
    for idx, move in enumerate(move_stack):
        if move.startswith("[Foundation"):
            last_foundation = idx

    print("")
    if not move_stack:
        print("Darn! No legal moves from this position would allow a foundation move.")
    else:
        print(f"Best sequence has {last_foundation+1} moves, "
              f"transferring {orig_tableau_length - len(tableau)} cards to the foundation "
              f"and leaving {len(tableau)} on the tableau.")
        print("")
        print("Moves:")
        for move in move_stack[:last_foundation+1]:
            print("  " + move)
        if last_foundation + 1 < len(move_stack):
            print(f"  ({len(move_stack) - last_foundation - 1} further move(s) omitted "
                  f"because they do not enable any further foundation moves)")

    print("")
    print(f"Final table state after deal {deal}:")
    print(tableau)
    print("")
    print(found)

    return tableau, found


def play_game():
    deck = Deck()
    tableau = Tableau()
    found = Foundations()

    # first deal: fill deck with 52 cards
    deck.fill()
    deck.shuffle()
    tableau.deal(deck)
    tableau, found = play_deal(tableau, found, 1)

    # second deal: fill deck with tableau contents
    assert not deck
    deck.add_many(tableau.gather())
    deck.shuffle()
    tableau.deal(deck)
    play_deal(tableau, found, 2)

    # third deal: fill deck with tableau contents
    assert not deck
    deck.add_many(tableau.gather())
    deck.shuffle()
    tableau.deal(deck)
    play_deal(tableau, found, 3)


play_game()