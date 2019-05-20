from logger import Logger
from pid import PID
import adafruit_bno055
import board
import busio


STANDBY = 0
LAUNCH = 1
COAST = 2
DESCENT = 3

# +-------------------------------+
# | SENSOR AND LOG INITIALIZATION |
# +-------------------------------+
# Opening up flight log, so we can see what happened during the flight
dataLog = Logger("DATA")
eventLog = Logger("LOG")
eventLog.event("Initializing connection to sensors")

# Create I2C object
i2c = busio.I2C(board.SCL, board.SDA)
eventLog.event("I2C object created succesfully")

# Create connection to BNO055 accelerometer
bno = adafruit_bno055.BNO055(i2c)
eventLog.event("BNO055 connection successful")

# TODO: Create connection to altimeter, may have to write our own driver
eventLog.event("MS5607 connection successful")


# +--------------------------------+
# |    VARIABLE INITIALIZATION     |
# +--------------------------------+
# Variable used as conditional for switching flight modes
MODE = STANDBY
eventLog.event("Standing by for launch...")

# Main event loop
while True:
    if MODE is STANDBY:
        # if altitude() > altitude_naught:
        #   MODE = LAUNCH
        #   events.event("Switching to LAUNCH mode")
        pass

    elif MODE is LAUNCH:
        # if acceleration() < 0:
        #   MODE = COAST
        #   events.event("Switching to COAST mode")
        pass

    elif MODE is COAST:
        # Deploy drag plates,
        pass

    elif MODE is DESCENT:
        eventLog.event("Closing data log")
        dataLog.close()
        # Retract plates
