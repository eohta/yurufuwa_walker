"""
MQTT版メインプログラム（ロボット側）：
MQTTのメッセージ（コマンド）を元にロボットを動作させます
"""
from robot_core import RobotCore
import configparser
import paho.mqtt.client as mqtt

# 設定ファイルを読み込む
def load_config(path='./config.ini'):
    config = configparser.ConfigParser()
    config.read(path, encoding='utf-8')
    return config

# MQTTのコールバック関数
def on_connect(client, userdata, flags, rc):
    print("MQTTブローカーに接続しました")
    client.subscribe(userdata['topic'])

def on_message(client, userdata, msg):
    message = msg.payload.decode('utf-8')
    print(f"受信: {message}")
    userdata['robot'].parse_command(message)

# メイン処理
if __name__ == '__main__':
    config = load_config()

    robot = RobotCore()

    topic = f"command/{config['mqtt']['topic_base']}/{config['info']['robot_id']}"

    client = mqtt.Client(userdata={'topic': topic, 'robot': robot})
    client.username_pw_set(
        username=config['mqtt']['user'],
        password=config['mqtt']['password']
    )

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(config['mqtt']['endpoint'], int(config['mqtt']['port']))
    client.loop_start()

    print("\nToy Robot MQTT Controller")
    print(f"トピック '{topic}' を購読中...\n")

    try:
        while True:
            pass  # メインスレッドは何もしないで待機
        
    except KeyboardInterrupt:
        print("\n終了します。")
        client.loop_stop()
        client.disconnect()
