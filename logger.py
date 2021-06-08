import matplotlib
import pickle

LOG_INTERVAL = 0.5 # seconds

class Logger:
    def __init__(self, use_qt=False):
        global plt
        if use_qt:
            matplotlib.use('Qt5Agg')
        from matplotlib import pyplot as plt

        self.time = 0
        self.x_pos_log = {
            "t": [],
            "x": []
        }
        self.y_pos_log = {
            "t": [],
            "y": []
        }
        self.heading_log = {
            "t": [],
            "theta": []
        }
        self.l_motor_speed_log = {
            "t": [],
            "omega": []
        }
        self.r_motor_speed_log = {
            "t": [],
            "omega": []
        }

        self.small_trash_mass_list = [] # smaller than megaplastics
        self.big_trash_mass_list = [] # megaplastics

        self.distance_travelled = 0
        self.gps_path = []

    def update_time(self, dt):
        self.time += dt

    def log_pos(self, pos):
        if len(self.x_pos_log["t"]) == 0 or self.time - self.x_pos_log["t"][-1] >= LOG_INTERVAL:
            self.x_pos_log["t"].append(self.time)
            self.x_pos_log["x"].append(pos[0])
            self.y_pos_log["t"].append(self.time)
            self.y_pos_log["y"].append(pos[1])

    def log_heading(self, heading):
        if len(self.heading_log["t"]) == 0 or self.time - self.heading_log["t"][-1] >= LOG_INTERVAL:
            self.heading_log["t"].append(self.time)
            self.heading_log["theta"].append(heading)

    def log_motors(self, l_motor_speed, r_motor_speed):
        if len(self.l_motor_speed_log["t"]) == 0 or self.time - self.l_motor_speed_log["t"][-1] >= LOG_INTERVAL:
            self.l_motor_speed_log["t"].append(self.time)
            self.l_motor_speed_log["omega"].append(l_motor_speed)
            self.r_motor_speed_log["t"].append(self.time)
            self.r_motor_speed_log["omega"].append(r_motor_speed)

    def log_trash(self, piece):
        if piece.size >= 0.5:
            self.big_trash_mass_list.append(piece)
        else:
            self.small_trash_mass_list.append(piece)

    def update_distance_travelled(self, distance):
        self.distance_travelled = distance

    def set_gps_path(self, gps_path):
        self.gps_path = gps_path

    def final_report(self):
        filename = 'report_30km.pickle'
        outfile = open(filename, 'wb')
        pickle.dump(self, outfile)
        outfile.close()
