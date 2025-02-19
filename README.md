# coastal_trapped_waves

# Input needed

1) The tide gauge data are an extension of the GESLA dataset: https://www.gesla.org/ They were obtained courtesy of Ivan Haigh (National Oceanography Centre, University of Southampton). 
2) The Bluelink Ocean Reanalysis - BRAN2020 (BLUELINK) data were downloaded from in August 2024 from https://geonetwork.nci.org.au/. 
3) The CMEMS data is the SEALEVEL_GLO_PHY_L4_MY_008_047 downloaded from https://marine.copernicus.eu/ downloaded first in August 2024 (Version DT2021) and then in February 2025 (Version DT2024). 
4) The MIOST data is the "Experimental multimission gridded L4 sea level heights and velocities with SWOT" product available from https://doi.org/10.24400/527896/A01-2024.007, downloaded in July 2024.
5) To correct the tide gauges for the atmospheric component, the Dynamic Atmospheric Correction (DAC) must be obtained from https://www.aviso.altimetry.fr/en/data/products/auxiliary-products/dynamic-atmospheric-correction.html


# Warning

When using the python code and the notebooks, you will have to actively look for the directories and adapt the locations based on where your inputs and outputs are saved


# How to process

1. gesla_processing_australia2023addon.ipynb 
    takes high-frequency tide gauge records from GESLA 3, averages them as hourly records, select for a specific year and region, smooths them by means of a lowess filter to remove tide contributions and correct them for the Dynamic Atmospheric Correction. The whole processing is needed to make GESLA dataset comparable to altimetry estimations. This particular code is adapted to process tide gauges in Australia for 2023, which are not yet part of GESLA 3. The original general code is gesla_processing.ipynb
    
2. model_data_reader.ipynb
    takes data from the bluelink reanalysis and saves them as daily grids similar to MIOST format 

3. create_filtered_time_series_tg.ipynb 
    isolates a set of TGs in Australia and filter them (saving the filtered version externally). Generates the figure area_of_study.jpg
    
    
4. create_filtered_time_series.py
    takes L4 products and create for each grid point a time series filtered in time, which is saved separately
    
5. create_filtered_grids.py 
    from the output of 3. reconstructs a daily L4 product, containing the signal filtered in time. There is also a ipynb version of it showing some plots.
    
6. correlate_tg_with_grids.ipynb
    takes the output of 2. (filtered tide gauges time series) and 3. (filtered altimetry time series) and correlate them, by offering the possibility to select a lag correlation. Generate the corresponding figures for the paper.

7. correlate_tg_with_grids_1d.ipynb 
    compare the time series with a filtered version of CMEMS and MIOST maps at the closest location to the tide gauges. Generates the figures: corr_examples.jpg and corr_bar_plot.jpg
    
8. phase_speed_computation.ipynb 
    compare the Hovmoller diagrams of the filtered signals and compute the phase speed with the radon transform. Generate the figures: hovmuller.jpg

9. EOF_analysis.ipynb 
    EOF analysis of the datasets along the coastal points. Generates the figures: EOF_PC_comparison.jpg and EOF_evolution.jpg (as well as a corresponding gif video)





