import socket
import RPi.GPIO as GPIO
import time
import requests
import base64
import json
import cv2
import pyzbar.pyzbar as pyzbar
import smtplib  # 导入smtp模块
from email.mime.text import MIMEText
from email.header import Header
import numpy as np
import os
import urllib
import urllib.request
import hashlib
import socket
import pyttsx3
import pyaudio
import wave
from aip import AipSpeech
import subprocess
import pyzbar.pyzbar as pyzbar

# 设置GPIO口为BCM编码方式
GPIO.setmode(GPIO.BCM)

# 忽略警告信息
GPIO.setwarnings(False)

#---------------------------ID------------------------------------

appID1 = "wx13cdb01f55164788"
appSecret1 = "ae3dfb41d64079051232d8e4fb17803b"
openId1 = 'oNUff6ds7HTV2Oww8YjfcclgrbPA'

# 设置百度API的账号信息
APP_ID2 = '90000091'
API_KEY2 = 'ug93XWc5TtrSPTr2rPUIWWrf'
SECRET_KEY2 = 'QtBLVyFRvuG4AMNdfWKl0kU4qzLl2OgP'  # 移除了前面的空格

API_KEY3 = "FrvX7CCd4pZ2yfQbvmi5CWjt"
SECRET_KEY3 = "GYAg5kP9WxralSKSwGJq0bVhibc0Q1y0"
APP_ID3 = "90343642"  # 替换为实际的AppID

#-----------------------------------------------------------------

# 管脚参数
# 小车按键定义
key = 8
# 小车电机引脚定义
IN1 = 20
IN2 = 21
IN3 = 19
IN4 = 26
ENA = 16
ENB = 13
# 超声波引脚定义
EchoPin = 0
TrigPin = 1
# RGB三色灯引脚定义
LED_R = 22
LED_G = 27
LED_B = 24
# 舵机引脚定义
FrontServoPin = 23
ServoUpDownPin = 9
ServoLeftRightPin = 11
# 红外避障引脚定义
AvoidSensorLeft = 12
AvoidSensorRight = 17
# 蜂鸣器引脚定义
buzzer = 8
# 灭火电机引脚设置
OutfirePin = 2  # 灭火电机
# 循迹红外引脚定义
TrackSensorLeftPin1 = 3  # 定义左边第一个循迹红外传感器引脚为3
TrackSensorLeftPin2 = 5  # 定义左边第二个循迹红外传感器引脚为5
TrackSensorRightPin1 = 4  # 定义右边第一个循迹红外传感器引脚为4
TrackSensorRightPin2 = 18  # 定义右边第二个循迹红外传感器引脚为18
# 光敏电阻引脚定义
LdrSensorLeft = 7
LdrSensorRight = 6




#-------------------器材探照灯--------------------------------

# def colorLED():                              #七彩探照灯
#     #RGB三色灯引脚定义
#     LED_R = 22
#     LED_G = 27
#     LED_B = 24
#
#
#     #RGB三色灯设置为输出模式
#     GPIO.setup(LED_R, GPIO.OUT)
#     GPIO.setup(LED_G, GPIO.OUT)
#     GPIO.setup(LED_B, GPIO.OUT)
#
#     #循环显示7种不同的颜色
#     try:
#         while True:
#             GPIO.output(LED_R, GPIO.HIGH)
#             GPIO.output(LED_G, GPIO.LOW)
#             GPIO.output(LED_B, GPIO.LOW)
#             time.sleep(1)
#             GPIO.output(LED_R, GPIO.LOW)
#             GPIO.output(LED_G, GPIO.HIGH)
#             GPIO.output(LED_B, GPIO.LOW)
#             time.sleep(1)
#             GPIO.output(LED_R, GPIO.LOW)
#             GPIO.output(LED_G, GPIO.LOW)
#             GPIO.output(LED_B, GPIO.HIGH)
#             time.sleep(1)
#             GPIO.output(LED_R, GPIO.HIGH)
#             GPIO.output(LED_G, GPIO.HIGH)
#             GPIO.output(LED_B, GPIO.LOW)
#             time.sleep(1)
#             GPIO.output(LED_R, GPIO.HIGH)
#             GPIO.output(LED_G, GPIO.LOW)
#             GPIO.output(LED_B, GPIO.HIGH)
#             time.sleep(1)
#             GPIO.output(LED_R, GPIO.LOW)
#             GPIO.output(LED_G, GPIO.HIGH)
#             GPIO.output(LED_B, GPIO.HIGH)
#             time.sleep(1)
#             GPIO.output(LED_R, GPIO.LOW)
#             GPIO.output(LED_G, GPIO.LOW)
#             GPIO.output(LED_B, GPIO.LOW)
#             time.sleep(1)
#     except:
#         print ("except")
#     #使用try except语句，当CTRL+C结束进程时会触发异常后
#     #会执行gpio.cleanup()语句清除GPIO管脚的状态
#     GPIO.cleanup()

#------------------------小车行进----------------------------------------



def key_scan():
    while GPIO.input(key):
        pass
    while not GPIO.input(key):
        time.sleep(0.01)
        if not GPIO.input(key):
            time.sleep(0.01)
        while not GPIO.input(key):
            pass

def Distance():
    GPIO.output(TrigPin, GPIO.LOW)
    time.sleep(0.000002)
    GPIO.output(TrigPin, GPIO.HIGH)
    time.sleep(0.000012)
    GPIO.output(TrigPin, GPIO.LOW)
    t3 = time.time()
    while not GPIO.input(EchoPin):  # 等回音超过3ms，视为无关障碍
        t4 = time.time()
        if (t4 - t3) > 0.003:
            return 1000
    t1 = time.time()
    while GPIO.input(EchoPin):  # 看回音持续了多久，超过3ms视为噪音
        t5 = time.time()
        if (t5 - t1) > 0.003:
            return 1000

    t2 = time.time()
    k1 = ((t2 - t1) * 340 / 2) * 100
    GPIO.output(TrigPin, GPIO.LOW)
    time.sleep(0.000002)
    GPIO.output(TrigPin, GPIO.HIGH)
    time.sleep(0.000012)
    GPIO.output(TrigPin, GPIO.LOW)
    t3 = time.time()
    while not GPIO.input(EchoPin):  # 等回音超过3ms，视为无关障碍
        t4 = time.time()
        if (t4 - t3) > 0.003:
            return 1000
    t1 = time.time()
    while GPIO.input(EchoPin):  # 看回音持续了多久，超过3ms视为噪音
        t5 = time.time()
        if (t5 - t1) > 0.003:
            return 1000

    t2 = time.time()
    k2 = ((t2 - t1) * 340 / 2) * 100

    GPIO.output(TrigPin, GPIO.LOW)
    time.sleep(0.000002)
    GPIO.output(TrigPin, GPIO.HIGH)
    time.sleep(0.000012)
    GPIO.output(TrigPin, GPIO.LOW)
    t3 = time.time()
    while not GPIO.input(EchoPin):  # 等回音超过3ms，视为无关障碍
        t4 = time.time()
        if (t4 - t3) > 0.003:
            return 1000
    t1 = time.time()
    while GPIO.input(EchoPin):  # 看回音持续了多久，超过3ms视为噪音
        t5 = time.time()
        if (t5 - t1) > 0.003:
            return 1000

    t2 = time.time()
    k3 = ((t2 - t1) * 340 / 2) * 100
    return (k1 + k2 + k3) / 3.0

# 舵机电压清零，持续保持在某个电平会使得电机持续运转，所以在设置后需要再清零，此时电机不会重置位置而是直接停机
def stop_servo_angle():
    pwm_FrontServo.ChangeDutyCycle(0)

# 舵机旋转到指定角度,占空比为2.5-12.5为0~180度
def set_servo_angle(k):
    pwm_FrontServo.ChangeDutyCycle(2.5 + 10 * k / 180)
    time.sleep(0.2)
    stop_servo_angle()

def set_camera_updown(k):
    pwm_UpDownServo.ChangeDutyCycle(2.5 + 10 * k / 180)
    time.sleep(0.2)
    stop_camera_updown()

def set_camera_leftright(k):
    pwm_LeftRightServo.ChangeDutyCycle(2.5 + 10 * k / 180)
    time.sleep(0.2)
    stop_camera_leftright()

def stop_camera_updown():
    pwm_UpDownServo.ChangeDutyCycle(0)

def stop_camera_leftright():
    pwm_LeftRightServo.ChangeDutyCycle(0)

# 设置七彩灯颜色
def set_color(R, G, B):
    if R == 1:
        GPIO.output(LED_R, GPIO.HIGH)
    else:
        GPIO.output(LED_R, GPIO.LOW)
    if G == 1:
        GPIO.output(LED_G, GPIO.HIGH)
    else:
        GPIO.output(LED_G, GPIO.LOW)
    if B == 1:
        GPIO.output(LED_B, GPIO.HIGH)
    else:
        GPIO.output(LED_B, GPIO.LOW)

# 小车鸣笛
def whistle():
    GPIO.output(buzzer, GPIO.LOW)
    time.sleep(1.5)
    GPIO.output(buzzer, GPIO.HIGH)
    time.sleep(0.001)

# 小车前进，两驱动轮前进
def run(leftSpeed, rightSpeed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(leftSpeed)
    pwm_ENB.ChangeDutyCycle(rightSpeed)

# 小车左转，右驱动轮前进
def left(leftSpeed, rightSpeed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(leftSpeed)
    pwm_ENB.ChangeDutyCycle(rightSpeed)

# 小车右转，左驱动轮前进
def right(leftSpeed, rightSpeed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(leftSpeed)
    pwm_ENB.ChangeDutyCycle(rightSpeed)

# 小车原地左转，左驱动轮后退，右驱动轮前进
def spin_left(leftSpeed, rightSpeed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(leftSpeed)
    pwm_ENB.ChangeDutyCycle(rightSpeed)

# 小车原地右转，左驱动轮前进，右驱动轮后退
def spin_right(leftSpeed, rightSpeed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_ENA.ChangeDutyCycle(leftSpeed)
    pwm_ENB.ChangeDutyCycle(rightSpeed)

# 小车停止
def brake():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)

# 小车后退，两驱动轮前进
def back(leftSpeed, rightSpeed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_ENA.ChangeDutyCycle(leftSpeed)
    pwm_ENB.ChangeDutyCycle(rightSpeed)

# 小车反方向左转，右驱动轮后退
def back_left(Speed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_ENA.ChangeDutyCycle(Speed)
    pwm_ENB.ChangeDutyCycle(Speed)

# 小车反方向右转，左驱动轮后退
def back_right(Speed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(Speed)
    pwm_ENB.ChangeDutyCycle(Speed)


def init():
    global pwm_ENA
    global pwm_ENB
    global pwm_FrontServo
    global pwm_UpDownServo
    global pwm_LeftRightServo
    global pwm_Rled
    global pwm_Gled
    global pwm_Bled

    GPIO.setup(ENA, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(IN1, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(IN2, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(ENB, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(IN3, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(IN4, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(buzzer, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(OutfirePin, GPIO.OUT)
    GPIO.setup(EchoPin, GPIO.IN)
    GPIO.setup(TrigPin, GPIO.OUT)
    GPIO.setup(LED_R, GPIO.OUT)
    GPIO.setup(LED_G, GPIO.OUT)
    GPIO.setup(LED_B, GPIO.OUT)
    GPIO.setup(ServoLeftRightPin, GPIO.OUT)
    GPIO.setup(FrontServoPin, GPIO.OUT)
    GPIO.setup(ServoUpDownPin, GPIO.OUT)
    GPIO.setup(AvoidSensorLeft, GPIO.IN)
    GPIO.setup(AvoidSensorRight, GPIO.IN)
    GPIO.setup(LdrSensorLeft, GPIO.IN)
    GPIO.setup(LdrSensorRight, GPIO.IN)
    GPIO.setup(TrackSensorLeftPin1, GPIO.IN)
    GPIO.setup(TrackSensorLeftPin2, GPIO.IN)
    GPIO.setup(TrackSensorRightPin1, GPIO.IN)
    GPIO.setup(TrackSensorRightPin2, GPIO.IN)

    # 设置pwm引脚和频率为2000hz
    pwm_ENA = GPIO.PWM(ENA, 2000)
    pwm_ENB = GPIO.PWM(ENB, 2000)
    pwm_ENA.start(0)
    pwm_ENB.start(0)

    # 设置舵机的频率和起始占空比
    pwm_FrontServo = GPIO.PWM(FrontServoPin, 50)
    pwm_UpDownServo = GPIO.PWM(ServoUpDownPin, 50)
    pwm_LeftRightServo = GPIO.PWM(ServoLeftRightPin, 50)
    pwm_FrontServo.start(0)
    pwm_UpDownServo.start(0)
    pwm_LeftRightServo.start(0)

    pwm_Rled = GPIO.PWM(LED_R, 1000)
    pwm_Gled = GPIO.PWM(LED_G, 1000)
    pwm_Bled = GPIO.PWM(LED_B, 1000)
    pwm_Rled.start(0)
    pwm_Gled.start(0)
    pwm_Bled.start(0)




def park():
    back(15, 15)
    time.sleep(1.18)
    brake()
    set_servo_angle(180)
    time.sleep(1)
    a = Distance()
    print(a)
    if a > 50:
        right(20, 20)
        time.sleep(1.2)
        back(15, 15)
        time.sleep(1.4)
        brake()
    else:
        set_servo_angle(0)
        a = Distance()
        if a > 50:
            left(20, 20)
            time.sleep(1.1)
            back(15, 15)
            time.sleep(1.4)
            brake()
        else:
            brake()


def search_line(color):
    while True:
        # 前方发现障碍，执行避障程序
        a = Distance()
        # print(a)
        if a <= 15:
            print("发现障碍物，进入避障模式！")
            avoid()
        else:
            # 检测到黑线时循迹模块相应的指示灯亮，端口电平为LOW
            # 未检测到黑线时循迹模块相应的指示灯灭，端口电平为HIGH
            TrackSensorLeftValue1 = GPIO.input(TrackSensorLeftPin1)
            TrackSensorLeftValue2 = GPIO.input(TrackSensorLeftPin2)
            TrackSensorRightValue1 = GPIO.input(TrackSensorRightPin1)
            TrackSensorRightValue2 = GPIO.input(TrackSensorRightPin2)

            # 全黑，表示抵达特殊任务点，返回2
            if TrackSensorLeftValue1 == False and TrackSensorLeftValue2 == False and TrackSensorRightValue1 == False and TrackSensorRightValue2 == False:
                print("遇到停止线")
                brake()
                color1 = color_recognizer()
                if (color1 == color):  # 右转进病房
                    spin_right(38, 38)
                    time.sleep(0.5)  # 当靠近障碍物时原地右转大约90度
                    run(15, 15)  # 转弯后当前方距离大于25cm时前进
                    time.sleep(1.5)
                    print("执行任务")
                    brake()
                    time.sleep(5)
                    bobao("请等待3秒，准备拍照")
                    time.sleep(3)
                    photo("192.168.50.122")
                    time.sleep(1)
                    bobao("你好，我是小赵，请问您有什么问题需要问我，我尽力帮您解决，请您等待1至2秒")
                    text = audio_to_text()
                    if text:
                        print("识别的文本:", text)
                    else:
                        print("没有识别到文本。")
                    result = ai(text)
                    bobao(result)
                    time.sleep(5)
                    qr_result = qr_code_recognition()
                    if(qr_result != None):
                        # 1.获取access_token
                        access_token_qr = get_access_token_qr()
                        # 2.发送模板消息
                        send_msg(access_token_qr,qr_result)
                        spin_left(25,25)
                        time.sleep(1.0)
                        run(20,20)
                        time.sleep(1.5)
                        spin_right(38,38)
                        time.sleep(0.5)
                        run(20,20)
                        time.sleep(0.4)
                        search_line(color)
                elif (color1 == "purple"):  # 掉头，倒车入库
                    spin_left(28, 28)
                    time.sleep(0.5)  # 转弯后前方距离小于25cm时向左原地转弯180度
                    back(20, 20)
                    time.sleep(1.0)
                    brake()
                    print("入药房")
                    break
                else:
                    print("继续行车")
                    search_line(color)

            # 处理右锐角和右直角的转动
            elif (TrackSensorLeftValue1 == False or TrackSensorLeftValue2 == False) and TrackSensorRightValue2 == False:
                print("right1")
                time.sleep(0.05)
                TrackSensorLeftValue1 = GPIO.input(TrackSensorLeftPin1)
                TrackSensorLeftValue2 = GPIO.input(TrackSensorLeftPin2)
                TrackSensorRightValue1 = GPIO.input(TrackSensorRightPin1)
                TrackSensorRightValue2 = GPIO.input(TrackSensorRightPin2)
                if TrackSensorLeftValue1 == False and TrackSensorLeftValue2 == False and TrackSensorRightValue1 == False and TrackSensorRightValue2 == False:
                        print("遇到停止线")
                        brake()
                        color1 = color_recognizer()
                        if (color1 == color):  # 右转进病房
                            spin_right(38, 38)
                            time.sleep(0.5)  # 当靠近障碍物时原地右转大约90度
                            run(15, 15)  # 转弯后当前方距离大于25cm时前进
                            time.sleep(1.5)
                            print("执行任务")
                            brake()
                            time.sleep(5)
                            bobao("请等待3秒，准备拍照")
                            time.sleep(3)
                            photo("192.168.50.122")
                            time.sleep(1)
                            bobao("你好，我是小赵，请问您有什么问题需要问我，我尽力帮您解决，请您等待1至2秒")
                            text = audio_to_text()
                            if text:
                                print("识别的文本:", text)
                            else:
                                print("没有识别到文本。")
                            result = ai(text)
                            bobao(result)
                            time.sleep(5)
                            qr_result = qr_code_recognition()
                            if (qr_result != None):
                                # 1.获取access_token
                                access_token_qr = get_access_token_qr()
                                # 2.发送模板消息
                                send_msg(access_token_qr, qr_result)
                                spin_left(25, 25)
                                time.sleep(1.0)
                                run(20, 20)
                                time.sleep(1.5)
                                spin_right(38, 38)
                                time.sleep(0.5)
                                run(20, 20)
                                time.sleep(0.4)
                            search_line(color)
                        elif (color1 == "purple"):  # 掉头，倒车入库
                            spin_left(28, 28)
                            time.sleep(0.5)  # 转弯后前方距离小于25cm时向左原地转弯180度
                            back(20, 20)
                            time.sleep(1.0)
                            brake()
                            print("入药房")
                            break
                        else:
                            print("继续执行")
                            search_line(color)
                else:
                    print("right2")
                    spin_right(25, 25)
                    set_color(0, 255, 0)
                    time.sleep(0.08)

            # 处理左锐角和左直角的转动
            elif TrackSensorLeftValue1 == False and (
                    TrackSensorRightValue1 == False or TrackSensorRightValue2 == False):
                print("left1")
                time.sleep(0.05)
                TrackSensorLeftValue1 = GPIO.input(TrackSensorLeftPin1)
                TrackSensorLeftValue2 = GPIO.input(TrackSensorLeftPin2)
                TrackSensorRightValue1 = GPIO.input(TrackSensorRightPin1)
                TrackSensorRightValue2 = GPIO.input(TrackSensorRightPin2)
                if TrackSensorLeftValue1 == False and TrackSensorLeftValue2 == False and TrackSensorRightValue1 == False and TrackSensorRightValue2 == False:
                    print("遇到停止线")
                    brake()
                    color1 = color_recognizer()
                    if (color1 == color):  # 右转进病房
                        spin_right(38, 38)
                        time.sleep(0.5)  # 当靠近障碍物时原地右转大约90度
                        run(15, 15)  # 转弯后当前方距离大于25cm时前进
                        time.sleep(1.5)
                        print("执行任务")
                        brake()
                        time.sleep(5)
                        bobao("请等待3秒，准备拍照")
                        time.sleep(3)
                        photo("192.168.50.122")
                        time.sleep(1)
                        bobao("你好，我是小赵，请问您有什么问题需要问我，我尽力帮您解决，请您等待1至2秒")
                        text = audio_to_text()
                        if text:
                            print("识别的文本:", text)
                        else:
                            print("没有识别到文本。")
                        result = ai(text)
                        bobao(result)
                        time.sleep(5)
                        qr_result = qr_code_recognition()
                        if (qr_result != None):
                            # 1.获取access_token
                            access_token_qr = get_access_token_qr()
                            # 2.发送模板消息
                            send_msg(access_token_qr, qr_result)
                            spin_left(25, 25)
                            time.sleep(1.0)
                            run(20, 20)
                            time.sleep(1.5)
                            spin_right(38, 38)
                            time.sleep(0.5)
                            run(20, 20)
                            time.sleep(0.4)
                        search_line(color)
                    elif (color1 == "purple"):  # 掉头，倒车入库
                        spin_left(28, 28)
                        time.sleep(0.5)  # 转弯后前方距离小于25cm时向左原地转弯180度
                        back(20, 20)
                        time.sleep(1.0)
                        brake()
                        print("入药房")
                        break
                    else:
                        print("继续行车")
                        search_line(color)
                else:
                    print("left2")
                    spin_left(25, 25)
                    set_color(255, 0, 0)
                    time.sleep(0.08)

            # 最左边检测到
            elif TrackSensorLeftValue1 == False:
                spin_left(15, 15)

            # 最右边检测到
            elif TrackSensorRightValue2 == False:
                spin_right(15, 15)

            # 处理左小弯
            elif TrackSensorLeftValue2 == False and TrackSensorRightValue1 == True:
                left(0, 15)

            # 处理右小弯
            elif TrackSensorLeftValue2 == True and TrackSensorRightValue1 == False:
                right(15, 0)

            # 处理直线
            elif TrackSensorLeftValue2 == False and TrackSensorRightValue1 == False:
                run(15, 15)

# 当为1 1 1 1时小车保持上一个小车运行状态
# 以下为避障函数
# 当距离障碍物30cm的时候从右侧绕过去，为了体现运行的速度，没有进行左右位置障碍物的判断
def avoid():
    set_color(255, 255, 255)
    brake()
    spin_right(33, 33)
    time.sleep(0.4)  # 当靠近障碍物时原地右转大约90度
    run(20, 20)  # 转弯后当前方距离大于25cm时前进
    time.sleep(0.6)
    spin_left(25, 25)
    time.sleep(0.5)  # 转弯后前方距离小于25cm时向左原地转弯90度
    run(10, 10)  # 转弯后当前方距离大于25cm时前进
    time.sleep(1.5)
    spin_left(32, 32)
    time.sleep(0.4)  # 转弯后前方距离小于25cm时向左原地转弯90度
    run(20, 20)  # 转弯后当前方距离大于25cm时前进
    time.sleep(0.6)
    while True:
        run(20, 20)
        TrackSensorLeftValue1 = GPIO.input(TrackSensorLeftPin1)
        TrackSensorLeftValue2 = GPIO.input(TrackSensorLeftPin2)
        TrackSensorRightValue1 = GPIO.input(TrackSensorRightPin1)
        TrackSensorRightValue2 = GPIO.input(TrackSensorRightPin2)
        if TrackSensorLeftValue2 == False or TrackSensorRightValue1 == False:
            spin_right(30, 30)
            time.sleep(0.1)
            print("break")
            return

#------------------------检测颜色--------------------------------------

def color_recognizer():
    cap = cv2.VideoCapture(-1) # 打开摄像头
    cap.set(3, 640)
    cap.set(4, 480) # 设置窗口的大小
    color_string = ""
    stable_color_count = 0
    stable_color = ""

    while cap.isOpened():
        flag, frame = cap.read()
        if not flag:
            print("无法读取摄像头！")
            cap.release()
            cv2.destroyAllWindows()
            return "none"
        elif frame is not None:
            kernel = np.ones((35, 35), np.uint8)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            Open = cv2.morphologyEx(hsv, cv2.MORPH_OPEN, kernel)  # 以上为图像处理
            hist = cv2.calcHist([Open], [0], None, [180], [0, 180])  # 对Open图像的H通道进行直方图统计
            hist_max = np.where(hist == np.max(hist))  # 找到直方图hist中列方向最大的点hist_max
            print(hist_max[0])

            if 100 < hist_max[0] < 124:  # H在100~124为蓝色
                color_string = "blue"
            elif 35 < hist_max[0] < 77:  # H在35~77为绿色
                color_string = "green"
            elif 15 <= hist_max[0] <= 35:  # H在15~35为黄色
                color_string = "yellow"
            elif 124 <= hist_max[0] <= 150:  # H在50~75为紫色
                color_string = "purple"
            else:  # H不在前两者之间跳出函数
                color_string = "none"

            # 显示摄像头画面
            cv2.imshow("Color Recognition", frame)

            # 如果检测到颜色,等待3秒后输出颜色
            if color_string != "none":
                if color_string == stable_color:
                    stable_color_count += 1
                else:
                    stable_color_count = 0
                    stable_color = color_string

                if stable_color_count >= 30:  # 连续检测到30帧相同的颜色
                    print("识别到的颜色:", stable_color)
                    cap.release()
                    cv2.destroyAllWindows()
                    return stable_color

            # 按下 'q' 退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                return "none"

#--------------------------小程序输入颜色---------------------------------

def run_udp_server(host='0.0.0.0', port=45678):
    """
    运行UDP服务器，接收到一个消息后停止监听并返回该消息字符串。
    :param host: 监听的主机地址
    :param port: 监听的端口号
    :return: 返回接收到的消息字符串
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        server_socket.bind((host, port))
        print(f"UDP 服务器正在监听 {host}:{port}")

        data, addr = server_socket.recvfrom(1024)
        message = data.decode()
        print(f"接收到来自 {addr} 的数据: {message}")

        return message

#-----------------------语音播报---------------------------------------

def bobao(text):
    engine = pyttsx3.init() #初始化语音引擎
    engine.setProperty('rate',120) #设置语速
    engine.setProperty('volume',10.0) #设置音量
    engine.setProperty('voice','zh') #设置语言
    engine.setProperty('per','2')
    voices=engine.getProperty('voices')
    engine.say(text)
    engine.runAndWait()
    engine.stop()

#------------------  -----拍照----------------------------------------

def photo(root):
    # 初始化摄像头
    cap = cv2.VideoCapture(-1)

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

#------------------------传照片至电脑-----------------------------------

def faceserver():
    # 创建套接字并监听
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 6666))
    server_socket.listen(1)

    print("等待客户端连接...")
    client, addr = server_socket.accept()
    print(f"客户端 {addr} 已连接")

    # 接收图片数据
    print("开始接收图片数据...")
    image_data = b''
    while True:
        data = client.recv(1024)
        if not data:
            break
        image_data += data

    # 保存图片数据到文件
    image_filename = f"received_image_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
    with open(image_filename, "wb") as f:
        f.write(image_data)
    print(f"图片 {image_filename} 保存完成")

    # 关闭连接
    client.close()
    server_socket.close()

#------------------------微信公众号------------------------------------

def get_access_token():
    # 获取access token的url
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}' \
        .format(appID1, appSecret1)
    response = requests.get(url).json()
    print(response)
    access_token = response.get('access_token')
    return access_token

def send_msg2(access_token):        #送达
    # touser 就是 openID
    # template_id 就是模板ID
    # url 就是点击模板跳转的url
    # data就按这种格式写，time和text就是之前{{time.DATA}}中的那个time，先试试你就知道了，value就是你要替换DATA的值
    for id in openId1:
        body = {
        "touser": openId1,
        "template_id": "c3BP0RJMOj-0aKhgiVwj7YYgSteJ5dro4idm2pPEeo8",
        "url": "http://weixin.qq.com/download",

    }
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(access_token)
    print(requests.post(url, json.dumps(body)).text)

def send_msg1(access_token):            #出发
    # touser 就是 openID
    # template_id 就是模板ID
    # url 就是点击模板跳转的url
    # data就按这种格式写，time和text就是之前{{time.DATA}}中的那个time，先试试你就知道了，value就是你要替换DATA的值
    for id in openId1:
        body = {
        "touser": openId1,
        "template_id": "bBL7WuVr0f71160ZaqiZZ0qJi-M__pDeSwTeQnZoZXc",
        "url": "http://weixin.qq.com/download",

    }
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(access_token)
    print(requests.post(url, json.dumps(body)).text)

#------------------------语音输入--------------------------------------

client = AipSpeech(APP_ID2, API_KEY2, SECRET_KEY2)

def audio_to_text():
    # 定义录音命令和参数
    command = ['arecord', '--device=plughw:2,0', '--format', 'S16_LE', '--rate',
               '16000', '-C', '1', '-d', '5', '/home/pi/111/1']  # 修正了格式字符串，移除了中间的空格
    options = {'dev_pid': 1536}  # 移除了不必要的'lm id'选项
    audio_file = '/home/pi/111/1'  # 确保路径与录音命令中的路径一致

    # 调用录音命令
    print("开始录音...")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    print("录音结束。")

    # 检查录音文件是否存在
    if not os.path.exists(audio_file):
        print(f"找不到文件: {audio_file}")
        return None

    # 打开音频文件并读取数据
    with wave.open(audio_file, 'rb') as wf:
        FORMAT = 'wav'  # 直接设置为'wav'
        rate = wf.getframerate()
        audio_data = wf.readframes(wf.getnframes())

    # 调用百度API进行语音识别
    # result = client.asr(audio_data, FORMAT, rate, options)
    # if 'err_no' not in result or result['err_no'] != 0:
    # pass
    # else:
    # return result['result'][0]
    result = client.asr(audio_data, 'wav', rate, options)
    if 'err_no' in result and result['err_no'] == 0:
        return result['result'][0]
    else:
        print(f"语音识别错误: {result.get('err_msg', '未知错误')}")
        return None

#------------------------文心------------------------------------------

def get_access_token_wenxin():
    auth_url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {
        'grant_type': 'client_credentials',
        'client_id': API_KEY3,
        'client_secret': SECRET_KEY3
    }
    response = requests.get(auth_url, params=params)
    print(f"Request URL: {response.url}")  # 打印请求的URL以便检查
    if response.status_code == 200:
        token_info = response.json()
        if "access_token" in token_info:
            return token_info["access_token"]
        else:
            raise Exception(f"Failed to obtain access token: {token_info}")
    else:
        raise Exception(f"Failed to obtain access token. Status code: {response.status_code}, Response: {response.text}")

def call_wenxin_api(prompt, access_token):
    url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-tiny-8k?access_token={access_token}"
    payload = {
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "appid": APP_ID3  # 添加AppID到请求中
    }
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(f"Request Headers: {headers}")  # 打印请求头以便检查
    print(f"Request Payload: {payload}")  # 打印请求数据以便检查

    if response.status_code == 200:
        result = response.json()
        if "result" in result:
            return result["result"]
        else:
            raise Exception(f"Unexpected response format: {result}")
    else:
        raise Exception(f"API request failed with status code: {response.status_code}, Response: {response.text}")

def ai(prompt):
    try:
        access_token_wenxin = get_access_token_wenxin()
        result = call_wenxin_api(prompt, access_token_wenxin)
        print(result)
        return result
    except Exception as e:
        print("Error:", e)

#------------------------二维码识别-------------------------------------

def qr_code_recognition():
    # 开启摄像头
    cap = cv2.VideoCapture(-1)
    while True:
        # 读取摄像头画面
        _, frame = cap.read()
        # 识别二维码
        barcodes = pyzbar.decode(frame)
        # 遍历识别到的二维码
        for barcode in barcodes:
            # 提取二维码数据
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
            # 在画面中绘制二维码位置
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # 在画面中显示二维码类型和数据
            text = "{} ({})".format(barcodeData, barcodeType)
            cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (36, 255, 12), 2)
            # 打印识别到的二维码信息
            print("Barcode: {} ({})".format(barcodeData, barcodeType))
            # 释放摄像头资源,关闭窗口
            cap.release()
            cv2.destroyAllWindows()
            return barcodeData
        # 显示摄像头画面
        cv2.imshow("QR Code Recognition", frame)
        # 按下 'q' 退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # 释放摄像头资源,关闭窗口
    cap.release()
    cv2.destroyAllWindows()
    return None  # 如果没有识别到二维码,返回 None

def get_QRdata(QRdata):
    global name, sex, color, num
    # 使用 split() 方法将字符串分割成列表
    qr_code_data = QRdata.split()
    # 将列表中的元素分别赋值给四个变量
    name = qr_code_data[0]
    sex = qr_code_data[1]
    color = qr_code_data[2]
    num = qr_code_data[3]
    # 输出变量值
    print("Name:", name)
    print("Sex:", sex)
    print("Color:", color)
    print("Num:", num)

def get_access_token_qr():
    # 获取access token的url

    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}' \
        .format(appID1, appSecret1)
    response = requests.get(url).json()
    print(response)
    access_token = response.get('access_token')
    return access_token


def send_msg(access_token,QRdata):
    get_QRdata(QRdata)
    # touser 就是 openID
    # template_id 就是模板ID
    # url 就是点击模板跳转的url
    # data就按这种格式写，time和text就是之前{{time.DATA}}中的那个time，先试试你就知道了，value就是你要替换DATA的值

    for id in openId1:
        body = {
            "touser": openId1,
            "template_id": "qXOkbp7Zx173hBCvkrFzFBRE5coGS2bHXth0CMZuoQ0",
            "url": "http://weixin.qq.com/download",
            "data":{
                    "first": {
                        "value": "病人已顺利取到药物！=）",
                        "color": "#173177"
                    },
                    "keyword1": {
                        "value": name,
                        "color": "#173177"
                    },
                    "keyword2": {
                        "value": sex,
                        "color": "#173177"
                    },
                    "keyword3": {
                        "value": color,
                        "color": "#173177"
                    },
                    "keyword4": {
                        "value": num,
                        "color": "#173177"
                    }
            }
        }
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}'.format(access_token)
    print(requests.post(url, json.dumps(body)).text)


#------------------------main()---------------------------------------

name = ''
sex = ''
color = ''
num = ''
init()
received_message = run_udp_server()
if(received_message == "blue" or received_message == "green" or received_message == "yellow"):
    bobao("出发咯")
    # 1.获取access_token
    access_token = get_access_token()
    # 2.发送模板消息
    send_msg1(access_token)
    run(20,20)
    time.sleep(0.8)
    spin_right(35,35)
    time.sleep(0.4)
    run(20,20)
    time.sleep(1.0)
    search_line(received_message)


