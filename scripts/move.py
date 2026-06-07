from utils.robot import make_robot, connect_robot, move_piece, move_to_rest


def main():
    robot = make_robot()
    connect_robot(robot)
    try:
        while True:
            raw = input("Move (e.g. d1d4): ").strip().lower()
            if len(raw) != 4 or raw[0] not in "abcdefgh" or raw[2] not in "abcdefgh" \
                    or not raw[1].isdigit() or not raw[3].isdigit():
                print("  Invalid format, expected e.g. d1d4")
                continue
            move_piece(robot, raw[:2], raw[2:])
    except KeyboardInterrupt:
        print("\nBye.")
    finally:
        move_to_rest(robot)
        robot.disconnect()


if __name__ == "__main__":
    main()
