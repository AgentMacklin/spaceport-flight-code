from logger import Logger
from pid import PID
import vehicle
import board
import busio


TARGET_ALT = 10000

STATUS = vehicle.FlightStatus.GO
MODE = vehicle.Runmode.STANDBY


# SENSOR AND LOG INITIALIZATION
# -----------------------------

# Opening up flight log, so we can see what happened during the flight
data_log = Logger("DATA", headers=(""))
event_log = Logger("LOG")
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


# Per docs, must call bno.begin() once before calling other functions
try:
    if bno.begin() is False:
        event_log.error("BNO055 connected but failed to start")
        STATUS = vehicle.FlightStatus.NOGO
except NameError:
    STATUS = vehicle.FlightStatus.NOGO
    

# MAIN EVENT LOOP
# ---------------

if STATUS is vehicle.FlightStatus.GO:
    event_log.event("Reading current altitude")
    init_alt = vehicle.init_current_altitude(mpl)
    threshold_alt = init_alt + 150
    target = init_alt + TARGET_ALT
    event_log.event(
        f"Altitude initialized to {init_alt:,}, setting target to {target:,}"
    )
    event_log.event("Standing by for launch...")

    # Main event loop
    while True:
        # Waiting for launch on the launhpad
        if MODE is vehicle.Runmode.STANDBY:
            if vehicle.altitude(mpl) > init_alt:
                if vehicle.verify_launch(mpl, threshold_alt):
                    MODE = vehicle.Runmode.LAUNCH
                    event_log.event("Switching to LAUNCH mode")
            pass

        # Waiting for motor to burn out
        elif MODE is vehicle.Runmode.LAUNCH:
            if bno.read_gravity() < 0:
                MODE = vehicle.Runmode.COAST
                event_log.event("Entering drag mode (COAST)")

        # Deploy drag plates and log data
        elif MODE is vehicle.Runmode.COAST:
            pass

        # Retract plates and close everything down
        elif MODE is vehicle.Runmode.DESCENT:
            event_log.event("Closing data log")
            data_log.close()
            # Retract plates

elif STATUS is vehicle.FlightStatus.NOGO:
    event_log.event("Errors occurred, flight is a no go, closing files and exiting")
    event_log.close()
    data_log.close()

