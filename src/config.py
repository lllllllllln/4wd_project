"""Project configuration.

Do not store passwords, API keys, email authorization codes, or private IP
credentials in this file.
"""

# 电机引脚来自“环境说明/硬件接口速查手册.xlsx”的 BCM 列。
# 注意：Python RPi.GPIO 使用 BCM 编号，不要把 wiringPi 编号填到这里。
# 一般调速度和动作时不需要改这里；只有确认硬件接线或接口表不一致时才改。
#
# 方向脚的作用：
# - IN1/IN2 控制左侧电机方向。
# - IN3/IN4 控制右侧电机方向。
# - 同一侧通常一个脚 HIGH、另一个脚 LOW 时电机转动。
# - 同一侧两个脚都 LOW 时该侧电机停止。
MOTOR_IN1 = 20
MOTOR_IN2 = 21
MOTOR_IN3 = 19
MOTOR_IN4 = 26

# ENA/ENB 是两侧电机的 PWM 使能脚。
# PWM 占空比越高，电机转得越快；占空比范围在 motor.py 中限制为 0 到 100。
MOTOR_ENA = 16
MOTOR_ENB = 13

# Yahboom 示例代码中电机 PWM 频率为 2000 Hz。
# 新手优先调 test_motor.py 的 --speed，不要先改 PWM 频率。
MOTOR_PWM_FREQUENCY = 2000
