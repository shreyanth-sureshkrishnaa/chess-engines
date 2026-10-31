# This is literally the entire engine. 

# A function which takes in the board state, and returns some legal move.

import random
import chess

def get_move(board: chess.Board) -> chess.Move:
    """Given any position, return some legal move."""

    return random.choice(list(board.legal_moves))


