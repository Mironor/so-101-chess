import json
import time

import numpy as np
from lerobot.robots.so_follower.config_so_follower import SOFollowerRobotConfig
from lerobot.robots.so_follower.so_follower import SOFollower

from utils.config import (
    PORT, ROBOT_ID,
    MOTOR_SPEED, PLOCK_DEG, GRIPPER_OPEN, GRIPPER_CLOSED,
    CELLS_IK_FILE, REST_FILE, URDF_FILE,
)

ARM_JOINTS = {"shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll"}
_ARM_JOINT_NAMES = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll"]

MOVE_TIMEOUT = 4.0
_STALL_TOL = 0.3
_STALL_COUNT = 3

_kin = None


def _get_kin():
    global _kin
    if _kin is None:
        from lerobot.model.kinematics import RobotKinematics
        _kin = RobotKinematics(
            urdf_path=str(URDF_FILE),
            target_frame_name="gripper_frame_link",
            joint_names=_ARM_JOINT_NAMES,
        )
    return _kin


def _xyz_to_joints(robot, xyz: dict) -> dict:
    kin = _get_kin()
    if "hint" in xyz:
        hint = np.array([xyz["hint"][j] for j in _ARM_JOINT_NAMES])
    else:
        obs = robot.get_observation()
        hint = np.array([obs[f"{j}.pos"] for j in _ARM_JOINT_NAMES])
    T = kin.forward_kinematics(hint)
    T[0, 3] = xyz["x"]
    T[1, 3] = xyz["y"]
    T[2, 3] = xyz["z"]
    result = kin.inverse_kinematics(hint, T, orientation_weight=0.01)
    return {name: float(val) for name, val in zip(_ARM_JOINT_NAMES, result)}


def make_robot() -> SOFollower:
    return SOFollower(SOFollowerRobotConfig(port=PORT, id=ROBOT_ID))


def set_speed(robot, speed: int = MOTOR_SPEED):
    robot.bus.sync_write("Goal_Velocity", {m: speed for m in robot.bus.motors})


def connect_robot(robot) -> None:
    robot.connect()
    set_speed(robot)


def send(robot, joints: dict):
    robot.send_action({f"{k}.pos": v for k, v in joints.items() if k in ARM_JOINTS})


def gripper(robot, value: float):
    robot.send_action({"gripper.pos": value})
    time.sleep(0.5)


def wait_for_joints(robot, timeout: float = MOVE_TIMEOUT):
    deadline = time.monotonic() + timeout
    prev = robot.get_observation()
    stalled = 0
    while time.monotonic() < deadline:
        time.sleep(0.05)
        obs = robot.get_observation()
        if max(abs(obs[f"{k}.pos"] - prev[f"{k}.pos"]) for k in ARM_JOINTS) < _STALL_TOL:
            stalled += 1
            if stalled >= _STALL_COUNT:
                return
        else:
            stalled = 0
        prev = obs


def peck_pos(hover: dict) -> dict:
    p = dict(hover)
    p["elbow_flex"] += PLOCK_DEG
    p["wrist_flex"] -= PLOCK_DEG
    return p


def move_to(robot, joints: dict):
    send(robot, joints)
    wait_for_joints(robot)


def move_to_xyz(robot, xyz: dict):
    move_to(robot, _xyz_to_joints(robot, xyz))


def ascend(robot, hover: dict):
    send(robot, hover)
    wait_for_joints(robot)


def read_joints(robot) -> dict:
    obs = robot.get_observation()
    return {j: obs[f"{j}.pos"] for j in _ARM_JOINT_NAMES}


def has_piece(robot) -> bool:
    actual = robot.get_observation()["gripper.pos"]
    return actual > GRIPPER_CLOSED + 3.0


def pick(robot, cells: dict, cell: str, shift: float = 0) -> bool:
    hover = _xyz_to_joints(robot, cells[cell])
    peck = peck_pos(hover)
    if shift:
        peck["elbow_flex"] += shift
        peck["wrist_flex"] -= shift
    move_to(robot, hover)
    gripper(robot, GRIPPER_OPEN)
    approach = dict(hover)
    approach["wrist_flex"] += 2.0
    send(robot, approach)
    wait_for_joints(robot)
    send(robot, peck)
    wait_for_joints(robot)
    peck["wrist_flex"] -= 2.0
    send(robot, peck)
    wait_for_joints(robot)
    gripper(robot, GRIPPER_CLOSED)
    ascend(robot, hover)
    return has_piece(robot)


def place(robot, cells: dict, cell: str):
    hover = _xyz_to_joints(robot, cells[cell])
    peck = peck_pos(hover)
    move_to(robot, hover)
    send(robot, peck)
    wait_for_joints(robot)
    peck["wrist_flex"] -= 2.0
    send(robot, peck)
    wait_for_joints(robot)
    gripper(robot, GRIPPER_OPEN)
    peck["wrist_flex"] += 5.0
    send(robot, peck)
    wait_for_joints(robot)
    ascend(robot, hover)
    gripper(robot, GRIPPER_CLOSED)


def move_to_rest(robot):
    rest = json.loads(REST_FILE.read_text())
    move_to(robot, rest)
    gripper(robot, rest["gripper"])


def move_piece(robot, cell_from: str, cell_to: str) -> bool:
    cells = json.loads(CELLS_IK_FILE.read_text())
    print(f"Moving piece {cell_from} → {cell_to}")
    if pick(robot, cells, cell_from):
        place(robot, cells, cell_to)
        return True
    print(f"  No piece detected at {cell_from}, aborting.")
    return False
