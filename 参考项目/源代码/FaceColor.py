# -*- coding:UTF-8 -*-

# 导入人脸识别API
import cv2
from aip import AipFace
import base64
import time
import RPi.GPIO as GPIO
import numpy as np



# 定义人脸识别常量
APP_ID ="90624719"
API_KEY ="ry49KuGupDUHtie1YpaW2CUS "
SECRET_KEY ="ZwA1twWNpPJhUQesm2IeidqoOIOpXAQA"
imageType = "BASE64"
groupIdList = "admin"   #人脸组


filePath="qgy.jpg"#照片路径

# 小车电机引脚定义
IN1 = 20
IN2 = 21
IN3 = 19
IN4 = 26
ENA = 16

ENB = 13

# 小车按键定义
key = 8

x=1

# 超声波引脚定义
EchoPin = 0
TrigPin = 1

# RGB三色灯引脚定义
LED_R = 22
LED_G = 27
LED_B = 24

# 舵机引脚定义
ServoPin = 23

# 循迹红外引脚定义
# TrackSensorLeftPin1 TrackSensorLeftPin2 TrackSensorRightPin1 TrackSensorRightPin2
#      3                 5                  4                   18
# 定义左边第一个循迹红外传感器引脚为3口
TrackSensorLeftPin1 = 3
# 定义左边第二个循迹红外传感器引脚为5口
TrackSensorLeftPin2 = 5
# 定义右边第一个循迹红外传感器引脚为4口
TrackSensorRightPin1 = 4
# 定义右边第二个循迹红外传感器引脚为18口
TrackSensorRightPin2 = 18

# 设置GPIO口为BCM编码方式
GPIO.setmode(GPIO.BCM)

# 忽略警告信息
GPIO.setwarnings(False)
# 电机引脚初始化为输出模式
# 按键引脚初始化为输入模式
# 寻迹引脚初始化为输入模式
# 超声波，RGB三色灯，舵机引脚初始化为输入模式

def init():
    global pwm_ENA
    global pwm_ENB
    global pwm_servo
    GPIO.setup(ENA, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(IN1, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(IN2, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(ENB, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(IN3, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(IN4, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(key, GPIO.IN)
    GPIO.setup(TrackSensorLeftPin1, GPIO.IN)
    GPIO.setup(TrackSensorLeftPin2, GPIO.IN)
    GPIO.setup(TrackSensorRightPin1, GPIO.IN)
    GPIO.setup(TrackSensorRightPin2, GPIO.IN)
    GPIO.setup(EchoPin, GPIO.IN)
    GPIO.setup(TrigPin, GPIO.OUT)
    GPIO.setup(LED_R, GPIO.OUT)
    GPIO.setup(LED_G, GPIO.OUT)
    GPIO.setup(LED_B, GPIO.OUT)
    GPIO.setup(ServoPin, GPIO.OUT)
    # 设置pwm引脚和频率为2000hz
    pwm_ENA = GPIO.PWM(ENA, 2000)
    pwm_ENB = GPIO.PWM(ENB, 2000)
    pwm_ENA.start(0)
    pwm_ENB.start(0)
    # 设置舵机的频率和起始占空比
    pwm_servo = GPIO.PWM(ServoPin, 50)
    pwm_servo.start(0)
#根据转动的角度来点亮相应的颜色
def corlor_light(pos):
    if pos > 150:
        GPIO.output(LED_R, GPIO.HIGH)
        GPIO.output(LED_G, GPIO.LOW)
        GPIO.output(LED_B, GPIO.LOW)
    elif pos > 125:
        GPIO.output(LED_R, GPIO.LOW)
        GPIO.output(LED_G, GPIO.HIGH)
        GPIO.output(LED_B, GPIO.LOW)
    elif pos >100:
        GPIO.output(LED_R, GPIO.LOW)
        GPIO.output(LED_G, GPIO.LOW)
        GPIO.output(LED_B, GPIO.HIGH)
    elif pos > 75:
        GPIO.output(LED_R, GPIO.HIGH)
        GPIO.output(LED_G, GPIO.HIGH)
        GPIO.output(LED_B, GPIO.LOW)
    elif pos > 50:
        GPIO.output(LED_R, GPIO.LOW)
        GPIO.output(LED_G, GPIO.HIGH)
        GPIO.output(LED_B, GPIO.HIGH)
    elif pos > 25:
        GPIO.output(LED_R, GPIO.HIGH)
        GPIO.output(LED_G, GPIO.LOW)
        GPIO.output(LED_B, GPIO.HIGH)
    elif pos > 0:
        GPIO.output(LED_R, GPIO.HIGH)
        GPIO.output(LED_G, GPIO.HIGH)
        GPIO.output(LED_B, GPIO.HIGH)
    else :
        GPIO.output(LED_R, GPIO.LOW)
        GPIO.output(LED_G, GPIO.LOW)
        GPIO.output(LED_B, GPIO.LOW)
            
#舵机来回转动
def servo_control_color():
    for pos in range(181):
        pwm_servo.ChangeDutyCycle(2.5 + 10 * pos/180)
        corlor_light(pos)
        time.sleep(0.009) 
    for pos in reversed(range(181)):
        pwm_servo.ChangeDutyCycle(2.5 + 10 * pos/180)
        corlor_light(pos)
        time.sleep(0.009)


# 小车前进
def run(leftspeed, rightspeed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(leftspeed)
    pwm_ENB.ChangeDutyCycle(rightspeed)


# 小车后退
def back(leftspeed, rightspeed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_ENA.ChangeDutyCycle(leftspeed)
    pwm_ENB.ChangeDutyCycle(rightspeed)


# 小车左转
def left(leftspeed, rightspeed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(leftspeed)
    pwm_ENB.ChangeDutyCycle(rightspeed)


# 小车右转
def right(leftspeed, rightspeed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(leftspeed)
    pwm_ENB.ChangeDutyCycle(rightspeed)


# 小车原地左转
def spin_left(leftspeed, rightspeed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(leftspeed)
    pwm_ENB.ChangeDutyCycle(rightspeed)


# 小车原地右转
def spin_right(leftspeed, rightspeed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_ENA.ChangeDutyCycle(leftspeed)
    pwm_ENB.ChangeDutyCycle(rightspeed)


# 小车停止
def brake():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)


# 按键检测
def key_scan():
    while GPIO.input(key):
        pass
    while not GPIO.input(key):
        time.sleep(0.01)
        if not GPIO.input(key):
            time.sleep(0.01)
            while not GPIO.input(key):
                pass

def color_detection(image_path):
    # 读取图像
    image = cv2.imread(image_path)

    # 将图像转换为HSV颜色空间
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 定义红色色块的颜色范围
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])

    # 创建红色色块的掩膜
    red_mask = cv2.inRange(hsv_image, lower_red, upper_red)


    # 执行形态学操作去除噪声
    kernel = np.ones((5, 5), np.uint8)
    red_mask = cv2.erode(red_mask, kernel, iterations=1)
    red_mask = cv2.dilate(red_mask, kernel, iterations=1)

    # 寻找红色色块的轮廓
    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 遍历红色色块的轮廓并绘制边界框和中心点
    for contour in red_contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2)
        M = cv2.moments(contour)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        cv2.circle(image, (cX, cY), 5, (0, 0, 255), -1)
        color="red"


    # 返回结果图像
    if "color" in locals():
        return image,color
    else:
        return image,"null"

# 超声波函数检测距离
def Distance_test():
    GPIO.output(TrigPin, GPIO.HIGH)
    time.sleep(0.000015)
    GPIO.output(TrigPin, GPIO.LOW)
    while not GPIO.input(EchoPin):
        pass
    t1 = time.time()
    while GPIO.input(EchoPin):
        pass
    t2 = time.time()
    print
    "distance is %d " % (((t2 - t1) * 340 / 2) * 100)
    time.sleep(0.01)
    return ((t2 - t1) * 340 / 2) * 100


# 舵机旋转到指定角度
def servo_appointed_detection(pos):
    for i in range(18):
        pwm_servo.ChangeDutyCycle(2.5 + 10 * pos / 180)


# 舵机旋转超声波测距避障，led根据车的状态显示相应的颜色
def servo_color_carstate():
        # 障碍物在正前方,亮品红色,向右转
    GPIO.output(LED_R, GPIO.HIGH)
    GPIO.output(LED_G, GPIO.LOW)
    GPIO.output(LED_B, GPIO.HIGH)

    # 实现向左半圆形型绕弯
    left(0, 40)
    time.sleep(0.5)
    run(20, 20)
    time.sleep(0.2)
    brake()
    # LED灯亮蓝色
    GPIO.output(LED_R, GPIO.LOW)
    GPIO.output(LED_G, GPIO.LOW)
    GPIO.output(LED_B, GPIO.HIGH)
    right(40, 0)
    time.sleep(0.9)
    run(20, 20)
    time.sleep(0.05)





global is_run
is_run=False
global is_face
is_face=False

# 主函数
try:
    init()
    key_scan()

    cap = cv2.VideoCapture(1)

    while True and is_face==False:
        print("check_face")

        # 初始化AipFace对象
        client = AipFace(APP_ID, API_KEY, SECRET_KEY)
        flag, frame = cap.read()  # 获取摄像头截取到的图片
        cv2.imshow("camera", frame)
        cv2.waitKey(1)
        cv2.imwrite(filePath, frame)
        f = open(filePath, "rb")
        data = base64.b64encode(f.read())
        f.close()
        image = str(data, "UTF-8")
        time.sleep(0.05)
        result = client.search(image, imageType, groupIdList)

        if result["error_msg"] in "SUCCESS":
            score = result["result"]["user_list"][0]["score"]
            user_id = result["result"]["user_list"][0]["user_id"]
            if score > 80:
                print(user_id, ":验证成功")
                is_face=True
                
                break;
            else:
                print("没有找到此人")
        else:
            print("error:", result["error_msg"])
    # 关闭摄像头：
    cap.release()
    # 关闭窗口：
    cv2.destroyAllWindows()

    time.sleep(4)

    camera = cv2.VideoCapture(1)
    time.sleep(1)
    while True and is_run == False:
        distance = Distance_test()
        print(distance)
        if distance < 20:
            camera.release()
            time.sleep(0.01)
            camera = cv2.VideoCapture(1)
            ret, frame = camera.read()
            camera.release()
            cv2.imwrite("temp.jpg", frame)
            result_image, col = color_detection('temp.jpg')
            print(col)

            if col != 'red':
                brake()
                time.sleep(1)
                servo_color_carstate()
                
            else:
                brake()
                time.sleep(5)


        #检测到黑线时循迹模块相应的指示灯亮，端口电平为LOW
        #未检测到黑线时循迹模块相应的指示灯灭，端口电平为HIGH
        TrackSensorLeftValue1  = GPIO.input(TrackSensorLeftPin1)
        TrackSensorLeftValue2  = GPIO.input(TrackSensorLeftPin2)
        TrackSensorRightValue1 = GPIO.input(TrackSensorRightPin1)
        TrackSensorRightValue2 = GPIO.input(TrackSensorRightPin2)

        #四路循迹引脚电平状态
        # 0 0 X 0
        # 1 0 X 0
        # 0 1 X 0
        #以上6种电平状态时小车原地右转
        #处理右锐角和右直角的转动
        if (TrackSensorLeftValue1 == False or TrackSensorLeftValue2 == False) and  TrackSensorRightValue2 == False:
            spin_right(10, 10)
            time.sleep(0.8)
 
        #四路循迹引脚电平状态
        # 0 X 0 0       
        # 0 X 0 1 
        # 0 X 1 0       
        #处理左锐角和左直角的转动
        elif TrackSensorLeftValue1 == False and (TrackSensorRightValue1 == False or  TrackSensorRightValue2 == False):
            spin_left(10, 10)
            time.sleep(0.8)
  
        # 0 X X X
        #最左边检测到
        elif TrackSensorLeftValue1 == False:
            spin_left(20, 20)
     
        # X X X 0
        #最右边检测到
        elif TrackSensorRightValue2 == False:
            spin_right(20, 20)
   
        #四路循迹引脚电平状态
        # X 0 1 X
        #处理左小弯
        elif TrackSensorLeftValue2 == False and TrackSensorRightValue1 == True:
            left(0,20)
   
        #四路循迹引脚电平状态
        # X 1 0 X  
        #处理右小弯
        elif TrackSensorLeftValue2 == True and TrackSensorRightValue1 == False:
            right(20, 0)
   
        #四路循迹引脚电平状态
        # X 0 0 X
        #处理直线
        elif TrackSensorLeftValue2 == False and TrackSensorRightValue1 == False:
            run(10, 10)
   
        #当为1 1 1 1时小车保持上一个小车运行状态
except KeyboardInterrupt:
    print('wrong')
pass

# 程序运行结束
pwm_ENA.stop()
pwm_ENB.stop()
pwm_servo.stop()
GPIO.cleanup()

