# robot_term.py
"""
ターミナル版メインプログラム（ロボット側）：
ターミナルからのテキストベースのコマンドにより、ロボットを動作させます
"""
from robot_core import RobotCore

# RobotCore を初期化
robot = RobotCore()

print("\nTerminal Type Controller")
print("コマンドを入力してください（例：dance, move forward, hands up など）")
print("終了するには 'exit' と入力してください。\n")

while True:
    try:
        command = input("> ").strip()
        if command.lower() == "exit":
            print("終了します。")
            break
        if command:
            robot.parse_command(command)
    except KeyboardInterrupt:
        print("\n終了します。")
        break
    except Exception as e:
        print(f"エラーが発生しました: {e}")
