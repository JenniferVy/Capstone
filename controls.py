from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
)
import math
import numpy as np
from pid import PID

WAYPOINT_THRESHOLD = 7 # (m) distance from waypoint when it is considered reached
TRASH_SIZE_THRESHOLD = 0.5 # (m) smallest trash size to go after
TRASH_COLLECTION_TIMEOUT = 3 # (seconds) amount of time to continue forward after trash is no longer visible in sonar

OPERATIONAL_SPEED = 1.5 # (m/s) operational speed in range [2,5] knots or [1.03, 2.57] m/s
MOTOR_MAX_SPEED = 125.7 # Motors have a max speed of 1200 RPM = 125.7 rad/s

HEADING_P = 0.22 # Input: heading_err [rad]; Output: ang_vel_sp [rad/s]
SIDEWAYS_VEL_P = 0.01 # Input: sideways_vel_err [m/s]; Output: ang_vel_sp [rad/s]
FORWARD_VEL_PID = (200, 25, 0) # Input: forward_vel_err [m/s]; Output: motor_speed [rad/s]. TODO may need some derivative control to compensate for motor acceleration time
FORWARD_VEL_FF = 0 # Input: forward_vel_sp^2 [(m/s)^2]; Output: motor_speed [rad/s]. TODO if integral works well enough, might not need feedforward 
ANG_VEL_PID = (2000, 10, 0) # Input: ang_vel_err [rad/s]; Output: motor_speed [rad/s]
ANG_VEL_FF = 0 # Input: ang_vel_sp^2 [(rad/s)^2]; Output: motor_speed [rad/s]

################################# Controls #####################################

class Controls:
    """ Manages controls and path planning of given boat """

    def __init__(self, sensors, gps_path=[]):
        """ Controls Class Constructor to initialize the object

        params:
        - Boat: boat object
        """
        self.sensors = sensors 
        self.gps_path = gps_path
        self.current_goal_index = 0
        self.trash_goal = None
        self.trash_goal_timeout = 0

        self.tripDuration = 0 # at start of trip, no time has passed

        self.forward_vel_pid = PID(*FORWARD_VEL_PID)
        next(self.forward_vel_pid)
        self.ang_vel_pid = PID(*ANG_VEL_PID)
        next(self.ang_vel_pid)

    def keyboardInput(self, pressed_keys, dt):
        l_motor_speed = 0 # rad/s
        r_motor_speed = 0
        if pressed_keys[K_UP]:
            l_motor_speed += 100
            r_motor_speed += 100
        if pressed_keys[K_LEFT]:
            l_motor_speed -= 50
            r_motor_speed += 50
        if pressed_keys[K_RIGHT]:
            l_motor_speed += 50
            r_motor_speed -= 50

        return self.motor_control(l_motor_speed, r_motor_speed, dt)

    def top_level_control(self, dt):
        # if there is a GPS goal to go to, determine heading
        gps_goal_heading = None
        if self.current_goal_index < len(self.gps_path):
            gps_goal = self.gps_path[self.current_goal_index]
            dx = gps_goal[0] - self.sensors.get_pos()[0]
            dy = gps_goal[1] - self.sensors.get_pos()[1]
            distance = math.sqrt(dx**2 + dy**2)
            if distance < WAYPOINT_THRESHOLD: # if close enough to the current goal, move on to the next one
                self.current_goal_index += 1
                if self.current_goal_index < len(self.gps_path):
                    gps_goal = self.gps_path[self.current_goal_index]
                    dx = gps_goal[0] - self.sensors.get_pos()[0]
                    dy = gps_goal[1] - self.sensors.get_pos()[1]
                else:
                    gps_goal = None
            if gps_goal:
                gps_goal_heading = math.atan2(dy, dx)
        
        if self.trash_goal:
            trash_goal = self.trash_goal
            self.trash_goal = None
            # check if there is a detected object that is likely to be the current trash_goal
            for object in self.sensors.get_sonar_objects():
                pos_diff = math.sqrt(trash_goal.distance**2 + object.distance**2 - 2*trash_goal.distance*object.distance*math.cos(object.azimuth-trash_goal.azimuth)) # distance from polar coords
                size_percent_diff = abs(object.size_est - trash_goal.size_est) / trash_goal.size_est
                if pos_diff < 0.5 and size_percent_diff < 0.2: # pos_diff: [meters], size_percent_diff: [%]
                    self.trash_goal = object
                    break
        else:
            for object in self.sensors.get_sonar_objects():
                if object.size_est >= TRASH_SIZE_THRESHOLD:
                    print("I see some trash!")
                    self.trash_goal = object
                    self.trash_goal_timeout = TRASH_COLLECTION_TIMEOUT
                    break

        if self.trash_goal:
            goal_heading = self.sensors.get_heading() + self.trash_goal.azimuth
            v_sp = (OPERATIONAL_SPEED * math.cos(goal_heading), OPERATIONAL_SPEED * math.sin(goal_heading))
            return self.global_velocity_control(v_sp, dt)
        elif self.trash_goal_timeout > 0:
            self.trash_goal_timeout -= dt
            return self.local_velocity_control(OPERATIONAL_SPEED, 0, dt) # move forward to ensure trash is collected
        elif gps_goal_heading is not None:
            v_sp = (OPERATIONAL_SPEED * math.cos(gps_goal_heading), OPERATIONAL_SPEED * math.sin(gps_goal_heading))
            return self.global_velocity_control(v_sp, dt)
        else:
            # nothing in particular to do, just move forward
            return self.local_velocity_control(OPERATIONAL_SPEED, 0, dt)        
    
    def global_velocity_control(self, v_sp, dt):
        heading = self.sensors.get_heading()
        sideways_vel = self.sensors.get_sideways_vel()

        forward_vel_sp = np.dot(v_sp, self.sensors.get_direction())
        sideways_vel_sp = np.dot(v_sp, (self.sensors.get_direction()[1], -self.sensors.get_direction()[0]))
        if (v_sp[0] == 0 and v_sp[1] == 0):
            heading_sp = heading
        else:
            heading_sp = math.atan2(v_sp[1], v_sp[0])

        sideways_vel_err = sideways_vel_sp - sideways_vel
        heading_err = heading_sp - heading
        while heading_err > math.pi:
            heading_err -= 2*math.pi
        while heading_err < -math.pi:
            heading_err += 2*math.pi

        ang_vel_sp = HEADING_P * heading_err + SIDEWAYS_VEL_P * sideways_vel_err

        return self.local_velocity_control(forward_vel_sp, ang_vel_sp, dt)

    def local_velocity_control(self, forward_vel_sp, ang_vel_sp, dt):
        forward_vel = self.sensors.get_forward_vel()
        ang_vel = self.sensors.get_ang_vel()

        # If feedforward is set, it adds a control signal proportional to the sqaure of the velocity, which helps overcome drag without relying as much on integral control.
        forward_vel_control = self.forward_vel_pid.send([forward_vel, forward_vel_sp, dt]) + FORWARD_VEL_FF * abs(forward_vel_sp) * forward_vel_sp
        ang_vel_control = self.ang_vel_pid.send([ang_vel, ang_vel_sp, dt]) + ANG_VEL_FF * abs(ang_vel_sp) * ang_vel_sp

        l_motor_speed = forward_vel_control + ang_vel_control
        r_motor_speed = forward_vel_control - ang_vel_control

        return self.motor_control(l_motor_speed, r_motor_speed)

    def motor_control(self, l_motor_speed, r_motor_speed):
        # Desaturate motor commands. TODO could change this to prioritize turning.

        if (l_motor_speed > MOTOR_MAX_SPEED):
            l_motor_speed = MOTOR_MAX_SPEED
        if (r_motor_speed > MOTOR_MAX_SPEED):
            r_motor_speed = MOTOR_MAX_SPEED

        if (l_motor_speed < 0):
            l_motor_speed = 0
        if (r_motor_speed < 0):
            r_motor_speed = 0

        return l_motor_speed, r_motor_speed

    def detDest(self):
        """
        Determines next destination coordinates 

        params: TBD
        returns: coordinates of next piece of trash to collect
        rtype: [float, float]
        """

        return []

    def detSpeed(self, coords):
        """
        Determines speed to get to next destination coordinates

        params: 
        - coords: destination coordinates 
        returns: operational speed of boat to reach destination coordinates within operational range
        rtype: float
        """

        return 0

    def detDir(self, coords):
        """
        Determines orientation of boat to get to next destination coordinates

        params:
        - coords: destination coordinates 
        returns: direction to get to next destination coordinates in degrees
        rtype: float
        """
    
        return 0

    def detOperState(self):
        """
        Determines operation state in case boat reaches unstable conditions

        params: TBD
        returns: updated operation state
        rtype: bool
        """
    
        return True

    def getTripDuration(self):
        """
        Returns current trip duration length 

        params: None
        returns: current trip duration in hours
        rtype: float
        """
    
        return self.tripDuration

    def getAreaCoveredDuringTrip(self):
        """
        Determines area covered during trip

        params: None
        returns: area covered during trip based on trajectories calculated
        rtype: float
        """
        
        return 0

    def getAreaCoveredPerHour(self):
        """
        Determines area covered per hour of trip

        params: None
        returns: area covered per hour during trip
        rtype: float
        """
        
        return self.getAreaCoveredDuringTrip()/self.getTripDuration()

############################## Path Planning ##################################
    def getCurrLoc(self):
        """
        Gets current location of boat

        params: None
        returns: current location coordinates of boat
        rtype: [float, float]
        """
        
        return [self.lat, self.long]
    
    def getDestLoc(self):
        """
        Using trash sensor, determines destination location of boat

        params: TBD
        returns: next destination of boat
        rtype: [float, float]
        """
        
        return []

    def getReturnLoc(self):
        """
        Determines path to return location of boat

        params: TBD
        returns: return destination of boat
        rtype: [float, float]
        """
        
        return []
    
    def calcTrajectory(self):
        """
        Determines trajectory from current location to destination location of boat

        params: TBD
        returns: next destination of boat
        rtype: [float, float]
        """
        
        return []

    def deviationThreshold(self):
        """
        Determines amount boat allowed to deviate from path

        params: TBD
        returns: amount boat is allowed to deviate from path
        rtype: float
        """
        
        return 0

    def areaCovered(self):
        """
        Determines area covered in current trajectory

        params: TBD
        returns: area covered in current trajectory
        rtype: float
        """
        
        return 0

############################## Naive Paths ##################################

    def pathForward(self):
        """
        Plans path of simple forward movement

        params: TBD
        returns: success state of path movement
        rtype: bool
        """
        
        return True

    def pathZigZag(self):
        """
        Plans path of zig zag movement

        params: TBD
        returns: success state of path movement
        rtype: bool
        """

        return True

    def pathSpiral(self):
        """
        Plans path of spiral movement

        params: TBD
        returns: success state of path movement
        rtype: bool
        """
        
        return True