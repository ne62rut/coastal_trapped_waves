import os
import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime
import time
from concurrent.futures import ProcessPoolExecutor
from scipy.signal import butter, filtfilt

from ctw_functions import butter_bandpass, butter_bandpass_filter, interpolate_nan, find_nearest_non_nan

# Function to check if a point is inside the parallelogram
def is_inside_parallelogram(lat, lon, vertices):
    """
    Check if a point (lat, lon) is inside the defined parallelogram
    """
    if lon < np.min(vertices[:, 0]) or lon > np.max(vertices[:, 0]):
        return False
    if lat < np.min(vertices[:, 1]) or lat > np.max(vertices[:, 1]):
        return False
    return True


# Function to check if a point is within a certain tolerance of another point
def is_close(a, b, tol=0.01):
    """Check if two floating-point numbers are within a certain tolerance."""
    return abs(a - b) < tol

# Function to reconstruct daily grids from filtered time series
def reconstruct_daily_grids(input_dir, original_grid_file, output_dir, start_date, end_date, parallelogram_vertices, test_days=5):
    # Start a timer to measure performance
    start_time = time.time()

    # Load the original grid to get the spatial structure (lat/lon dimensions)
    original_dataset = xr.open_dataset(original_grid_file)
    latitudes = original_dataset.latitude.values
    longitudes = original_dataset.longitude.values

    # Filter latitudes and longitudes based on the parallelogram
    lat_indices, lon_indices = [], []
    for lat_idx, lat in enumerate(latitudes):
        for lon_idx, lon in enumerate(longitudes):
            if is_inside_parallelogram(lat, lon, parallelogram_vertices):
                lat_indices.append(lat_idx)
                lon_indices.append(lon_idx)

    # Reduce latitudes and longitudes to the region of interest
    valid_latitudes = latitudes[np.unique(lat_indices)]
    valid_longitudes = longitudes[np.unique(lon_indices)]

    # Create a time range for the target dates
    time_range = pd.date_range(start=start_date, end=end_date, freq='D')
    #time_range = time_range[:test_days]  # Limit to the specified number of test days

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Initialize a dictionary to store all the time series data
    time_series_data = {}

    # Load all time series files (assuming format filtered_sla_lat_xx_lon_xx.nc) from input directory
    for file_name in os.listdir(input_dir):
        if file_name.startswith('filtered_sla') and file_name.endswith('.nc'):
            lat_lon_str = file_name.replace('filtered_sla_lat_', '').replace('.nc', '')
            lat_str, lon_str = lat_lon_str.split('_lon_')
            lat, lon = round(float(lat_str), 2), round(float(lon_str), 2)  # Round to two decimal places

            # Load the time series for this grid point
            ds = xr.open_dataset(os.path.join(input_dir, file_name))
            time_series_data[(lat, lon)] = ds['filtered_sla'].values
            ds.close()

    # For each day in the range, reconstruct the grid and save as NetCDF
    for day in time_range:
        print(f"Reconstructing grid for {day}")

        # Initialize an empty array for the grid (valid lat, valid lon)
        grid = np.full((len(valid_latitudes), len(valid_longitudes)), np.nan)

        # Iterate over each valid grid point and assign the value for the current day
        for lat_idx, lat in enumerate(valid_latitudes):
            for lon_idx, lon in enumerate(valid_longitudes):
                found = False

                # Check against each time series data point
                for (ts_lat, ts_lon), values in time_series_data.items():
                    if is_close(lat, ts_lat) and is_close(lon, ts_lon):
                        # Find the corresponding value for the current day
                        try:
                            # Extract the time array once
                            time_values = ds['time'].values

                            # Make sure the current day is in the time series
                            day_index = np.where(time_values == np.datetime64(day))[0]
                            
                            if day_index.size > 0:
                                grid[lat_idx, lon_idx] = values[day_index[0]]
                                found = True
                                break  # Exit loop after finding the correct data

                        except Exception as e:
                            print(f"Error accessing data for ({lat}, {lon}) on {day}: {e}")

#                 if not found:
#                     # Only print if the point truly has no corresponding time series data
#                     print(f"Missing time series for ({lat}, {lon})")

        # Create a new dataset for the current day
        filtered_dataset = xr.Dataset(
            {
                'sla': (['latitude', 'longitude'], grid)
            },
            coords={
                'latitude': valid_latitudes,
                'longitude': valid_longitudes,
                'time': pd.to_datetime([day])
            }
        )

        # Save the reconstructed grid for this day
        output_file = os.path.join(output_dir, f"filtered_grid_{day.strftime('%Y%m%d')}.nc")
        filtered_dataset.to_netcdf(output_file)
        print(f"Saved reconstructed grid for {day} to {output_file}")

    original_dataset.close()

    # End the timer and print the total processing time
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total processing time for reconstruction: {total_time:.2f} seconds")



# Main function to drive the reconstruction process
def main():
    input_dir = '/nfs/DGFI8/H/work_marcello/coastal_trapped_waves_data/filtered_grids_SWOT'
    output_dir = '/nfs/DGFI8/H/work_marcello/coastal_trapped_waves_data/filtered_daily_grids_SWOT_reconstructed'
    
    # Dynamically select any original grid file from the specified directory
    original_grid_dir = '/DGFI8/D/SWOT_L4/SWOT_Daily_Product_L4'
    original_grid_files = [f for f in os.listdir(original_grid_dir) if f.endswith('.nc')]
    
    if not original_grid_files:
        raise FileNotFoundError("No original grid files found in the specified directory.")

    original_grid_file = os.path.join(original_grid_dir, original_grid_files[0])  # Use the first file found
    print(f"Using original grid file: {original_grid_file}")

    start_date = datetime(2023, 8, 29)
    end_date = datetime(2023, 11, 30)

    # Define the vertices of the parallelogram (EAST_AUSTRALIA region)
    parallelogram_vertices = np.array([
        [149, -38],  # Bottom-left
        [158, -38],  # Bottom-right
        [158, -25],  # Top-right
        [149, -25]   # Top-left
    ])

    # Run reconstruction with a limit on the number of days to process
    reconstruct_daily_grids(input_dir, original_grid_file, output_dir, start_date, end_date, parallelogram_vertices, test_days=5)

if __name__ == "__main__":
    main()
