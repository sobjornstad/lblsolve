from copy import deepcopy
from typing import List

from lucie import Tableau, Foundations, MERCI_TO_FOUNDATION_FAN


def move_players(tableau: Tableau, found: Foundations, move_stack: List) -> bool:
    """
    Scan all fans and move all possible cards to the foundations. Repeat
    until a complete scan of all fans has been made and no plays were
    possible.
    """
    function_success = False
    any_success = True  # to pass the loop the first time
    while any_success:
        any_success = False
        for fan in tableau.fans:
            while fan and found.insert(fan.top()):
                move_stack.append(f"[Foundation move] {fan.top()}")
                function_success = any_success = True
                fan.pop()
        tableau.teardown_empty_fans()
    return function_success


def safe_builds(tableau, move_stack: List) -> bool:
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
        for target_fan in tableau.fans:
            for source_fan in tableau.fans:
                if target_fan.safe_build(source_fan.top()):
                    move_stack.append(f"[Safe build     ] {source_fan.top()} => {target_fan}")
                    target_fan.push(source_fan.pop())
                    function_success = any_success = True
                    if not source_fan:
                        break_out = True
                        break  # must tear down empty fans now
            if break_out:
                break
        tableau.teardown_empty_fans()
    return function_success

def run_automatic_actions(tableau, foundation, move_stack) -> None:
    """
    Perform all actions that are always safe.
    """
    while move_players(tableau, foundation, move_stack) or safe_builds(tableau, move_stack):
        pass


def recursive_hypothetical(tableau, foundation, move_stack, merci=False, reclvl=0):
    """
    Perform a complete tree search for the best possible series of blocking
    moves. Between each blocking move, all automatic moves are applied. The
    "best" series of blocking moves is the one that ends (reaches a state
    with no more legal moves) with the largest number of cards on the
    foundation. (Nothing else matters because we reshuffle the tableau once
    we reach that end state anyway.)
    """
    global tot_searches
    if tot_searches == 0 or not tot_searches % 100:
        print(f"\rDFS for best blocking moves: {tot_searches} legal permutations...", end='')
    tot_searches += 1

    if merci:
        legal_moves = tableau.moves(merci, foundation)
    else:
        legal_moves = tableau.moves()

    # Base case: There are no legal moves in this state. This can happen either
    # because we are blocked or because we have won. Return the number of
    # cards on the foundation.
    if not legal_moves or not tableau:
        #print(" " * 2 * reclvl + f"No legal moves at level {reclvl}.")
        return len(foundation), (tableau, foundation, move_stack)

    # Recursive case: find the sequence of moves following on from this one.
    best_foundation = 0
    best_state = None
    for card, target_fan_index, is_merci in legal_moves:
        # Take a copy of the tableau and foundation.
        t = deepcopy(tableau)
        f = deepcopy(foundation)
        ms = deepcopy(move_stack)

        # For each candidate move, make the move and run any follow-on
        # automatic actions.
        cur_fan = t.fan_of(card)
        assert cur_fan is not None
        if target_fan_index == MERCI_TO_FOUNDATION_FAN:
            ms.append(f"[Merci          ] {card} => foundation")
            merci = False  # only one merci is allowed during the tree
            cur_fan.pop(card)
            f.insert(card)
        else:
            if is_merci:
                ms.append(f"[Merci          ] {card} => {tableau.fan(target_fan_index)}")
                merci = False  # only one merci is allowed during the tree
            else:
                assert cur_fan.top() == card  # the card is on top, or it wouldn't be a legal move
                ms.append(f"[Blocking move  ] {card} => {tableau.fan(target_fan_index)}")
            cur_fan.pop(card)
            t.fan(target_fan_index).push(card)
        run_automatic_actions(t, f, ms)

        # Recurse into child states, recording the best state of any
        # of this state's children.
        #print(" " * 2 * reclvl + f"Foundation size after this move: {len(foundation)}")
        child_foundation, child_state = recursive_hypothetical(t, f, ms, merci, reclvl+1)
        if child_foundation > best_foundation:
            best_foundation = child_foundation
            best_state = child_state

    #print(" " * 2 * reclvl + f"Return foundation size {best_foundation}")
    return best_foundation, best_state


def play_deal(tableau, found, deal, merci=False):
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
    _, state = recursive_hypothetical(tableau, found, move_stack, merci)
    print(f"\rDFS for best blocking moves: {tot_searches} legal permutations...", end='')
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
