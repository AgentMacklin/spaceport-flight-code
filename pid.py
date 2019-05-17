# PID controller class for creating generic PID controllers


class PID(object):
    ''' PID takes in gains and an initial setpoint. '''

    def __init__(self, KP, KI, KD, setpoint, max_output=None, min_output=None):
        ''' Initialize gains and other important variables. '''
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
        ''' Output a value, given a time step. '''
        P = input_val - self.setpoint
        I = self.I0 + (P * time_diff)
        D = (P - self.P0) / 2

        diff_output = (P * self.KP) + (I * self.KI) * (D * self.KD)
        self.P0 = P
        self.I0 = I

        self.output_val += diff_output

        # If PID instance has values for max and min output, clamp the output
        if self.max_output is not None:
            self.output_val = self.output_val if self.output_val < self.max_output else self.max_output
        elif self.min_output is not None:
            self.output_val = self.output_val if self.output_val > self.min_output else self.min_output

        return self.output_val
