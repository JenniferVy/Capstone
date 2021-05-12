from boat import Boat
from trash_sensor import Trash_Sensor
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

MOTOR_MAX_SPEED = 125.7 # Motors have a max speed of 1200 RPM = 125.7 rad/s

HEADING_P = 0.22 # Input: heading_err [rad]; Output: ang_vel_sp [rad/s]
SIDEWAYS_VEL_P = 0.01 # Input: sideways_vel_err [m/s]; Output: ang_vel_sp [rad/s]
FORWARD_VEL_PID = (200, 25, 0) # Input: forward_vel_err [m/s]; Output: motor_speed [rad/s]. TODO may need some derivative control to compensate for motor acceleration time
FORWARD_VEL_FF = 0 # Input: forward_vel_sp^2 [(m/s)^2]; Output: motor_speed [rad/s]. TODO if integral works well enough, might not need feedforward 
ANG_VEL_PID = (1500, 10, 0) # Input: ang_vel_err [rad/s]; Output: motor_speed [rad/s]
ANG_VEL_FF = 0 # Input: ang_vel_sp^2 [(rad/s)^2]; Output: motor_speed [rad/s]

################################# Controls #####################################

class Controls:
    """ Manages controls and path planning of given boat """

    def __init__(self, boat, trash_sensor):
        """ Controls Class Constructor to initialize the object

        params:
        - Boat: boat object
        """
        self.boat = boat
        self.sensor = trash_sensor 

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

        self.motor_control(l_motor_speed, r_motor_speed, dt)
    
    def global_velocity_control(self, v_sp, dt):
        heading = -math.radians(self.boat.angle) + math.pi/2
        forward_vel = np.dot(self.boat.lin_vel, self.boat.direction)
        sideways_vel = np.linalg.norm(self.boat.lin_vel - (forward_vel * self.boat.direction))

        forward_vel_sp = np.dot(v_sp, self.boat.direction)
        sideways_vel_sp = np.linalg.norm(v_sp - (forward_vel_sp * self.boat.direction))
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

        self.local_velocity_control(forward_vel_sp, ang_vel_sp, dt)

    def local_velocity_control(self, forward_vel_sp, ang_vel_sp, dt):
        forward_vel = np.dot(self.boat.lin_vel, self.boat.direction)
        ang_vel = -self.boat.ang_vel

        # If feedforward is set, it adds a control signal proportional to the sqaure of the velocity, which helps overcome drag without relying as much on integral control.
        forward_vel_control = self.forward_vel_pid.send([forward_vel, forward_vel_sp, dt]) + FORWARD_VEL_FF * abs(forward_vel_sp) * forward_vel_sp
        ang_vel_control = self.ang_vel_pid.send([ang_vel, ang_vel_sp, dt]) + ANG_VEL_FF * abs(ang_vel_sp) * ang_vel_sp

        l_motor_speed = forward_vel_control + ang_vel_control
        r_motor_speed = forward_vel_control - ang_vel_control

        self.motor_control(l_motor_speed, r_motor_speed, dt)

    def motor_control(self, l_motor_speed, r_motor_speed, dt):
        # Desaturate motor commands. TODO could change this to prioritize turning.

        if (l_motor_speed > MOTOR_MAX_SPEED):
            l_motor_speed = MOTOR_MAX_SPEED
        if (r_motor_speed > MOTOR_MAX_SPEED):
            r_motor_speed = MOTOR_MAX_SPEED

        if (l_motor_speed < 0):
            l_motor_speed = 0
        if (r_motor_speed < 0):
            r_motor_speed = 0

        self.boat.update(l_motor_speed, r_motor_speed, dt)

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