import random

from utils.robot import make_robot, connect_robot, move_piece, move_to_rest

CELLS = [f"{col}{row}" for col in "de" for row in range(1, 9)]
START = "d1"


def main():
    robot = make_robot()
    connect_robot(robot)
    try:
        current = START
        while True:
            target = random.choice([c for c in CELLS if c != current])
            if not move_piece(robot, current, target):
                print(f"Stopped at move {current} → {target}: no piece detected.")
                break
            current = target
    finally:
        move_to_rest(robot)
        robot.disconnect()


if __name__ == "__main__":
    main()
