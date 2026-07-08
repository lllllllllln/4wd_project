#-*- coding:UTF-8 -*-
#邮件发送相关库
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

#物体识别相关库
import json
from aip import AipImageClassify
import requests
import base64
import cv2

#小车硬件库
import RPi.GPIO as GPIO
import time

# 二维码识别部分
import enum
import cv2
import threading
import time
import numpy as np
import pyzbar.pyzbar as pyzbar
from PIL import Image
import ipywidgets.widgets as widgets
from IPython.core.display import display

#-------------------------A*规划部分----------------------------------
# 初始化网格迷宫（矩阵 值为1表示可达、值为-1表示不可达）
def maze_build(maze):
    [a, b] = list(map(int, input().split()))  # a为行,b为列
    for i in range(a):  # 输入0、1矩阵
        maze.append([int(j) for j in input().split()])


# A*搜索问题部分

import math

# mazw 迷宫 对应的是一个矩阵
# 使用0表示迷宫有通路
# 使用1表示迷宫有障碍物
maze = []
a = 6  # 矩阵长度
b = 6

# 矩阵宽度


# 将整个矩阵初始化为0
def initmaze(maze):
    # a=int(input("x of target:"))
    # b=int(input("y of target:"))
    for i in range(0, a):
        maze.append(b * [0])
    pass


def barrier(listx):
    print("请输入障碍的坐标，以负值结束输入")
    while 1:
        barx = int(input("请输入障碍的x坐标（从0开始）:"))
        bary = int(input("请输入障碍的y坐标:"))
        if barx >= 0 and bary >= 0:
            listx[barx][bary] = 1
        else:  # 输入负数结束输入
            break
    pass


# 启发函数中的最优函数的计算
def get_h(now_node, end_node):
    return math.sqrt(pow((end_node.x - now_node.x), 2) + pow((end_node.y - now_node.y), 2))


def path_out(s_node, G, beg_node):  # 从终点开始
    global trackx   #节点的x坐标列表
    global tracky   #节点的y坐标列表
    trackx = []
    tracky = []
    # 打印结点情况是倒序输出的
    print("path", end=":")
    for item in G:
        if item.x == s_node.x and item.y == s_node.y:
            item.p_out()
            # 实现列表的倒转
            while True:
                trackx.append(item.x)
                tracky.append(item.y)
                if item.x == beg_node.x and item.y == beg_node.y:
                    break
                item.x = item.pre.x
                item.y = item.pre.y
                item = item.pre
    trackx = trackx[::-1]
    tracky = tracky[::-1]


count = 0


# A*搜索方法
def A_star():
    global count
    # global endx
    # global endx
    global currsite
    if (count == 0):
        # A*搜索问题的初始化
        initmaze(maze)  # 初始化，得5x5矩阵
        # barrier(maze)  # 初始化，矩阵中加入障碍物
        #maze[1][1]=maze[1][3]=maze[4][0]=maze[3][2]=maze[2][4]=1#初始默认的障碍物的情况
        #maze[1][0]=maze[2][3]=maze[3][1]=maze[4][0]=1#初始默认的障碍物的情况 测试
        beg_node=node(0,0,None)#初始默认起点
        count = count + 1
    else: # 新添加障碍物
        # xx = int(input("中间过程请输入障碍的x坐标（从0开始）:"))
        # if (xx >= 0):
        #     yy = int(input("请输入障碍的y坐标:"))
        #     maze[xx][yy] = 1
        beg_node = node(currsite[0], currsite[1], None)  # 初始默认起点
    print(maze)

    # beg_node = node(int(input("请输入起点的x坐标:")), int(input("请输入起点的y坐标:")), None)
    # beg_node=node(0,0,None)
    beg_node.father = beg_node
    # end_node = node(int(input("请输入终点的x坐标:")), int(input("请输入终点的y坐标:")), None)
    end_node = node(endx, endy, None)

    beg_node.h = get_h(beg_node, end_node)
    beg_node.get_f()  # 初始化开始节点，赋f值
    open = [beg_node]  # open表
    close = []  # close表

    class search_node:
        def __init__(self, in_x, in_y, in_pre):
            self.x = in_x
            self.y = in_y
            self.pre = in_pre

        # 寻找结点的时候 使用的是倒序输出
        def p_out(self):
            print("<-(%d,%d)" % (self.x, self.y), end="")
            if self.pre != None:
                self.pre.p_out()
            else:
                print("\n")
            pass

    G = [search_node(beg_node.x, beg_node.y, None)]  # 搜索过的点
    M = []  # 产生的新节点集合
    # open表的处理
    while len(open) != 0:
        min_f = open[0].f
        min_node = open[0]

        print("-----new-------cycle-----\nopen:")
        for item in open:
            item.n_out()
        print("finish open")  # 打印open表

        for item in open:  # 选择open表中代价最小的结点
            if item.f < min_f:
                min_f = item.f
                min_node = item

        print("find min_node:", end=" ")  # 寻找f最小的节点并打印
        min_node.n_out()
        # 从open表中取出f最小的结点（也是表中第一个结点）
        open.remove(min_node)
        close.append(min_node)  # 从open表中选择的结点已经经过了扩展放在closed表中
        min_s_node = search_node(min_node.x, min_node.y, None)  # 用于寻找的类表示当前结点是待扩展的结点 存放的结点的前序结点

        if min_node.x == end_node.x and min_node.y == end_node.y:
            path_out(min_s_node, G, beg_node)  # 找到目标节点，输出路径
            return
        # 扩展结点M的寻找
        if min_node.x - 1 >= 0 and maze[min_node.x - 1][min_node.y] == 0:  # 上节点 注意当前的迷宫maze使用0表示有通路 使用1表示有障碍物
            new_node = node(min_node.x - 1, min_node.y, min_node)  # 父节点是当前的min_node
            new_node.g = min_node.g + 1  # 实际代价的更新
            new_node.h = get_h(new_node, end_node)  # 计算结点的期望代价
            new_node.get_f()  # 计算结点的估计代价
            if not (new_node.x == min_node.father.x and new_node.y == min_node.father.y):  # 子节点不与父节点相同
                M.append(new_node)
        if min_node.y - 1 >= 0 and maze[min_node.x][min_node.y - 1] == 0:  # 左节点
            new_node = node(min_node.x, min_node.y - 1, min_node)
            new_node.g = min_node.g + 1
            new_node.h = get_h(new_node, end_node)
            new_node.get_f()
            if not (new_node.x == min_node.father.x and new_node.y == min_node.father.y):
                M.append(new_node)
        if min_node.x + 1 <= a - 1 and maze[min_node.x + 1][min_node.y] == 0:  # 下节点 位置上受到的是矩阵边界的限制
            new_node = node(min_node.x + 1, min_node.y, min_node)
            new_node.g = min_node.g + 1
            new_node.h = get_h(new_node, end_node)
            new_node.get_f()
            if not (new_node.x == min_node.father.x and new_node.y == min_node.father.y):
                M.append(new_node)
        if min_node.y + 1 <= b - 1 and maze[min_node.x][min_node.y + 1] == 0:  # 右节点
            new_node = node(min_node.x, min_node.y + 1, min_node)
            new_node.g = min_node.g + 1
            new_node.h = get_h(new_node, end_node)
            new_node.get_f()
            if not (new_node.x == min_node.father.x and new_node.y == min_node.father.y):
                M.append(new_node)

        print("M:")  # 打印M表 对当前产生的扩展结点进行打印
        for item in M:
            item.n_out()
        print("finish M")
        # 对于未扩展结点的open表 插入新的结点需要按照估价函数值f的大小 寻找确定的位置进行插入
        for index, item in enumerate(M):
            find = False
            for g_index, g_item in enumerate(G):  # 对M中每个元素，在G中查找 将新扩展的结点和已经搜索过的点进行比较
                if g_item.x == item.x and g_item.y == item.y:
                    find = True
                    if min_node.g + 1 < item.g:
                        g_item.pre = min_s_node
                        item.g = min_node.g + 1
                        item.get_f()  # 找到:比较f值，取较小者
            if not find:
                open.append(item)  # 未找到：入open表
                for g_index, g_item in enumerate(G):
                    if g_item.x == min_s_node.x and g_item.y == min_s_node.y:
                        new_search_node = search_node(item.x, item.y, g_item)  # 生成路径点
                        G.append(new_search_node)

        print("G:")  # 打印G表
        for item in G:
            print("(%d,%d)" % (item.x, item.y))
        print("finish G")

        M.clear()
    print("找不到路径！")
    return

#-------------------------A*节点定义----------------------------------
class node:
    def __init__(self, in_x, in_y, in_father):
        self.x = in_x
        self.y = in_y
        self.g = 0
        self.h = 0.0
        self.f = self.g + self.h  # 初始化时候的启发函数值
        self.father = in_father

    def get_f(self):
        self.f = self.g + self.h  # 计算节点f值

    def n_out(self):
        print("(%d,%d),f=%f" % (self.x, self.y, self.f))  # 打印节点属性
        return
    

#-------------------------循迹与节点判断部分----------------------------------
# 小车电机引脚定义
IN1 = 20
IN2 = 21
IN3 = 19
IN4 = 26
ENA = 16
ENB = 13
# 循迹红外引脚定义
# TrackSensorLeftPin1 TrackSensorLeftPin2 TrackSensorRightPin1 TrackSensorRightPin2
#      3                 5                  4                   18
TrackSensorLeftPin1 = 3  # 定义左边第一个循迹红外传感器引脚为3口
TrackSensorLeftPin2 = 5  # 定义左边第二个循迹红外传感器引脚为5口
TrackSensorRightPin1 = 4  # 定义右边第一个循迹红外传感器引脚为4口
TrackSensorRightPin2 = 18  # 定义右边第二个循迹红外传感器引脚为18口

# 超声波引脚定义
EchoPin = 0
TrigPin = 1

# RGB三色灯引脚定义
LED_R = 22
LED_G = 27
LED_B = 24

# 舵机引脚定义
ServoPin = 23

# 小车按键定义
key = 8

# 红外避障引脚定义
AvoidSensorLeft = 12
AvoidSensorRight = 17

# 设置GPIO口为BCM编码方式
GPIO.setmode(GPIO.BCM)

# 忽略警告信息
GPIO.setwarnings(False)

# 初始化部分
# 电机引脚初始化为输出模式
# 按键引脚初始化为输入模式
# 寻迹引脚初始化为输入模式
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
    GPIO.setup(key, GPIO.IN)#按键
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
    GPIO.setup(AvoidSensorLeft, GPIO.IN)
    GPIO.setup(AvoidSensorRight, GPIO.IN)
    # 设置pwm引脚和频率为2000hz
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
    # time.sleep(t_filter)
    pwm_ENA.ChangeDutyCycle(leftspeed*n)
    # time.sleep(t_filter)
    pwm_ENB.ChangeDutyCycle(rightspeed*n)
    # time.sleep(t_filter)
    # time.sleep(t_forward)


# 小车后退
def back(leftspeed, rightspeed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_ENA.ChangeDutyCycle(leftspeed*n)
    pwm_ENB.ChangeDutyCycle(rightspeed*n)
    time.sleep(t_back)

# 小车原地左转
def spin_left(leftspeed, rightspeed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    time.sleep(t_filter)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(leftspeed*n)
    pwm_ENB.ChangeDutyCycle(rightspeed*n)
    # time.sleep(t_filter)
    # time.sleep(t_zhijiao)

# 小车原地右转
def spin_right(leftspeed, rightspeed):
    #右侧反转
    #
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    time.sleep(t_filter)#加入时间 参考按键代码 实现滤波
    #因为 小车速度比较慢的时候 电平占空比比较低 对应的干扰更多 有效信号更少 导致无处的情况更容易
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle((leftspeed+20)*n)
    pwm_ENB.ChangeDutyCycle((rightspeed)*n)#右轮力气小 减少电平高度
    # time.sleep(t_filter)
    # time.sleep(t_zhijiao)

# 小车停止
def brake(tt):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    time.sleep(tt)


# 小车左转
def left(leftspeed, rightspeed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(leftspeed*n)
    pwm_ENB.ChangeDutyCycle(rightspeed*n)
    # time.sleep(t_xiaowan)


# 小车右转
def right(leftspeed, rightspeed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(leftspeed*n)
    pwm_ENB.ChangeDutyCycle(rightspeed*n)
    # time.sleep(t_xiaowan)


# 超声波函数
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
    time.sleep(0.01)
    return ((t2 - t1) * 340 / 2) * 100


# 舵机旋转到指定角度
def servo_appointed_detection(pos):
    for i in range(18):
        pwm_servo.ChangeDutyCycle(2.5 + 10 * pos / 180)


# 进入到地图之后的小车自主找节点与循迹
car_head=1#默认状态下小车朝向下
vector_head=1#目标方向向量朝向
car_degree=0#表示小车转向的角度
march_times=0
def march():
    global car_degree
    global car_head
    global trackn
    global march_times
    global trackx
    global tracky
    forthflag=True#;默认状态下 节点向前 但是寻找节点后退之后 后面的对准转为后退
    currstate=False#记录小车当前在通路False还是节点True上 避免出现小车经过节点数量的判断i出现过分累加的情况 初始情况在起点上
    i=0
    iscomplete=True
    while True:
        #到达终点
        if i==trackn:
            brake(5)
            print("end")
            return iscomplete
        # 检测到黑线时循迹模块相应的指示灯亮，端口电平为LOW
        # 未检测到黑线时循迹模块相应的指示灯灭，端口电平为HIGH
        TrackSensorLeftValue1 = GPIO.input(TrackSensorLeftPin1)
        TrackSensorLeftValue2 = GPIO.input(TrackSensorLeftPin2)
        TrackSensorRightValue1 = GPIO.input(TrackSensorRightPin1)
        TrackSensorRightValue2 = GPIO.input(TrackSensorRightPin2)
        #判断当前位置是否是节点
        #节点位置引脚电平
        # 0 0 0 x
        # x 0 0 0
        #当前位置是节点
        # brake(0.001)
        if (TrackSensorLeftValue2==False and TrackSensorRightValue1==False and(TrackSensorRightValue2==False or TrackSensorLeftValue1==False) and not currstate) \
                or march_times==0:
            march_times+=1
            brake(0.001)
            print("当前是%d个节点"%(i))
            currstate=True#小车当前在节点上
            print("当前位置：(%d,%d)"%(currsite[0],currsite[1]))
            if i==trackn-1:#当前已经到达终点
                return iscomplete
            #在节点判断下一个节点的相对位置
            #障碍物检测 应该修改为多线程情况
            isbarrier=servo_color_carstate()
            if isbarrier:#存在障碍物
                iscomplete=False
                return iscomplete
            #在节点判断下一个节点的相对位置
            #前方
            try:
                if trackx[i+1]==currsite[0]+1 and tracky[i+1]==currsite[1]:
                    vector_head=1#目标方向朝下
                    car_degree=(car_head-vector_head)*90
                #后方
                elif trackx[i+1]==currsite[0]-1 and tracky[i+1]==currsite[1]:
                    vector_head = 3  # 目标方向朝上
                    car_degree = (car_head - vector_head) * 90

                #右侧
                elif trackx[i+1]==currsite[0] and tracky[i+1]==currsite[1]-1:
                    vector_head = 4  # 目标方向朝左
                    car_degree = (car_head - vector_head) * 90

                #左侧
                elif trackx[i+1]==currsite[0] and tracky[i+1]==currsite[1]+1:
                    vector_head = 2  # 目标方向朝右
                    car_degree = (car_head - vector_head) * 90

                car_head = vector_head # 更新当前小车方向
                #车辆转向
                if car_degree==90:
                    #右直角
                    right_zhijjiao()
                    print("节点向右")
                elif car_degree==-90:
                    # 左直角
                    spin_left(85, 85)
                    time.sleep(t_zhijiao)
                    print("节点向左")
                elif car_degree==0:
                    run(100, 100)
                    print("节点向前")
                elif car_degree==-180 or car_degree==180:
                    mydiaotou()
                    print("节点向后")
            except:
                pass
            #补充 原版还提供了一种锐角的情况
            i = i + 1  # 节点数量更新 当前到达新的节点
            print(i)
            print(trackn)
            # 更新当前坐标
            currsite[0]=trackx[i]
            currsite[1]=tracky[i]
        else:#寻迹行走
            currstate=False#小车当前在通路上
            # 四路循迹引脚电平状态
            # 0 0 X 0
            # 1 0 X 0
            # 0 1 X 0
            # 以上6种电平状态时小车原地右转
            # 处理右锐角和右直角的转动
            if (TrackSensorLeftValue1 == False or TrackSensorLeftValue2 == False) and TrackSensorRightValue2 == False:
                spin_right(100, 100)
                # print("右直角")
                time.sleep(0.08)

            # 四路循迹引脚电平状态
            # 0 X 0 0
            # 0 X 0 1
            # 0 X 1 0
            # 处理左锐角和左直角的转动
            elif TrackSensorLeftValue1 == False and (
                    TrackSensorRightValue1 == False or TrackSensorRightValue2 == False):
                spin_left(100, 100)
                # print("左直角")
                time.sleep(0.08)

            # 0 X X X
            # 最左边检测到
            elif TrackSensorLeftValue1 == False:
                spin_left(80, 80)
                # print("左80调节")

            # X X X 0
            # 最右边检测到
            elif TrackSensorRightValue2 == False:
                spin_right(80, 80)
                # print("右80调节")

            # 四路循迹引脚电平状态
            # X 0 1 X
            # 处理左小弯
            elif TrackSensorLeftValue2 == False and TrackSensorRightValue1 == True:
                left(0, 90)
                # print("左小弯")

            # 四路循迹引脚电平状态
            # X 1 0 X
            # 处理右小弯
            elif TrackSensorLeftValue2 == True and TrackSensorRightValue1 == False:
                right(90, 0)
                # print("右小弯")

            # 四路循迹引脚电平状态
            # X 0 0 X
            # 处理直线
            elif TrackSensorLeftValue2 == False and TrackSensorRightValue1 == False:
                if forthflag==False:
                    back(100,100)
                elif forthflag==True:
                    run(100, 100)
            #其他情况下 保持动作
# 舵机旋转超声波测距避障，led根据车的状态显示相应的颜色
def servo_color_carstate():
    isbarrier=False
    # 开红灯
    GPIO.output(LED_R, GPIO.HIGH)
    GPIO.output(LED_G, GPIO.LOW)
    GPIO.output(LED_B, GPIO.LOW)
    # back(20, 20)
    # time.sleep(0.08)
    brake(t_brake)

    # 舵机旋转到0度，即右侧，测距
    servo_appointed_detection(0)
    time.sleep(0.8)
    rightdistance = Distance_test()

    # 舵机旋转到180度，即左侧，测距
    servo_appointed_detection(180)
    time.sleep(0.8)
    leftdistance = Distance_test()

    # 舵机旋转到90度，即前方，测距
    servo_appointed_detection(90)
    time.sleep(0.8)
    frontdistance = Distance_test()
    print("左侧距离%d" %(leftdistance))
    print("右侧距离%d" % (rightdistance))
    print("前方距离%d" % (frontdistance))
    barrier_head=-1#默认不存在障碍物
    # if leftdistance < 30 and rightdistance < 30 and frontdistance < 30:
    # 对于小车来说 小车的左侧 前方和右侧方向角的损失分别是1 0 -1
    if(leftdistance < n_barrier_dis and rightdistance < n_barrier_dis and frontdistance < n_barrier_dis):
        barrier_head = 10
    elif(leftdistance < n_barrier_dis and frontdistance < n_barrier_dis):
        barrier_head = 11
    elif(rightdistance < n_barrier_dis and frontdistance < n_barrier_dis):
        barrier_head = 12
    elif rightdistance < n_barrier_dis and leftdistance < n_barrier_dis :
        barrier_head = 13
    elif leftdistance < n_barrier_dis :
        # 亮品红色
        GPIO.output(LED_R, GPIO.HIGH)
        GPIO.output(LED_G, GPIO.LOW)
        GPIO.output(LED_B, GPIO.HIGH)
        barrier_head=car_head+1#

        # spin_right(85, 85)
        # time.sleep(0.58)
    # elif leftdistance >= rightdistance:
    elif rightdistance < n_barrier_dis :
        # 亮蓝色
        GPIO.output(LED_R, GPIO.LOW)
        GPIO.output(LED_G, GPIO.LOW)
        GPIO.output(LED_B, GPIO.HIGH)
        barrier_head=car_head-1
        # spin_left(85, 85)
        # time.sleep(0.28)
    elif frontdistance<n_barrier_dis:
        # 亮品红色，向右转
        GPIO.output(LED_R, GPIO.HIGH)
        GPIO.output(LED_G, GPIO.LOW)
        GPIO.output(LED_B, GPIO.HIGH)
        barrier_head=car_head+0
        # spin_right(85, 85)
        # time.sleep(0.28)
    #障碍物的判断
    if barrier_head==1:
        #障碍物的方向是当前位置朝下x+1
        if maze[currsite[0]+1][currsite[1]]==1:
            isbarrier=False
            pass
        else:
            maze[currsite[0]+1][currsite[1]]=1
            isbarrier=True
            print("当前位置的下方存在障碍物")
    elif barrier_head==2:
        #障碍物的方向是当前位置朝右y+1
        if maze[currsite[0]][currsite[1]+1]==1:
            isbarrier=False
            pass
        else:
            maze[currsite[0]][currsite[1]+1]=1
            isbarrier=True
            print("当前位置的右方存在障碍物")
    elif barrier_head==3:
        #障碍物的方向是当前位置朝上x-1
        if maze[currsite[0]-1][currsite[1]]==1:
            isbarrier=False
            pass
        else:
            maze[currsite[0]-1][currsite[1]]=1
            isbarrier=True
            print("当前位置的上方存在障碍物")
    elif barrier_head==4:
        #障碍物的方向是当前位置朝左y+1
        if maze[currsite[0]][currsite[1]-1]==1:
            isbarrier=False
            pass
        else:
            maze[currsite[0]][currsite[1]-1]=1
            isbarrier=True
            print("当前位置的左方存在障碍物")
    if car_head == 1:
        
        if barrier_head == 10:
            if  maze[currsite[0]+1][currsite[1]]==1 and maze[currsite[0]][currsite[1]+1] == 1 and maze[currsite[0]][currsite[1]-1] == 1:
                isbarrier=False
                pass
            else:
                maze[currsite[0]+1][currsite[1]] = 1
                maze[currsite[0]][currsite[1]+1] = 1
                maze[currsite[0]][currsite[1]-1] = 1
                isbarrier=True
        elif barrier_head == 11:
            if  maze[currsite[0]][currsite[1]+1]==1 and maze[currsite[0]+1][currsite[1]] == 1:
                isbarrier=False
                pass
            else:
                maze[currsite[0] ][currsite[1]+1] = 1
                maze[currsite[0] + 1][currsite[1]] = 1
                isbarrier=True
        elif barrier_head == 12:
            if  maze[currsite[0]+1][currsite[1]]==1 and maze[currsite[0]][currsite[1]-1] == 1:
                isbarrier=False
                pass
            else: 
                maze[currsite[0] + 1][currsite[1]] = 1
                maze[currsite[0]][currsite[1]-1] = 1
                isbarrier=True
        elif barrier_head == 13:
            if  maze[currsite[0]][currsite[1]+1]==1 and maze[currsite[0]][currsite[1]-1] == 1:
                isbarrier=False
                pass
            else:
                maze[currsite[0]][currsite[1]+1] = 1
                maze[currsite[0]][currsite[1]-1] = 1
                isbarrier=True
    elif car_head == 2:
        if barrier_head == 10:
            if  maze[currsite[0]-1][currsite[1]]==1 and maze[currsite[0]+1][currsite[1]] == 1 and  maze[currsite[0]][currsite[1]+1] == 1:
                isbarrier=False
                pass
            else:
                maze[currsite[0] - 1][currsite[1]] = 1
                maze[currsite[0] + 1][currsite[1]] = 1
                maze[currsite[0]][currsite[1]+1] = 1
                isbarrier=True
        elif barrier_head == 11:
            if  maze[currsite[0]-1][currsite[1]]==1 and  maze[currsite[0]][currsite[1]+1] == 1:
                isbarrier=False
                pass
            else:
                maze[currsite[0] - 1][currsite[1]] = 1
                maze[currsite[0]][currsite[1]+1] = 1
                isbarrier=True
        elif barrier_head == 12:
            if  maze[currsite[0]][currsite[1]+1]==1 and  maze[currsite[0]+1][currsite[1]] == 1:
                isbarrier=False
                pass
            else:
                maze[currsite[0]][currsite[1]+1] = 1
                maze[currsite[0] + 1][currsite[1]] = 1
                isbarrier=True
        elif barrier_head == 13:
            if  maze[currsite[0]-1][currsite[1]]==1 and  maze[currsite[0]+1][currsite[1]] == 1:
                isbarrier=False
                pass
            else:
                maze[currsite[0] - 1][currsite[1]] = 1
                maze[currsite[0] + 1][currsite[1]] = 1
                isbarrier=True
    elif car_head == 3:
        if barrier_head == 10:
            if  maze[currsite[0]][currsite[1]+1]==1 and  maze[currsite[0]][currsite[1]-1] == 1 and maze[currsite[0] - 1][currsite[1]] == 1:
                isbarrier=False
                pass
            else:
                maze[currsite[0]][currsite[1]+1] = 1
                maze[currsite[0]][currsite[1]-1] = 1
                maze[currsite[0] - 1][currsite[1]] = 1
                isbarrier=True
        elif barrier_head == 11:
            if  maze[currsite[0]-1][currsite[1]]==1 and  maze[currsite[0]][currsite[1]-1] == 1:
                isbarrier=False
                pass
            else:
                maze[currsite[0] - 1][currsite[1]] = 1
                maze[currsite[0]][currsite[1]-1] = 1
                isbarrier=True
        elif barrier_head == 12:
            if  maze[currsite[0]-1][currsite[1]]==1 and  maze[currsite[0]][currsite[1]+1] == 1:
                isbarrier=False
                pass
            else:
                maze[currsite[0] - 1][currsite[1]] = 1
                maze[currsite[0]][currsite[1]+1] = 1
                isbarrier=True
        elif barrier_head == 13:
            if  maze[currsite[0]][currsite[1]-1]==1 and  maze[currsite[0]][currsite[1]+1] == 1:
                isbarrier=False
                pass
            else:
                maze[currsite[0]][currsite[1]-1] = 1
                maze[currsite[0]][currsite[1]+1] = 1
                isbarrier=True
    elif car_head == 4:
        if barrier_head == 10:
            if  maze[currsite[0]-1][currsite[1]]==1 and  maze[currsite[0]+1][currsite[1]] == 1 and maze[currsite[0]][currsite[1]-1] == 1:
                isbarrier=False
                pass
            else:
                maze[currsite[0] - 1][currsite[1]] = 1
                maze[currsite[0] + 1][currsite[1]] = 1
                maze[currsite[0]][currsite[1]-1] = 1
                isbarrier=True
        elif barrier_head == 11:
            if  maze[currsite[0]][currsite[1]-1]==1 and  maze[currsite[0]+1][currsite[1]] == 1:
                isbarrier=False
                pass
            else:
                maze[currsite[0]][currsite[1]-1] = 1
                maze[currsite[0] + 1][currsite[1]] = 1
                isbarrier=True
        elif barrier_head == 12:
            if  maze[currsite[0]][currsite[1]-1]==1 and  maze[currsite[0]-1][currsite[1]] == 1:
                isbarrier=False
                pass
            else:
                maze[currsite[0]][currsite[1]-1] = 1
                maze[currsite[0] - 1][currsite[1]] = 1
                isbarrier=True
        elif barrier_head == 13:
            if  maze[currsite[0]-1][currsite[1]]==1 and  maze[currsite[0]+1][currsite[1]] == 1:
                isbarrier=False
                pass
            else:
                maze[currsite[0] - 1][currsite[1]] = 1
                maze[currsite[0] + 1][currsite[1]] = 1
                isbarrier=True
    return isbarrier
# 右直角转动
def right_zhijjiao():
    run(100, 100)
    time.sleep(0.10)
    print("向前")
    brake(0.5)
    print("暂停")
    spin_right(82, 82)
    time.sleep(t_zhijiao+0.20)
    print("节点向右")
    brake(0.001)
    run(100,100)
    time.sleep(0.05)

# 小车掉头函数
def mydiaotou():
    run(100, 100)
    time.sleep(0.1)
    brake(0.5)
    spin_left(85, 85)
    time.sleep(t_diaotou)
    brake(0.001)


#---------------------------------------------------------------------
trackx = []
# global tracky
tracky = []
trackn=0#最短路径中结点的数量
# 小车轨迹的终点是确定的
# global endx
# global endy
endx = 0
endy = 0
t_xiaowan=0.2
t_forward=0.1
# t_zhijiao=0.28#标准
t_zhijiao=0.5
t_diaotou=1.3
t_back=0.1
t_brake=0.5
t_match=0.08
t_filter=0.005
n=0.25
n_t_zhijiao=0.5
n_barrier_dis=30+4
currsite=[]

# 目标点存储
global str_point
str_point = None
#---------------------------------------------------------------------


#------------------------opncv二维码识别部分----------------------------
#bgr8转jpeg格式

def bgr8_to_jpeg(value, quality=75):
    return bytes(cv2.imencode('.jpg', value)[1])

image_widget = widgets.Image(format='jpeg', width=320, height=240)
display(image_widget)                                      #显示摄像头组件

# 二维码解码函数
def decodeDisplay(image):
    print("请展示目的地信息二维码")
    global str_point
    global FLAG
    barcodes = pyzbar.decode(image)
    for barcode in barcodes:
        # 提取二维码的边界框的位置
        # 画出图像中条形码的边界框
        (x, y, w, h) = barcode.rect
        cv2.rectangle(image, (x, y), (x + w, y + h), (225, 225, 225), 2)

        # 提取二维码数据为字节对象，所以如果我们想在输出图像上
        # 画出来，就需要先将它转换成字符串
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type

        # 绘出图像上条形码的数据和条形码类型
        text = "{} ({})".format(barcodeData, barcodeType)
        cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,0.5, (225, 225, 225), 2)

        # 向终端打印条形码数据和条形码类型
        print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
        
        # 以','为分界得到目标点存储于列表中
        str_point = barcodeData.split(',')
        FLAG = False
        #print(sp)
        return image
    return image

# 二维码识别调度函数
def detect():
    # FLAG为二维码识别完成标志
    global FLAG
    camera = cv2.VideoCapture(1)
    #print("1")
    camera.set(3, 320)
    camera.set(4, 240)
    camera.set(5, 120)  #设置帧率
    # fourcc = cv2.VideoWriter_fourcc(*"MPEG")
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
    camera.set(cv2.CAP_PROP_BRIGHTNESS, 40) #设置亮度 -64 - 64  0.0
    camera.set(cv2.CAP_PROP_CONTRAST, 50) #设置对比度 -64 - 64  2.0
    camera.set(cv2.CAP_PROP_EXPOSURE, 156) #设置曝光值 1.0 - 5000  156.0
    ret, frame = camera.read()
    image_widget.value = bgr8_to_jpeg(frame)
    while True:
        # 读取当前帧
        ret, frame = camera.read()
        cv2.imshow("camera", frame)
        # 转为灰度图像
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        im= decodeDisplay(gray)

        cv2.waitKey(5)
        image_widget.value = bgr8_to_jpeg(im)
        # 如果按键q则跳出本次循环
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
        if(FLAG == False):
            break
        #print(FLAG)
    camera.release()
    cv2.destroyAllWindows()

#按键检测
def key_scan():
    while GPIO.input(key):
        pass
    while not GPIO.input(key):
        time.sleep(0.01)
        if not GPIO.input(key):
            time.sleep(0.01)
            while not GPIO.input(key):
                pass

global FLAG
FLAG = True


#------------------------邮件发送部分-------------------------------
# 发送邮件函数
def send_email():
    #html格式的邮件正文
    content = '''
    <body>
    <p>您好，已找到你要达到的目的地!</p>
    <p>情况照片：</p>
    <p><img src="cid:testimage" alt="testimage"></p>
    </body>
    '''
    email.attach(MIMEText(content,'html','utf-8'))
    #读取图片
    fp = open('testimage.jpg', 'rb')  #打开文件
    msgImage = MIMEImage(fp.read()) #读入 msgImage 中
    fp.close() #关闭文件
    #定义图片 ID，在 HTML 文本中引用
    msgImage.add_header('Content-ID', 'testimage')
    email.attach(msgImage)
    # 建立与SMTP服务器的连接
    server = smtplib.SMTP('smtp.qq.com',25)  # 以Gmail为例，如果使用其他邮件服务提供商，请相应地更改服务器和端口号
    server.ehlo()
    # 开启安全连接
    server.starttls()
    server.ehlo
    # 登录到您的邮箱账户
    server.login(sender_email, sender_passcode)
    # 发送邮件
    server.sendmail(sender_email, receiver_email, email.as_string())
    # 关闭连接
    server.close()
    print('邮件发送成功！')


# 获取图片并且保存
def get_img():
    camera = cv2.VideoCapture(1)
    print("已经获取图片")
    camera.set(3, 320)
    camera.set(4, 240)
    camera.set(5, 120)  #设置帧率
    # fourcc = cv2.VideoWriter_fourcc(*"MPEG")
    camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
    camera.set(cv2.CAP_PROP_BRIGHTNESS, 40) #设置亮度 -64 - 64  0.0
    camera.set(cv2.CAP_PROP_CONTRAST, 50) #设置对比度 -64 - 64  2.0
    camera.set(cv2.CAP_PROP_EXPOSURE, 156) #设置曝光值 1.0 - 5000  156.0
    ret, frame = camera.read() # 摄像头读取信息
    cv2.imwrite("testimage.jpg",frame) # 将图片保存下来
    camera.release()

# 物体识别函数-调用识别以及邮件发送函数
def img_test():
    global SEND_FLAG
    # 需要识别的本地图片
    path = r"testimage.jpg"
    # 显示图片
    p = cv2.imread(path)
    cv2.imshow("pic_test",p)
    # 使用SDK包识别
    pic_sb(path)
    # 使用token识别
    ans = pic_sb1(path)
    # 输出识别结果
    print("最终识别结果：")
    print(ans)
    if(ans == "包装盒" or ans == "纸箱"):
        SEND_FLAG = True # 邮件可以发送
        send_email()
    else:
        print("快递识别失败，请重新放置照片")

    # 一直显示图片
    #cv2.waitKey()
    #cv2.destroyAllWindows()

# 邮件发送标志
global SEND_FLAG
SEND_FLAG = False

# 邮件基础信息配置
# 配置邮件信息
sender_email = '1484572105@qq.com'
sender_passcode= 'irqbjyyfarnkjcee'
receiver_email = '2789175147@qq.com'
subject = 'test'
message = 'OK.'

# 创建邮件对象
email = MIMEMultipart()
email['From'] = sender_email
email['To'] = receiver_email
email['Subject'] = subject




#------------------------主程序调度部分----------------------------
init()
while 1:
    # 循迹到达目的地，准备识别二维码
    if(FLAG == True):
        # 二维码识别
        detect()
        # 得到目标点位
        endx = int(str_point[0])
        endy = int(str_point[1])
        #endx = 1
        #endy = 4
        print(endx,endy)
        FLAG = False #识别标志置位False
    else:
        # 识别到二维码以后，开始走
        currsite = [0, 0]  # 记录小车当前位置 修改
        # 记录最终轨迹顺序下结点的横纵坐标
        # A*算法中计算当前情况下的最短路径
        iscomplete=False
        while not iscomplete:
            A_star()
            print(len(trackx))
            march_times=0
            # 得到路径长度
            trackn=len(trackx)
            # 开始路径规划
            iscomplete=march()
        print(car_head)
        # 等待按键输入
        key_scan()
        # 获取图片
        get_img()
        # 发送邮件
        send_email()
        print('已经拍到目的地情况，准备返回！')
        # 等待按键输入
        key_scan()
        # 小车回城
        # 目标节点更新
        car_degree=0#表示小车转向的角度
        currsite[0] = endx
        currsite[1] = endy
        endx = 0
        endy = 0
        iscomplete = False
        i = 0
        # 再次做路径规划
        while not iscomplete:
            A_star()
            march_times=0
            trackn=len(trackx)
            iscomplete=march()
        if(iscomplete):
            break
print("已经到达出发点，感谢使用")

