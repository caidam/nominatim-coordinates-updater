Data Engineering Technical Test

# Nominatim API Address Coordinates Updater

This script is designed to update address coordinates using the Nominatim API. It fetches latitude and longitude for addresses from a given dataset and updates a MySQL database with the obtained coordinates.

## Requirements

- Python 3.x
- Packages: `pwd`, `time`, `tqdm`, `requests`, `pandas`, `sqlalchemy`

## Usage

1. Install the required Python packages using pip:

   ```bash
   pip install pwd time tqdm requests pandas sqlalchemy
   ```
2. Run the script:

   ```bash
   python wcs_updatecoordinates.py
   ```
## Description

The script uses the Nominatim API to fetch latitude and longitude for addresses in a MySQL database. It then updates the database with the obtained coordinates.

The script is divided into two main functions:
- `fetch(address)`: Calls the Nominatim API for a given address and returns the response.
- `update_coordinates(engine, tablename)`: Updates the latitude and longitude columns in the specified database table using the Nominatim API.

The script also includes an additional SQL query to find the customer with the highest number of rentals.

## Note

Ensure you have the necessary permissions and access to the MySQL database specified in the script.

---

**Disclaimer:** Respect Nominatim's usage policy and adhere to rate limits and terms of use.

For more information, refer to the [Nominatim Usage Policy](https://operations.osmfoundation.org/policies/nominatim/)
