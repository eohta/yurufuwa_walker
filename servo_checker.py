"""
サーボチェッカー（ロボット側）：
サーボにサーボホーンを取り付ける際の角度調整に使えるコマンドラインツールです
"""

import board
import busio
import time
import argparse
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

def main():
    parser = argparse.ArgumentParser(description="サーボを指定角度に動かし、必要に応じて力を抜きます。")
    parser.add_argument("channel", type=int, help="サーボのチャンネル番号 (0-15)")
    parser.add_argument("angle", type=float, help="移動する角度 (通常0-180度)")
    parser.add_argument("--release", action="store_true", help="移動後にサーボの力を抜く")
    args = parser.parse_args()

    # --- I2CバスとPCA9685初期化 ---
    i2c = busio.I2C(board.SCL, board.SDA)
    pca = PCA9685(i2c)
    pca.frequency = 50

    # --- 指定されたチャンネルにサーボを割り当て ---
    my_servo = servo.Servo(pca.channels[args.channel])

    print(f"サーボチャンネル {args.channel} を {args.angle} 度に移動します...")
    my_servo.angle = args.angle

    # 少し待って安定させる
    time.sleep(3)

    if args.release:
        print("力を抜きます...")
        pca.channels[args.channel].duty_cycle = 0

    print("完了しました。プログラムを終了します。")

if __name__ == "__main__":
    main()
