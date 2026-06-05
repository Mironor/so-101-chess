import json

from chess import pawn_path
from utils.config import CELLS_FILE
from utils.robot import make_robot, move_to, move_piece


def main():
    robot = make_robot()

    try:
        robot.connect()

        path = pawn_path("d1d8")
        for i in range(len(path) - 1):
            move_piece(robot, path[i], path[i + 1])
            input("  (press Enter for next)")

        print("→ a1 (home)")
        cells = json.loads(CELLS_FILE.read_text())
        move_to(robot, cells["a1"])
        print("Done.")

    finally:
        robot.disconnect()


if __name__ == "__main__":
    main()
