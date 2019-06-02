#
# Main entry point for flight code, below is a flow diagram for the flight code
# logic.
#
#
#              Entry point
#      +---------------------------+                      +-------------------------------+
#      |                           |   Connections were   |                               |
#      | Open log files and create |   successful         | Read in current altitude, set |
#      | connections to sensors    +--------------------->+ target altitude accordingly.  |
#      |                           |                      | Enter standby mode            |
#      +------------+--------------+                      |                               |
#                   |                                     +---------------+---------------+
#          Errors   |                                                     |
#          occured  |                               +---------------------+
#                   |                               |                     v
#      +------------+--------------+                |     +---------------+---------------+
#      |                           |             No |     |                               |
#      | Flight is a no go, system |                |     | Has altitude increased by 100 |
# +----+ remains dormant           |                +-----+ feet?                         |
# |    |                           |                      |                               |
# |    +---------------------------+                      +------------------+------------+
# |                                                                          |
# |                                                                          | Yes
# |    +----------------+       +---------------------------+                v
# |    |                |       |                           |     +----------+------------+
# |    | Switch to drag |       | Has vertical acceleration |     |                       |
# |    | mode           +<------+ gone from positive to     +--+--+ Switch to launch mode |
# |    |                |  Yes  | negative?                 |  ^  |                       |
# |    +---+------------+       |                           |  |  +-----------------------+
# |        |                    +-------------+-------------+  |
# |        |     +-----+                      |                |
# |        +<----+ PID +<---+                 +----------------+
# |        |     +-----+    | No                     No
# |        v                |
# |    +---+----------------+------+
# |    |                           |        +------------------------+
# |    | Has the vertical velocity |  Yes   |                        |
# |    | become negative?          +------->+ Switch to descent mode |
# |    |                           |        |                        |
# |    +---------------------------+        +-----------+------------+
# |                                                     |
# |    +---------------------------+                    |
# |    |                           |                    |
# |    | Close log files and make  |                    |
# +--->+ sure plates are retracted +<-------------------+
#      |                           |
#      +---------------------------+
#                End


from logger import Logger
from pid import PID
import vehicle as vehicle
from time import monotonic, sleep
import board
import busio


TARGET_ALT = 10000  # altitude to reach from ground
TIME_SINCE_LAUNCH = 0  # used for data logging during coast mode
DELTA_T = 0


# Mode of operation and flight readiness flags
STATUS = vehicle.FlightStatus.GO
MODE = vehicle.Runmode.STANDBY


# SENSOR AND LOG INITIALIZATION

# Opening up flight log, so we can see what happened during the flight
event_log = Logger("LOG")

# Data log
data_log = Logger(
    "DATA",
    headers=(
        "Time (seconds)",
        "Acceleration (x)",
        "Acceleration (y)",
        "Acceleration (z)",
        "Velocity (x)",
        "Velocity (y)",
        "Velocity (z)",
        "Position (x)",
        "Position (y)",
        "Altitude (z)",
        "PID Controller Output",
        "Projected Altitude",
    ),
)
event_log.event("Initializing connection to sensors")

# Create I2C object
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    event_log.event("i2c object created succesfully")
except RuntimeError:
    event_log.error("Failed to create an i2c object")
    STATUS = vehicle.FlightStatus.NOGO

# Create connection to BNO055 accelerometer
try:
    bno = vehicle.bno055.BNO055(i2c)
    event_log.event("Connection to BNO055 successful")
except (RuntimeError, OSError, ValueError):
    event_log.error("Failed to connect to BNO055")
    STATUS = vehicle.FlightStatus.NOGO

# Create connection to MPL3115a2 altimeter
try:
    mpl = vehicle.mpl3115a2.MPL3115A2(i2c)
    event_log.event("Connection to MPL3115 successful")
except (RuntimeError, OSError, ValueError):
    event_log.error("Failed to connect to MPL3115")
    STATUS = vehicle.FlightStatus.NOGO

# Create a connection to servos
try:
    servos = vehicle.ServoKit(channels=16, i2c=i2c)
except (RuntimeError, OSError, ValueError):
    event_log.error("Failed to connect to servos")
    STATUS = vehicle.FlightStatus.NOGO


# MAIN EVENT LOOP
if STATUS is vehicle.FlightStatus.GO:
    DELTA_T = monotonic()
    event_log.event("Reading current altitude")
    init_alt = vehicle.init_current_altitude(mpl)
    threshold_alt = init_alt + 100  # altitude at which to switch to launch mode
    target = init_alt + TARGET_ALT
    event_log.event(
        f"Altitude initialized to {init_alt:,}, setting target to {target:,}"
    )
    event_log.event("Standing by for launch...")

    # Create a PID controller object
    pid = PID(0.1, 0.05, 0.001, target, min_output=0, max_output=180)

    # Main event loop
    while True:
        # Time elapsed since last loop
        DELTA_T = monotonic() - DELTA_T

        # Waiting for launch on the launhpad
        if MODE is vehicle.Runmode.STANDBY:
            if vehicle.altitude(mpl) > init_alt:
                if vehicle.verify_launch(mpl, threshold_alt):
                    MODE = vehicle.Runmode.LAUNCH
                    event_log.event("Switching to LAUNCH mode")
            pass

        # Waiting for motor to burn out
        elif MODE is vehicle.Runmode.LAUNCH:
            if vehicle.inertial_acceleration(bno)[2] < 0:
                MODE = vehicle.Runmode.COAST
                event_log.event("Entering drag mode (COAST)")
                TIME_SINCE_LAUNCH = monotonic()  # start coast counter
                vehicle.ALTITUDE = mpl.altitude

        # Deploy drag plates and log data
        elif MODE is vehicle.Runmode.COAST:
            acceleration = vehicle.inertial_acceleration(bno)
            velocity = vehicle.velocity(mpl, acceleration, DELTA_T)
            position = vehicle.position(velocity, DELTA_T)
            p_alt = vehicle.projected_altitude(
                acceleration[2], velocity[2], mpl.altitude
            )
            angle = pid.output(p_alt, DELTA_T)
            vehicle.move_servos(servos, angle)
            data_tup = (
                monotonic() - TIME_SINCE_LAUNCH,
                acceleration[0],
                acceleration[1],
                acceleration[2],
                velocity[0],
                velocity[1],
                velocity[2],
                position[0],
                position[1],
                vehicle.altitude(mpl),
                angle,
                p_alt,
            )
            if vehicle.vertical_velocity(mpl, DELTA_T) < 0:
                if vehicle.verify_apogee(mpl, DELTA_T):
                    MODE = vehicle.Runmode.DESCENT
                    event_log.event(f"Reached apogee: {mpl.altitude:,} feet")
                    event_log.event("Switching to DESCENT mode")

        # Retract plates and close everything down
        elif MODE is vehicle.Runmode.DESCENT:
            event_log.event("Closing data log")
            data_log.close()
            # Retract plates
            vehicle.move_servos(servos, 0)
            event_log.event("Retracting plates")
            sleep(3)  # give the servos some time to retract
            event_log.event("Flight complete, exiting program")
            event_log.close()
            break

elif STATUS is vehicle.FlightStatus.NOGO:
    event_log.event("Errors occurred, flight is a no go, closing files and exiting")
    event_log.close()
    data_log.close()

