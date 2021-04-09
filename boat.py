############################### Trash Storage ##################################

MAX_LOAD = 5000 # max trash load capacity in kg

class Trash_Storage:
  def __init__(self):
    self.maxStorage = MAX_LOAD
    self.trashCapacity = 0
    self.conveyorOn = False

  def activateConveyor(self):
    return False
  
  def conveyorOn(self):
    return True
  
################################# Boat ########################################
MAX_SPEED = 10 # final max boat speed in range [5,10]

BOAT_LENGTH = 20 # final boat length in range [5, 20]
BOAT_WIDTH = 6 # final boat width in range [2, 6]
BOAT_HEIGHT = 6 # final boat height in range [2, 6]

class Boat:
  def __init__(self, start_lat = 0, start_long, fuel = 80, trash_stor = Trash_Storage()):

    # boat dimensions in meters
    self.length = BOAT_LENGTH
    self.width = BOAT_WIDTH
    self.height = BOAT_HEIGHT

    # boat speed
    self.maxSpeed = MAX_SPEED
    self.currSpeed = 0 # operational speed  in range [2,5]

    # coordinates
    self.start_lat = start_lat;
    self.start_long = start_long;
    self.curr_lat = start_lat;
    self.curr_long = start_long;
    self.fuel = fuel;
    self.amountTrash = 0
  
