import adafruit_bno055 as bno055
import adafruit_mpl3115a2 as mpl3115a2
from adafruit_servokit import ServoKit
from time import monotonic
from enum import IntEnum
from math import log, fabs
import numpy as np

GRAV = 32.174
METERSTOFEET = 3.2808399

VELOCITY = np.ndarray(shape=(1, 3))
POSITION: np.ndarray = np.ndarray(shape=(1, 3))
ALTITUDE: float = 0

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


def sqr(x):
    """ Helper function for squaring values. """
    return x * x


def move_servos(servoKit: ServoKit, degrees):
    """ Move servos to specified degrees. """
    for servo in servoKit.servo:
        servo.angle = degrees


def verify_launch(mpl: mpl3115a2.MPL3115A2, threshold_alt):
    """ Make sure vehicle has actually launched. """
    has_launched = True
    current_time = monotonic()
    while fabs(monotonic() - current_time) < 0.5:
        alt = altitude(mpl)
        if alt < threshold_alt:
            has_launched = False
    return has_launched


def verify_burnout(bno: bno055.BNO055):
    has_burntout = True
    c_time = monotonic()
    while fabs(monotonic() - c_time) < 0.5:
        accel = inertial_acceleration(bno)
        if accel[2] > 0:
            has_burntout = True
            break
    return has_burntout


def verify_apogee(mpl: mpl3115a2.MPL3115A2, dt):
    is_descending = True
    c_time = monotonic()
    while fabs(monotonic() - c_time) < 0.5:
        velocity = vertical_velocity(mpl, dt)
        if velocity > 0:
            is_descending = False
            break
    return is_descending


def init_current_altitude(mpl: mpl3115a2.MPL3115A2):
    """ Get an average of the current altitude on the launchpad. """
    current_time = monotonic()
    data = list()
    while fabs(monotonic() - current_time) > 3:
        data.append(mpl.altitude * METERSTOFEET)
    return sum(data) / len(data)


def altitude(mpl: mpl3115a2.MPL3115A2):
    """ Return altitude in feet instead of meters. """
    return mpl.altitude * METERSTOFEET


def inertial_acceleration(bno: bno055.BNO055) -> np.ndarray:
    """ Return the inertial of the vehicle, in feet per second. """
    accel = np.asarray(bno.acceleration).T  # .T to convert row vector to column vector
    t_matrix = vehicle_to_inertial(bno.quaternion)
    inertial_accel = t_matrix * accel
    return inertial_accel * METERSTOFEET


def vehicle_to_inertial(quaternion: tuple):
    """ Create a transformation matrix. 
        a, b, c, d are given from quaternions supplied by the bno055. """
    a = quaternion[0]
    b = quaternion[1]
    c = quaternion[2]
    d = quaternion[3]
    return np.array(
        [
            sqr(a) + sqr(b) - sqr(c) - sqr(d),
            2 * b * c - 2 * a * d,
            2 * b * d + 2 * a * c,
        ],
        [
            2 * b * c + 2 * a * d,
            sqr(a) - sqr(b) + sqr(c) - sqr(d),
            2 * c * d - 2 * a * b,
        ],
        [
            2 * b * d - 2 * a * c,
            2 * c * d + 2 * a * b,
            sqr(a) - sqr(b) - sqr(c) + sqr(d),
        ],
    )


def velocity(mpl: mpl3115a2.MPL3115A2, acceleration: np.ndarray, dt):
    VELOCITY += acceleration * dt
    VELOCITY[2] = vertical_velocity(mpl, dt)
    return VELOCITY


def position(velocity: np.ndarray, dt):
    POSITION += velocity * dt
    return POSITION


def vertical_velocity(mpl: mpl3115a2.MPL3115A2, dt):
    veloc = (mpl.altitude - ALTITUDE) / dt
    ALTITUDE = mpl.altitude
    return veloc


def projected_altitude(accel, veloc, alt):
    """ The projected apogee of the vehicle. """
    try:
        return -((veloc ** 2) / (2 * (accel + GRAV))) * log(-accel / GRAV) + alt
    except (ValueError, ZeroDivisionError):
        return 0

