from copy import deepcopy
from typing import List

from lucie import Tableau, Foundations, MERCI_TO_FOUNDATION_FAN, Move


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
                move_stack.append(Move(fan.top()))
                function_success = any_success = True
                fan.pop()
        tableau.teardown_empty_fans()
    return function_success


def safe_builds(tableau, move_stack: List) -> bool:
    """
    Scan all fans and perform all safe builds. Repeat until a complete
    scan of all fans has been made and no plays were possible.

    TODO: Probably we should do foundation moves after *each* safe build?
    e.g., this is a little silly: [Safe build     ] A♣ => 7♠  5♦  3♣  2♣
    """
    function_success = False
    any_success = True  # to pass the loop the first time
    while any_success:
        any_success = False
        break_out = False
        for t_idx, target_fan in enumerate(tableau.fans):
            for source_fan in tableau.fans:
                if target_fan.safe_build(source_fan.top()):
                    move_stack.append(Move(source_fan.top(), target_fan, t_idx, is_safe=True))
                    target_fan.push(source_fan.pop())
                    function_success = any_success = True
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


def maximize_state(cur_best_foundation, new_foundation, cur_best_state, new_state):
    if new_foundation > cur_best_foundation:
        return new_foundation, new_state
    else:
        return cur_best_foundation, cur_best_state


def try_legal_move(tableau, foundation, move_stack, merci, move, reclvl, best_foundation, best_state):
    cur_fan = tableau.fan_of(move.card)
    assert cur_fan is not None

    # Move cards as appropriate, and unset merci for future moves if we did a merci.
    cur_fan.pop(move.card)
    move_stack.append(move)
    move.apply(tableau, foundation)
    merci = merci and not move.is_merci

    # Proceed as far as we can with automatic actions.
    run_automatic_actions(tableau, foundation, move_stack)

    # Recurse into child states, recording the best state of any child.
    #print(" " * 2 * reclvl + f"Foundation size after this move: {len(foundation)}")
    child_foundation, child_state = recursive_hypothetical(tableau, foundation, move_stack, merci, reclvl+1)
    return maximize_state(best_foundation, child_foundation, best_state, child_state)


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
    if not legal_moves:
        #print(" " * 2 * reclvl + f"No legal moves at level {reclvl}.")
        return len(foundation), (tableau, foundation, move_stack)

    # Recursive case: find the sequence of moves following on from this one.
    best_foundation = 0
    best_state = None
    for move in legal_moves:
        # Take a copy of the tableau and foundation.
        t = deepcopy(tableau)
        f = deepcopy(foundation)
        ms = deepcopy(move_stack)

        child_foundation, child_state = try_legal_move(t, f, ms, merci, move, reclvl, best_foundation, best_state)
        best_foundation, best_state = maximize_state(best_foundation, child_foundation,
                                                     best_state, child_state)

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
        if move.is_foundation_move:
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
            print("  " + str(move))
        if last_foundation + 1 < len(move_stack):
            print(f"  ({len(move_stack) - last_foundation - 1} further move(s) omitted "
                  f"because they do not enable any further foundation moves)")

    print("")
    print(f"Final table state after deal {deal}:")
    print(tableau)
    print("")
    print(found)

    return tableau, found
