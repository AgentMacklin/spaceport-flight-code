# Custom logging utilities, written specifically for this flight code.

import time


def open_log_file():
    ''' Create a file and return the file handle '''
    current_time = time.ctime().replace(" ", "-")
    file_name = "LOG-" + current_time + ".txt"
    return open(file_name, "w")


def open_data_file():
    ''' Create a file and return the file handle '''
    current_time = time.ctime().replace(" ", "-")
    file_name = "DATA-" + current_time + ".txt"
    return open(file_name, "w")


# This is for testing
if __name__ == "__main__":
    log_handle = open_log_file()
    data_handle = open_data_file()

    log_handle.write("Beginning flight code log...\n")
    data_handle.write("Beginning flight code data file...\n")

    data_handle.close()
    log_handle.close()
