from plugins.base_plugin import BasePlugin
from datetime import datetime, timezone
import gpxpy
import os

class Plugin(BasePlugin):
    plugin_name = "gpxtracker"
    
    def __init__(self):
        super().__init__()

        # Load configuration options
        self.allowed_device_ids = self.config.get('allowed_device_ids', ["*"]) # Will change to [] ASAP. When MMR project merges PR
        self.gpx_directory = self.config.get('gpx_directory', './data/gpx_data')
        self.log_global_coverage = self.config.get('log_global_coverage', False)  # New option for global coverage logging
        self.coverage_resolution = self.config.get('coverage_resolution', 4)  # New option for global coverage resolution (Hardcoded minimum of 4)
        
        # Create an instance of GPXHandler
        self.gpx_handler = GPXHandler(self.gpx_directory, self.logger)
        # Warn if no allowed device IDs are set
        if not self.allowed_device_ids:
            self.logger.warning("[CONFIG_WARNING] Allowed device IDs list is empty. No locations will be logged.")

        # Ensure the GPX directory exists
        try:
            os.makedirs(self.gpx_directory, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Failed to prepare GPX directory '{self.gpx_directory}': {e}")

    async def handle_meshtastic_message(self, packet, formatted_message, longname, meshnet_name):
        """
        Handles Meshtastic messages and updates the GPX file for the corresponding device.
        """
        try:
            # Ensure the message is valid and contains the necessary data
            decoded = packet.get("decoded", {})
            position = decoded.get("position", {})
            if not decoded or decoded.get("portnum") != "POSITION_APP" or not position or "precisionBits" not in position:
                return

            # Extract device ID
            device_id_raw = packet.get("fromId", "")
            device_id_hex = device_id_raw.lstrip("!")
            # Extract position data
            latitude = position.get("latitude")
            longitude = position.get("longitude")
            altitude = position.get("altitude", 0)
            # Generate track name and file path
            now = datetime.now(tz=timezone.utc)
            track_name = now.strftime("%Y-%m-%d")
            gpx_file_path = os.path.join(self.gpx_directory, f"{device_id_hex}.gpx")

            # Check if the device is allowed or if wildcard is enabled
            if "*" in self.allowed_device_ids or device_id_hex in self.allowed_device_ids:
                # Save the location and log to debug
                self.gpx_handler.add_location_to_gpx(
                    latitude=latitude,
                    longitude=longitude,
                    altitude=altitude,
                    track_name=track_name,
                    file_path=gpx_file_path,
                    timestamp=now
                )
                self.logger.info(f"Processed data from Device={device_id_hex}: Latitude={latitude}, Longitude={longitude}, Altitude={altitude}, track_name={track_name}, Path={gpx_file_path}")

            else:
                self.logger.debug(f"Device ID {device_id_hex} is not in the allowed list. Ignoring message.")

            if self.log_global_coverage:
                self.logger.debug(f"Coverage logging enabled. Anonymizing and saving location for global track.")
                coverage_file_path = os.path.join(self.gpx_directory, "coverage_map.gpx")
                self.gpx_handler.anonymize_and_save(
                    latitude=latitude,
                    longitude=longitude,
                    altitude=altitude,
                    file_path=coverage_file_path,
                    track_name="global_coverage",
                    resolution=self.coverage_resolution
                )

        except Exception as e:
            self.logger.error(f"Error handling Meshtastic message: {e}")   

    async def handle_room_message(self, room, event, full_message):
        """Placeholder for Matrix messages (if needed)."""
        return


class GPXHandler:
    def __init__(self, gpx_directory, logger):
        self.gpx_directory = gpx_directory
        self.logger = logger

    def add_location_to_gpx(self, latitude, longitude, altitude, track_name, file_path, timestamp=None):
        """
        Adds a location to a GPX file for the specified track.
        Parameters:
            latitude (float): Latitude of the location.
            longitude (float): Longitude of the location.
            altitude (float): Altitude of the location (optional).
            track_name (str): The name of the track to which the location should be added.
            file_path (str): The file path where the GPX data is stored.
            timestamp (datetime, optional): Timestamp of the location. If None, no timestamp is recorded (anonymization).
        """
        try:
            # Load or create the GPX file
            gpx = self.load_gpx(file_path)

            # Find or create the track
            track = self.get_or_create_track(gpx, track_name)

            # Create the location point
            point = gpxpy.gpx.GPXTrackPoint(latitude, longitude, elevation=altitude, time=timestamp)

            # Add the point to the track
            self.add_point_to_track(track, point)

            # Save the GPX file
            self.save_gpx(gpx, file_path)
            self.logger.debug(f"Location saved to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to add location to GPX: {e}")

    def load_gpx(self, file_path):
        """Loads or creates a GPX file."""
        if os.path.exists(file_path):
            with open(file_path, "r") as gpx_file:
                return gpxpy.parse(gpx_file)
        return gpxpy.gpx.GPX()

    def save_gpx(self, gpx, file_path):
        """Saves a GPX file to the specified path."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as gpx_file:
            gpx_file.write(gpx.to_xml())

    def get_or_create_track(self, gpx, track_name):
        """Finds or creates a GPX track by name."""
        track = next((t for t in gpx.tracks if t.name == track_name), None)
        if not track:
            track = gpxpy.gpx.GPXTrack(name=track_name)
            gpx.tracks.append(track)
        return track

    def add_point_to_track(self, track, point):
        """Adds a point to the first segment of a GPX track."""
        if not track.segments:
            track.segments.append(gpxpy.gpx.GPXTrackSegment())
        track.segments[0].points.append(point)

    def anonymize_and_save(self, latitude, longitude, altitude, file_path, track_name="anonymized-track", resolution=4):
        """
        Anonymizes the location data, checks for duplicates, and saves it to the specified GPX file.
        Parameters:
            latitude (float): Latitude of the location.
            longitude (float): Longitude of the location.
            altitude (float): Altitude of the location (optional).
            file_path (str): The file path where the anonymized GPX data is stored.
            track_name (str): The name of the track to which the anonymized location should be added.
            resolution (int): Number of decimal places to retain for latitude and longitude (default is 4).
        """ 
        try:
            # Ensure resolution is not less than 4
            if resolution < 4:
                self.logger.warning(f"Resolution {resolution} is too low. Setting to minimum resolution of 4.")
                resolution = 4
            # Reduce precision for anonymization
            latitude = round(latitude, resolution)
            longitude = round(longitude, resolution)

            # Load or create the GPX file
            gpx = self.load_gpx(file_path)

            # Check for duplicate points
            if self.is_duplicate_point(gpx, latitude, longitude):
                #Placeholder for managing the GPX Extensions RSSI and SNR
                return

            # Add anonymized location to the GPX file
            self.add_location_to_gpx(
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
                track_name=track_name,
                file_path=file_path,
                timestamp=None
            )
        except Exception as e:
            self.logger.error(f"Error during anonymization process: {e}")

    def is_duplicate_point(self, gpx, latitude, longitude, threshold=0.0001):
        """
        Checks if a given point already exists in the GPX file.
        Parameters:
            gpx (gpxpy.gpx.GPX): The GPX object to search.
            latitude (float): Latitude of the point.
            longitude (float): Longitude of the point.
            threshold (float): Distance threshold for considering points as duplicates.
        Returns:
            bool: True if the point is a duplicate, False otherwise.
        """
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    if abs(point.latitude - latitude) < threshold and abs(point.longitude - longitude) < threshold:
                        return True
        return False