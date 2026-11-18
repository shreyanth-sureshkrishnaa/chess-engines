# We now apply positional evaluations, so that better placed pieces are incentivized. 

import random
import chess

PIECE_VALUES = {
    chess.PAWN:   100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK:   500,
    chess.QUEEN:  900,
    chess.KING:   0,
}

MATE_SCORE = 1_000_000
INF = 10_000_000
DEPTH = 4

# Same way the board is laid out: 

PAWN_PST = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]

KNIGHT_PST = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

BISHOP_PST = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]

ROOK_PST = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0,
]

QUEEN_PST = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]

KING_MIDDLEGAME_PST = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20,
]

KING_ENDGAME_PST = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50,
]

PST = {
    chess.PAWN:   PAWN_PST,
    chess.KNIGHT: KNIGHT_PST,
    chess.BISHOP: BISHOP_PST,
    chess.ROOK:   ROOK_PST,
    chess.QUEEN:  QUEEN_PST,
}

nodes = 0

def is_endgame(board: chess.Board) -> bool:
    return not board.pieces(chess.QUEEN, chess.WHITE) and not board.pieces(chess.QUEEN, chess.BLACK)

def move_score(board: chess.Board, move: chess.Move) -> int:
    """Guess how good a move is, only to decide the search order."""
    score = 0
    if board.is_capture(move):
        victim = board.piece_type_at(move.to_square) or chess.PAWN
        attacker = board.piece_type_at(move.from_square)
        score += 10 * PIECE_VALUES[victim] - PIECE_VALUES[attacker]
    if move.promotion:
        score += PIECE_VALUES[move.promotion]
    return score

# Getting PST Values for each piece, wherever it is. 
def pst_value(piece: chess.Piece, square: int, endgame: bool) -> int:
    if piece.piece_type == chess.KING:
        table = KING_ENDGAME_PST if endgame else KING_MIDDLEGAME_PST
    else:
        table = PST[piece.piece_type]

    # Flip the table for Black
    index = square ^ 56 if piece.color == chess.WHITE else square
    return table[index]

def ordered_moves(board: chess.Board):
    moves = list(board.legal_moves)
    moves.sort(key=lambda m: move_score(board, m), reverse=True)
    return moves


def evaluate(board: chess.Board) -> int:
    endgame = is_endgame(board)
    score = 0

    for square, piece in board.piece_map().items():
        value = PIECE_VALUES[piece.piece_type] + pst_value(piece, square, endgame)
        score += value if piece.color == chess.WHITE else -value

    return score if board.turn == chess.WHITE else -score

def negamax(board: chess.Board, depth: int, alpha: int, beta: int) -> int:
    global nodes
    nodes += 1

    if board.is_checkmate():
        return -(MATE_SCORE + depth)
    if board.is_game_over():
        return 0
    if depth == 0:

        return evaluate(board)

    for move in ordered_moves(board):
        board.push(move)
        score = -negamax(board, depth - 1, -beta, -alpha)
        board.pop()

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score

    return alpha


def get_move(board: chess.Board) -> chess.Move:
    global nodes
    nodes = 0

    moves = list(board.legal_moves)
    random.shuffle(moves)
    moves.sort(key=lambda m: move_score(board, m), reverse=True)

    best_move = moves[0]
    alpha = -INF
    for move in moves:
        board.push(move)
        score = -negamax(board, DEPTH - 1, -INF, -alpha)
        board.pop()

        if score > alpha:
            alpha = score
            best_move = move

    return best_move