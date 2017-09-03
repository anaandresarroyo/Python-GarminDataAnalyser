# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo

Reads Garmin database entries.
"""

from MatplotlibSettings import *
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == '__main__':
    
    database_path = 'C:/Users/Ana Andres/Documents/Garmin/database/Garmin-Ana.csv'
    
    df = pd.read_csv(database_path, 
                     parse_dates='start_time',
                     index_col='start_time',
                     )
    sports = df['sport'].unique()
    
    colours = {'walking':'g',
               'cycling':'b',
               'running':'r',
               'driving':'b',
               'train': 'm',
               'water': 'c',
               'training':'m',
               'test':'g',
               'lucia':'k',
               }
    
    label_x = 'daytime'
    label_y = 'weekday'
    label_z = 'avg_speed'
    labels = [label_x, 
              label_y, 
              label_z,
              ]
    plot_data = dict.fromkeys(labels)
    date_range = '05-2017'
    weekday = '0' # 0 Monday, ... 6 Sunday
    #sports = {'cycling'}
    
    
    for sport in sports:
        print sport + ': ' + str(df['sport'].str.match(sport).sum())# + '\n'
        try:
            for label in labels:
                print label
                if label == 'hour':
                    plot_data[label] = df[df['sport']==sport].loc[date_range,:].index.hour        
                elif label == 'daytime':
                    plot_data[label] = df[df['sport']==sport].loc[date_range,:].index.time        
                elif label == 'weekday':
                    plot_data[label] = df[df['sport']==sport].loc[date_range,:].index.weekday        
                else:
                    plot_data[label] = df[df['sport']==sport].loc[date_range,label].values
                        
            if len(plot_data) == 2:
                plt.plot(plot_data[label_x], plot_data[label_y], label=sport,
                         linestyle='None', marker='.', markersize=22)
    
            elif len(plot_data) == 3:
                plt.scatter(plot_data[label_x], plot_data[label_y], 
                            s=plot_data[label_z]*100, 
                            c=colours[sport], edgecolors='none',
                            label=sport+': '+label_z,
                            )
                
        except:
            print "\nWARNING: No data to plot!!!\n"
            raise
            
    plt.legend(loc=1)
    plt.xlabel(label_x)
    plt.ylabel(label_y)
    plt.axis('auto')
    plt.title(date_range)
    