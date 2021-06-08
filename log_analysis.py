#!/usr/bin/env python3

import pickle
import math
import matplotlib.pyplot as plt
import numpy as np

log_file = "report_25km.pickle"

log = pickle.load(open(log_file, "rb"))

distance_travelled = 0
for t in range(1, len(log.x_pos_log["t"])):
    distance_travelled += math.sqrt((log.x_pos_log["x"][t] - log.x_pos_log["x"][t-1])**2 + (log.y_pos_log["y"][t] - log.y_pos_log["y"][t-1])**2)
distance_travelled /= 1000
print("distance travelled: {} km".format(distance_travelled))

small_trash_mass = 0
for piece in log.small_trash_mass_list:
    small_trash_mass += piece.mass
print("collected {} kg of meso and macro-plastics:".format(small_trash_mass))

mega_trash_mass = 0
for piece in log.big_trash_mass_list:
    mega_trash_mass += piece.mass
print("collected {} kg of megaplastics:".format(mega_trash_mass))

total_trash_mass = small_trash_mass + mega_trash_mass
print("collected {} kg total of plastic:".format(total_trash_mass))

print("small plastic collection rate: {} kg/km".format(small_trash_mass / distance_travelled))
print("megaplastic collection rate: {} kg/km".format(mega_trash_mass / distance_travelled))
print("total collection rate: {} kg/km".format(total_trash_mass / distance_travelled))
print("total collection rate: {} kg/h".format(total_trash_mass / (log.time/3600)))

plt.figure()
plt.plot(log.x_pos_log["t"], log.x_pos_log["x"])
plt.title("Boat X Position")
plt.xlabel("t (s)")
plt.ylabel("x (m)")
plt.show()

plt.figure()
plt.plot(log.y_pos_log["t"], log.y_pos_log["y"])
plt.title("Boat Y Position")
plt.xlabel("t (s)")
plt.ylabel("y (m)")
plt.show()

plt.figure()
plt.plot(log.heading_log["t"], np.rad2deg(log.heading_log["theta"]))
plt.title("Boat Heading")
plt.xlabel("t (s)")
plt.ylabel("heading (degrees)")
plt.show()
