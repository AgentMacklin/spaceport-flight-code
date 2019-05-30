# +------------------------------------------------------------------------------+
# |         ___         |                                                        |
# |  _____ / _ \ _____  |  Author:   Austen LeBeau                               |
# |  |_ _|/ /_\ \|_ _|  |  Date:     May 14, 2019                                |
# |   | |/ _____ \| |   |                                                        |
# |   | / /_   _\ \ |   |  Description:                                          |
# |  |_____|___|_____|  |  Implementation of the Atmosphere class, which acts    |
# |    \___________/    |  as an engine for calculating atmospheric properties   |
# |                     |  at different altitudes.                               |
# +------------------------------------------------------------------------------+

FTORANK = 459.67


class Atmosphere:
    def temperature(self, altitude):
        return 59 - 0.00356 * altitude

    def pressure(self, altitude):
        temp = self.temperature(altitude)
        return 2116 * ((temp + FTORANK) / 518.6) ** 5.256

    def density(self, altitude):
        press = self.pressure(altitude)
        temp = self.temperature(altitude)
        return press / (1718 * (temp + FTORANK))
