"""
POC: Move robot cell-to-cell using IK. Enter a cell name to move, empty input to quit.
"""

import json
import numpy as np

from lerobot.model.kinematics import RobotKinematics

from utils.config import CELLS_FILE
from utils.robot import make_robot, connect_robot, move_to, move_to_rest

URDF = "data/so101_new_calib.urdf"
JOINT_NAMES = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll"]
HOVER_Z = 0.085  # metres — fixed hover height for all cells


def to_array(pos: dict) -> np.ndarray:
    return np.array([pos[j] for j in JOINT_NAMES])


def to_dict(arr: np.ndarray) -> dict:
    return {name: float(val) for name, val in zip(JOINT_NAMES, arr)}


def main():
    cells = json.loads(CELLS_FILE.read_text())
    kin = RobotKinematics(
        urdf_path=URDF,
        target_frame_name="gripper_frame_link",
        joint_names=JOINT_NAMES,
    )

    robot = make_robot()
    try:
        connect_robot(robot)
        while True:
            cell = input("Cell (or Enter to quit): ").strip().lower()
            if not cell:
                break
            if cell not in cells:
                print(f"  Unknown cell '{cell}'")
                continue
            calibrated = to_array(cells[cell])
            T = kin.forward_kinematics(calibrated)
            T[2, 3] = HOVER_Z
            ik_joints = kin.inverse_kinematics(calibrated, T)
            move_to(robot, to_dict(ik_joints))
    finally:
        move_to_rest(robot)
        robot.disconnect()


if __name__ == "__main__":
    main()
