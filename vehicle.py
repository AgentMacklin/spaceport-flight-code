import Adafruit_BNO055.BNO055 as bno055
import adafruit_mpl3115a2 as mpl3115a2
from adafruit_servokit import ServoKit
from time import time
from enum import IntEnum
from math import log, fabs

GRAV = 32.174
METERSTOFEET = 3.2808399

# Different modes of operation during flight
class Runmode(IntEnum):
    STANDBY = 0
    LAUNCH = 1
    COAST = 2
    DESCENT = 3


# For checking if everything is okay to go, or not. If there was a problem connecting to
# anything, the program will change the flight status to no go and close everything after
# running through all the initialization procedures, this way we can see what actually did
# connect succesfully instead of cutting the program short whenever there's an error
class FlightStatus(IntEnum):
    GO = 0
    NOGO = 1


def move_servos(servoKit: ServoKit, degrees):
    # Move servos to specified degrees
    for servo in servoKit.servo:
        servo.angle = degrees


# Make sure vehicle has actually launched
def verify_launch(mpl: mpl3115a2.MPL3115A2, threshold_alt):
    has_launched = True
    current_time = time()
    while fabs(time() - current_time) < 0.5:
        alt = altitude(mpl)
        if alt < threshold_alt:
            has_launched = False
    return has_launched


# Get an average of the current altitude on the launchpad
def init_current_altitude(mpl: mpl3115a2.MPL3115A2):
    current_time = time()
    data = list()
    while fabs(time() - current_time) > 3:
        data.append(mpl.altitude * METERSTOFEET)
    return sum(data) / len(data)


# Return altitude in feet instead of meters
def altitude(mpl: mpl3115a2.MPL3115A2):
    return mpl.altitude * METERSTOFEET


def projected_altitude(accel, veloc, alt):
    return -((veloc ** 2) / (2 * (accel + GRAV))) * log(-accel / GRAV) + alt

