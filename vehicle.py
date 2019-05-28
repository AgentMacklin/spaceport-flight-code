import adafruit_bno055
from adafruit_servokit import ServoKit
from math import log

GRAV = 32.174

# Both connect functions take the same i2c object
# created in main.py
def connect_BNO055(i2c):
    try:
        return adafruit_bno055.BNO055(i2c)
    except:
        return "Connection to BNO055 unsuccessful"


def connect_MS5607(i2c):
    try:
        pass
    except:
        return "Connection to MS5607 unsuccessful"


def connect_servos():
    # 16 channels per specs for Servo bonnet
    return ServoKit(channels=16)


def move_servos(servoKit: ServoKit, degrees):
    # Move servos to specified degrees
    for servo in servoKit.servo:
        servo.angle = degrees


def projected_altitude(accel, veloc, alt):
    return -((veloc ** 2) / (2 * (accel + GRAV))) * log(-accel / GRAV) + alt

