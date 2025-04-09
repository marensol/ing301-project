# smarthouse/domain.py

class Room:
    def __init__(self, id, floor, size, name):
        self.id = id
        self.floor = floor
        self.size = size
        self.name = name
        self.devices = []

    def add_device(self, device):
        self.devices.append(device)

class Floor:
    def __init__(self, level):
        self.level = level

class Device:
    def __init__(self, id, name, type, state=None):
        self.id = id
        self.name = name
        self.type = type
        self.state = state

class Sensor(Device):
    def __init__(self, id, name, type, unit, state=None):
        super().__init__(id, name, type, state)
        self.unit = unit

class Actuator(Device):
    def __init__(self, id, name, type, state=None):
        super().__init__(id, name, type, state)

class Measurement:
    def __init__(self, value, timestamp):
        self.value = value
        self.timestamp = timestamp

class SmartHouse:
    def __init__(self):
        self.floors = {}  # Store floors using a dictionary
        self.rooms = {}   # Store rooms using a dictionary
        self.devices = {}  # Store devices using a dictionary
        self.measurements = []  # Store measurements (for later use in repository)

    def register_floor(self, floor_level):
        # Register a floor and return a Floor object
        floor = Floor(floor_level)
        self.floors[floor_level] = floor
        return floor

    def get_floor(self, floor_level):
        # Get a floor by its level
        return self.floors.get(floor_level)

    def register_room(self, floor, size, name):
        # Register a room and return the room object
        room_id = len(self.rooms) + 1  # Unique ID for the room
        room = Room(room_id, floor, size, name)
        self.rooms[room_id] = room
        return room

    def get_room_by_id(self, room_id):
        # Retrieve a room by its ID
        return self.rooms.get(room_id)

    def register_device(self, room, device):
        # Register a device to a room
        room.add_device(device)
        self.devices[device.id] = device

    def get_device_by_id(self, device_id):
        # Get a device by its ID
        return self.devices.get(device_id)

    def add_measurement(self, measurement):
        # Store a measurement
        self.measurements.append(measurement)

    def get_measurements(self):
        # Return all measurements
        return self.measurements
