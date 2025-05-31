#! /usr/bin/env python
"""
コントローラー GUI（パソコン側）：
MQTT経由でロボットにテキストベースのコマンドを送信します
"""

import tkinter as tk
import subprocess
import configparser
from functools import partial
import paho.mqtt.client as mqtt

# MQTT通信を担当するクラス
class RobotMQTTClient:
    def __init__(self, config):
        # MQTT設定を読み込み
        self.topic = f"command/{config['mqtt']['topic_base']}/{config['info']['robot_id']}"
        self.client = mqtt.Client()
        self.client.username_pw_set(
            username=config['mqtt']['user'],
            password=config['mqtt']['password']
        )
        self.broker = config['mqtt']['endpoint']
        self.port = int(config['mqtt']['port'])
        self.client.on_connect = self.on_connect

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT broker: {self.topic}")

    def connect(self):
        self.client.connect(self.broker, self.port)

    def send_command(self, message):
        print(f"Sending command: {message}")
        self.client.publish(self.topic, message)

    def loop(self):
        self.client.loop()


# GStreamerによるビデオストリーム受信を担当するクラス
class GStreamerDisplay:

    def __init__(self, config):
        self.port = int(config['video']['gstreamer_port'])
        self.width = int(config['video']['width'])
        self.height = int(config['video']['height'])
        self.camera_type = config['video']['camera_type']
        self.process = None

    def start(self):
        # カメラに応じてコマンドを切り替え
        if self.camera_type == 'webcam':
            command = [
                'C:/gstreamer/1.0/msvc_x86_64/bin/gst-launch-1.0',
                'udpsrc', f'port={self.port}',
                'caps=application/x-rtp, media=video, encoding-name=JPEG, payload=26', '!',
                'rtpjpegdepay', '!',
                'jpegdec', '!',
                'autovideosink'
            ]
        elif self.camera_type == 'picam':
            command = [
                'C:/gstreamer/1.0/msvc_x86_64/bin/gst-launch-1.0',
                'udpsrc', f'port={self.port}',
                'caps=application/x-rtp, media=video, encoding-name=H264, payload=96', '!',
                'rtph264depay', '!',
                'h264parse', '!',
                'avdec_h264', '!',
                'autovideosink'
            ]
        else:
            print("Unsupported Camera")
            return

        self.process = subprocess.Popen(command)
        print("GStreamer started")

    def stop(self):
        
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
            print("GStreamer stopped")


# ロボットのコントローラーUI（Tkinter）
class RobotControllerUI:

    def __init__(self, mqtt_client, gstreamer):
        self.mqtt_client = mqtt_client
        self.gstreamer = gstreamer

        self.root = tk.Tk()
        self.root.geometry("400x220")
        self.root.title("Robot Controller")

        self.create_camera_controls()
        self.create_monitor_controls()
        self.create_action_controls()
        self.create_movement_controls()

    def create_camera_controls(self):
        frame = tk.LabelFrame(self.root, text="Remote Camera")
        frame.place(x=10, y=10, width=120, height=90)
        tk.Button(frame, text="Start", command=partial(self.send, "start camera")).pack(pady=5)
        tk.Button(frame, text="Stop", command=partial(self.send, "stop camera")).pack(pady=2)

    def create_monitor_controls(self):
        frame = tk.LabelFrame(self.root, text="Monitor")
        frame.place(x=10, y=110, width=120, height=90)
        tk.Button(frame, text="Start", command=self.gstreamer.start).pack(pady=5)
        tk.Button(frame, text="Stop", command=self.gstreamer.stop).pack(pady=2)

    def create_action_controls(self):
        frame = tk.LabelFrame(self.root, text="Action")
        frame.place(x=140, y=10, width=120, height=180)
        for label, cmd in [("Hello!", "hello"), ("Dance!", "dance"), ("Yeah!", "yeah"), ("Rush!", "rush"), ("Reset", "reset")]:
            tk.Button(frame, text=label, command=partial(self.send, cmd)).pack(pady=2)

    def create_movement_controls(self):
        frame = tk.LabelFrame(self.root, text="Move")
        frame.place(x=270, y=10, width=120, height=140)
        tk.Button(frame, text="↑", command=partial(self.send, "move forward")).pack(side=tk.TOP, pady=10)
        tk.Button(frame, text="↓", command=partial(self.send, "move backward")).pack(side=tk.BOTTOM, pady=10)
        tk.Button(frame, text="←", command=partial(self.send, "turn left")).pack(side=tk.LEFT, padx=10)
        tk.Button(frame, text="→", command=partial(self.send, "turn right")).pack(side=tk.RIGHT, padx=10)

    def send(self, message):
        # ボタン押下でMQTTコマンドを送信
        self.mqtt_client.send_command(message)

    def run(self):
        # GUIイベントループ開始
        self.root.mainloop()


# ----- メイン実行部 ----- #
if __name__ == '__main__':

    # 設定ファイル読み込み
    config = configparser.ConfigParser()
    config.read('./config.ini', encoding='utf-8')

    # MQTTクライアントとGStreamerを初期化
    mqtt_client = RobotMQTTClient(config)
    mqtt_client.connect()
    mqtt_client.client.loop_start()

    gstreamer = GStreamerDisplay(config)

    # UI起動
    ui = RobotControllerUI(mqtt_client, gstreamer)
    ui.run()
