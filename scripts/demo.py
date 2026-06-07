import json
import sys

from chess import pawn_path
from utils.config import CELLS_FILE
from utils.robot import make_robot, connect_robot, move_to, move_piece, move_to_rest


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in list("abcdefgh"):
        print("Usage: uv run python demo.py <column>  (e.g. d)")
        return

    col = sys.argv[1].lower()
    robot = make_robot()

    try:
        connect_robot(robot)

        path = pawn_path(f"{col}1{col}8")
        for i in range(len(path) - 1):
            move_piece(robot, path[i], path[i + 1])

        print(f"→ a1 (home)")
        cells = json.loads(CELLS_FILE.read_text())
        move_to(robot, cells["a1"])
        print("Done.")

    finally:
        move_to_rest(robot)
        robot.disconnect()


if __name__ == "__main__":
    main()
