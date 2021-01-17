import chess
from collections import defaultdict
from evaluate import evaluate_move_value, piece_values

def sort_moves_by_value(board, moves):
    return sorted(moves, key=lambda move: evaluate_move_value(board, move), reverse=True)

def determine_victim_and_aggressor_types(board, move):
    if board.is_en_passant(move):
        return [move, piece_values[chess.PAWN], piece_values[chess.PAWN]]

    aggressor = board.piece_at(move.from_square).piece_type
    victim = board.piece_at(move.to_square).piece_type

    return [move, piece_values[victim], piece_values[aggressor]]

# Most valuable victim, lease valuable aggressor: https://www.chessprogramming.org/MVV-LVA
def sort_mvv_lva(board, moves):
    victims_and_aggressors = [determine_victim_and_aggressor_types(board, move) for move in moves]
    # move is index 0, victim values are index 1, aggressor values are index 2
    return list(map(lambda x: x[0], sorted(victims_and_aggressors, key=lambda x: (-x[1], x[2]))))

def prioritize_legal_moves(board):
    legal_moves = board.legal_moves

    grouped_moves = groupby(legal_moves, compose_move_type(board))
    sorted_check_moves = sort_moves_by_value(board, grouped_moves['check'])
    sorted_capture_moves = sort_mvv_lva(board, grouped_moves['capture'])
    sorted_quiet_moves = sort_moves_by_value(board, grouped_moves['quiet'])

    # nonquiet moves should be searched first, since they are most likely to increase value
    return sorted_check_moves + sorted_capture_moves + sorted_quiet_moves

def get_moves_to_dequiet(board):
    if board.is_check():
        return prioritize_legal_moves(board)

    legal_moves = board.legal_moves
    
    grouped_moves = groupby(legal_moves, compose_move_type(board))

    sorted_check_moves = sort_moves_by_value(board, grouped_moves['check'])
    sorted_capture_moves = sort_mvv_lva(board, grouped_moves['capture'])

    return sorted_check_moves + sorted_capture_moves

# input list to split, function to group by
def groupby(list_to_group, fn):
    grouped_list = defaultdict(list)

    for i in list_to_group:
        key = fn(i)
        grouped_list[key].append(i)

    return grouped_list

def compose_move_type(board):
    def determine_move_type(move):
        if board.gives_check(move):
            return 'check'
        elif board.is_capture(move):
            return 'capture'
        else:
            return 'quiet'

    return determine_move_type
