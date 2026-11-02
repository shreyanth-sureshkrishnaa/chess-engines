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
DEPTH = 3

def evaluate(board: chess.Board) -> int:
    me = board.turn
    score = 0
    for piece_type, value in PIECE_VALUES.items():
        score += value * len(board.pieces(piece_type, me))
        score -= value * len(board.pieces(piece_type, not me))

    return score


def negamax(board: chess.Board, depth: int) -> int:
    """Best score the side to move can reach, looking `depth` plies ahead."""
    if board.is_checkmate():
        # Side to move is mated. Extra `depth` makes faster mates score better.
        return -(MATE_SCORE + depth)
        
    if board.is_game_over():
        return 0                          # stalemate / draw

    if depth == 0:
        return evaluate(board)

    best_score = -float("inf")

    for move in board.legal_moves:
        board.push(move)

        score = -negamax(board, depth - 1)

        board.pop()

        best_score = max(best_score, score)

    return best_score


def get_move(board: chess.Board) -> chess.Move:
    best_score = -float("inf")
    best_moves = []

    for move in list(board.legal_moves):
        board.push(move)
        score = -negamax(board, DEPTH - 1)
        board.pop()

        if score > best_score:
            best_score = score
            best_moves = [move]
        elif score == best_score:
            best_moves.append(move)

    return random.choice(best_moves)