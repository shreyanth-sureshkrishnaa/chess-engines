import random
import chess

PIECE_VALUES = {
    chess.PAWN : 100, 
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,

}

MATE_SCORE = 1000000

def material(board: chess.Board, color: chess.Color) -> int:
    score = 0
    for piece_type, value in PIECE_VALUES.items():
        score += value * len(board.pieces(piece_type, color))
        score -= value * len(board.pieces(piece_type, not color))

    return score

def get_move(board: chess.Board) -> chess.Move:

    me = board.turn
    best_score = -float("inf")
    best_moves = list()

    for move in list(board.legal_moves):
        board.push(move)

        if board.is_checkmate():
            score = MATE_SCORE

        elif board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves():
            score = 0

        else: 
            score = material(board, me)

        board.pop()

        if score > best_score:
            best_score = score
            best_moves = [move]

        elif score == best_score:
            best_moves.append(move)

    return random.choice(best_moves)
