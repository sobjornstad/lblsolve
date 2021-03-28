from typing import List, Iterable

from card import Card


MERCI_TO_FOUNDATION_FAN = -1


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

    def __getitem__(self, index) -> 'Fan':
        return self.cards[index]

    def __len__(self):
        return len(self.cards)

    def top(self):
        assert self.cards  # invalid to call an empty fan
        return self.cards[-1]

    def pop(self, card=None) -> Card:
        if card:
            return self.cards.pop(self.cards.index(card))
        else:
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
        assert self.can_push(card), f"{card} {card.after()} {self.top()} {self}"
        self.cards.append(card)

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

    def immovable_cards(self) -> Iterable[Fan]:
        for fan in self.fans:
            for card in fan[:-1]:
                yield card

    def moves(self, merci=False, foundation=None):
        legal_moves = []
        for card in self.movable_cards():
            for idx, target_fan in enumerate(self.fans):
                if target_fan.can_push(card):
                    legal_moves.append((card, idx, False))

        if merci:
            assert foundation is not None  # only required for merci moves
            for card in self.immovable_cards():
                if foundation.can_insert(card):
                    legal_moves.append((card, MERCI_TO_FOUNDATION_FAN, True))

                for idx, target_fan in enumerate(self.fans):
                    if target_fan.can_push(card):
                        legal_moves.append((card, idx, True))

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

