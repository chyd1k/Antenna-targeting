import datetime
import time
from skyfield.api import load, Topos, EarthSatellite

import pathlib

class SatellitesManager:

    def __init__(self):
        self.__TLE_FILE = str(pathlib.Path(__file__).parent.resolve().absolute()) + "\\active_satellites.tle"

        self.__satellites = load.tle(self.__TLE_FILE)
        # self.print_satellites_info()

    
    def print_satellites_info(self):
        # [print(sat) for sat in self.__satellites.values()]
        # [print(i) for i in self.__satellites]
        [print(name) for name in list(set([sat.name for sat in self.__satellites.values()]))]

    def get_satellites_names(self):
        names = list(set([sat.name for sat in self.__satellites.values()]))
        names.sort()
        return names

    def get_aim_degrees(self, satellite_name: str, local_position_lat: float, local_position_lon: float):
        if (satellite_name not in self.__satellites):
            return

        if (abs(local_position_lat) > 180.):
            local_position_lat = local_position_lat - 360. if local_position_lat > 0 else 360. + local_position_lat

        if (abs(local_position_lon) > 180.):
            local_position_lon = local_position_lon - 360. if local_position_lon > 0 else 360. + local_position_lon

        str_lat = f"{abs(local_position_lat)} S" if (local_position_lat < 0.) else f"{abs(local_position_lat)} N"
        str_lon = f"{abs(local_position_lon)} W" if (local_position_lon < 0.) else f"{abs(local_position_lon)} E"

        ts = load.timescale()
        t = ts.now()
        location = Topos(str_lat, str_lon)

        difference = self.__satellites[satellite_name] - location
        topocentric = difference.at(t)

        alt, az, distance = topocentric.altaz()

        # if alt.degrees > 0:
        #     print('The satellite is above the horizon')

        # print('Altitude:', alt.degrees)
        # print('Azimuth:', az.degrees)
        # print('Distance: {:.1f} km'.format(distance.km))

        return az.degrees, alt.degrees, distance.km

        # azValue = int(str(az).replace('deg', '').split(" ")[0])

        # a = 123
        # if alt.degrees >= MIN_DEGREE and azValue >= MIN_AZ and azValue <= MAX_AZ:
        #     print(sat.name, alt, az)
        


# TLE_FILE = "https://celestrak.com/NORAD/elements/active.txt" # DB file to download

# MIN_DEGREE = 45
# MIN_AZ = 50
# MAX_AZ = 140

# satellites = load.tle(TLE_FILE)
# ts = load.timescale()
# t = ts.now()

# # Локация с которой мы наблюдаем
# location = Topos('52.173141 N', '44.108612 E')

# for sat in satellites.values():
#     difference = sat - location
#     topocentric = difference.at(t)

#     alt, az, distance = topocentric.altaz()

#     azValue = int(str(az).replace('deg', '').split(" ")[0])

#     if alt.degrees >= MIN_DEGREE and azValue >= MIN_AZ and azValue <= MAX_AZ:
#         print(sat.name, alt, az)