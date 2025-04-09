import sqlite3
from smarthouse.domain import SmartHouse, Room, Device, Sensor, Actuator, Measurement

class SmartHouseRepository:
    def __init__(self, db_path):
        self.db_path = db_path

    def cursor(self):
        conn = sqlite3.connect(self.db_path)
        return conn.cursor()

    def load_smarthouse_deep(self):
        """
        Retrieves the complete single instance of the SmartHouse
        object stored in this database, including floors, rooms, and devices.
        """
        cursor = self.cursor()

        # Load floors (assuming no table for floors, just rooms with a floor level)
        cursor.execute("SELECT DISTINCT floor FROM rooms")
        floor_levels = cursor.fetchall()

        smarthouse = SmartHouse()

        # Create floors
        floors = {}
        for floor_level in floor_levels:
            floor = smarthouse.register_floor(floor_level[0])
            floors[floor_level[0]] = floor

        # Load rooms and assign them to floors
        cursor.execute("SELECT * FROM rooms")
        rooms = cursor.fetchall()
        for room in rooms:
            floor = floors[room[1]]  # Assuming room[1] is the floor_level
            smarthouse.register_room(floor, room[2], room[3])  # room[2] is room size, room[3] is room name

        # Load devices and assign them to rooms
        cursor.execute("SELECT * FROM devices")
        devices = cursor.fetchall()
        for device in devices:
            room = smarthouse.get_room_by_id(device[1])  # Assuming device[1] is room_id
            if device[4] == "actuator":
                dev = Actuator(device[0], device[2], device[3], device[4])
            elif device[4] == "sensor":
                dev = Sensor(device[0], device[2], device[3], device[4], device[5])  # Assuming unit is device[5]
            smarthouse.register_device(room, dev)

        return smarthouse

    def get_latest_reading(self, sensor):
        """
        Retrieves the most recent sensor reading for the given sensor if available.
        """
        cursor = self.cursor()
        cursor.execute("""
            SELECT * FROM measurements
            WHERE device_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (sensor.id,))
        result = cursor.fetchone()

        if result:
            return Measurement(result[1], result[2], result[3])  # Assuming (timestamp, value, unit)
        return None

    def update_actuator_state(self, actuator):
        """
        Saves the state of the given actuator in the database.
        """
        cursor = self.cursor()
        cursor.execute("""
            UPDATE devices
            SET state = ?
            WHERE id = ?
        """, (actuator.state, actuator.id))
        cursor.connection.commit()

    def calc_avg_temperatures_in_room(self, room, from_date=None, until_date=None):
        """
        Calculates the average temperatures in the given room for the given time range.
        """
        cursor = self.cursor()

        # Build the SQL query with optional date filtering
        query = """
            SELECT AVG(value)
            FROM measurements
            WHERE device_id IN (SELECT id FROM devices WHERE room_id = ?)
            AND unit = 'Celsius'  -- Assuming we are measuring temperature in Celsius
        """

        params = [room.id]

        if from_date:
            query += " AND timestamp >= ?"
            params.append(from_date)

        if until_date:
            query += " AND timestamp <= ?"
            params.append(until_date)

        cursor.execute(query, tuple(params))
        result = cursor.fetchone()

        if result:
            return result[0]
        return None

    def calc_hours_with_humidity_above(self, room, date):
        """
        Determines which hours of the given day had more than three measurements
        with humidity above the average recorded humidity in that room.
        """
        cursor = self.cursor()

        # First, calculate the average humidity in the room on that day
        cursor.execute("""
            SELECT AVG(value)
            FROM measurements
            WHERE device_id IN (SELECT id FROM devices WHERE room_id = ?)
            AND unit = 'Humidity'
            AND DATE(timestamp) = ?
        """, (room.id, date))
        avg_humidity = cursor.fetchone()[0]

        if avg_humidity is None:
            return []

        # Now find the hours with more than 3 measurements above the average humidity
        cursor.execute("""
            SELECT strftime('%H', timestamp) AS hour, COUNT(*)
            FROM measurements
            WHERE device_id IN (SELECT id FROM devices WHERE room_id = ?)
            AND unit = 'Humidity'
            AND DATE(timestamp) = ?
            AND value > ?
            GROUP BY hour
            HAVING COUNT(*) > 3
        """, (room.id, date, avg_humidity))

        result = cursor.fetchall()
        return [int(row[0]) for row in result]


class Persistence:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_repository(self):
        return SmartHouseRepository(self.db_path)
