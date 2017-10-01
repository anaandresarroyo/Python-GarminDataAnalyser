# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo

Reads a records .csv file and plots the coordinates in a html file
"""

import os
import pandas as pd
import gmplot
    
    
if __name__ == '__main__':

    directory_path_read = 'C:/Users/Ana Andres/Documents/Garmin/csv/'
#    directory_path_read = 'C:/Users/Ana Andres/Documents/Garmin/2017 USA/csv/'
    directory_path_save = 'C:/Users/Ana Andres/Documents/Garmin/figures/'
#    directory_path_save = 'C:/Users/Ana Andres/Documents/Garmin/2017 USA/figures/'

    map_name = 'mymap.html'
    
    sports = [
             'all',
#             'walking',
#             'cycling',
#             'running',
#             'driving',
#             'train',
#             'water',
#             'training',
#             'test',
#             'lucia',
             ]
    colours = {'walking':'g',
               'cycling':'k',
               'running':'r',
               'driving':'b',
               'train': 'm',
               'water': 'c',
               'training':'m',
               'test':'g',
               'lucia':'k',
               'all':'k',
               }
    
    plot_map=True
    
    # ---------------------------------------
    
    # select files to read     
    file_paths = []    
    file_sports = []
    for sport in sports:
        directory_path_sport = directory_path_read + sport + '/'
#        directory_path_sport = directory_path_read
#        for file_name in os.listdir(directory_path_sport):
        for file_name in reversed(os.listdir(directory_path_sport)):
            file_paths.append(directory_path_sport + file_name)
            file_sports.append(sport)    
    
    if plot_map:
        gmap = gmplot.GoogleMapPlotter(52.202, 0.12, 13) # Cambridge 
#        gmap = gmplot.GoogleMapPlotter(43, -120, 5) # USA West Coast
#        gmap = gmplot.GoogleMapPlotter(46.36, 14.09, 11) # Lake Bled
    
#    number_of_files = 1
    number_of_files = len(file_paths);
    for file_path, sport, ifn in zip(file_paths, file_sports, range(number_of_files)):
        verbose=True
        if verbose:
            print "%s / %s: %s" % (ifn+1, number_of_files, sport)
        # Read data from .csv file
        df = pd.read_csv(file_path)
        verbose=False
        if verbose:
            print file_path
            print df['timestamp'][0]
            print
        

        if plot_map:
            # Add a line plot to the gmap object which will be save to an .html file
            # Use line instead of scatter plot for faster speed and smaller file size
            # Make sure to remove NaNs or the plot won't work
            gmap.plot(df['position_lat'].dropna()*180/2**31, df['position_long'].dropna()*180/2**31, 
                      color=colours[sport], edge_width=3)
        

    if plot_map:
        gmap.draw(directory_path_save + map_name)