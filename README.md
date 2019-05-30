# 2019 Auburn University Spaceport America Altitude Control FLight Code

Contains the main source code for the altitude control system, as well as some rudimentary testing code and some bash scripts to simplify configuring a Raspberry Pi Zero. This was written in Python since the drivers for the altimeter and accelerometer are only available in Python, but we are also using this competition to test how well Python performs in flight for future competitions, since it is also more accessible to beginners than C/C++.

The `flightcode` directory contains the actual flight code:
- `__init__.py` makes flightcode a module itself (for those of you new to Python)
- `logger.py` contains a class that creates text files and writes formatted text, which can be used for logging events and taking data
- `main.py` is the main execution point for the program
- `pid.py` defines a PID controller for controlling the position of the drag plates, but could also be used for other stuff since it is written generically
- `vehicle.py` defines functions and classes for getting altitude, position, velocity, as well as flags `main.py` uses for logic flow, etc. It does a bunch of different things

Likewise, `sim` contains programs for simulating the flight for testing on the ground, and `bash` contains bash scripts for installing python packages and cleaning up log files, so utility scripts go here.

This flight code uses the latest version of Python3, it will not work with any Python version that does not support f-strings. Also, when installing Python packages using pip, use this method instead:

```
python3.7 -m pip install --user <package> 
```

Since using other normal methods seems to not work on the Pi, and it can't find them unless using the method above.

