from boat import Boat
from trash_sensor import Trash_Sensor

################################# Controls #####################################

class Controls:
    """ Manages controls and path planning of given boat """

    def __init__(self, boat = Boat(45), trash_sensor = Trash_Sensor()):
        """ Controls Class Constructor to initialize the object

        params:
        - Boat: boat object
        """
        self.lat = boat.curr_lat
        self.long = boat.curr_long
        self.ori = boat.orientation

        self.sensor = trash_sensor 

        self.tripDuration = 0 # at start of trip, no time has passed
    
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
        
        return []
    
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