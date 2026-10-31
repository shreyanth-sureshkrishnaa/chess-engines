import sys
import importlib
import chess

def human_move(board: chess.Board) -> chess.Move:

    while True:
        text = input("Your move: ").strip()

        try:
            return board.parse_san(text)

        except ValueError:
            pass

        try:
            move = chess.Move.from_uci(text)
            if move in board.legal_moves:
                return move
        except:
            pass

        print("Illegal move. Try again.")

def load_player(name: str):
    if name == "human":
        return human_move

    return importlib.import_module(f"engine_{name}").get_move

def play(white, black, show=True) -> str:
    board = chess.Board()
    while not board.is_game_over(claim_draw=True):

        if show:
            print(board, "\n")

        player = white if board.turn == chess.WHITE else black
        move = player(board)

        if show:
            side = "White" if board.turn == chess.WHITE else "Black"
            print(f"{side} plays {move.uci()}")

        board.push(move)

    outcome = board.outcome(claim_draw=True)

    if show:
        print(board)
        print("Result: ", board.result(claim_draw=True), "-", outcome.termination.name)
        if outcome.winner is None:
            print("It's a draw.")
        else:
            print("White" if outcome.winner == chess.WHITE else "Black", "wins")

    return board.result(claim_draw=True)
    
if __name__ == "__main__":
    # usage: python play.py <white> <black>
    #   python play.py human random     -> you play White vs the engine
    #   python play.py random random    -> engine vs engine
    white = load_player(sys.argv[1])
    black = load_player(sys.argv[2])
    play(white, black)