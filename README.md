# Yurufuwa Walker

こちらのコードは、ゆるふわロボをパソコンから遠隔操作により動かすためのサンプルコードです。あまり良いコードでないと思いますので、あくまで参考程度に留めておいて下さい。バグ等を発見された場合は、ご一報頂けましたら幸いです。

ロボットの遠隔操作の方法としては、SSH等のターミナルを使う方法と、MQTT 経由の通信による方法があります。コードを実際に試す場合は、ターミナルを使う方が簡単かと思いますので、まずはそちらからお試し頂くことをお勧めします。

## 特徴
- ロボットはパソコンからテキストベースのコマンドを受け取り、さまざまな動作を行います
- 前進・後退・旋回・ダンスなどの動作を行います（サーボが搭載されている場合）
- カメラ画像の配信も行うことができます（カメラが搭載されている場合）


## 必要なハードウェア

- Raspberry Pi を搭載したゆるふわロボ
- サーボモータードライバー（PCA9685を搭載したもの）
- サーボモーター Tower Pro SG92R（腕部）
- サーボモーター FEETECH FS90R（車輪部）
- Raspberry Pi に対応したカメラ（カメラ映像を配信する場合）
- Windows パソコン（操作用マシン）


## ファイル構成

| ファイル | 説明 |
|:---|:---|
| `robot_core.py` | コアプログラム（ロボット側） |
| `robot_term.py` | メインプログラム(ロボット側 - ターミナルによる操作) |
| `robot_mqtt.py` | メインプログラム(ロボット側 - MQTT&GUI による操作) |
| `controller.py` | 操作用GUI（パソコン側 - MQTT） |
| `config.ini` | 設定ファイル（ロボット側とパソコン側と同じものが必要） |
| `README.md` | このファイル |

## ソフトウェアのインストール

### ロボット側（Raspberry Pi）
以下のパッケージおよびソフトウェアのインストールが必要です。

- GStreamer（画像配信）
- Mosquitto（MQTT）
- adafruit-pca9685
- paho-mqtt

下のコマンドでインストールします。

```bash
sudo apt update
sudo apt install python3-pip libgstreamer1.0-dev gstreamer1.0-tools mosquitto mosquitto-clients
pip3 install adafruit-pca9685 paho-mqtt
```

このレポジトリのコードも必要ですので、適当な場所へダウンロードして下さい。


### パソコン側
以下のパッケージおよびソフトウェアのインストールが必要です。

- paho-mqtt
- GStreamer（画像配信）
- Mosquitto（MQTT）

Python のパッケージは、次のコマンドでインストールします。

```bash
pip3 install paho-mqtt
```

このレポジトリのコードも必要ですので、適当な場所へダウンロードして下さい。


ロボットからのカメラ画像を受信をする場合には、パソコン側にも GStreamer のインストールが必要です。下の手順に沿ってインストールして下さい。

https://gstreamer.freedesktop.org/documentation/installing/on-windows.html


また、MQTT での通信を行う場合は、動作確認等に mosquitto があると便利です。インストールする場合は、以下よりインストーラーをダウンロードして使って下さい。

https://mosquitto.org/download/

## ソースコードの編集
ロボット側のソースコードを実際のサーボの接続チャネルに合わせて書き換えます。デフォルトでは、次のような配線を採用しています。

- 右の車輪：CH-0
- 左の車輪：CH-1
- 右の腕：CH-2
- 左の腕：CH-3

## 設定ファイルの編集
設定ファイルを実際の環境に合わせて、編集して下さい。下の例は、次の条件のもとでの設定ファイル（config.ini）の例です。

- ロボット側の IPアドレス： 192.168.10.29
- パソコン側の IPアドレス： 192.168.10.120
- メッセージブローカーの IPアドレス：192.168.10.29

```ini
[info]
# ロボットのIDを指定します（01, 02 など、好きなものでOK）
robot_id = 01

# パソコンのIPアドレスを指定します
operator_ip = 192.168.10.120

[mqtt]
# メッセージブローカーのIPアドレスを指定します
endpoint = 192.168.10.29

# MQTTポート番号（通常1883）
port = 1883

# コマンド送信に使うトピックのベース
topic_base = robot

# MQTT認証情報（不要なら空白でOK）
user = 
password = 

[video]
# GStreamerで使用するUDPポート番号
gstreamer_port = 47000

# 使用するカメラの種類 ('webcam' または 'picam')
camera_type = webcam

# ストリームの形式 ('jpeg' または 'h264')
stream_format = jpeg

# カメラの解像度（横幅）
width = 1280

# カメラの解像度（高さ）
height = 720

[move]
# 前進・後退の際の動作継続時間
move_duration = 1

# 旋回の際の動作継続時間
turn_duration = 0.2
```


## 遠隔操作の方法
ロボットをリモート操作する方法については、次の２通りの方法があります。

- ロボットに搭載されている Raspberry Pi に直接ログインして、コマンドを打ち込む（SSH や VNC を利用）
- MQTT 経由でコマンドを送る

### 直接ログインによる遠隔操作
SSH や VNC 等を使って、ロボット（Raspberry Pi）にログインします。ターミナルから次のコマンドを実行して下さい。

```bash
python robot_term.py
```

コマンドモードに入ったら、"move forward" とか "turn right" といったロボットに実行させたいコマンドを打ち込みます。

### MQTT による遠隔操作
MQTT による遠隔操作を行うためには、まず MQTT による通信環境のセットアップが必要になります。下にある「通信環境のセットアップ」を参考に通信環境を整えておいて下さい。次に、ロボット（Raspberry Pi）にログインします。ターミナルから次のコマンドを実行して下さい。

```bash
python robot_mqtt.py
```

うまく起動できたら、ロボットは既に MQTTによるコマンドを受信できるようになっていますので、次はパソコン側で遠隔操作アプリを起動します。下のコマンドで遠隔操作アプリを起動して下さい。

```bash
python controller.py
```

遠隔操作アプリの画面にあるボタンを押すことで、ロボットを動かしたり、画像配信の開始や停止などを行うことができます。


## コマンド一覧
ロボット側が解釈できるコマンドの一覧です。

| コマンド | 動作 |
|:---|:---|
| move forward | 前進 |
| move backward | 後退 |
| turn left | 左旋回 |
| turn right | 右旋回 |
| hands up | 手を上げる |
| hands down | 手を下げる |
| hello | あいさつ |
| dance | ダンス |
| yeah | わーい |
| rush | 連続パンチ |
| start camera | カメラ画像の送信開始 |
| stop camera | カメラ画像の送信停止 |
| reset | 初期状態にリセット |

## 通信環境のセットアップ（MQTT）

ロボットのリモート操作に MQTT を使う場合は、「メッセージブローカー」と呼ばれるメッセージのメッセージのやり取りをサポートするプログラムをどこかのマシンで動かしてやる必要があります。メッセージブローカーは、基本的にロボット本体の方で動かすのがお勧めです（遊び終わったら、ロボットの電源は落とすようにして下さい）。

MQTT は、実際の産業分野でも使われている技術ですが、下で説明する手順は「自宅でロボットをラジコンとして楽しむ」ことを想定した手順になります。通信の安全が担保されていない場所では、もう少しセキュリティを高めた設定が必要になります。また、自宅で遊ぶ場合でもセキュリティには、十分に注意して下さい。

こちらのコードでは、MQTT による通信に mosquitto を利用します。ロボットに mosquitto をインストールする手順は、次のようになります。

```bash
sudo apt install mosquitto mosquitto-clients
```

設定を編集して、メッセージブローカーに誰でも接続できるようにします。より安全な環境にするには、接続できるユーザーを制限することもできますが、ここでは簡単のため、セキュリティ的に緩い設定をします。

```bash
sudo nano /etc/mosquitto/mosquitto.conf
```

次を追記して下さい。

```
listener 1883 0.0.0.0
allow_anonymous true
```

ロボットの起動と共に mosquitto が自動的に立ち上がるようにするには、次のコマンドをターミナルで実行しておきます。

```bash
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto
```


## MQTT による通信の確認手順

下は、MQTT による通信がうまく行かない場合の確認手順です。以下の手順は、次の条件の元での例になります。

- ロボット側の IPアドレス： 192.168.10.29
- パソコン側の IPアドレス： 192.168.10.120
- メッセージブローカーの IPアドレス：192.168.10.29

IPアドレスは、実際の環境に合わせて読み替えて下さい。

1. ネットワーク接続の確認
パソコン側でターミナル（PowerShell等）を開いて、次のコマンドでネットワーク接続の確認をします。

```bash
ping 192.168.10.29
```

2. MQTT による通信の確認
ロボット側で MQTT の確認をします。まず、ターミナルを開いて、下のコマンドでメッセージの購読を開始します。

```bash
mosquitto_sub -h 192.168.10.29 -t test
```

次に、上とは別のターミナルを開いて、下のコマンドでメッセージを送信します。

```bash
mosquitto_pub -h 192.168.10.29 -t test -m "hello"
```

先に開いたターミナルで "hello" が受信できていれば OK です。


次に、パソコン側で開いているターミナル（PowerShell等）から同じコマンドを送信して、同じようにメッセージが受信できているか確認して下さい（パソコン側からメッセージを送信するには、パソコン側にも mosquitto のインストールが必要です）。

## GStreamer による画像配信の確認手順

下は、カメラによる画像配信がうまく行かない場合、ターミナルからコマンドを直接打ち込んで、エラーの原因を特定して下さい。エラーメッセージを ChatGPT等に投げると、問題解決のさまざまなヒントがもらえます。

### WebCam の場合（Logicool C270 等）

一般的な WebCam を使う場合は、画像圧縮に JPEG を利用します。

送信側【ロボット側】
```bash
gst-launch-1.0 v4l2src device=/dev/video0 ! image/jpeg,width=1280,height=720,framerate=30/1 ! rtpjpegpay ! udpsink host=192.168.10.120 port=47000
```

受信側【パソコン側】
```bash
gst-launch-1.0 udpsrc port=47000 ! application/x-rtp, encoding-name=JPEG,payload=26 ! rtpjpegdepay ! jpegdec ! autovideosink
```

### Raspberry Pi Camera Module の場合（Camera Module V2, V3等）

Raspberry Camera Module が使える場合は、画像圧縮に H264 を利用します。

送信側【ロボット側】
```bash
libcamera-vid -t 0 --inline --width 1280 --height 720 --framerate 30 -o - | gst-launch-1.0 fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=192.168.10.120 port=47000
```

受信側【パソコン側】
```bash
gst-launch-1.0 udpsrc port=47000 caps="application/x-rtp,media=video,encoding-name=H264,payload=96" ! rtph264depay ! avdec_h264 ! autovideosink
```

なお、上のコマンドは、下の条件での例になります。適宜、実際の環境に合わせて、コマンドは読み替えて下さい。

- パソコン側の IP アドレス: 192.168.10.120
- UDPポート: 47000

## 技術的背景

### なぜ MQTT なのか？
通常、ロボットのためのフレームワークとしては、ROS(Robot Operating System) が有名ですが、ゆるふわロボでは通信のため MQTT を採用しています。それは、主に次のような２つの理由によります。

- ROS が要求するハードウェアスペックが割と高い
- MQTT であれば、マイコン等との通信がやり易い

MQTT であれば、M5Stack 等のマイコンとの通信などもやり易く、ロボットが専門の方でなくても扱いやすいのではないかと考えました。

### なぜ GStreamer なのか？
ROS 等のフレームワークを使えば、実際にはカメラからの画像も扱うことができますが、GStreamer という画像配信向けの汎用のプラットフォームを使うことで、ロボットが専門でない方でも入り易くなるのではないかと考えました。将来的に画像を配信するアプリなどを開発したい学生の方にとってもよい学びの機会になるかもしれません。
