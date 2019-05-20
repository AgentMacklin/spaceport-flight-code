import matplotlib.pyplot as plt
from atmosphere import Atmosphere
from pid import PID
from vehicle import projected_altitude

CD = 0.5  # Approximate drag coefficient of vehicle
AREA = 0.79  # Frontal area of rocket
GRAV = 32.174
DENSITY = 0.0765  # constant for simplicity for now
MASS = 1.24324  # lbs
TIME = 0
STEP = 0.01


def acceleration(velocity, density, input):
    cd = CD + (0.75 * input)
    return -GRAV - (cd * AREA * density * (velocity ** 2) / (2 * MASS))


AtmosEngine = Atmosphere()
altitude = 1000
velocity = 700
accel = acceleration(velocity, AtmosEngine.density(altitude), 0)

pid = PID(0.00025, 0.001, 0.1, 3500, 0, 1)

pid_outputs = []

while velocity > 0:
    altitude += velocity * STEP
    velocity += accel * STEP
    p_alt = projected_altitude(accel, velocity, altitude)
    pid_output = pid.output(p_alt, STEP)
    accel = acceleration(velocity, AtmosEngine.density(altitude), pid_output)
    pid_outputs.append(pid_output)

print(f"Altitude: {altitude}")
plt.plot(pid_outputs)
plt.show()
