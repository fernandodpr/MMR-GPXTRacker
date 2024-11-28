# GPX Tracker Plugin

> ⚠ **Upcoming Breaking Change**
>
> Starting with the next version, you’ll need to explicitly configure tracked devices. For now, the plugin defaults to logging all devices (`allowed_device_ids: ["*"]`) for compatibility, but this will change in future releases.

The GPX Tracker plugin for Meshtastic allows you to log location data from your mesh network devices into individual GPX files. Each device's track is stored separately and organized by date, making it easy to manage and analyze location data for your devices.

## Features
*   **Per-Device GPX Logging**:
    - Per-Device GPX Logging: Logs detailed GPX tracks for each device ID specified in the allowed_device_ids list.
    - Tracks data by date, ensuring organized and chronological records.
    - Compatible with GPX visualization tools for further analysis and mapping.
*   **Global Coverage Map**:
    *   Logs anonymized locations into a single GPX file (`global_coverage.gpx`).
    *   Configurable via the `log_global_coverage` option.
    *   Anonymization precision can be adjusted with `coverage_resolution` (default: 4, minimum: 4).


## Usage
Simply add the plugin to your Meshtastic setup, and it will automatically handle incoming location data from the network.

```yaml
community-plugins:
  gpxtracker:
    active: true
    repository: https://github.com/fernandodpr/MMR-GPXTRacker.git
    tag: dev  # Use 'dev' branch for the latest features
    gpx_directory: "./data/gpx_data"  # Directory where GPX files will be stored
    allowed_device_ids:
      - "fd3e19c2"  # Example (specific device ID)
      - "*"         # Wildcard to save all location messages
    log_global_coverage: true  # Enable or disable coverage map logging
    coverage_resolution: 4     # Resolution for anonymized coverage map (minimum: 4)
```
### **Configuration Options**

*   **`active`**: Enables/disables the plugin. (`true` = active, `false` = inactive)
*   **`repository`**: URL of the plugin’s Git repository.
*   **`tag`**: Branch or tag to use (`main` for stable, `dev` for latest features).
*   **`gpx_directory`**: Directory where GPX files are saved (default: `./data/gpx_data`).
*   **`allowed_device_ids`**: List of device IDs to log; use `*` to log all devices.
*   **`log_global_coverage`**: Logs anonymized locations into a single global GPX file (`true` = enabled).
*   **`coverage_resolution`**: Decimal precision for anonymized locations; minimum is 4 (e.g., 4 = ~111m accuracy).

## Ethical and Legal Considerations
Be aware that tracking and logging location data from Meshtastic devices without the explicit consent of users may be a violation of privacy laws or ethical guidelines in your jurisdiction. Always ensure that all parties are informed and have given their consent to the use of this plugin.

## Upcoming Features
We welcome your suggestions! Please share your ideas in the Issues section.

## License
See the LICENSE file for more details.
