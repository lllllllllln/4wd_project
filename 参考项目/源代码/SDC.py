# -*- coding:UTF-8 -*-
import RPi.GPIO as GPIO
import time
import heapq
import threading
import cv2
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from aip import AipFace
import base64
import datetime


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

class Node:
    def __init__(self, position, parent=None):
        self.position = position  # 格子的坐标，如(0, 0)
        self.parent = parent  # 父节点
        self.g = 0  # 从起点到该节点的移动代价
        self.h = 0  # 启发式代价（从该节点到终点的估计代价）
        self.f = 0  # 总代价（g + h）

    def __lt__(self, other):
        return self.f < other.f

def heuristic(a, b):
    # 使用曼哈顿距离作为启发式函数
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(grid, start, end):
    open_list = []
    closed_list = set()
    start_node = Node(start)
    end_node = Node(end)
    
    heapq.heappush(open_list, start_node)
    
    while open_list:
        current_node = heapq.heappop(open_list)
        closed_list.add(current_node.position)
        
        # 找到终点，返回路径
        if current_node.position == end_node.position:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]  # 反转路径
        
        # 获取邻居节点
        neighbors = [
            (0, -1), (-1, 0), (0, 1), (1, 0)
        ]
        for dx, dy in neighbors:
            neighbor_pos = (current_node.position[0] + dx, current_node.position[1] + dy)
            if 0 <= neighbor_pos[0] < len(grid) and 0 <= neighbor_pos[1] < len(grid[0]):
                if neighbor_pos in closed_list or grid[neighbor_pos[0]][neighbor_pos[1]] == 'X':
                    continue
                neighbor_node = Node(neighbor_pos, current_node)
                neighbor_node.g = current_node.g + 1
                neighbor_node.h = heuristic(neighbor_pos, end_node.position)
                neighbor_node.f = neighbor_node.g + neighbor_node.h
                
                if not any(node.position == neighbor_node.position and node.g <= neighbor_node.g for node in open_list):
                    heapq.heappush(open_list, neighbor_node)
    
    return None  # 未找到路径

# 定义5x5方格，'X'表示障碍物
grid = [
    ['A', 'A', 'X', 'X', 'A'],
    ['A', 'A', 'A', 'A', 'A'],
    ['X', 'A', 'A', 'A', 'A'],
    ['A', 'A', 'X', 'X', 'A'],
    ['A', 'A', 'A', 'X', 'A']
]

def grid_to_string(grid):
    result = ""
    for row in grid:
        result += ' '.join(row) + '\n'
    return result


# 获取用户输入的起点和终点
def get_input(prompt):
    while True:
        try:
            value = input(prompt).strip().upper()
            if len(value) == 2 and value[0] in "ABCDE" and value[1] in "12345":
                row = ord(value[0]) - ord('A')
                col = int(value[1]) - 1
                if grid[row][col] != 'X':
                    return (row, col)
                else:
                    print("位置是障碍物，请选择其他位置。")
            else:
                print("输入无效。请使用格式如A1、B2等。")
        except Exception as e:
            print(f"输入错误: {e}")

def format_path(path):
    formatted_path = []
    for pos in path:
        row_char = chr(pos[0] + ord('A'))
        col_char = str(pos[1] + 1)
        formatted_path.append(f"{row_char}{col_char}")
    return formatted_path

def init():
    global pwm_ENA, pwm_ENB, pwm_servo
    GPIO.setup(ENA, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(IN1, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(IN2, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(ENB, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(IN3, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(IN4, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(key, GPIO.IN)
    GPIO.setup(EchoPin, GPIO.IN)
    GPIO.setup(TrigPin, GPIO.OUT)
    GPIO.setup(LED_R, GPIO.OUT)
    GPIO.setup(LED_G, GPIO.OUT)
    GPIO.setup(LED_B, GPIO.OUT)
    GPIO.setup(ServoPin, GPIO.OUT)
    GPIO.setup(TrackSensorLeftPin1, GPIO.IN)
    GPIO.setup(TrackSensorLeftPin2, GPIO.IN)
    GPIO.setup(TrackSensorRightPin1, GPIO.IN)
    GPIO.setup(TrackSensorRightPin2, GPIO.IN)
    GPIO.setup(BuzzerPin, GPIO.OUT)
    # 设置pwm引脚和频率为2000hz
    pwm_ENA = GPIO.PWM(ENA, 2000)
    pwm_ENB = GPIO.PWM(ENB, 2000)
    pwm_ENA.start(0)
    pwm_ENB.start(0)
    # 设置舵机的频率和起始占空比
    pwm_servo = GPIO.PWM(ServoPin, 50)
    pwm_servo.start(0)

# 小车前进
def run(leftspeed, rightspeed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(leftspeed)
    pwm_ENB.ChangeDutyCycle(rightspeed)
    # 设置前进时的LED灯颜色为绿色
    GPIO.output(LED_R, GPIO.LOW)
    GPIO.output(LED_G, GPIO.HIGH)
    GPIO.output(LED_B, GPIO.LOW)

# 小车后退
def back(leftspeed, rightspeed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_ENA.ChangeDutyCycle(leftspeed)
    pwm_ENB.ChangeDutyCycle(rightspeed)
    # 设置后退时的LED灯颜色为绿色
    GPIO.output(LED_R, GPIO.LOW)
    GPIO.output(LED_G, GPIO.HIGH)
    GPIO.output(LED_B, GPIO.LOW)

# 小车左转
def left(leftspeed, rightspeed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(leftspeed)
    pwm_ENB.ChangeDutyCycle(rightspeed)
    # 设置左转时的LED灯颜色为蓝色
    GPIO.output(LED_R, GPIO.LOW)
    GPIO.output(LED_G, GPIO.LOW)
    GPIO.output(LED_B, GPIO.HIGH)

# 小车右转
def right(leftspeed, rightspeed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(leftspeed)
    pwm_ENB.ChangeDutyCycle(rightspeed)
    # 设置右转时的LED灯颜色为蓝色
    GPIO.output(LED_R, GPIO.LOW)
    GPIO.output(LED_G, GPIO.LOW)
    GPIO.output(LED_B, GPIO.HIGH)

# 小车原地左转
def spin_left(leftspeed, rightspeed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(leftspeed)
    pwm_ENB.ChangeDutyCycle(rightspeed)
    # 设置原地左转时的LED灯颜色为红色
    GPIO.output(LED_R, GPIO.HIGH)
    GPIO.output(LED_G, GPIO.LOW)
    GPIO.output(LED_B, GPIO.LOW)

# 小车原地右转
def spin_right(leftspeed, rightspeed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_ENA.ChangeDutyCycle(leftspeed)
    pwm_ENB.ChangeDutyCycle(rightspeed)
    # 设置原地右转时的LED灯颜色为红色
    GPIO.output(LED_R, GPIO.HIGH)
    GPIO.output(LED_G, GPIO.LOW)
    GPIO.output(LED_B, GPIO.LOW)

# 小车停止
def brake():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    # 设置停止时的LED灯颜色熄灭
    GPIO.output(LED_R, GPIO.LOW)
    GPIO.output(LED_G, GPIO.LOW)
    GPIO.output(LED_B, GPIO.LOW)

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

# 判断是否在节点上
def track_node_check():
    TrackSensorLeftValue1 = GPIO.input(TrackSensorLeftPin1)
    TrackSensorLeftValue2 = GPIO.input(TrackSensorLeftPin2)
    TrackSensorRightValue1 = GPIO.input(TrackSensorRightPin1)
    TrackSensorRightValue2 = GPIO.input(TrackSensorRightPin2)
    return TrackSensorLeftValue1 == False and TrackSensorLeftValue2 == False and TrackSensorRightValue1 == False and TrackSensorRightValue2 == False

# 判断是否在节点上
def is_at_node():
    return track_node_check()

# 超声波测距函数
def Distance():
    GPIO.output(TrigPin, GPIO.LOW)
    time.sleep(0.000002)
    GPIO.output(TrigPin, GPIO.HIGH)
    time.sleep(0.000015)
    GPIO.output(TrigPin, GPIO.LOW)

    t3 = time.time()
    while not GPIO.input(EchoPin):
        t4 = time.time()
        if (t4 - t3) > 0.10:
            return -1

    t1 = time.time()
    while GPIO.input(EchoPin):
        t5 = time.time()
        if (t5 - t1) > 0.10:
            return -1

    t2 = time.time()
    time.sleep(0.01)
    return ((t2 - t1) * 340 / 2) * 100

def Distance_test():
    num = 0
    ultrasonic = []
    while num < 4:
        distance = Distance()
        while int(distance) == -1:
            distance = Distance()
        while int(distance) >= 500 or int(distance) == 0:
            distance = Distance()
        ultrasonic.append(distance)
        num += 1
        time.sleep(0.01)
    distance = (ultrasonic[1] + ultrasonic[2] + ultrasonic[3]) / 3
    #print("distance is %f"%(distance))
    return distance

# 超声波避障
def avoid_obstacle():
    while True:
        global obstacle_detected
        distance = Distance_test()
        if distance < 20:  # 检测到24厘米以内的障碍物
            obstacle_detected = True
        else:
            obstacle_detected = False

def color_recongnition():
    global color_is_red
    # 初始化摄像头
    cap = cv2.VideoCapture(1)  # 1表示第一个摄像头设备

    min_area=1500
    max_area=5000

    while True:
        # 读取当前帧
        ret, frame = cap.read()
        # 如果不能读取帧，退出循环
        if not ret:
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

    # 释放摄像头并关闭所有窗口
    cap.release()
    cv2.destroyAllWindows()

def SMAsending():
    # 创建邮件对象
    msg = MIMEMultipart()
    msg['From'] = '2265339886@qq.com'
    msg['To'] = '2265339886@qq.com'
    msg['Subject'] = '未知障碍！地图已更新。'
    str = grid_to_string(grid)

    # 邮件正文内容
    body = str
    msg.attach(MIMEText(body, 'plain'))

    # SMTP服务器设置
    server = smtplib.SMTP_SSL('smtp.qq.com', 465)  # 使用SSL
    server.login('2265339886@qq.com', 'dpcmosfzkrzlecdf')  # 登录认证

    # 发送邮件
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

# 循迹返回函数
def run_track_back():
    while not track_node_check():
        # 检测到黑线时循迹模块相应的指示灯亮，端口电平为LOW
        # 未检测到黑线时循迹模块相应的指示灯灭，端口电平为HIGH
        TrackSensorLeftValue1 = GPIO.input(TrackSensorLeftPin1)
        TrackSensorLeftValue2 = GPIO.input(TrackSensorLeftPin2)
        TrackSensorRightValue1 = GPIO.input(TrackSensorRightPin1)
        TrackSensorRightValue2 = GPIO.input(TrackSensorRightPin2)
        
        # 四路循迹引脚电平状态
        # X 0 1 X
        # 处理左小弯
        if TrackSensorLeftValue2 == False and TrackSensorRightValue1 == True or TrackSensorLeftValue1 ==False:
            left(0, 80)
        
        # 四路循迹引脚电平状态
        # X 1 0 X  
        # 处理右小弯
        elif TrackSensorLeftValue2 == True and TrackSensorRightValue1 == False or TrackSensorRightValue2 == False:
            right(100, 0)

        # 四路循迹引脚电平状态
        # X 0 0 X
        # 处理直线
        elif TrackSensorLeftValue2 == False and TrackSensorRightValue1 == False:
            run(20,20)
        
        else:
            spin_left(8,8)

# 循迹函数
def run_track():
    global obstacle_detected
    global color_is_red
    global current_orientation 
    run(20,20)
    time.sleep(0.2)
    
    while not track_node_check():
        if obstacle_detected == True:
            print("检测到障碍物，停止并重新规划路径")
            brake()
            time.sleep(1)
            return False
        
        # 判断红绿灯  
        if color_is_red:  
            print("红灯，等待...")
            brake()  
            time.sleep(1)
            while color_is_red:  # 等待直到红灯变为绿灯  
                time.sleep(0.1)  # 短暂休眠以避免过度占用CPU  
            print("绿灯，前进")

        # 检测到黑线时循迹模块相应的指示灯亮，端口电平为LOW
        # 未检测到黑线时循迹模块相应的指示灯灭，端口电平为HIGH
        TrackSensorLeftValue1 = GPIO.input(TrackSensorLeftPin1)
        TrackSensorLeftValue2 = GPIO.input(TrackSensorLeftPin2)
        TrackSensorRightValue1 = GPIO.input(TrackSensorRightPin1)
        TrackSensorRightValue2 = GPIO.input(TrackSensorRightPin2)
        
        # 四路循迹引脚电平状态
        # X 0 1 X
        # 处理左小弯
        if TrackSensorLeftValue2 == False and TrackSensorRightValue1 == True or TrackSensorLeftValue1 ==False:
            left(0, 80)

        # 四路循迹引脚电平状态
        # X 1 0 X  
        # 处理右小弯
        elif TrackSensorLeftValue2 == True and TrackSensorRightValue1 == False or TrackSensorRightValue2 == False:
            right(100, 0)

        # 四路循迹引脚电平状态
        # X 0 0 X
        # 处理直线
        elif TrackSensorLeftValue2 == False and TrackSensorRightValue1 == False:
            run(20,20)
        
        else:
            spin_left(5,5)
        
    return True

     # 根据当前朝向确定小车的左右转向
def update_orientation(next_orientation):
    global current_orientation
    if current_orientation == 1:
        if next_orientation == 2:
            spin_left(18,18)  # 后转
            time.sleep(1.2)
        elif next_orientation == 3:
            spin_left(15,15)  # 左转
            time.sleep(0.5)
        elif next_orientation == 4:
            spin_right(15,15)   # 右转
            time.sleep(0.8)
    elif current_orientation == 2:
        if next_orientation == 1:
            spin_left(18,18)  # 后转
            time.sleep(1.3)
        elif next_orientation == 3:
            spin_right(15,15)  # 左转
            time.sleep(0.8)
        elif next_orientation == 4:
            spin_left(15,15)   # 右转
            time.sleep(0.5)
    elif current_orientation == 3:
        if next_orientation == 1:
            spin_right(15,15)  # 右转
            time.sleep(0.80)
        elif next_orientation == 2:
            spin_left(15,15)  # 左转
            time.sleep(0.5)
        elif next_orientation == 4:
            spin_left(18,18)   # 后转
            time.sleep(1.2)
    elif current_orientation == 4:
        if next_orientation == 1:
            spin_left(15,15)  # 左转
            time.sleep(0.50)
        elif next_orientation == 2:
            spin_right(15,15)  # 右转
            time.sleep(0.8)
        elif next_orientation == 3:
            spin_left(18,18)   # 后转
            time.sleep(1.2)

# 移动到下一个位置
def move_to_next_position(current_pos, next_pos):
    global current_orientation
    global obstacle_detected
    # 确定下一个朝向
    if next_pos[0] == current_pos[0] - 1:  # 上
        next_orientation = 1
    elif next_pos[0] == current_pos[0] + 1:  # 下
        next_orientation = 2
    elif next_pos[1] == current_pos[1] - 1:  # 左
        next_orientation = 3
    elif next_pos[1] == current_pos[1] + 1:  # 右
        next_orientation = 4
    else:
        print("未找到路径")

    # 更新小车朝向
    update_orientation(next_orientation)
    current_orientation = next_orientation
    t = current_orientation

    # 移动小车到下一个节点
    if not run_track():
        if t == 1:
            t = 2
        elif t == 2:
            t = 1
        elif t == 3:
            t = 4
        elif t == 4:
            t = 3
        current_orientation=t
        spin_left(20,20)   # 后转
        time.sleep(1.2)
        run_track_back()
        brake()  # 再次到达节点后停止并等待一秒
        time.sleep(1)
        return False

    brake()  # 再次到达节点后停止并等待一秒
    time.sleep(1)
    return True

# 跟随路径移动
def follow_path(path):
    global current_orientation
    for i in range(len(path) - 1):
        if not move_to_next_position(path[i], path[i + 1]):
            grid[path[i+1][0]][path[i+1][1]] = 'X'
            SMAsending()
            return path[i]
    return 

# 主控制函数
def main_control():
    global current_orientation
    init()  # 初始化GPIO设置
    print("欢迎使用智能小车控制系统！")
    if not is_at_node():
        print("不在节点上")
        return
    obstacle_thread = threading.Thread(target=avoid_obstacle)
    obstacle_thread.start()
    color_thread = threading.Thread(target=color_recongnition)
    color_thread.start()
    print("请选择起点和终点：")
    start = get_input("请输入起点位置：")
    end = get_input("请输入终点位置：")

    while True:
        print(f"起点位置：{chr(start[0] + ord('A'))}{start[1] + 1}")
        print(f"终点位置：{chr(end[0] + ord('A'))}{end[1] + 1}")
        path = astar(grid, start, end)
        if path:
            print("找到路径：", format_path(path))
            obstacle_position = follow_path(path)
            if obstacle_position:
                # 更新路径
                path = astar(grid, obstacle_position, end)
                if not path:
                    print("无法找到绕过障碍物的路径")
                    start = obstacle_position
                    end = get_input("请输入下一终点位置：")
                else:
                    print("重新规划路径：")
                    start = obstacle_position
                    continue
            else:
                brake()  # 到达终点后停止
                GPIO.output(BuzzerPin,GPIO.LOW)
                time.sleep(2)
                GPIO.output(BuzzerPin,GPIO.HIGH)
                start = end
                end = get_input("请输入下一终点位置：")
        else:
            print("未找到路径。")
    obstacle_thread.join()
    color_thread.join()
    
#人脸识别函数（调用主控制函数)
def face_recongnition():
    # 百度人脸识别API账号信息
    APP_ID = '90547753'
    API_KEY = 'WC190nFO8pHioR23HW2YaFWV'
    SECRET_KEY = 'x34bIkirrA9ozfqHdNiU6OWImIy1W7fl'
    client = AipFace(APP_ID, API_KEY, SECRET_KEY)  # 创建一个客户端用以访问百度云

    # 图像编码方式
    IMAGE_TYPE = 'BASE64'

    # 用户组
    GROUP = '4_17'

    # 用户映射
    user_map = {
        'hjh': 'laohe',
    }

    # 对图片的格式进行转换
    def transimage(frame):
        _, buffer = cv2.imencode('.jpg', frame)
        img = base64.b64encode(buffer)
        return img
    
    # 上传到百度API进行人脸检测
    def go_api(image):
        result = client.search(str(image, 'utf-8'), IMAGE_TYPE, GROUP)  # 在百度云人脸库中寻找有没有匹配的人脸
        if result['error_msg'] == 'SUCCESS':  # 如果成功了
            user_list = result['result']['user_list'][0]
            user_id = user_list['user_id']
            score = user_list['score']
            if score > 30:  # 如果相似度大于30
                name = user_map.get(user_id, 'Unknow')
                print('相似度为：%.2f' % score)
                print("欢迎%s!" % name)
                log_access(name)
                return name, score
            else:
                print('相似度为：%.2f' % score)
                print("抱歉，识别失败！请重试！")
                return None, score
        elif result['error_msg'] == 'pic not has face':
            print('检测不到人脸')
            return None, 0
        else:
            print(f"Error {result['error_code']}: {result['error_msg']}")
            return None, 0

    # 记录访问日志
    def log_access(name):
        curren_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('ming_dan.txt', 'a') as f:
            f.write(f"姓名: {name}   时间: {curren_time}\n")

    # 实时读取和显示
    cap = cv2.VideoCapture(1)  # 初始化摄像头
    if not cap.isOpened():
        print("无法打开摄像头")
        return

    while True:
        ret, frame = cap.read()  # 读取一帧
        if not ret:
            print("无法获取图像")
            break
        
        img = transimage(frame)  # 转换照片格式
        name, score = go_api(img)  # 将转换了格式的图片上传到百度云

        if name:
            print("人脸识别成功！")
            cap.release()
            cv2.destroyAllWindows()
            main_control()
            break
        
        time.sleep(1)  # 增加1秒延时，降低请求频率


# 主程序入口
if __name__ == '__main__':
    try:
        face_recongnition()
    except KeyboardInterrupt:
        pass
    finally:
        pwm_ENA.stop()
        pwm_ENB.stop()
        pwm_servo.stop()
        GPIO.cleanup