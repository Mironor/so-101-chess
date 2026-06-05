"""
Chess move logic. Accepts UCI notation (e.g. "e1e8").
"""

COLS = list("abcdefgh")
ROWS = list(range(1, 9))


def pawn_path(move: str) -> list[str]:
    """
    Return the full list of cells from source to destination for a pawn move.
    Input: UCI notation like "e1e8".
    Output: ["e1", "e2", "e3", "e4", "e5", "e6", "e7", "e8"]
    """
    move = move.strip().lower()
    if len(move) != 4:
        raise ValueError(f"Expected UCI format like 'e2e4', got '{move}'")

    src_col, src_row = move[0], int(move[1])
    dst_col, dst_row = move[2], int(move[3])

    if src_col != dst_col:
        raise ValueError(f"Pawn moves stay on the same file (got {src_col} → {dst_col})")
    if src_col not in COLS or dst_col not in COLS:
        raise ValueError(f"Invalid column in move '{move}'")
    if src_row not in ROWS or dst_row not in ROWS:
        raise ValueError(f"Invalid row in move '{move}'")

    step = 1 if dst_row > src_row else -1
    return [f"{src_col}{r}" for r in range(src_row, dst_row + step, step)]
