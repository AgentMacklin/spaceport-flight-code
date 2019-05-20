# Custom logging utilities, written specifically for this flight code.

import time
from datetime import datetime


class Logger:
    """ Generic data and/or event logging class """

    def __init__(self, prefix):
        self.log_file = self.create_log_file(prefix)

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
            log_text = f"[ {ctime} | EVENT ]\t{msg}\n"
            self.log_file.write(log_text)

    def error(self, msg):
        """ Log an error """
        if not self.log_file.closed:
            ctime = self.time_stamp()
            log_text = f"[ {ctime} | ERROR ]\t{msg}\n"
            self.log_file.write(log_text)

    def writeln(self, msg):
        """ A simple write to file. """
        if not self.log_file.closed:
            log_text = f"{msg}\n"
            self.log_file.write(log_text)

    def close(self):
        if not self.log_file.closed:
            self.log_file.close()


# This is for testing
if __name__ == "__main__":
    events = Logger("LOG")
    events.event("Initializing sensors")
    time.sleep(1)
    events.event("Reading altitude")
    time.sleep(1)
    events.event("Standing by...")
    time.sleep(3)
    events.event("Launch!")
    time.sleep(2.5)
    events.event("Beginning data log")
    data = Logger("DATA")
    for i in range(1000):
        data.writeln(f"1{i}0\t42{i*3}43\t{i/2}4234")
    events.error("Sensor disconnected")
    events.writeln("Terminating flight program...")
    events.close()
    data.close()
