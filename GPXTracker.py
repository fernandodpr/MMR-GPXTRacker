from plugins.base_plugin import BasePlugin
from datetime import datetime, timezone
import gpxpy
import os

class Plugin(BasePlugin):
    plugin_name = "gpxtracker"

    
    def __init__(self, config_file='config.yaml'):
        super().__init__()
        # Load configuration options
        self.allowed_device_ids = self.config.get('allowed_device_ids', ["*"])
        self.gpx_directory = self.config.get('gpx_directory', './data/gpx_data')


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

        # Ensure the message is valid and contains the necessary data
        decoded = packet.get("decoded", {})
        position = decoded.get("position", {})
        if not decoded or decoded.get("portnum") != "POSITION_APP" or not position or "precisionBits" not in position:
            return

        # Extract device ID
        device_id_raw = packet.get("fromId", "")
        device_id_hex = device_id_raw.lstrip("!")

        # Check if the device is allowed or if wildcard is enabled
        if "*" not in self.allowed_device_ids and device_id_hex not in self.allowed_device_ids:
            self.logger.debug(f"Device ID {device_id_hex} sent a location but is not in the allowed list. Ignoring message.")
            return

        # Extract position data
        latitude = position.get("latitude")
        longitude = position.get("longitude")
        altitude = position.get("altitude", 0)

        now = datetime.now(tz=timezone.utc)
        track_name = now.strftime("%Y-%m-%d")

        # Create GPX file path
        gpx_file_path = os.path.join(self.gpx_directory, f"{device_id_hex}.gpx")

        # Log processed data
        self.logger.info(f"Processed data from Device={device_id_hex}: Latitude={latitude}, Longitude={longitude}, Altitude={altitude}, track_name={track_name}, Path={gpx_file_path}")

        # Load or create GPX file
        try:
            if os.path.exists(gpx_file_path):
                with open(gpx_file_path, "r") as gpx_file:
                    gpx = gpxpy.parse(gpx_file)
            else:
                gpx = gpxpy.gpx.GPX()
        except Exception as e:
            self.logger.error(f"Error loading or creating GPX file {gpx_file_path}: {e}")
            return

        # Create or find the track for the current day
        track = next((t for t in gpx.tracks if t.name == track_name), None)
        if not track:
            track = gpxpy.gpx.GPXTrack(name=track_name)
            gpx.tracks.append(track)

        # Create a segment if none exists
        if not track.segments:
            track.segments.append(gpxpy.gpx.GPXTrackSegment())
        segment = track.segments[0]

        # Add a point to the segment
        point = gpxpy.gpx.GPXTrackPoint(latitude, longitude, elevation=altitude, time=now)
        segment.points.append(point)

        # Save the GPX file
        try:
            with open(gpx_file_path, "w") as gpx_file:
                gpx_file.write(gpx.to_xml())
            self.logger.debug(f"Data saved in {gpx_file_path} for device {device_id_hex}")
        except Exception as e:
            self.logger.error(f"Error saving GPX file {gpx_file_path}: {e}")


    async def handle_room_message(self, room, event, full_message):
        """Placeholder for Matrix messages (if needed)."""
        return
