import os
import time
from datetime import datetime
import xarray as xr
import numpy as np
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from scipy.signal import butter, filtfilt

from ctw_functions import butter_bandpass, butter_bandpass_filter, interpolate_nan, find_nearest_non_nan

# Define the vertices of the parallelogram for EAST_AUSTRALIA
parallelogram_vertices = np.array([
    [149, -38],  # Bottom-left
    [158, -38],  # Bottom-right
    [158, -25],  # Top-right
    [149, -25]   # Top-left
])

# Check if a point is inside the parallelogram
def is_inside_parallelogram(lat_grid, lon_grid, vertices):
    # Mask for points inside the bounding box (min/max lat/lon)
    mask_lon = (lon_grid >= vertices[:, 0].min()) & (lon_grid <= vertices[:, 0].max())
    mask_lat = (lat_grid >= vertices[:, 1].min()) & (lat_grid <= vertices[:, 1].max())
    return mask_lon & mask_lat

# Function to process each valid point and save to NetCDF in parallel
def process_grid_point(latitude, longitude, date_file_list, lowcut, highcut, fs, output_dir, case):
    sla_data = []
    date_list = []

    for file_date, file_path in date_file_list:
        dataset = xr.open_dataset(file_path)
        
        # Check if we are processing Bluelink, adjust the latitude/longitude dimensions accordingly
        if case == 'BLUELINK':
            lat_coord = dataset.yt_ocean
            lon_coord = dataset.xt_ocean
            sla_var = 'sla'
        else:  # SWOT or CMEMS
            lat_coord = dataset.latitude
            lon_coord = dataset.longitude
            sla_var = 'sla'

        # Find nearest indices to the specified latitude and longitude
        lat_idx = abs(lat_coord - latitude).argmin()
        lon_idx = abs(lon_coord - longitude).argmin()

        # Extract SLA at the specified point
        sla_data_point = dataset[sla_var].isel({lat_coord.dims[0]: lat_idx, lon_coord.dims[0]: lon_idx}).values.item()

        # Only proceed if the SLA point is non-NaN
        if not np.isnan(sla_data_point):
            sla_data.append(sla_data_point)
            date_list.append(file_date)
        else:
            # Attempt to find a nearby non-NaN value
            sla_data_point = find_nearest_non_nan(dataset, lat_idx, lon_idx)
            if not np.isnan(sla_data_point):
                sla_data.append(sla_data_point)
                date_list.append(file_date)

        dataset.close()

    if not sla_data:  # If no valid data collected, return NaN-filled arrays
        return latitude, longitude, np.nan, np.nan

    # Convert the list to xarray DataArray with time dimension
    time_index = pd.to_datetime(date_list)
    sla_time_series_da = xr.DataArray(sla_data, dims=['time'], coords={'time': time_index})

    # Apply the Butterworth bandpass filter if valid
    series = sla_time_series_da.values
    nan_count = np.isnan(series).sum()

    if nan_count <= 0.9 * len(sla_time_series_da.time):
        if nan_count > 0:
            series = interpolate_nan(series)  # Interpolate NaNs
        filtered_series = butter_bandpass_filter(series, lowcut, highcut, fs, order=5)
    else:
        filtered_series = np.full_like(series, np.nan)  # Create NaN-filled array

    # Save results to NetCDF
    save_to_netcdf(latitude, longitude, sla_time_series_da, filtered_series, output_dir)

    return latitude, longitude, series, filtered_series

def save_to_netcdf(lat, lon, unfiltered_series, filtered_series, output_dir):
    """Save the unfiltered and filtered series to NetCDF format."""
    file_name = f"filtered_sla_lat_{lat:.2f}_lon_{lon:.2f}.nc"
    output_path = os.path.join(output_dir, file_name)

    # Create a dataset with unfiltered and filtered SLA data
    ds = xr.Dataset(
        {
            "unfiltered_sla": xr.DataArray(unfiltered_series.values, dims=["time"], coords={"time": unfiltered_series.time}),
            "filtered_sla": xr.DataArray(filtered_series, dims=["time"], coords={"time": unfiltered_series.time})
        },
        coords={"latitude": lat, "longitude": lon}
    )

    # Save to NetCDF format
    ds.to_netcdf(output_path)
    #print(f"Saved {output_path}")

# Main processing function
def main():
    
    case = 'BLUELINK'  # Choose SWOT, CMEMS, or BLUELINK
    
    # CASE SWOT
    if case == 'SWOT':    
        base_dir = '/DGFI8/D/SWOT_L4/SWOT_Daily_Product_L4'
        output_dir = '/nfs/DGFI8/H/work_marcello/coastal_trapped_waves_data/filtered_grids_SWOT'
    
    elif case == 'CMEMS':            
        # CASE CMEMS
        base_dir = '/DGFI8/H/work_marcello/giussani_machinelearning_data/SEALEVEL_GLO_PHY_L4_NRT_008_046/2023'
        output_dir = '/nfs/DGFI8/H/work_marcello/coastal_trapped_waves_data/filtered_grids_CMEMS'
    
    elif case == 'BLUELINK':
        # CASE BLUELINK
        base_dir = '/DGFI8/D/SWOT_L4/Bluelink_Daily_Product_L4'
        output_dir = '/nfs/DGFI8/H/work_marcello/coastal_trapped_waves_data/filtered_grids_BLUELINK'

    os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists

    # Collect all NetCDF file paths and dates
    date_file_list = []
    start_date = datetime(2023, 8, 29)
    end_date = datetime(2023, 11, 30)

    if case == 'CMEMS':
        # Iterate through each month subdirectory "01" to "12"
        for month in range(1, 13):
            month_str = f"{month:02d}"  # Format month as "01", "02", ..., "12"
            month_dir = os.path.join(base_dir, month_str)
            if os.path.exists(month_dir):
                for file_name in os.listdir(month_dir):
                    if file_name.endswith('.nc'):
                        file_date_str = file_name.split('_')[-2]
                        file_date = datetime.strptime(file_date_str, "%Y%m%d")
                        if start_date <= file_date <= end_date:
                            file_path = os.path.join(month_dir, file_name)
                            date_file_list.append((file_date, file_path))

    elif case == 'SWOT':
        # For SWOT, just check the base directory
        for file_name in os.listdir(base_dir):
            if file_name.endswith('.nc'):
                file_date_str = file_name.split('_')[-2]
                file_date = datetime.strptime(file_date_str, "%Y%m%d")
                if start_date <= file_date <= end_date:
                    file_path = os.path.join(base_dir, file_name)
                    date_file_list.append((file_date, file_path))
    
    elif case == 'BLUELINK':
        # For BLUELINK, file naming is dt_global_allsat_phy_l4_YYYYMMDD.nc
        for file_name in os.listdir(base_dir):
            if file_name.endswith('.nc'):
                file_date_str = file_name.split('_')[-1].replace('.nc', '')  # Extract date part
                file_date = datetime.strptime(file_date_str, "%Y%m%d")
                if start_date <= file_date <= end_date:
                    file_path = os.path.join(base_dir, file_name)
                    date_file_list.append((file_date, file_path))

    date_file_list.sort()

    # Use a ProcessPoolExecutor to parallelize processing for each valid grid point
    with ProcessPoolExecutor() as executor:
        futures = []
        # Open a sample dataset to get lat/lon values
        sample_file_path = date_file_list[0][1] if date_file_list else None
        if sample_file_path:
            sample_dataset = xr.open_dataset(sample_file_path)
            
            if case == 'BLUELINK':
                latitudes = sample_dataset.yt_ocean.values
                longitudes = sample_dataset.xt_ocean.values
            else:
                latitudes = sample_dataset.latitude.values
                longitudes = sample_dataset.longitude.values

            # Create 2D grids of lat/lon using meshgrid
            lat_grid, lon_grid = np.meshgrid(latitudes, longitudes)

            # Get the mask for valid grid points within the parallelogram
            mask = is_inside_parallelogram(lat_grid, lon_grid, parallelogram_vertices)
            valid_lats = lat_grid[mask]
            valid_lons = lon_grid[mask]

            for latitude, longitude in zip(valid_lats, valid_lons):
                # Check if the SLA data point is non-NaN in the first sample dataset
                lat_idx = abs(latitudes - latitude).argmin()
                lon_idx = abs(longitudes - longitude).argmin()
                if case == 'BLUELINK':
                    sla_data_point = sample_dataset['sla'].isel(yt_ocean=lat_idx, xt_ocean=lon_idx).values.item()
                else:
                    sla_data_point = sample_dataset['sla'].isel(latitude=lat_idx, longitude=lon_idx).values.item()
                
                if not np.isnan(sla_data_point):
                    futures.append(executor.submit(process_grid_point, latitude, longitude, date_file_list, lowcut, highcut, fs, output_dir, case))

            # Retrieve results and print summary for the first few points
            for future in futures:
                latitude, longitude, unfiltered, filtered = future.result()
                #print(f"Processed point at lat: {latitude}, lon: {longitude}")

if __name__ == '__main__':
    # Define the frequency cutoffs for the filter
    lowcut = 0.035  # Lower cutoff in cycles per day
    highcut = 0.15  # Upper cutoff in cycles per day
    fs = 1.0  # Sampling frequency in cycles per day

    # Start a timer to measure performance
    start_time = time.time()
    main()  # Call the main processing function
    end_time = time.time()
    #print(f"Processing completed in {end_time - start_time:.2f} seconds.")

