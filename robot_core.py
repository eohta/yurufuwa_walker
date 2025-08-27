"""
コアプログラム（ロボット側）：
テキストベースのコマンドをロボットの動作に結びつけます
"""
import time
import subprocess
import configparser
from Adafruit_PCA9685 import PCA9685

# 下の部分は実際にサーボが接続しているチャネルに合わせて書き換えて下さい
CH_WHEEL_R = 0
CH_WHEEL_L = 1
CH_HAND_R = 2
CH_HAND_L = 3

class RobotCore:

    def __init__(self, config_path='./config.ini'):
        self.load_config(config_path)
        self.setup_hardware()

    def load_config(self, path):
        config = configparser.ConfigParser()
        config.read(path, encoding='utf-8')
        self.config = config

        self.move_duration = float(config['move']['move_duration'])
        self.turn_duration = float(config['move']['turn_duration'])

    def setup_hardware(self):
        self.pca = PCA9685(address=0x40, busnum=1)
        self.pca.set_pwm_freq(50)
        self.hands_down()
        self.stop_wheels()

    def set_FS90R_throttle(self, channel, throttle):
        pulse_length = 1500 + (throttle * 800)
        pwm_val = int(pulse_length * 4096 / 20000)
        self.pca.set_pwm(channel, 0, pwm_val)

    def set_SG92R_angle(self, channel, angle):
        throttle = (angle - 90) / 90
        pulse_length = 1500 + (throttle * 1000)
        pwm_val = int(pulse_length * 4096 / 20000)
        self.pca.set_pwm(channel, 0, pwm_val)

    def set_wheel_throttle(self, wheel_throttle_L, wheel_throttle_R):
        self.set_FS90R_throttle(CH_WHEEL_L, wheel_throttle_L)
        self.set_FS90R_throttle(CH_WHEEL_R, wheel_throttle_R)

    def set_hand_angle(self, hand_angle_L, hand_angle_R):
        self.set_SG92R_angle(CH_HAND_L, hand_angle_L)
        self.set_SG92R_angle(CH_HAND_R, hand_angle_R)

    def move_forward(self):
        self.set_wheel_throttle(1.0, -1.0)
        time.sleep(self.move_duration)
        self.stop_wheels()

    def move_backward(self):
        self.set_wheel_throttle(-1.0, 1.0)
        time.sleep(self.move_duration)
        self.stop_wheels()

    def turn_left(self):
        self.set_wheel_throttle(-1.0, -1.0)
        time.sleep(self.turn_duration)
        self.stop_wheels()

    def turn_right(self):
        self.set_wheel_throttle(1.0, 1.0)
        time.sleep(self.turn_duration)
        self.stop_wheels()

    def stop_wheels(self):
        self.pca.set_pwm(CH_WHEEL_L, 0, 0)
        self.pca.set_pwm(CH_WHEEL_R, 0, 0)
        time.sleep(0.05)

    def hands_up(self):
        self.set_hand_angle(0, 180)

    def hands_down(self):
        self.set_hand_angle(150, 30)

    def hands_level(self):
        self.set_hand_angle(90, 90)

    def hands_high(self):
        self.set_hand_angle(30, 150)

    def hello_move(self):
        self.set_hand_angle(150, 150)
        time.sleep(0.5)
        self.set_hand_angle(150, 30)

    def yeah_move(self):
        self.set_wheel_throttle(1.0, 1.0)
        time.sleep(2)
        self.stop_wheels()
        self.set_hand_angle(0, 180)

    def dance_move(self):

        self.turn_right()

        for _ in range(3):
            self.set_hand_angle(30, 30)
            time.sleep(0.3)
            self.set_hand_angle(150, 150)
            time.sleep(0.3)

        self.turn_left()
        self.turn_left()

        for _ in range(3):
            self.set_hand_angle(30, 30)
            time.sleep(0.3)
            self.set_hand_angle(150, 150)
            time.sleep(0.3)

        self.turn_right()
        self.hands_down()

    def rush_move(self):

        self.hands_level()
        
        for _ in range(5):
            self.turn_right()
            time.sleep(0.2)
            self.turn_left()
            
        self.hands_down()

    def parse_command(self, message):
        message = message.lower()
        if "forward" in message:
            self.move_forward()
        elif "backward" in message:
            self.move_backward()
        elif "left" in message:
            self.turn_left()
        elif "right" in message:
            self.turn_right()
        elif "hands up" in message:
            self.hands_up()
        elif "hands down" in message:
            self.hands_down()
        elif "hands level" in message:
            self.hands_level()
        elif "hands high" in message:
            self.hands_high()
        elif "hello" in message:
            self.hello_move()
        elif "yeah" in message:
            self.yeah_move()
        elif "dance" in message:
            self.dance_move()
        elif "rush" in message:
            self.rush_move()
        elif "start camera" in message:
            self.start_camera()
        elif "stop camera" in message:
            self.stop_camera()
        elif "reset" in message:
            self.stop_wheels()
            self.hands_down()

    def start_camera(self):
        self.camera_type = self.config['video']['camera_type']
        self.operator_ip = self.config['info']['operator_ip']
        self.port = int(self.config['video']['gstreamer_port'])

        if self.camera_type == 'picam':

            # libcamera-vidプロセス
            self.proc_libcam = subprocess.Popen([
                'libcamera-vid',
                '-t', '0',
                '--inline',
                '--width', self.config['video']['width'],
                '--height', self.config['video']['height'],
                '--framerate', '30',
                '--codec', 'h264',
                '--profile', 'baseline',
                '--bitrate', '1500000',
                '-o', '-'
            ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

            # gst-launch-1.0プロセス (libcameraのstdoutをgstのstdinへ)
            self.proc_gst = subprocess.Popen([
                'gst-launch-1.0',
                'fdsrc', 'fd=0', '!',
                'h264parse', '!',
                'rtph264pay', 'config-interval=1', 'pt=96', '!',
                'udpsink', f"host={self.operator_ip}", f"port={self.port}"
            ], stdin=self.proc_libcam.stdout, stderr=subprocess.DEVNULL)

            print("Camera streaming started")

        else:
            self.proc_webcam = subprocess.Popen([
                'gst-launch-1.0',
                'v4l2src', 'device=/dev/video0', '!',
                f"image/jpeg,width={self.config['video']['width']},height={self.config['video']['height']},framerate=30/1", '!',
                'rtpjpegpay', '!',
                'udpsink', f"host={self.operator_ip}", f"port={self.port}"
            ])

            print("Camera streaming started")

    def stop_camera(self):

        # それぞれのプロセスを終了
        if hasattr(self, 'proc_gst') and self.proc_gst:
            self.proc_gst.terminate()
            self.proc_gst.wait()

        if hasattr(self, 'proc_libcam') and self.proc_libcam:
            self.proc_libcam.terminate()
            self.proc_libcam.wait()

        if hasattr(self, 'proc_webcam') and self.proc_webcam:
            self.proc_webcam.terminate()
            self.proc_webcam.wait()

        print("Camera streaming stopped")
