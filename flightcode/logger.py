# Custom logging utilities, written specifically for this flight code.

import time
from datetime import datetime
from random import randint

# why
LOG_HEADER = """\
         ___         
  _____ / _ \ _____  
  |_ _|/ /_\ \|_ _|  
   | |/ _____ \| |   
   | / /_   _\ \ |   
  |_____|___|_____|  
    \___________/    
  
"""


class Logger:
    """ Generic data and/or event logging class """

    # If using the class as an event logger, pass nothing in for table, else pass
    # in a tuple containing the headers for column data
    def __init__(self, prefix, headers=None):
        self.log_file = self.create_log_file(prefix)
        self.log_file.write(LOG_HEADER)
        if headers is not None:
            self.headers = headers
            for header in headers:
                self.log_file.write(header + "\t\t")
            self.log_file.write("\n")

    def create_log_file(self, prefix):
        """ Create a file and return the file handle """
        current_time = time.ctime().replace(" ", "-")
        file_name = f"{prefix}-" + current_time + ".txt"
        return open(file_name, "w")

    def time_stamp(self):
        """ Generate a time stamp for logging """
        now = datetime.now()
        ctime = now.strftime("%H:%M:%S")
        return str(ctime)

    def event(self, msg):
        """ Write text to event log """
        if not self.log_file.closed:
            ctime = self.time_stamp()
            log_text = f"[ {ctime} ][ EVENT ]\t{msg}\n"
            self.log_file.write(log_text)

    def error(self, msg):
        """ Log an error """
        if not self.log_file.closed:
            ctime = self.time_stamp()
            log_text = f"[ {ctime} ][ ERROR ]\t{msg}\n"
            self.log_file.write(log_text)

    def writeln(self, msg):
        """ A simple write to file. """
        if not self.log_file.closed:
            log_text = f"{msg}\n"
            self.log_file.write(log_text)

    def write_to_table(self, data_tup: tuple):
        """ Write right-justified data to file. """
        for i in range(len(data_tup)):
            data = f"{data_tup[i]:.3f}"
            indent = str(" ") * (len(self.headers[i]) - len(data))
            if i == len(data_tup) - 1:
                self.log_file.write(indent + data + "\n")
            else:
                self.log_file.write(indent + data + "\t\t")

    def close(self):
        if not self.log_file.closed:
            self.log_file.close()


# This is for testing
if __name__ == "__main__":
    alt = 400
    events = Logger("LOG")
    events.event("Initializing sensors")
    events.event("Reading altitude")
    events.event(
        f"Altitude initialized to {alt:,} feet, setting target to {alt + 10000:,} feet"
    )
    events.event("Standing by...")
    events.event("Launch!")
    events.event("Beginning data log")
    data = Logger(
        "DATA", headers=("Speed (fps)", "Acceleration (ft/s^2)", "Orientation (pitch)")
    )
    for i in range(1000):
        a = randint(1, 1000)
        b = randint(1, 1000)
        c = randint(1, 1000)
        data.write_to_table((a / b, a / b, b / c))
    events.error("Sensor disconnected")
    events.event("Terminating flight program...")
    events.close()
    data.close()
