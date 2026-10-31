import sys
from play import play, load_player


def tournament(a, b, n=100):
    """Play n games between engines a and b, alternating colors."""
    a_wins = b_wins = draws = 0
    for i in range(n):
        a_is_white = (i % 2 == 0)
        white, black = (a, b) if a_is_white else (b, a)
        result = play(white, black, show=False)

        if result == "1/2-1/2":
            draws += 1
        elif (result == "1-0") == a_is_white:
            a_wins += 1
        else:
            b_wins += 1
    return a_wins, b_wins, draws


if __name__ == "__main__":
    # usage: python tournament.py <engine_a> <engine_b> [n_games]
    a = load_player(sys.argv[1])
    b = load_player(sys.argv[2])
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    a_wins, b_wins, draws = tournament(a, b, n)
    print(f"{sys.argv[1]}: {a_wins}  {sys.argv[2]}: {b_wins}  draws: {draws}")