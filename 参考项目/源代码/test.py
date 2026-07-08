#-*- coding:UTF-8 -*-
import RPi.GPIO as GPIO
import time
import heapq
import threading
import cv2
import numpy as np
import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from aip import AipFace
import base64
import datetime
import socket


# 小车电机引脚定义
IN1 = 20
IN2 = 21
IN3 = 19
IN4 = 26
ENA = 16
ENB = 13

# RGB三色灯引脚定义
LED_R = 22
LED_G = 27
LED_B = 24

# 舵机引脚定义
ServoPin = 23

# 超声波引脚定义
EchoPin = 0
TrigPin = 1

#蜂鸣器
BuzzerPin = 8

# 小车按键定义
key = 8

# 循迹红外引脚定义
TrackSensorLeftPin1 = 3
TrackSensorLeftPin2 = 5
TrackSensorRightPin1 = 4
TrackSensorRightPin2 = 18

# 设置GPIO口为BCM编码方式
GPIO.setmode(GPIO.BCM)

# 忽略警告信息
GPIO.setwarnings(False)

# 全局变量
pwm_ENA = None
pwm_ENB = None
pwm_servo = None
obstacle_detected = False  # 用于线程间通信，指示是否检测到障碍物
current_orientation = 2 # 初始化小车朝向为下
color_is_red=False

def servo_pulse(myangle,myPin):
    pulsewidth = (myangle * 11) + 500
    GPIO.output(myPin, GPIO.HIGH)
    time.sleep(pulsewidth/1000000.0)
    GPIO.output(myPin, GPIO.LOW)
    time.sleep(20.0/1000-pulsewidth/1000000.0)

#舵机来回转动
def servo_control(myPin):
    for pos in range(181):
        servo_pulse(pos,myPin)
        time.sleep(0.001) 
    for pos in reversed(range(181)):
        servo_pulse(pos)
        time.sleep(0.001)


    
def color_recongnition():
    global color_is_red
    # 初始化摄像头
    cap = cv2.VideoCapture(1)  # 1表示第一个摄像头设备

    min_area=1500
    max_area=5000
    
    if not cap.isOpened():
        print("无法打开摄像头")
    
    while True:
        # 读取当前帧
        ret, frame = cap.read()
        # 如果不能读取帧，退出循环
        if not ret:
            print("failed")
            break
        # 将图像转换为HSV颜色空间
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # 定义绿色的HSV阈值范围
        lower_green = np.array([50, 150, 150])
        upper_green = np.array([70, 255, 255])
        # 根据阈值创建绿色的掩码
        mask_green = cv2.inRange(hsv, lower_green, upper_green)
        # 查找绿色区域的轮廓
        contours_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # 如果检测到绿色的轮廓则为假
        if contours_green:
            color_is_red=False
            print('green')
        # 定义红色的HSV阈值范围（红色通常分两个区域）
        lower_red1 = np.array([0, 150, 150])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 150, 150])
        upper_red2 = np.array([180, 255, 255])
        # 根据阈值创建红色的掩码
        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask_red = cv2.add(mask_red1, mask_red2)
        # 查找红色区域的轮廓
        contours_red, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours_red:
            area = cv2.contourArea(contour)
            if min_area<=area<=max_area:
                color_is_red=True
                print('red')

    # 释放摄像头并关闭所有窗口
    cap.release()
    cv2.destroyAllWindows()

    
def photo(root):
    # 初始化摄像头
    cap = cv2.VideoCapture(1)

    # 加载人脸和眼睛的haar级联分类器
    face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    # 检测到的人脸的坐标
    face_coords = None
    stable_frames = 0
    required_stable_frames = 10  # 设置需要人脸稳定的帧数

    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法获取摄像头帧")
            break

        # 转换为灰度图像
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            x, y, w, h = faces[0]  # 取第一个检测到的人脸
            new_face_coords = (x, y, w, h)

            if face_coords is None:
                face_coords = new_face_coords
                stable_frames = 1
            else:
                # 如果人脸坐标变化不大，则认为人脸稳定
                if abs(face_coords[0] - new_face_coords[0]) < 10 and abs(face_coords[1] - new_face_coords[1]) < 10:
                    stable_frames += 1
                else:
                    stable_frames = 1
                face_coords = new_face_coords

            # 在图像中标记人脸
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # 如果人脸稳定帧数达到了要求，拍摄照片
            if stable_frames >= required_stable_frames:
                image_path = "captured_image.jpg"
                cv2.imwrite(image_path, frame)
                print(f"已保存照片: {image_path}")

                # 创建套接字并连接到服务器
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((root, 6666))

                    # 读取照片文件并转换为二进制数据
                    with open(image_path, 'rb') as file:
                        image_data = file.read()

                    # 发送照片数据
                    sock.sendall(image_data)
                    print("照片数据已发送")

                except socket.error as e:
                    print(f"套接字错误: {e}")

                finally:
                    # 关闭套接字
                    sock.close()

                break

        # 显示图像
        cv2.imshow('Video', frame)

        # 按 'q' 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放摄像头资源
    cap.release()
    cv2.destroyAllWindows()


# 主程序入口
if __name__ == '__main__':
    try:
#         main_control()
        photo("192.168.23.154")
    except KeyboardInterrupt:
        pass
    finally:
#         pwm_ENA.stop()
#         pwm_ENB.stop()
#         pwm_servo.stop()
        GPIO.cleanup