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

nodes = 0   # counts positions visited

def evaluate(board: chess.Board) -> int:
    """Material balance from the point of view of the side TO MOVE."""
    me = board.turn
    score = 0
    for piece_type, value in PIECE_VALUES.items():
        score += value * len(board.pieces(piece_type, me))
        score -= value * len(board.pieces(piece_type, not me))
    return score

 
def move_score(board: chess.Board, move: chess.Move) -> int:
    score = 0
    if board.is_capture(move):
        victim = board.piece_type_at(move.to_square) or chess.PAWN # Fallback for en passant.
        attacker = board.piece_type_at(move.from_square)

        score = 10 * (PIECE_VALUES[victim] - PIECE_VALUES[attacker]) # A less valuable piece capturing a more valuable piece is a great move!

    return score

def ordered_moves(board: chess.Board):
    moves = list(board.legal_moves)
    moves.sort(key=lambda m: move_score(board, m), reverse=True)
    return moves



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
            return beta            # cutoff: opponent will avoid this line
        if score > alpha:
            alpha = score          # new best for us

    return alpha


def get_move(board: chess.Board) -> chess.Move:
    global nodes
    nodes = 0

    moves = list(board.legal_moves)
    random.shuffle(moves)                                   # random tie-breaks
    moves.sort(key=lambda m: move_score(board, m), reverse=True)  # stable sort keeps shuffle among equals

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
