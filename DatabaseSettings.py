# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo
Settings for DatabaseRead.py
"""
import os

class DatabaseSettings():
    def __init__(self, kind='none'):

        self.database_path = os.getcwd()       
        self.records_path = os.getcwd()
        self.map_path = os.getcwd()
        
        self.MapTab = True
        self.TracesTab = True
        self.RecordsTab = True
        
        self.filters = None
        # TODO: fix errors that appear if filters = None
        
###############################################################################
        
        # if a dataframe column is not listed here the figures will not display units
        self.units = {'elapsed_time':'s',
                      'total_elapsed_time':'s',
                      'total_timer_time':'s',
                      
                      'timezone':'h',
                      'weekday':'1 = Monday, 7 = Sunday',
                        
                      'distance':'m',
                      'altitude':'m',
                      'total_distance':'m',
                      'total_ascent':'m',
                      'total_descent':'m',
                        
                      'position_lat':'semicircles',
                      'position_long':'semicircles',                                
                      'start_position_lat':'semicircle',
                      'start_position_long':'semicircles',
                      'end_position_lat':'semicircle',
                      'end_position_long':'semicircles',

                      'cadence':'rpm',
                      'avg_cadence':'rpm',
                      'max_cadence':'rpm',
                        
                      'total_strides':'strides',

                      'heart_rate':'bpm',
                      'avg_heart_rate':'bpm',
                      'max_heart_rate':'bpm',
                      
                      'speed':'m/s',
                      'avg_speed':'m/s',
                      'max_speed':'m/s',
                      'enhanced_speed':'m/s',
                      'enhanced_avg_speed':'m/s',
                        
                      'total_calories':'kcal',
                        
                      'Amount':'GBP',
                      'Balance':'GBP',
                      
                      'delay':'min'}
                      
###############################################################################
                      
        # intenational system (SI) units
        self.units_SI = {'elapsed_time':'s',
                         'position':'semicircles',                         
                         'distance':'m',
                         'speed':'m/s'}  
                         
        # unit options and conversion factors from SI units
        # multiply SI units by these factors to get these units
        # divide these units by these factors to get SI units
        time_factors = {'s':1,
                        'min':1./60,
                        'h':1./60/60}
                        
        position_factors = {'semicircles':1,
                            'deg':0.00000008381903171539306640625} # 180/2**31
                            
        distance_factors = {'m':1,
                            'km':1e-3,
                            'miles':0.000621371}
                            
        speed_factors = {'m/s':1,
                         'km/h':3.6,
                         'mph':2.23694,
                         'min/km':3.6,
                         'min/mile':2.23694}
                            
        self.unit_factors = {'elapsed_time':time_factors,
                             'position':position_factors,
                             'distance':distance_factors,
                             'speed':speed_factors}
                             
        self.timedelta_factors = {'D':1,
                                  'W':7,
                                  'M':365/12, # this is not very precise but it should be enough to get an idea
                                  'Y':365}
        
###############################################################################
        
        self.default = dict()
        self.options = dict()

        self.default['histogram_y'] = 'counts'
        self.options['histogram_y'] = ['counts','frequency']       

        self.default['legend_location'] = 'best'
        self.options['legend_location'] = ['best','upper right','upper left',
                                           'lower left','lower right',
                                           'center left','center right','lower center',
                                           'upper center','center']
                                           
        self.default['colormap'] = 'jet'
        self.options['colormap'] = ['jet','hsv',
                                    'viridis','plasma','inferno',
                                    'CMRmap',
                                    'PiYG','PuOr','RdBu','RdYlBu','RdYlGn',
                                    'Set1','Accent','Paired']
                                    
        self.default['kind_trace'] = 'line'
        self.options['kind_trace'] = ['line','scatter']

        self.default['kind_summary'] = None
        self.options['kind_summary'] = ['barh', 'bar', 'line']
        
        self.default['stacked'] = 'yes'
        self.options['stacked'] = ['yes', 'no']
        
        self.default['measure'] = 'sum'
        self.options['measure'] = ['sum','mean','count','last']
        
        self.default['frequency'] = 'all'
        self.options['frequency'] = ['all','D','W','M','Y']
        
        self.default['sort'] = 'category'
        self.options['sort'] = ['category', 'quantity']
        
        self.default['location'] = 'and'
        self.options['location'] = ['and', 'or']
        

###############################################################################

        self.column_default = dict()
        self.column_options = dict()
        
        self.column_default['category1'] = None
        self.column_options['category1'] = ['sport','activity','gear','weekday',
                                            'Category','Account',
                                            'weekday_name',
                                            'week','month','year',
                                            'year_week','year_month', 'year_month_day',
                                            'category']
                                            
        self.column_default['category2'] = None
        self.column_options['category2'] = self.column_options['category1']
        
        self.column_default['quantity'] = None
        self.column_options['quantity'] = ['total_distance','total_elapsed_time',
                                           'avg_speed', 'avg_heart_rate',
                                           'Amount','Balance',
                                           'delay']
                                           
        self.column_default['legend_variable'] = None
        self.column_options['legend_variable'] = ['sport','activity','gear','file_name',
                                                  'weekday_name',
#                                                  'month', 'year', # TODO: fix error: 'numpy.int64' object is not iterable
                                                  'year_month',
                                                  'Category','Account',
                                                  'category']        
        
###############################################################################
        
        self.numeric_default = dict()
        self.numeric_options = dict()        
        
        self.numeric_default['scatter_x'] = None
        self.numeric_default['scatter_y'] = None
        self.numeric_default['histogram_x'] = None       
        
        # 'start_daytime_local' is not a datetime or numeric type but it does work in the scatter plot
        self.numeric_options['scatter_x'] = ['start_daytime_local']
        self.numeric_options['scatter_y'] = []
        self.numeric_options['histogram_x'] = []
        
###############################################################################
        
        self.trace_default = dict()
        self.trace_default['top_x'] = None
        self.trace_default['top_y'] = None
        self.trace_default['bottom_x'] = None
        self.trace_default['bottom_y'] = None
        
###############################################################################
                
        if kind.lower() == 'gps':
            self.set_settings_gps()
        elif kind.lower() == 'expenses':
            self.set_settings_expenses()
        elif kind.lower() == 'late':
            self.set_settings_late()

###############################################################################            

    def set_settings_gps(self):
        self.database_path = 'C:/Users/Ana Andres/Documents/Garmin/Ana/database/'
        self.records_path = 'C:/Users/Ana Andres/Documents/Garmin/Ana/csv/'
        self.map_path = 'C:/Users/Ana Andres/Dropbox/Dropbox-Ana\Garmin\Ana - maps\mymap.html'
        self.locations_path = 'C:/Users/Ana Andres/Documents/Garmin/Ana/database/Garmin-Locations.csv'
        
        self.filters = ['sport','activity','gear']
        
        self.default['kind_summary'] = 'barh'
        
        self.column_default['category1'] = 'sport'
        self.column_default['category2'] = 'activity'
        self.column_default['quantity'] = 'total_distance'
        self.column_default['legend_variable'] = 'sport'
        
        self.numeric_default['scatter_x'] = 'avg_speed'
        self.numeric_default['scatter_y'] = 'avg_heart_rate'
        self.numeric_default['histogram_x'] = 'avg_speed'        
        
        self.TracesTab = True
        self.trace_default['top_x'] = 'elapsed_time'
        self.trace_default['top_y'] = 'speed'
        self.trace_default['bottom_x'] = 'position_long'
        self.trace_default['bottom_y'] = 'position_lat' 
        
###############################################################################
        
    def set_settings_expenses(self):
        self.database_path = 'C:/Users/Ana Andres/Dropbox/Dropbox-Ana/Contabilidad/'
        
        self.MapTab = False
        self.TracesTab = False
        self.RecordsTab = False
        
        self.filters = ['Account','Category']
        
        self.default['kind_summary'] = 'bar'
        
        self.column_default['category1'] = 'year_month'
        self.column_default['category2'] = 'Category'
        self.column_default['quantity'] = 'Amount'
        self.column_default['legend_variable'] = 'Category'
        
        self.numeric_default['scatter_x'] = 'Date'
        self.numeric_default['scatter_y'] = 'Amount'
        self.numeric_default['histogram_x'] = 'Amount'

    def set_settings_late(self):
        self.database_path = 'C:/Users/Ana Andres/Dropbox/Dropbox-Ana/'
        
        self.MapTab = False
        self.TracesTab = False
        self.RecordsTab = False
        
        self.filters = ['category']
        
        self.default['kind_summary'] = 'bar'
        
        self.column_default['category1'] = 'category'
        self.column_default['category2'] = 'category'
        self.column_default['quantity'] = 'delay'
        self.column_default['legend_variable'] = 'category'
        
        self.numeric_default['scatter_x'] = 'meeting_time'
        self.numeric_default['scatter_y'] = 'delay'
        self.numeric_default['histogram_x'] = 'delay'
        