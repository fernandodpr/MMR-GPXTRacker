# GPX Tracker Plugin

The GPX Tracker plugin for Meshtastic allows you to log location data from your mesh network devices into individual GPX files. Each device's track is stored separately and organized by date, making it easy to manage and analyze location data for your devices.

## Features
- Automatically creates and updates GPX files for each device in the mesh network.
- Tracks data by date, ensuring organized and chronological records.
- Compatible with GPX visualization tools for further analysis and mapping.

## Usage
Simply add the plugin to your Meshtastic setup, and it will automatically handle incoming location data from the network.

```yaml
community-plugins:
  gpxtracker:
    active: true
    repository: https://github.com/fernandodpr/MMR-GPXTRacker.git
    tag: main
    gpx_directory: "./data/gpx_data"
    allowed_device_ids:
      - "fd3e19c2"  # Example (random ID)
      - "*" # To save all location messages that are received.
```

## Ethical and Legal Considerations
Be aware that tracking and logging location data from Meshtastic devices without the explicit consent of users may be a violation of privacy laws or ethical guidelines in your jurisdiction. Always ensure that all parties are informed and have given their consent to the use of this plugin.

## Upcoming Features
We welcome your suggestions! Please share your ideas in the Issues section.

## License
See the LICENSE file for more details.
