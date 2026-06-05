"""
Interactive cell position adjuster. Steps through a column, adjusts each cell, saves to cells.json.
Usage: uv run python adjust_cell.py d

  a / z  →  shoulder_pan   +/-
  w / s  →  shoulder_lift  +/-
  e / d  →  elbow_flex     +/-
  r / f  →  wrist_flex     +/-
  u / j  →  wrist_roll     +/-
  t      →  test sequence at current position
  Enter  →  save and move to next cell
  q      →  quit without saving current cell
"""

import json
import sys
import termios
import time
import tty

from utils.config import CELLS_FILE, GRIPPER_OPEN, GRIPPER_CLOSED
from utils.robot import make_robot, send, gripper, peck_pos

STEP = 1.0
ARM_JOINTS = {"shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll"}


def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def test_sequence(robot, pos: dict):
    print("\n  [test] open maw...", flush=True)
    gripper(robot, GRIPPER_OPEN)
    time.sleep(1.0)

    print("  [test] plock down...", flush=True)
    send(robot, peck_pos(pos))
    time.sleep(1.0)

    print("  [test] close maw...", flush=True)
    gripper(robot, GRIPPER_CLOSED)
    time.sleep(0.5)

    load = robot.bus.read("Present_Load", "gripper")
    actual = robot.get_observation()["gripper.pos"]
    detected = actual > GRIPPER_CLOSED + 3.0
    print(f"  [test] load={load}  gripper_pos={actual:.2f} (commanded {GRIPPER_CLOSED})  {'PIECE DETECTED' if detected else 'no piece'}", flush=True)

    print("  [test] up...", flush=True)
    send(robot, pos)
    time.sleep(1.0)

    print("  [test] down...", flush=True)
    send(robot, peck_pos(pos))
    time.sleep(1.0)

    print("  [test] open maw...", flush=True)
    gripper(robot, GRIPPER_OPEN)
    time.sleep(0.5)

    print("  [test] up...", flush=True)
    send(robot, pos)
    time.sleep(1.0)

    print("  [test] open maw...", flush=True)
    gripper(robot, GRIPPER_OPEN)
    time.sleep(0.5)

    print("  [test] done.", flush=True)


def print_state(pos: dict):
    print(
        f"\r  shoulder_pan {pos['shoulder_pan']:7.2f} [a/z]  "
        f"shoulder_lift {pos['shoulder_lift']:7.2f} [w/s]  "
        f"elbow_flex {pos['elbow_flex']:7.2f} [e/d]  "
        f"wrist_flex {pos['wrist_flex']:7.2f} [r/f]  "
        f"wrist_roll {pos['wrist_roll']:7.2f} [u/j]     ",
        end="", flush=True,
    )


def adjust_cell(robot, cells, cell) -> bool:
    if cell not in cells:
        print(f"Cell '{cell}' not found in {CELLS_FILE}, skipping.")
        return True

    pos = dict(cells[cell])
    send(robot, pos)

    print(f"\nAdjusting [{cell}]  —  t=test  Enter=save & next  q=quit")
    print_state(pos)

    while True:
        key = getch()

        if key in ("\r", "\n"):
            cells[cell] = pos
            CELLS_FILE.write_text(json.dumps(cells, indent=2))
            print(f"\n  Saved {cell}.")
            return True
        elif key == "q":
            print("\nQuit.")
            return False
        elif key == "t":
            test_sequence(robot, pos)
            print_state(pos)
            continue
        elif key == "a":
            pos["shoulder_pan"] = round(pos["shoulder_pan"] + STEP, 2)
        elif key == "z":
            pos["shoulder_pan"] = round(pos["shoulder_pan"] - STEP, 2)
        elif key == "w":
            pos["shoulder_lift"] = round(pos["shoulder_lift"] + STEP, 2)
        elif key == "s":
            pos["shoulder_lift"] = round(pos["shoulder_lift"] - STEP, 2)
        elif key == "e":
            pos["elbow_flex"] = round(pos["elbow_flex"] + STEP, 2)
        elif key == "d":
            pos["elbow_flex"] = round(pos["elbow_flex"] - STEP, 2)
        elif key == "r":
            pos["wrist_flex"] = round(pos["wrist_flex"] + STEP, 2)
        elif key == "f":
            pos["wrist_flex"] = round(pos["wrist_flex"] - STEP, 2)
        elif key == "u":
            pos["wrist_roll"] = round(pos["wrist_roll"] + STEP, 2)
        elif key == "j":
            pos["wrist_roll"] = round(pos["wrist_roll"] - STEP, 2)
        else:
            continue

        send(robot, pos)
        print_state(pos)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in list("abcdefgh"):
        print("Usage: uv run python adjust_cell.py <column>  (e.g. d)")
        return

    col = sys.argv[1].lower()
    cells = json.loads(CELLS_FILE.read_text())
    robot = make_robot()

    try:
        robot.connect()
        print("Keys: a/z=shoulder_pan  w/s=shoulder_lift  e/d=elbow_flex  r/f=wrist_flex  u/j=wrist_roll  t=test  Enter=save & next  q=quit")

        for row in range(1, 9):
            if not adjust_cell(robot, cells, f"{col}{row}"):
                break

        print("Done.")

    finally:
        robot.disconnect()


if __name__ == "__main__":
    main()
