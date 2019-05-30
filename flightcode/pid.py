# +------------------------------------------------------------------------------+
# |         ___         |                                                        |
# |  _____ / _ \ _____  |  Author:   Austen LeBeau                               |
# |  |_ _|/ /_\ \|_ _|  |  Date:     May 14, 2019                                |
# |   | |/ _____ \| |   |                                                        |
# |   | / /_   _\ \ |   |  Description:                                          |
# |  |_____|___|_____|  |  Generic PID controller class, which can be used to    |
# |    \___________/    |  control any thing that needs to be controlled. Takes  |
# |                     |  in gains, a target, and optional min and max outputs. |
# |                     |                                                        |
# +------------------------------------------------------------------------------+


class PID:
    """ PID takes in gains and an initial setpoint. """

    def __init__(self, KP, KI, KD, setpoint, min_output=None, max_output=None):
        """ Initialize gains and other important variables. """
        self.KP = KP
        self.KI = KI
        self.KD = KD

        self.setpoint = setpoint
        self.P0 = 0
        self.I0 = 0

        self.output_val = 0
        self.max_output = max_output
        self.min_output = min_output

    def output(self, input_val, time_diff):
        """ Output a value, given a time step. """
        P = input_val - self.setpoint
        I = self.I0 + (P * time_diff)
        D = (P - self.P0) / 2

        diff_output = (self.KP * P) + (self.KI * I) * (self.KD * D)
        self.P0 = P
        self.I0 = I

        self.output_val += diff_output

        # If PID instance has values for max and min output, clamp the output
        if self.max_output is not None:
            if self.output_val > self.max_output:
                self.output_val = self.max_output
        if self.min_output is not None:
            if self.output_val < self.min_output:
                self.output_val = self.min_output

        return self.output_val

    def __str__(self):
        return f"""\
Setpoint:  {self.setpoint}
Max:       {self.max_output}
Min:       {self.min_output}
KP:        {self.KP}
KI:        {self.KI}
KD:        {self.KD}"""
