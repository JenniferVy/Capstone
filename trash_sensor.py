############################### Trash Sensor ###################################

TRASH_SIZE = 5 # default trash size, collecting macro and above
TRASH_SENSOR_RADIUS = 10

class Trash_Sensor:
  """

  """
  def __init__(self, enviro = Environment()):
    # TODO: establish trash size ranges
    self.trash_size = TRASH_SIZE
    self.sensor_radius = TRASH_SENSOR_RADIUS

  def detectTrash(self):
    """
    Detects trash of trash_size within radius of sensor_radius

    params: None
    returns: latitude and longitude of closest trash surpassing trash size in radius
    rtype: [float, float]
    """
    # TODO: detect trash and return its coordinates
    return []
