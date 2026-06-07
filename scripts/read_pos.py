from utils.robot import make_robot, connect_robot


def main():
    robot = make_robot()
    connect_robot(robot)
    try:
        obs = robot.get_observation()
        for key, value in sorted(obs.items()):
            print(f"  {key}: {value:.2f}")
    finally:
        robot.disconnect()


if __name__ == "__main__":
    main()
