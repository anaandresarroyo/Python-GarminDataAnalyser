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
    
    df = pd.read_csv(database_path, index_col='start_time')
    df = df.set_index(pd.to_datetime(df.index))
    
    plot_xaxis = 'avg_heart_rate'
    plot_yaxis = 'avg_speed'
    sports = df['sport'].unique()
#    sports = {'cycling'}
    
    for sport in sports:
        print sport
        try:
            df[df['sport']==sport].loc['2017',{plot_xaxis,plot_yaxis}].dropna().plot(
                x=plot_xaxis, y=plot_yaxis,
                linestyle='None', marker='.', markersize=22, 
                label=sport, ax=plt.gca())
        except:
            print "\nWARNING: No " + sport + " data to plot!!!\n"
            
    plt.legend(loc=1)
    plt.xlabel(plot_xaxis)
    plt.ylabel(plot_yaxis)
    plt.axis('auto')
    