#!/usr/bin/env python
# coding: utf-8

# In[ ]:
from scipy.signal import butter, filtfilt
import numpy as np

# Define the Butterworth bandpass filter
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data, axis=0)
    return y

def interpolate_nan(data):
    """Interpolate NaNs in the data."""
    nans, x = np.isnan(data), lambda z: z.nonzero()[0]
    data[nans] = np.interp(x(nans), x(~nans), data[~nans])
    return data

def find_nearest_non_nan(dataset, lat_idx, lon_idx):
    """Find the nearest non-NaN value in the dataset around the given indices."""
    max_radius = 5  # Define the maximum search radius
    for radius in range(1, max_radius + 1):
        for dlat in range(-radius, radius + 1):
            for dlon in range(-radius, radius + 1):
                if abs(dlat) == radius or abs(dlon) == radius:
                    new_lat_idx = lat_idx + dlat
                    new_lon_idx = lon_idx + dlon
                    if (0 <= new_lat_idx < dataset.dims['latitude']) and (0 <= new_lon_idx < dataset.dims['longitude']):
                        sla_data_point = dataset['sla'].isel(latitude=new_lat_idx, longitude=new_lon_idx).values.item()
                        if not np.isnan(sla_data_point):
                            return sla_data_point
    return np.nan

