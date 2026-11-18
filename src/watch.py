import argparse
import importlib
import random
import sys
import time

import chess

CLEAR = "\033[2J\033[H"
HOME = "\033[H"
CLEAR_BELOW = "\033[J"
RESET = "\033[0m"
LIGHT, DARK = "\033[48;5;180m", "\033[48;5;94m"
LIGHT_HI, DARK_HI = "\033[48;5;186m", "\033[48;5;142m"   # last-move highlight
WHITE_FG, BLACK_FG = "\033[38;5;255m", "\033[38;5;16m"

# Solid glyphs for both colors; the foreground color tells the sides apart.
GLYPH = {
    chess.PAWN: "\u265f\ufe0e", chess.KNIGHT: "\u265e", chess.BISHOP: "\u265d",
    chess.ROOK: "\u265c", chess.QUEEN: "\u265b", chess.KING: "\u265a",
}


def load_engine(spec: str):
    """'alphabeta' or 'alphabeta:3' (engine name, optional depth)."""
    name, _, depth = spec.partition(":")
    module = importlib.import_module(f"engine_{name}")
    if depth:
        module.DEPTH = int(depth)
    return name, module


def render(board: chess.Board, last_move) -> str:
    hi = {last_move.from_square, last_move.to_square} if last_move else set()
    lines = []
    for rank in range(7, -1, -1):
        row = f" {rank + 1} "
        for file in range(8):
            sq = chess.square(file, rank)
            light = (file + rank) % 2 == 1
            if sq in hi:
                bg = LIGHT_HI if light else DARK_HI
            else:
                bg = LIGHT if light else DARK
            piece = board.piece_at(sq)
            if piece:
                fg = WHITE_FG if piece.color == chess.WHITE else BLACK_FG
                row += f"{bg}{fg} {GLYPH[piece.piece_type]} {RESET}"
            else:
                row += f"{bg}   {RESET}"
        lines.append(row)
    lines.append("    a  b  c  d  e  f  g  h")
    return "\n".join(lines)


def draw(board, last_move, white, black, sans, status, clocks, info, tally):
    out = [HOME]
    out.append(f" {white}  (White)   vs   {black}  (Black)")
    if tally:
        out.append(f" Score so far: {tally}")
    out.append("")
    out.append(render(board, last_move))
    out.append("")
    out.append(f" {status}")
    out.append(f" Clock used: White {clocks[chess.WHITE]:.1f}s | Black {clocks[chess.BLACK]:.1f}s")
    out.append(f" {info}")
    out.append("")
    # last 12 plies as numbered moves
    start = max(0, len(sans) - 12)
    start -= start % 2
    moves = []
    for i in range(start, len(sans), 2):
        pair = f"{i // 2 + 1}. {sans[i]}"
        if i + 1 < len(sans):
            pair += f" {sans[i + 1]}"
        moves.append(pair)
    out.append(" " + "  ".join(moves))
    sys.stdout.write("\n".join(out) + "\n" + CLEAR_BELOW)
    sys.stdout.flush()


def play_live(white_spec, black_spec, delay, random_plies, tally=""):
    w_name, w_mod = load_engine(white_spec)
    b_name, b_mod = load_engine(black_spec)
    w_label, b_label = white_spec, black_spec
    engines = {chess.WHITE: w_mod, chess.BLACK: b_mod}

    board = chess.Board()
    sans, clocks = [], {chess.WHITE: 0.0, chess.BLACK: 0.0}
    last_move = None

    for _ in range(random_plies):          # varied openings
        move = random.choice(list(board.legal_moves))
        sans.append(board.san(move))
        board.push(move)
        last_move = move

    while not board.is_game_over(claim_draw=True):
        side = board.turn
        label = w_label if side == chess.WHITE else b_label
        side_name = "White" if side == chess.WHITE else "Black"

        draw(board, last_move, w_label, b_label, sans,
             f"{label} ({side_name}) is thinking...", clocks, "", tally)

        start = time.time()
        move = engines[side].get_move(board)
        elapsed = time.time() - start
        clocks[side] += elapsed

        san = board.san(move)               # SAN must be computed BEFORE push
        nodes = getattr(engines[side], "nodes", None)
        info = f"{label} played {san} in {elapsed:.2f}s"
        if nodes:
            info += f" ({nodes:,} nodes, {nodes / max(elapsed, 1e-9):,.0f} nodes/s)"

        sans.append(san)
        board.push(move)
        last_move = move

        draw(board, last_move, w_label, b_label, sans,
             f"Move {len(sans)} played.", clocks, info, tally)
        time.sleep(delay)

    result = board.result(claim_draw=True)
    outcome = board.outcome(claim_draw=True)
    draw(board, last_move, w_label, b_label, sans,
         f"GAME OVER: {result} ({outcome.termination.name})", clocks, "", tally)
    return result


def main():
    p = argparse.ArgumentParser(description="Watch two engines play live.")
    p.add_argument("white", help="engine name, optionally with depth: alphabeta:4")
    p.add_argument("black", help="engine name, optionally with depth: positional:3")
    p.add_argument("--delay", type=float, default=0.5, help="pause after each move (s)")
    p.add_argument("--games", type=int, default=1, help="games to play, colors alternate")
    p.add_argument("--random-plies", type=int, default=0,
                   help="random opening moves before the engines start")
    args = p.parse_args()

    sys.stdout.write(CLEAR + "\033[?25l")       # clear screen, hide cursor
    wins = {args.white: 0, args.black: 0}
    draws = 0
    try:
        for g in range(args.games):
            a_is_white = g % 2 == 0
            white, black = (args.white, args.black) if a_is_white else (args.black, args.white)
            tally = (f"game {g + 1}/{args.games} | {args.white}: {wins[args.white]}  "
                     f"{args.black}: {wins[args.black]}  draws: {draws}")
            result = play_live(white, black, args.delay, args.random_plies, tally)
            if result == "1/2-1/2":
                draws += 1
            elif result == "1-0":
                wins[white] += 1
            else:
                wins[black] += 1
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\033[?25h\n")          # show cursor again
        print(f"Final: {args.white}: {wins[args.white]}  "
              f"{args.black}: {wins[args.black]}  draws: {draws}")


if __name__ == "__main__":
    main()