"""
Interactive cell position adjuster. Adjusts x/y of each cell and saves to cells_ik.json.
Usage: uv run python scripts/adjust_cell.py

  w / s  →  x  +/-  (further / closer)
  a / d  →  y  +/-  (left / right)
  t      →  test pick & place at current position
  Enter  →  save and ask for next cell
  q      →  quit without saving current cell
"""

import json
import sys
import termios
import tty

from utils.config import CELLS_IK_FILE
from utils.robot import make_robot, connect_robot, move_to_xyz, pick, place, read_joints, move_to_rest

STEP = 0.001  # metres per key press (1 mm)


def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def print_state(pos: dict):
    print(
        f"\r  x {pos['x']:8.4f} [w/s]   y {pos['y']:8.4f} [a/d]     ",
        end="", flush=True,
    )


def test_sequence(robot, pos: dict):
    all_cells = json.loads(CELLS_IK_FILE.read_text())
    move_to_xyz(robot, all_cells["a1"])
    cells = {"_": pos}
    pick(robot, cells, "_")
    place(robot, cells, "_")


def ask_cell() -> str:
    while True:
        raw = input("Cell to adjust (e.g. d4, or Enter to quit): ").strip().lower()
        if raw == "":
            return ""
        if len(raw) == 2 and raw[0] in "abcdefgh" and raw[1] in "12345678":
            return raw
        print("  Invalid cell, expected e.g. d4")


def adjust_cell(robot, cells, cell) -> bool:
    if cell not in cells:
        print(f"Cell '{cell}' not found, skipping.")
        return True

    pos = dict(cells[cell])
    move_to_xyz(robot, pos)
    pos["hint"] = read_joints(robot)

    print(f"\nAdjusting [{cell}]  —  w/s=x  a/d=y  t=test  Enter=save  q=quit")
    print_state(pos)

    while True:
        key = getch()

        if key in ("\r", "\n"):
            cells[cell] = pos
            CELLS_IK_FILE.write_text(json.dumps(cells, indent=2))
            print(f"\n  Saved {cell}.")
            return True
        elif key == "q":
            print("\nQuit.")
            return False
        elif key == "t":
            test_sequence(robot, pos)
            print_state(pos)
            continue
        elif key == "w":
            pos["x"] = round(pos["x"] + STEP, 6)
        elif key == "s":
            pos["x"] = round(pos["x"] - STEP, 6)
        elif key == "a":
            pos["y"] = round(pos["y"] + STEP, 6)
        elif key == "d":
            pos["y"] = round(pos["y"] - STEP, 6)
        else:
            continue

        move_to_xyz(robot, pos)
        pos["hint"] = read_joints(robot)
        print_state(pos)


def main():
    cells = json.loads(CELLS_IK_FILE.read_text())
    robot = make_robot()

    try:
        connect_robot(robot)
        print("Keys: w/s=x±  a/d=y±  t=test  Enter=save  q=quit")

        cell = ask_cell()
        while cell:
            if not adjust_cell(robot, cells, cell):
                break
            cell = ask_cell()

        print("Done.")

    finally:
        move_to_rest(robot)
        robot.disconnect()


if __name__ == "__main__":
    main()
