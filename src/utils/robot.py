import json
import time

from lerobot.robots.so_follower.config_so_follower import SOFollowerRobotConfig
from lerobot.robots.so_follower.so_follower import SOFollower

from utils.config import (
    PORT, ROBOT_ID,
    PLOCK_DEG, GRIPPER_OPEN, GRIPPER_CLOSED, CELLS_FILE,
)

ARM_JOINTS = {"shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll"}


def make_robot() -> SOFollower:
    return SOFollower(SOFollowerRobotConfig(port=PORT, id=ROBOT_ID))


def send(robot, joints: dict):
    robot.send_action({f"{k}.pos": v for k, v in joints.items() if k in ARM_JOINTS})


def gripper(robot, value: float):
    robot.send_action({"gripper.pos": value})
    time.sleep(0.5)


def peck_pos(hover: dict) -> dict:
    p = dict(hover)
    p["elbow_flex"] += PLOCK_DEG
    p["wrist_flex"] -= PLOCK_DEG
    return p


def move_to(robot, hover: dict):
    send(robot, hover)
    time.sleep(1.0)


def descend(robot, hover: dict):
    send(robot, peck_pos(hover))
    time.sleep(1.0)


def ascend(robot, hover: dict):
    send(robot, hover)
    time.sleep(1.0)


def has_piece(robot) -> bool:
    actual = robot.get_observation()["gripper.pos"]
    return actual > GRIPPER_CLOSED + 3.0


def pick(robot, cells: dict, cell: str, shift: float = 0) -> bool:
    hover = cells[cell]
    peck = peck_pos(hover)
    if shift:
        peck["elbow_flex"] += shift
        peck["wrist_flex"] -= shift
    move_to(robot, hover)
    gripper(robot, GRIPPER_OPEN)
    send(robot, peck)
    time.sleep(1.0)
    gripper(robot, GRIPPER_CLOSED)
    ascend(robot, hover)
    return has_piece(robot)


def place(robot, cells: dict, cell: str):
    hover = cells[cell]
    peck = peck_pos(hover)
    peck["wrist_flex"] -= 2.0
    move_to(robot, hover)
    send(robot, peck)
    time.sleep(1.0)
    gripper(robot, GRIPPER_OPEN)
    peck["wrist_flex"] += 3.0
    send(robot, peck)
    time.sleep(0.5)
    ascend(robot, hover)
    gripper(robot, GRIPPER_CLOSED)


def move_piece(robot, cell_from: str, cell_to: str):
    cells = json.loads(CELLS_FILE.read_text())
    print(f"Moving piece {cell_from} → {cell_to}")
    for shift in (0, 5):
        if pick(robot, cells, cell_from, shift):
            place(robot, cells, cell_to)
            return
    print(f"  No piece detected at {cell_from}, aborting.")
