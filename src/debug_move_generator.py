import math
import time
from evaluate import evaluate, evaluate_move_value
from treelib import Node, Tree
import uuid

def call_counter(func):
    def helper(*args, **kwargs):
        helper.calls += 1
        return func(*args, **kwargs)
    helper.calls = 0
    helper.__name__= func.__name__

    return helper

def timer(func):
    def helper(*args, **kwargs):
        tic = time.perf_counter()
        result = func(*args, **kwargs)
        toc = time.perf_counter()
        print(f"{func.__name__} took {toc - tic:0.4f} seconds to execute")
        return result
    helper.__name__= func.__name__

    return helper

def sort_moves_by_value(board, moves):
    return sorted(moves, key=lambda move: evaluate_move_value(board, move), reverse=True)

def prioritize_legal_moves(board):
    legal_moves = board.legal_moves

    grouped_moves = groupby(legal_moves, compose_move_type(board))
    sorted_nonquiet_moves = sort_moves_by_value(board, grouped_moves['nonquiet'])
    sorted_quiet_moves = sort_moves_by_value(board, grouped_moves['quiet'])

    # nonquiet moves should be searched first, since they are most likely to increase value
    return sorted_nonquiet_moves + sorted_quiet_moves

# should checks be handled differently than captures? the bot is pretty bad at checkmating
# how to handle en passant?
def get_moves_to_dequiet(board):
    moves_to_dequiet = list(filter(lambda move: board.is_capture(move) or board.gives_check(move), board.legal_moves))

    return sort_moves_by_value(board, moves_to_dequiet)

# https://www.chessprogramming.org/Quiescence_Search
# implement capture ordering... https://chess.stackexchange.com/questions/27257/chess-engine-quiescence-search-increases-required-time-by-a-factor-of-20
# only quiesce on the square where the previous move was made!!
@call_counter
def quiesce(board, depth, alpha, beta, maximizing_player, tree, parent_id):
    if board.is_variant_win() and maximizing_player:
        # black wins (white made prior move)
        return -math.inf
    elif board.is_variant_loss() and maximizing_player:
        # white wins (black made prior move)
        return math.inf
    elif board.is_variant_win() and not maximizing_player:
        # white wins (black made prior move)
        return math.inf
    elif board.is_variant_loss() and not maximizing_player:
        # black wins (white made prior move)
        return -math.inf
    elif board.is_variant_draw():
        return 0

    if depth == 0:
        return evaluate(board)

    dequiet_moves = get_moves_to_dequiet(board)

    if not dequiet_moves:
        return evaluate(board)

    if maximizing_player:
        max_eval = -math.inf
        for move in dequiet_moves:
            node_id = uuid.uuid4()
            tree.create_node(str(board.turn) + " " + str(move), node_id, parent=parent_id)
            board.push(move)
            move_eval = quiesce(board, depth - 1, alpha, beta, not maximizing_player, tree, node_id)
            alpha = max(alpha, move_eval)
            max_eval = max(max_eval, move_eval)
            node = tree.get_node(node_id)
            node.tag = f"{node.tag} eval={str(move_eval)} alpha={alpha} beta={beta} minimax_calls={minimax.calls} quiesce_calls={quiesce.calls} [quiesce]"
            board.pop()
            if beta <= alpha:
                break
        return alpha
    else:
        min_eval = math.inf
        for move in dequiet_moves:
            node_id = uuid.uuid4()
            tree.create_node(str(board.turn) + " " + str(move), node_id, parent=parent_id)
            board.push(move)
            move_eval = quiesce(board, depth - 1, alpha, beta, not maximizing_player, tree, node_id)
            beta = min(beta, move_eval)
            min_eval = min(min_eval, move_eval)
            node = tree.get_node(node_id)
            node.tag = f"{node.tag} eval={str(move_eval)} alpha={alpha} beta={beta} minimax_calls={minimax.calls} quiesce_calls={quiesce.calls} [quiesce]"
            board.pop()
            if beta <= alpha:
                break
        return beta

@call_counter
def smart_quiescence(board, depth, alpha, beta, maximizing_player, tree, parent_id):
    if board.is_checkmate() and maximizing_player:
        # black wins (white made prior move)
        return -math.inf
    elif board.is_checkmate() and not maximizing_player:
        # white wins (black made prior move)
        return math.inf
    elif board.is_stalemate() or board.can_claim_draw() or board.is_fivefold_repetition() or board.is_seventyfive_moves():
        return 0

    stand_pat = evaluate(board)

    if depth == 0:
        return stand_pat

    if maximizing_player:
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat
    else:
        if stand_pat <= alpha:
            return alpha
        if beta > stand_pat:
            beta = stand_pat

    moves = get_moves_to_dequiet(board)
    
    if maximizing_player:
        for move in moves:
            node_id = uuid.uuid4()
            tree.create_node(str(board.turn) + " " + str(move), node_id, parent=parent_id)
            board.push(move)
            score = smart_quiescence(board, depth - 1, alpha, beta, not maximizing_player, tree, node_id)
            board.pop()
            node = tree.get_node(node_id)
            node.tag = f"W {str(move)} {str(score)} [q]"


            if score >= beta:
                return beta
            if beta <= alpha:
                break

            alpha = max(alpha, score)
        return alpha
    else:
        for move in moves:
            node_id = uuid.uuid4()
            tree.create_node(str(board.turn) + " " + str(move), node_id, parent=parent_id)
            board.push(move)
            score = smart_quiescence(board, depth - 1, alpha, beta, not maximizing_player, tree, node_id)
            board.pop()
            node = tree.get_node(node_id)
            node.tag = f"B {str(move)} {str(score)} [q]"

            if score <= alpha:
                return alpha
            if beta <= alpha:
                break
            beta = min(beta, score)
        return beta

# Minimax algorithm w/ alpha beta pruning: https://www.youtube.com/watch?v=l-hh51ncgDI
# what happens if maximizing player is black? account for this in the evaluate function
@call_counter
def minimax(board, depth, alpha, beta, maximizing_player, tree, parent_id):
    if board.is_checkmate() and maximizing_player:
        # black wins (white made prior move)
        return -math.inf
    elif board.is_checkmate() and not maximizing_player:
        # white wins (black made prior move)
        return math.inf
    elif board.is_stalemate() or board.can_claim_draw() or board.is_fivefold_repetition() or board.is_seventyfive_moves():
        return 0

    # "dequiet" the position if it's a capture/check
    # https://www.naftaliharris.com/blog/chess/
    if depth == 0:
        # return evaluate(board)
        # the hand-off is incorrect... seems to be returning the first quiesced value
        # return quiesce(board, 7, alpha, beta, not maximizing_player, tree, parent_id)
        return smart_quiescence(board, 5, -math.inf, math.inf, maximizing_player, tree, parent_id)

    prioritized_moves = prioritize_legal_moves(board) if not quiesce else get_moves_to_dequiet(board)

    if maximizing_player:
        max_eval = -math.inf
        for move in prioritized_moves:
            node_id = uuid.uuid4()
            board.push(move)
            move_eval = minimax(board, depth - 1, alpha, beta, not maximizing_player, tree, node_id)
            alpha = max(alpha, move_eval)
            max_eval = max(max_eval, move_eval)
            if move_eval > alpha:
                tree.create_node("W " + str(move), node_id, parent=parent_id)
                node = tree.get_node(node_id)
                node.tag = f"W {str(move)} eval={str(move_eval)} alpha={alpha} beta={beta} minimax_calls={minimax.calls} quiesce_calls={smart_quiescence.calls}"
            board.pop()
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in prioritized_moves:
            node_id = uuid.uuid4()
            board.push(move)
            move_eval = minimax(board, depth - 1, alpha, beta, not maximizing_player, tree, node_id)
            beta = min(beta, move_eval)
            min_eval = min(min_eval, move_eval)
            if move_eval < beta:
                tree.create_node(str(maximizing_player) + " " + str(move), node_id, parent=parent_id)
                node = tree.get_node(node_id)
                node.tag = f"B {str(move)} eval={str(move_eval)} alpha={alpha} beta={beta} minimax_calls={minimax.calls} quiesce_calls={smart_quiescence.calls}"
            board.pop()
            if beta <= alpha:
                break
        return min_eval

# input list to split, function to group by
def groupby(list, fn):
    grouped_list = {
        'nonquiet': [],
        'quiet': []
    }

    for i in list:
        key = fn(i)

        # could initialize keys rather than checking here
        if key not in grouped_list:
            grouped_list[key] = []

        grouped_list[key].append(i)

    return grouped_list

# get rid of this
@timer
def evaluate_move(board, move, depth, maximizing_player, tree):
    node_id = uuid.uuid4()
    tree.create_node(str(board.turn) + " " + str(move), node_id, parent="root")
    board.push(move)
    print(f"maximizing_player={maximizing_player}")
    move_value = minimax(board, depth - 1, -math.inf, math.inf, not maximizing_player, tree, node_id)
    node = tree.get_node(node_id)
    node.tag = node.tag + " " + str(move_value)
    board.pop()
    return move_value

def compose_move_type(board):
    def determine_move_type(move):
        if board.is_capture(move) or board.gives_check(move):
            return 'nonquiet'
        else:
            return 'quiet'

    return determine_move_type

def next_move(board, depth):
    color = board.turn
    best_move_value = -math.inf if color else math.inf
    best_move = None

    legal_moves = board.legal_moves
    grouped_moves = groupby(legal_moves, compose_move_type(board))

    sorted_nonquiet_moves = sorted(grouped_moves['nonquiet'], key=lambda move: evaluate_move_value(board, move), reverse=True)
    sorted_quiet_moves = sorted(grouped_moves['quiet'], key=lambda move: evaluate_move_value(board, move), reverse=True)
    ordered_moves = sorted_nonquiet_moves + sorted_quiet_moves

    tree = Tree()
    tree.create_node(str(not color) + " " + str(evaluate(board)), "root")

    tic = time.perf_counter()

    for move in ordered_moves:
        move_value = evaluate_move(board, move, depth, color, tree)
        print(f"move={move}; move_value={move_value}")

        if color and move_value > best_move_value:
            best_move_value = move_value
            best_move = move
        elif not color and move_value < best_move_value:
            best_move_value = move_value
            best_move = move

    # tree.show()
    tree.to_graphviz(filename='decision_tree', shape=u'circle', graph=u'digraph')

    toc = time.perf_counter()
    print(f"Searched {minimax.calls} minimax moves and {quiesce.calls} quiesce moves, and found best move value: {best_move_value} in {toc - tic:0.4f} seconds")

    return best_move

