import matplotlib

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

    def update_time(self, dt):
        self.time += dt

    def log_pos(self, pos):
        self.x_pos_log["t"].append(self.time)
        self.x_pos_log["x"].append(pos[0])
        self.y_pos_log["t"].append(self.time)
        self.y_pos_log["y"].append(pos[1])

    def final_report(self):
        plt.figure()
        plt.plot(self.x_pos_log["t"], self.x_pos_log["x"])
        plt.title("Boat X Position")
        plt.xlabel("t (s)")
        plt.ylabel("x (m)")
        plt.show()

        plt.figure()
        plt.plot(self.y_pos_log["t"], self.y_pos_log["y"])
        plt.title("Boat Y Position")
        plt.xlabel("t (s)")
        plt.ylabel("y (m)")
        plt.show()
