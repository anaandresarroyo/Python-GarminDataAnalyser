# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo
GUI which reads, analyses, plots, and updates the database CSV file and the activities' CSV files.
"""
import gmplot
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from PyQt4 import QtGui, QtCore, uic

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from MatplotlibSettings import *

# matplotlib.rcParams.update({'font.size': 50})

class DataBaseGUI(QtGui.QMainWindow):
    """
    GUI which analyses and plots GPS and fitness data.
    """
    def __init__(self, parent=None):
        super(DataBaseGUI, self).__init__(parent)
        # Load GUI design
        ui_file = 'DataBaseGUIdesign.ui'
        uic.loadUi(ui_file, self)    
        
        # Maximise GUI window
#        self.showMaximized()
        
        # Set initial splitter sizes
        self.splitter.setSizes([50,6000])
        self.SummarySplitter.setSizes([50,6000])
        
        # Set initial tabs        
        self.DatabaseTabsWidget.setCurrentIndex(1)   
        self.PlotTabsWidget.setCurrentIndex(0)
        self.SummaryTabsWidget.setCurrentIndex(0)
        
#        self.file_path = os.getcwd()        
        self.file_path = 'C:/Users/Ana Andres/Documents/Garmin/Ana/database/'   
#        self.file_path = QtGui.QFileDialog.getOpenFileName(self, 'Choose database .csv file to read.', self.file_path, "CSV files (*.csv)")
        self.ReadDatabasePathWidget.insert(self.file_path)
        self.MapFilePathWidget.insert('C:/Users/Ana Andres/Documents/Garmin/Ana/maps/mymap.html')                
        self.records_directory = 'C:/Users/Ana Andres/Documents/Garmin/Ana/csv/'
        self.RecordsPathWidget.insert(self.records_directory)

        # intenational system (SI) units
        self.SI_units = {'elapsed_time':'s',
                         'position':'semicircles',                         
                         'distance':'m',
                         'speed':'m/s',
                         }  
                         
        # unit options and conversion factors from SI units
        # multiply SI units by these factors to get these units
        # divide these units by these factors to get SI units
        self.time_units = {'s':1,
                           'min':1./60,
                           'h':1./60/60,
                           }
        self.position_units = {'semicircles':1,
                               'deg':0.00000008381903171539306640625, # 180/2**31
                               }
        self.distance_units = {'m':1,
                               'km':1e-3,
                               'miles':0.000621371,
                               }
        self.speed_units = {'m/s':1,
                            'km/h':3.6,
                            'mph':2.23694,
                            'min/km':3.6,
                            'min/mile':2.23694,
                            }
                               
        # default SI units for all fields in the dataframes
        # TODO: what if the dataframes have some fields not listed here?
        self.dataframe_units = {'elapsed_time':'s',
                                'timestamp':None,
                                'cadence':'rpm',
                                'distance':'m',
                                'enhanced_speed':'m/s',
                                'heart_rate':'bpm',
                                'position_lat':'semicircles',
                                'position_long':'semicircles',
                                'speed':'m/s',
                                'timestamp':None,
                                'unknown_88':None,
                                'activity':None,
                                'avg_cadence':'rpm',
                                'avg_heart_rate':'bpm',
                                'avg_speed':'m/s',
                                'daytime':None,
                                'start_daytime':None,
                                'start_daytime_local':None,
                                'altitude':'m',
                                'enhanced_avg_speed':'m/s',
                                'event':None,
                                'event_type':None,
                                'file_name':None,
                                'first_lap_index	':None,
                                'gear':None,
                                'max_cadence':'rpm',
                                'max_heart_rate':'bpm',
                                'max_speed':'m/s',
                                'message_index':None,
                                'num_laps':None,
                                'sport':None,
                                'start_position_lat':'semicircle',
                                'start_position_long':'semicircles',
                                'end_position_lat':'semicircle',
                                'end_position_long':'semicircles',
                                'start_time':None,
                                'start_time_local':None,
                                'sub_sport':None,
                                'timestamp':None,
                                'timezone':'h',
                                'total_calories':'kcal',
                                'total_distance':'m',
                                'total_ascent':'m',
                                'total_descent':'m',
                                'total_elapsed_time':'s',
                                'total_strides':'strides',
                                'total_timer_time':'s',
                                'trigger':None,
                                'weekday':'1 = Monday, 7 = Sunday',
                                'weekday_name':None,
                                'week':None,                                
                                'month':None,
                                'year':None,
                                'year_week':None,
                                'year_month':None,
                                'year_month_day':None,                                
                                'comments':None, 
                                }            
        
        # Connect GUI elements
        self.NewDatabasePushButton.clicked.connect(self.new_database)
        self.NewRecordsPathPushButton.clicked.connect(self.new_records)
        self.FilterPlotDatabasePushButton.clicked.connect(self.filter_and_plot_database)      
        self.PlotTracePushButton.clicked.connect(self.select_and_plot_trace)  
        self.SaveDatabasePushButton.clicked.connect(self.save_data)  
        self.SaveMapPushButton.clicked.connect(self.save_map)  
        self.SummaryPushButton.clicked.connect(self.plot_summary)
        self.ScatterPushButton.clicked.connect(self.plot_scatter)  
        self.HistogramPushButton.clicked.connect(self.plot_histogram)
        self.PlotMapPushButton.clicked.connect(self.generate_map)  
        self.UpdateUnitsPushButton.clicked.connect(self.update_units)  
        self.SIUnitsPushButton.clicked.connect(self.set_SI_units)
        self.SIUnitsPushButton.clicked.connect(self.set_SI_units)
             

        # TODO: create function for making the figures
        self.figure_scatter = Figure()
        self.canvas_scatter = FigureCanvas(self.figure_scatter)
        self.toolbar_scatter = NavigationToolbar(self.canvas_scatter, self)
        self.PlotScatterWidgetContainer.addWidget(self.toolbar_scatter)
        self.PlotScatterWidgetContainer.addWidget(self.canvas_scatter)    
       
        self.figure_hist = Figure()
        self.canvas_hist = FigureCanvas(self.figure_hist)
        self.toolbar_hist = NavigationToolbar(self.canvas_hist, self)
        self.PlotHistWidgetContainer.addWidget(self.toolbar_hist)
        self.PlotHistWidgetContainer.addWidget(self.canvas_hist) 

        self.figure_trace = Figure()
        self.canvas_trace = FigureCanvas(self.figure_trace)
        self.toolbar_trace = NavigationToolbar(self.canvas_trace, self)
        self.PlotTraceWidgetContainer.addWidget(self.toolbar_trace)
        self.PlotTraceWidgetContainer.addWidget(self.canvas_trace)  
        
        self.figure_map = Figure()
        self.canvas_map = FigureCanvas(self.figure_map)
        self.toolbar_map = NavigationToolbar(self.canvas_map, self)
        self.MapWidgetContainer.addWidget(self.toolbar_map)
        self.MapWidgetContainer.addWidget(self.canvas_map) 
        
        self.figure_summary = Figure()
        self.canvas_summary = FigureCanvas(self.figure_summary)
        self.toolbar_summary = NavigationToolbar(self.canvas_summary, self)
        self.PlotSummaryWidgetContainer.addWidget(self.toolbar_summary)
        self.PlotSummaryWidgetContainer.addWidget(self.canvas_summary) 
        
        colour_variable_list = ['sport','activity','gear','file_name']
        self.populate_combobox(colour_variable_list, 'sport',
                          [self.ColourVariableComboBox])
       
        colormap_list = ['jet','hsv',
                         'viridis','plasma','inferno',
                         'CMRmap',
                         'PiYG','PuOr','RdBu','RdYlBu','RdYlGn',
                         'Set1','Accent']
        self.populate_combobox(colormap_list, 'jet',
                          [self.CMapComboBox])
        
        plot_kind_list = ['line','scatter']
        self.populate_combobox(plot_kind_list, 'line',
                          [self.TraceTopKindComboBox, self.TraceBottomKindComboBox])

        legend_location_list = ['best','upper right','upper left',
                                'lower left','lower right',
                                'center left','center right','lower center',
                                'upper center','center']
        self.populate_combobox(legend_location_list, 'best',
                          [self.LegendLocationComboBox])
                          
        self.populate_combobox(['elapsed_time'], 'elapsed_time',
                          [self.TraceTopXComboBox])
        self.populate_combobox(['speed'], 'speed',
                          [self.TraceTopYComboBox])   
        self.populate_combobox(['position_long'], 'position_long',
                          [self.TraceBottomXComboBox])
        self.populate_combobox(['position_lat'], 'position_lat',
                          [self.TraceBottomYComboBox])  
                          
        self.populate_combobox(['avg_speed'], 'avg_speed',
                          [self.HistXComboBox])  
        self.populate_combobox(['avg_speed'], 'avg_speed',
                          [self.ScatterXComboBox]) 
        self.populate_combobox(['avg_heart_rate'], 'avg_heart_rate',
                          [self.ScatterYComboBox]) 
                          
        self.populate_combobox(self.time_units.keys(), 's',
                          [self.TimeUnitsComboBox])
        self.populate_combobox(self.position_units.keys(), 'semicircles',
                          [self.PositionUnitsComboBox])
        self.populate_combobox(self.distance_units.keys(), 'm',
                          [self.DistanceUnitsComboBox])
        self.populate_combobox(self.speed_units.keys(), 'm/s',
                          [self.SpeedUnitsComboBox])
                          
        self.populate_combobox(['sport'], 'sport',
                          [self.SummaryCategory1ComboBox])
        self.populate_combobox(['activity'], 'activity',
                          [self.SummaryCategory2ComboBox])
        self.populate_combobox(['total_distance'], 'total_distance',
                          [self.SummaryQuantityComboBox])
                          
        summary_measure_list = ['sum','mean','count']
        self.populate_combobox(summary_measure_list, 'sum',
                          [self.SummaryMeasureComboBox])
                          
        summary_kind_list = ['barh', 'bar', 'line']
        self.populate_combobox(summary_kind_list, 'barh',
                          [self.SummaryKindComboBox])
    
        # Read file      
        self.new_database()

        
    def populate_combobox(self, items_list, item_default, combobox_list):
        # populate comboboxes
        for combobox in combobox_list:
            combobox.clear()
            for item in items_list:                
                combobox.addItem(item,0)
            if item_default in items_list:
                index = combobox.findText(item_default)
            else:
                index = 0                
            combobox.setCurrentIndex(index)

    def new_database(self):
        """Select a new Garmin DataBase CSV file and locations file.""" 
        self.location_list()
        file_path = self.ReadDatabasePathWidget.text()
        file_path = QtGui.QFileDialog.getOpenFileName(self, 'Choose database .csv file to read.', file_path, "CSV files (*.csv)")
        if len(file_path):
            self.file_path = file_path
            self.ReadDatabasePathWidget.clear()
            self.SaveDatabasePathWidget.clear()
            self.ReadDatabasePathWidget.insert(self.file_path)
            self.SaveDatabasePathWidget.insert(self.file_path)
            self.read_database()      
            
            summary_category_list = ['sport','activity','gear','weekday',
                                     'weekday_name',
                                     'week','month','year',
                                     'year_week','year_month', 'year_month_day',
                                     ]
            self.populate_combobox(np.sort(list(set(summary_category_list) & set(self.df.columns))), 
                                   'sport', [self.SummaryCategory1ComboBox])
            self.populate_combobox(np.sort(list(set(summary_category_list) & set(self.df.columns))), 
                                   'activity', [self.SummaryCategory2ComboBox])
                              
            summary_quantity_list = ['total_distance','total_elapsed_time', 'avg_speed', 'avg_heart_rate']
            self.populate_combobox(np.sort(list(set(summary_quantity_list) & set(self.df.columns))), 
                                   'total_distance', [self.SummaryQuantityComboBox])
                          
            # make a copy so the current_units can be modified independently from the SI_units
            self.current_units = dict(self.SI_units) 
            self.update_units() # includes self.filter_and_plot_database()
#            self.filter_and_plot_database()            
            # TODO: don't overwrite previous user input settings
        else:
            print "WARNING: No file chosen. Choose another file to avoid errors.\n" 
                
    def new_records(self):
        file_path = self.RecordsPathWidget.text()
        file_path = QtGui.QFileDialog.getExistingDirectory(self, 'Choose directory containing .csv record files.', file_path)
        file_path = file_path + '\\'
        if len(file_path):
            self.records_directory = file_path
            self.RecordsPathWidget.clear()
            self.RecordsPathWidget.insert(file_path)
        else:
            print "WARNING: No directory chosen. Choose another directory to avoid errors.\n"            
        
    def read_database(self):
        """Read the CSV file."""
        print self.file_path + '\n'
        
        self.df = pd.read_csv(self.file_path, parse_dates=['start_time'], dayfirst=True)
        self.df['timezone'] = pd.to_timedelta(self.df['timezone'])
        # TODO: what if the dates column is not called start_time
        # TODO: fix errors that appear when some activities have empty gear
        # TODO: make empty comments be blank, not nan
        
        # Create a variable with the column names to use when saving the database
        self.database_columns_to_save = self.df.columns

        self.df = self.calculate_new_columns(self.df)                    
        self.df_selected = self.df.copy()
        
        self.StartDateEdit.setDate(self.df['start_time_local'].min())
        self.EndDateEdit.setDate(self.df['start_time_local'].max())
        
        self.sports = self.populate_list('sport', self.SportsListWidget)
        self.activities = self.populate_list('activity', self.ActivitiesListWidget)
        self.gear = self.populate_list('gear', self.GearListWidget)
           

#        plot_variables = self.df.columns
        # TODO: disable unwanted options

        plot_variables = []
        # 'start_daytime_local' is not a datetime or numeric but it does work in the plot so i manually add it
        plot_variables.append('start_daytime_local')
        for column in self.df.columns:
#            print column
#            print self.df[column].dtype
            if self.df[column].dtype in ['float64', 'int64', 'datetime64[ns]']:
                plot_variables.append(column)
                
        self.populate_combobox(np.sort(plot_variables), 
                               self.ScatterXComboBox.currentText(), 
                               [self.ScatterXComboBox])
                               
        plot_variables = []
        for column in self.df.columns:
            if self.df[column].dtype in ['float64', 'int64']:
                plot_variables.append(column)
                
        self.populate_combobox(np.sort(plot_variables), 
                               self.HistXComboBox.currentText(), 
                               [self.HistXComboBox])

        self.populate_combobox(np.sort(plot_variables), 
                               self.ScatterYComboBox.currentText(), 
                               [self.ScatterYComboBox])
        
    def calculate_new_columns(self, df): 
        # take into account the timezone        
        temp =  df['start_time'] + df['timezone']
#        df['start_time_local'] = pd.to_datetime(temp.values)
        # TODO: what if there is no timezone?       
#        df['start_time_local'] = temp.values
        df['start_time_local'] = temp
#        df['start_daytime_local'] = temp.dt.time.values
        df['start_daytime_local'] = temp.dt.time
        # TODO: add end_daytime info when it's added in DatabaseWrite.py
        df['weekday'] = temp.dt.weekday+1 # numeric        
        df['weekday_name'] = (temp.dt.weekday+1).apply(str) + ': ' + temp.dt.weekday_name # string
#        self.dataframe_units['weekday'] = None
        df['week'] = temp.dt.week
        df['year_week'] = temp.dt.year.apply(str) + '-' + temp.dt.week.apply(str).str.pad(2,fillchar='0')
        df['month'] = temp.dt.month
        df['year_month'] = temp.dt.year.apply(str) + '-' + temp.dt.month.apply(str).str.pad(2,fillchar='0')
        df['year_month_day'] = df['year_month'] + '-' + temp.dt.day.apply(str).str.pad(2,fillchar='0')
        df['year'] = temp.dt.year
        # TODO: add end_time_local info when it's added in DatabaseWrite.py             
        return df
    
    def set_SI_units(self):       
        index = self.TimeUnitsComboBox.findText(self.SI_units['elapsed_time'])
        self.TimeUnitsComboBox.setCurrentIndex(index)
        index = self.PositionUnitsComboBox.findText(self.SI_units['position'])
        self.PositionUnitsComboBox.setCurrentIndex(index)
        index = self.DistanceUnitsComboBox.findText(self.SI_units['distance'])
        self.DistanceUnitsComboBox.setCurrentIndex(index)
        index = self.SpeedUnitsComboBox.findText(self.SI_units['speed'])
        self.SpeedUnitsComboBox.setCurrentIndex(index)
        
        # update the units
        self.update_units()
        
    def update_units(self):
        # dataframes to update: df, df_selected
        # converting self.df also converts self.df_selected because it's just a section of it
        
        # convert from current_units to SI_units
#        print self.current_units['position']
#        print 'to SI:'        
        self.df = self.convert_units(self.df, self.current_units, to_SI=True)
#        print self.df['start_position_lat'].iloc[0]
#        print self.df_selected['start_position_lat'].iloc[0]
        self.df_selected = self.convert_units(self.df_selected, self.current_units, to_SI=True)
#        print self.df_selected['start_position_lat'].iloc[0]
#        print
        
        # read new dataframe_units from GUI
        self.current_units['elapsed_time'] = self.TimeUnitsComboBox.currentText()
        self.current_units['position'] = self.PositionUnitsComboBox.currentText()
        self.current_units['distance'] = self.DistanceUnitsComboBox.currentText()
        self.current_units['speed'] = self.SpeedUnitsComboBox.currentText()
        
                
        # convert from SI_units to current_units
#        print self.current_units['position']
#        print 'to other:'
        self.df = self.convert_units(self.df, self.current_units, to_SI=False)
#        print self.df['start_position_lat'].iloc[0]
#        print self.df_selected['start_position_lat'].iloc[0]
        self.df_selected = self.convert_units(self.df_selected, self.current_units, to_SI=False)
#        print self.df_selected['start_position_lat'].iloc[0]
#        print
        
        # repopulate the database table
#        self.fill_table(self.df_selected, self.Table1Widget, self.DatabaseRowsSpinBox.value())               
        
        # re-filter the database
        self.filter_and_plot_database()
        # TODO: also convert units in the trace plot
    
    def convert_units(self, df, units, to_SI=False):
        # if to_SI = False: convert from SI_units to dataframe_units
        # if to_SI = True: convert from dataframe_units to SI_units
        if to_SI:
            factor = -1.
        else: 
            factor = 1.
    
        # update the elapsed_time units so it is calculated correctly when reading the records csv file
        self.dataframe_units['elapsed_time'] = units['elapsed_time']
        
        for column_name in df.columns:
            if 'elapsed_time' in column_name:
                self.dataframe_units[column_name] = units['elapsed_time']
                df[column_name] = df[column_name] * (self.time_units[units['elapsed_time']] ** factor)
            if 'position' in column_name:
                self.dataframe_units[column_name] = units['position']
                df[column_name] = df[column_name] * (self.position_units[units['position']] ** factor)
            if 'distance' in column_name:
                self.dataframe_units[column_name] = units['distance']
                df[column_name] = df[column_name] * (self.distance_units[units['distance']] ** factor)
            if 'speed' in column_name:
                self.dataframe_units[column_name] = units['speed']                
                if 'min/' in units['speed']:
                    if to_SI:
                        df[column_name] = 60 / df[column_name]
                        df[column_name] = df[column_name] * (self.speed_units[units['speed']] ** factor)
                    else:
                        df[column_name] = df[column_name] * (self.speed_units[units['speed']] ** factor)
                        df[column_name] = 60 / df[column_name]
                else:
                    df[column_name] = df[column_name] * (self.speed_units[units['speed']] ** factor)
        return df
           
    def populate_list(self, column, widget):
        """Populate the tree widget with items from the dataframe column."""
        items = np.sort(self.df[column].unique())
        widget.clear()
        for row, item in enumerate(items):
            widget.addItem(item)
            widget.item(row).setSelected(True)
        return items                
    
    def select_dates(self, df):
        start_date = self.StartDateEdit.date().toPyDate()
        end_date = self.EndDateEdit.date().toPyDate()
#        print df.columns
        df_copy = df.copy()
        df_copy.set_index('start_time_local', inplace=True)
        df_selected = df_copy.loc[str(start_date) : str(end_date + pd.DateOffset(1))]
        df_selected.reset_index(inplace=True)
#        print df_selected.columns
        return df_selected
        
    def list_selection(self, widget):
        selected_options = []
        for item in widget.selectedItems():
            selected_options.append(item.text())
        return selected_options       
        
    def location_list(self):
        """Populate the start and end location tree widgets."""
        self.StartLocationListWidget.clear()
        self.StartLocationListWidget.addItem('any')  
        self.StartLocationListWidget.setCurrentRow(0) 
        
        self.EndLocationListWidget.clear()
        self.EndLocationListWidget.addItem('any')  
        self.EndLocationListWidget.setCurrentRow(0)
        
        file_path = 'C:/Users/Ana Andres/Documents/Garmin/Ana/database/Garmin-Locations.csv'        
        #file_path = QtGui.QFileDialog.getOpenFileName(self, 'Choose .csv file with list of locations.', file_path, "CSV files (*.csv)")
        if len(file_path):
            self.df_locations = pd.read_csv(file_path)
            for item in self.df_locations['name']:
                self.StartLocationListWidget.addItem(item)
                self.EndLocationListWidget.addItem(item)      
        else:
            print "No file chosen. Choose another file to avoid errors.\n"  
            
    def location_mask(self, df, when, selected_options):
        # TODO: add option to select start OR end locations as well as AND
        # TODO: add option to select mid-trajectory locations... maybe?
        # TODO: fix error with weird characters such as "ñ" in "Logroño"
        if 'any' in selected_options:
            mask = True
        else:
            mask = df['sport'] == 'nothing'
            for option in selected_options:
                # TODO: what the activity doesn't have gps data?
                radius = self.df_locations.loc[self.df_locations['name'] == option, 'radius'].values[0]
                lon_deg = self.df_locations.loc[self.df_locations['name'] == option, 'position_long']
                lat_deg = self.df_locations.loc[self.df_locations['name'] == option, 'position_lat']
                distance = Distance(df[when+'_position_long'], df[when+'_position_lat'],                                     
                                    units_gps=self.current_units['position'], units_d='m', mode='fixed', 
                                    fixed_lon=lon_deg*self.position_units[self.current_units['position']]/0.00000008381903171539306640625, 
                                    fixed_lat=lat_deg*self.position_units[self.current_units['position']]/0.00000008381903171539306640625,
                                    )
#                                    units_gps='semicircles', units_d='m', mode='fixed', 
#                                    fixed_lon=lon_deg*2**31/180, fixed_lat=lat_deg*2**31/180)
                option_mask = distance.abs() <= radius
                mask = mask | option_mask                                    
        return mask
        
    def generate_mask(self, df, column, selected_options):       
        mask = df[column] == 'nothing'
        for option in selected_options:
            option_mask = df[column] == option
            mask = mask | option_mask
        return mask
        # TODO: what if some rows are empy in this column?
        # TODO: allow several gear for the same activity - maybe?
    
    def filter_database(self):
        df_dates = self.select_dates(self.df)
        
        self.selected_sports = self.list_selection(self.SportsListWidget)
        self.selected_activities = self.list_selection(self.ActivitiesListWidget)
        self.selected_gear = self.list_selection(self.GearListWidget)
        self.selected_start_locations = self.list_selection(self.StartLocationListWidget)
        self.selected_end_locations = self.list_selection(self.EndLocationListWidget)
        # TODO: add more selection options - speed, heart_rate, time, distance...
        # TODO: add checkbockes to enable/disable activities, gear, sport and location selection
        
        mask_sports = self.generate_mask(df_dates, 'sport', self.selected_sports)
        mask_activities = self.generate_mask(df_dates, 'activity', self.selected_activities)
        mask_gear = self.generate_mask(df_dates, 'gear', self.selected_gear)
        mask_location_start = self.location_mask(df_dates, 'start', self.selected_start_locations)
        mask_location_end = self.location_mask(df_dates, 'end', self.selected_end_locations)
        
        mask = mask_sports & mask_activities & mask_gear & mask_location_start & mask_location_end
        self.df_selected = df_dates.loc[mask]
        
    def filter_and_plot_database(self):
        self.filter_database()
        self.DatabaseSizeSpinBox.setValue(len(self.df_selected))
        self.fill_table(self.df_selected, self.Table1Widget, self.DatabaseRowsSpinBox.value())
        self.plot_histogram()
        self.plot_scatter()
        if self.MapCheckBox.checkState():
            self.generate_map()
        self.StartTimeDoubleSpinBox.setValue(0)
        self.EndTimeDoubleSpinBox.setValue(999999)
        self.plot_summary()
              
    
    
    def generate_colours(self, df, column, cmap_name):
        labels = np.sort(df[column].unique())
        cmap = plt.get_cmap(cmap_name)
        colours = cmap(np.linspace(0,1,len(labels)+1))
        colour_dict = dict(zip(labels,colours))
        return colour_dict

    def plot_scatter(self):
        df = self.df_selected        
        x = self.ScatterXComboBox.currentText()
        y = self.ScatterYComboBox.currentText()
        cmap_name = self.CMapComboBox.currentText()   
        alpha = self.TransparencyDoubleSpinBox.value()
        legend = self.ColourVariableComboBox.currentText()
        kind = 'line'
               
        self.figure_scatter.clear()
        ax = self.figure_scatter.add_subplot(111)
        
        colour_dict = self.generate_colours(df, legend, cmap_name)
        for label in np.sort(colour_dict.keys()):
            
            # select data according to the legend variable selected            
            df_plot = df.loc[df[legend]==label][[x,y]]
#            df_plot.set_index(x, inplace=True)
            
#        df_plot = df.groupby([x,legend])
#        self.temp = df_plot
#        df_plot = df.groupby([legend])[[x,y]].set_index(x)
#        plot_options = self.populate_plot_options(kind=kind, alpha=alpha, cmap_name=cmap_name)
#        df_plot[y].unstack(level=1).plot(ax=ax, **plot_options)
#        df_plot.plot(ax=ax, **plot_options)
            
            
            if len(df_plot) > 0:
                 # convert .tolist() in order to plot timestamps
#                 ax.scatter(x=df_plot[x].tolist(), y=df_plot[y].tolist(), s = 400,
#                             color = [colour_dict[label],] * len(df_plot),
#                             # the RGB colour array is duplidated for every data points
#                             # otherwise when having just 4 data points it gets confused
#                             # due to a bug in matplotlib
#                             label = label, 
#                             alpha = alpha, 
#                             edgecolors = 'face',
#                             )   

                 # TODO: fix errors that appear when x = y
                 df_plot.plot(x=x, y=y,
                              ax=ax,
                              kind=kind,
#                 ax.plot(df_plot[x], df_plot[y],
                              label=label, 
                              alpha=alpha, 
                              c=colour_dict[label],
#                              s=400,
#                              edgecolors='face',
                              marker='.',
                              markersize=50,
                              linestyle='None',
                              ) 
        
        ax.autoscale(enable=True, axis='both', tight='False')
        ax.margins(0.1,0.1)
                
        xlabel = x.replace('_',' ')
        if self.dataframe_units[x]:
            xlabel = xlabel + ' (' + self.dataframe_units[x] + ')'
        
        ylabel = y.replace('_',' ')
        if self.dataframe_units[y]:
            ylabel = ylabel + ' (' + self.dataframe_units[y] + ')'
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        legend = ax.legend(loc=self.LegendLocationComboBox.currentText())
        if legend:
            legend.set_visible(self.LegendCheckBox.checkState())
        self.canvas_scatter.draw()
        
            
    def plot_histogram(self):
        df = self.df_selected
        x = self.HistXComboBox.currentText()  
        legend = self.ColourVariableComboBox.currentText()
        cmap_name = self.CMapComboBox.currentText()
        alpha = self.TransparencyDoubleSpinBox.value()
        
        self.figure_hist.clear()
        ax = self.figure_hist.add_subplot(111)

        try:
            bins = np.linspace(min(df[x]), max(df[x]), 20)
            histogram = True
            # TODO: what if it's start_time, daytime, or weekday?
        except:
            # TODO: try/except is a temporary solution: fix it
            print "Cannot generate histogram.\n"
            histogram = False
            
        colour_dict = self.generate_colours(df, legend, cmap_name)
        for label in np.sort(colour_dict.keys()):                
            x_data = df.loc[df[legend]==label, x]
            
            if len(x_data) > 1:                
                # histogram plot
                if histogram:
                    ax.hist(x_data, bins=bins,
                            color=colour_dict[label],
                            label=label, 
                            normed=True, 
                            alpha=alpha,
                            )
                            
        
        xlabel = x.replace('_',' ')
        if self.dataframe_units[x]:
            xlabel = xlabel + ' (' + self.dataframe_units[x] + ')'        
        
        if histogram:
            ax.set_xlabel(xlabel)
            ax.set_ylabel('frequency')
            legend = ax.legend(loc=self.LegendLocationComboBox.currentText())
            if legend:
                legend.set_visible(self.LegendCheckBox.checkState())
            self.canvas_hist.draw()

        
    def populate_plot_options(self, kind, alpha, cmap_name, df=pd.DataFrame(), index=False, column=False):
        plot_options = dict()   
        plot_options['kind'] = kind    
        plot_options['alpha'] = alpha

        if not df.empty:
            colour_dict = self.generate_colours(df, column, cmap_name)
            label = df.loc[index,column]
            plot_options['c'] = colour_dict[label]
            plot_options['label'] = str(label)
        else:
            plot_options['colormap'] = cmap_name
            
        if kind == 'line':
            plot_options['marker'] = '.'
            plot_options['markersize'] = 20
            # TODO: move default marker size to MatplotlibSettings.py
            
        elif kind == 'scatter':
            plot_options['edgecolors'] = 'face'
            plot_options['s'] = 20

        elif 'bar' in kind:
            plot_options['stacked'] = True
            plot_options['edgecolor'] = 'none'                
        
        return plot_options   
            
    def plot_summary(self):
        summary_quantity_list = [self.SummaryQuantityComboBox.itemText(i) for i in range(self.SummaryQuantityComboBox.count())]
        summary_category_list = [self.SummaryCategory1ComboBox.itemText(i) for i in range(self.SummaryCategory1ComboBox.count())]
        summary_list = np.unique(summary_category_list + summary_quantity_list)

        # TODO: fix this temporary solution
        summary_list = list(set(summary_list) & set(self.df_selected.columns))
        
        df = self.df_selected[summary_list]        
        
        measure = self.SummaryMeasureComboBox.currentText()
        quantity = self.SummaryQuantityComboBox.currentText()
        category1 = self.SummaryCategory1ComboBox.currentText()
        category2 = self.SummaryCategory2ComboBox.currentText()
        kind = self.SummaryKindComboBox.currentText()
        cmap_name = self.CMapComboBox.currentText()     
        alpha = self.TransparencyDoubleSpinBox.value()        
        
        if measure == 'sum':
            self.df_summary_single = df.groupby([category1]).sum()
            self.df_summary_double = df.groupby([category1,category2]).sum()
        elif measure == 'mean':
            self.df_summary_single = df.groupby([category1]).mean()
            self.df_summary_double = df.groupby([category1,category2]).mean()
        elif measure == 'count':
            self.df_summary_single = df.groupby([category1]).count()
            self.df_summary_double = df.groupby([category1,category2]).count()
            
        self.fill_table(self.df_summary_single[quantity].reset_index(), self.SummarySingleTableWidget)
        self.fill_table(self.df_summary_double[quantity].reset_index(), self.SummaryDoubleTableWidget)
        
        self.figure_summary.clear()
        ax = self.figure_summary.add_subplot(111)

        plot_options = self.populate_plot_options(kind=kind, alpha=alpha, cmap_name=cmap_name)
        self.df_summary_double[quantity].unstack(level=1).plot(ax=ax, **plot_options)
            
        legend = ax.legend(loc=self.LegendLocationComboBox.currentText())
        legend.set_visible(self.LegendCheckBox.checkState())
        
        label = quantity.replace('_',' ')
        if self.dataframe_units[quantity]:
            label = label + ' (' + self.dataframe_units[quantity] + ')' 
        if kind == 'barh':
            ax.set_xlabel(label)
        else:
            ax.set_ylabel(label)
        
        self.canvas_summary.draw() 
        
        
        
    def fill_table(self, df, table, max_rows=50):    
        
        # initialise the GUI table columns
        table.clear()
        # disable sorting to solve issues with repopulating
        table.setSortingEnabled(False)        
        
        table.setColumnCount(len(df.columns))
        table.setHorizontalHeaderLabels(df.columns)
            
        # fill the GUI table
        row = 0
        while row <= min(max_rows-1,len(df.index)-1):
            table.setRowCount(row+1)
            for col in range(len(df.columns)):                
                table.setItem(row,col,QtGui.QTableWidgetItem(str(df.iloc[row,col])))
                table.resizeColumnToContents(col)
            row = row + 1
        # enable table sorting by columns
        table.setSortingEnabled(True)
        # TODO: fix number sorting as it currently does: 1, 13, 24, 33, 356, 4, ...
    
    def read_table(self, table, rows=[]):
        # read GUI table size
        if not len(rows):
            rows = range(table.rowCount())
        columns = range(table.columnCount())
        
        # read column names from the GUI table
        column_names = []
        for column in columns:
            column_names.append(table.horizontalHeaderItem(column).text())

        # initialise dataframe with certain columns
        df = pd.DataFrame(columns=column_names)
        
        # read data from GUI table
        for row in rows:
            for column_number, column_name in enumerate(column_names):
                df.loc[row,column_name] = table.item(row,column_number).data(0)
                  
        # TODO: make this formatting more automatic
        # format data types
        datetime_column_names = ['start_time', 'start_time_local', 'timesetamp']                  
        for column_name in column_names:
            # format dates
            if column_name in datetime_column_names:
                df[column_name] = pd.to_datetime(df[column_name])
            elif 'position' in column_name:
                df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
            # change strings to numbers
            elif column_name != 'file_name':
                df[column_name] = pd.to_numeric(df[column_name], errors='ignore')        
        
        return df            

    
    def read_selected_table_rows(self, table):
        selected_rows = []
        for item in table.selectedIndexes():
            selected_rows.append(item.row())
        selected_rows = np.unique(selected_rows)
        # read the selected_rows from the table
        df = self.read_table(table, selected_rows)
        # return the dataframe
        return df
    
    def read_records(self, file_path):
        df = pd.read_csv(file_path, parse_dates=['timestamp'])
        self.records_columns_to_save = df.columns
        
        # use these lines if we want to eliminate columns titled 'Unnamed'
#        self.records_columns_to_save = []
#        for item in df.columns:
#            if not 'Unnamed' in item:
#                self.records_columns_to_save.append(item)
        
        df['elapsed_time'] = ElapsedTime(df['timestamp'], units_t=self.dataframe_units['elapsed_time'])
        
                # TODO: these options are wrong, fix it
        self.populate_combobox(np.sort(df.columns), self.TraceTopXComboBox.currentText(),
                          [self.TraceTopXComboBox])
        self.populate_combobox(np.sort(df.columns), self.TraceTopYComboBox.currentText(),
                          [self.TraceTopYComboBox])   
        self.populate_combobox(np.sort(df.columns), self.TraceBottomXComboBox.currentText(),
                          [self.TraceBottomXComboBox])
        self.populate_combobox(np.sort(df.columns), self.TraceBottomYComboBox.currentText(),
                          [self.TraceBottomYComboBox])  
                          
        return df
        
    def select_times(self, df):
        start_time = self.StartTimeDoubleSpinBox.value()
        end_time = self.EndTimeDoubleSpinBox.value()
        mask_start = df['elapsed_time'] >= start_time
        mask_end = df['elapsed_time'] <= end_time
        return df.loc[mask_start & mask_end]
    
    def merge_dataframes(self,left,right,index):        
        left.set_index(index, inplace=True)
        right.set_index(index, inplace=True)        
        for row in right.index:
            for column in right.columns:
                left.loc[row,column] = right.loc[row,column]
        left.reset_index(inplace=True)
        return left
    
    def save_data(self):
        # read file name
        file_path = self.SaveDatabasePathWidget.text()
#        file_path = QtGui.QFileDialog.getSaveFileName(self, 'Choose database .csv file to save.', file_path, "CSV files (*.csv)")
        self.SaveDatabasePathWidget.clear()
        self.SaveDatabasePathWidget.insert(file_path)
        self.ReadDatabasePathWidget.clear()
        self.ReadDatabasePathWidget.insert(file_path)
        
        # TODO: strange characters like ñ screw it up
        print 'Saving database...'
        # read data from Table 1
        df_widget = self.read_table(self.Table1Widget)
        # combine df_widget with the rest of the activities not shown in Table 1
#        print self.df.head()
#        print df_widget.head()
        df_save = self.merge_dataframes(self.df, df_widget, 'start_time_local')
        # TODO: merge by file_name instead of start_time_local
        self.df = df_save.copy()
        # TODO: check wether this is causing issues from the data formats        
        
        # convert to SI units before saving
        df_save = self.convert_units(df_save, self.current_units, to_SI=True)
        # TODO: fix issues with unit conversions when saving the data
        # the function convert_units changes the current_units dictionary and we don't want this
        
        
        # save database
        df_save.to_csv(file_path, sep=',', header=True, index=False, columns=self.database_columns_to_save)
        print 'Database saved! \n'
        
        # read selected rows from the database
        self.df_trace = self.read_selected_table_rows(self.Table1Widget)
        print 'Saving record files...'
        for index in self.df_trace.index:
            file_number = self.df_trace.loc[index,'file_name']
            # read records file
            file_path = self.records_directory + str(file_number) + '_record.csv'
            df = self.read_records(file_path)
            # crop records by time
            # TODO: crop by database time and not start and end time from the GUI
            df = self.select_times(df)
            # recalculate distance
            df['distance'] = df['distance'] - df.loc[df.index[0],'distance']
#            df = df.drop('elapsed_time', axis=1)
            # save records
            df.to_csv(file_path, sep=',', header=True, index=False, columns=self.records_columns_to_save)                
        print 'Record files saved! \n'
        
    
    def generate_map(self):    
        number_of_activities = self.MapActivitiesSpinBox.value()  
        column = self.ColourVariableComboBox.currentText()
        cmap_name = self.CMapComboBox.currentText()  
        colour_dict = self.generate_colours(self.df_selected, column, cmap_name)           
        
        self.figure_map.clear()
        ax = self.figure_map.add_subplot(111)
        
        self.map_data = {}
        self.map_colours = {}
        avg_lat = []
        avg_long = []
        for index in self.df_selected.iloc[0:number_of_activities].index:
            file_number = self.df_selected.loc[index,'file_name']
            
            file_path = self.records_directory + str(file_number) + '_record.csv'
            # read the csv file
            df = self.read_records(file_path)  
            df = self.convert_units(df, self.current_units)
            # Extract location information, remove missing data, convert to degrees
            self.map_data[file_number] = df.loc[:,['position_lat','position_long']].dropna()
#            self.map_colours[file_number] = 'k'
            self.map_colours[file_number] = colour_dict[self.df_selected.loc[index,column]]
            
            avg_long.append(self.map_data[file_number]['position_long'].mean())
            avg_lat.append(self.map_data[file_number]['position_lat'].mean())
            
            # TODO: user option: line (faster) or scatter (better if many nan) plot
            ax.plot(self.map_data[file_number]['position_long'], 
                    self.map_data[file_number]['position_lat'],
                    label = file_number,
                    c=self.map_colours[file_number],
                    )     
#            ax.scatter(self.map_data[file_number]['position_long'], 
#                       self.map_data[file_number]['position_lat'],
#                       label = file_number,
#                       )     
                
              
        # make sure x and y axis have the same spacing
        ax.axis('equal')        
        
        # label axes        
        xlabel = 'position_long (' + self.dataframe_units['position_long'] + ')'
        ylabel = 'position_lat (' + self.dataframe_units['position_lat'] + ')'  
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        
        self.canvas_map.draw()
        
        # TODO: calculate the required zoom too
        # TODO: adjust histogram number of bins depending on the data
#        temp = np.histogram(avg_long,bins=100)
#        centre_long = (temp[1][np.argmax(temp[0])] + temp[1][np.argmax(temp[0])+1])/2
#        temp = np.histogram(avg_lat,bins=100)
#        centre_lat = (temp[1][np.argmax(temp[0])] + temp[1][np.argmax(temp[0])+1])/2
#        self.map_centre = [centre_long, centre_lat]        
#        self.map_centre = [np.mean(avg_long), np.mean(avg_lat)]       
        self.map_centre = [np.median(avg_long), np.median(avg_lat)]
        
        
    def save_map(self):   
        print "Saving HTML map..."
        print "WARNING: HTML map saving will only work if the GPS units is set to 'deg'!"
        # TODO: this will only work if the GPS units is set to "deg", allow other options
    
        gmap = gmplot.GoogleMapPlotter(self.map_centre[1], self.map_centre[0], 13)
#        gmap = gmplot.GoogleMapPlotter(52.202, 0.12, 13) # Cambridge 
#        gmap = gmplot.GoogleMapPlotter(43, -120, 5) # USA West Coast
#        gmap = gmplot.GoogleMapPlotter(46.36, 14.09, 11) # Lake Bled        
        
        for key in self.map_data:             
            # Add a line plot to the gmap object which will be save to an .html file
            # Use line instead of scatter plot for faster speed and smaller file size
            
            # TODO: user option: line (faster) or scatter (very very slow) plot
            # so if there are nan, e.g. metro, separate the plots into several line plots
            gmap.plot(self.map_data[key]['position_lat'], 
                      self.map_data[key]['position_long'], 
#                      color=self.map_colours[key],
                      color='k', # TODO: it doesn't like RGB values, fix it
                      edge_width=3,
                      )
#            gmap.scatter(self.map_data[key]['position_lat'][0:-1:5], 
#                         self.map_data[key]['position_long'][0:-1:5], 
#                         color=self.map_colours[key], size=10, marker=False)
        
        file_path = self.MapFilePathWidget.text()
        file_path = QtGui.QFileDialog.getSaveFileName(self, 'Choose .html file to save map.', file_path, "HTML files (*.html)")
        self.MapFilePathWidget.clear()
        self.MapFilePathWidget.insert(file_path)        
        gmap.draw(file_path)
        print "Finished HTML map!"
            
    def select_and_plot_trace(self):
        print "Starting trace plots..."
        self.df_trace = self.read_selected_table_rows(self.Table1Widget)
    
        x1 = self.TraceTopXComboBox.currentText()
        y1 = self.TraceTopYComboBox.currentText()
        x2 = self.TraceBottomXComboBox.currentText()
        y2 = self.TraceBottomYComboBox.currentText()
        
        self.figure_trace.clear()
        
        if self.TraceTopCheckBox.checkState() and self.TraceBottomCheckBox.checkState():
            ax1 = self.figure_trace.add_subplot(211)
            ax2 = self.figure_trace.add_subplot(212)
        elif self.TraceTopCheckBox.checkState():
            ax1 = self.figure_trace.add_subplot(111)
        elif self.TraceBottomCheckBox.checkState():
            ax2 = self.figure_trace.add_subplot(111)
                    
        if len(self.df_trace) > 20:
            print "WARNING: " + str(len(self.df_trace)) + " trace plots might take a long time!"
            
        for index in self.df_trace.index:
            file_number = self.df_trace.loc[index,'file_name']
            file_path = self.records_directory + str(file_number) + '_record.csv'
            # read the csv file
            df = self.read_records(file_path)
            # select data based on start and end values of elapsed_time
            df = self.select_times(df)

            # recalculate mean and max values (heart_rate, speed, ...) and update Table 1
            self.recalculate_statistics(df,file_number)
            
            if index == self.df_trace.index[0]:
                self.fill_table(df, self.Table2Widget)   
            
            if self.TraceTopCheckBox.checkState():
                trace_top_plot_options = self.populate_plot_options(df=self.df_trace,
                        index=index,
                        column=self.ColourVariableComboBox.currentText(),
                        cmap_name=self.CMapComboBox.currentText(),
                        kind=self.TraceTopKindComboBox.currentText(), 
                        alpha=self.TransparencyDoubleSpinBox.value())
                        
                df.plot(x=x1, y=y1, 
                        ax=ax1, 
                        **trace_top_plot_options)
                # TODO: fix errors that appear when plotting timestamps - see plot_scatter()
                        
                xlabel = x1.replace('_',' ')
                if self.dataframe_units[x1]:
                    xlabel = xlabel + ' (' + self.dataframe_units[x1] + ')'
                
                ylabel = y1.replace('_',' ')
                if self.dataframe_units[y1]:
                    ylabel = ylabel + ' (' + self.dataframe_units[y1] + ')'
                
                if self.TraceTopAxesEqualCheckBox.checkState():
                    # set x and y axis to have the same spacing - good for GPS coordinates
                    ax1.axis('equal')    
                    
                ax1.set_xlabel(xlabel)
                ax1.set_ylabel(ylabel)
                ax1.autoscale(enable=True, axis='both', tight='False')
                ax1.margins(0.1,0.1)
                legend = ax1.legend(loc=self.LegendLocationComboBox.currentText())
                legend.set_visible(self.LegendCheckBox.checkState())

                    
            if self.TraceBottomCheckBox.checkState():
                trace_bottom_plot_options = self.populate_plot_options(df=self.df_trace,
                        index=index,
                        column=self.ColourVariableComboBox.currentText(),
                        cmap_name=self.CMapComboBox.currentText(),
                        kind=self.TraceBottomKindComboBox.currentText(), 
                        alpha=self.TransparencyDoubleSpinBox.value())
                    
                df.plot(x=x2, y=y2, 
                        ax=ax2, 
                        **trace_bottom_plot_options)
        
                xlabel = x2.replace('_',' ')
                if self.dataframe_units[x2]:
                    xlabel = xlabel + ' (' + self.dataframe_units[x2] + ')'
                
                ylabel = y2.replace('_',' ')
                if self.dataframe_units[y2]:
                    ylabel = ylabel + ' (' + self.dataframe_units[y2] + ')'
                
                if self.TraceBottomAxesEqualCheckBox.checkState():
                    # set x and y axis to have the same spacing - good for GPS coordinates
                    ax2.axis('equal')    
                
                ax2.set_xlabel(xlabel)
                ax2.set_ylabel(ylabel)
                ax2.autoscale(enable=True, axis='both', tight='False')
                ax2.margins(0.1,0.1)
                legend = ax2.legend(loc=self.LegendLocationComboBox.currentText())
                legend.set_visible(self.LegendCheckBox.checkState())
        
        self.canvas_trace.draw()
        print "Finished trace plots!\n"
        
            
    def recalculate_statistics(self,df,file_number):
        # TODO: take into account non SI units!!!
        print "WARNING: do not recalculate statistics with non SI units!"
    
        row = self.Table1Widget.findItems(str(file_number),QtCore.Qt.MatchExactly)[0].row()
        
        number_of_columns = self.Table1Widget.columnCount()
        column_dict = {}
        for column in range(number_of_columns):
            column_name = self.Table1Widget.horizontalHeaderItem(column).text()
            column_dict[column_name] = column
               
        if 'speed' in df.columns:
            avg_speed = df['speed'].mean()
            self.Table1Widget.setItem(row, column_dict['avg_speed'], 
                                      QtGui.QTableWidgetItem(format(avg_speed,'.3f')))
        
        if 'heart_rate' in df.columns:                                                           
            avg_heart_rate = df['heart_rate'].mean()
            self.Table1Widget.setItem(row, column_dict['avg_heart_rate'], 
                                      QtGui.QTableWidgetItem(format(avg_heart_rate,'.0f')))
                      
        if 'max_heart_rate' in df.columns:
            max_heart_rate = df['heart_rate'].max()
            self.Table1Widget.setItem(row, column_dict['max_heart_rate'], 
                                      QtGui.QTableWidgetItem(format(max_heart_rate,'.0f')))
                                  
        # TODO: fix the mean cadence calculation because it decreases drastically for no apparent reason
#        avg_cadence = df['cadence'].mean()
#        self.Table1Widget.setItem(row, column_dict['avg_cadence'], 
#                                  QtGui.QTableWidgetItem(format(avg_cadence,'.1f')))
                                 
        if 'max_cadence' in df.columns:
            max_cadence = df['cadence'].max()
            self.Table1Widget.setItem(row, column_dict['max_cadence'], 
                                      QtGui.QTableWidgetItem(format(max_cadence,'.1f')))
        
        if 'start_position_lat' in df.columns:
            start_position_lat = df['position_lat'].dropna().iloc[0]
            self.Table1Widget.setItem(row, column_dict['start_position_lat'], 
                                      QtGui.QTableWidgetItem(format(start_position_lat,'.0f')))

        if 'start_position_long' in df.columns:
            start_position_long = df['position_long'].dropna().iloc[0]
            self.Table1Widget.setItem(row, column_dict['start_position_long'], 
                                      QtGui.QTableWidgetItem(format(start_position_long,'.0f')))    
                                  
        if 'end_position_lat' in df.columns:
            end_position_lat = df['position_lat'].dropna().iloc[-1]
            self.Table1Widget.setItem(row, column_dict['end_position_lat'], 
                                      QtGui.QTableWidgetItem(format(end_position_lat,'.0f')))

        if 'end_position_long' in df.columns:
            end_position_long = df['position_long'].dropna().iloc[-1]
            self.Table1Widget.setItem(row, column_dict['end_position_long'], 
                                      QtGui.QTableWidgetItem(format(end_position_long,'.0f')))        
        
        if 'total_distance' in df.columns:
            total_distance = df.loc[df.index[-1],'distance'] - df.loc[df.index[0],'distance']
            self.Table1Widget.setItem(row, column_dict['total_distance'], 
                                      QtGui.QTableWidgetItem(format(total_distance,'.2f')))        

        if 'total_elapsed_time' in df.columns:
            total_elapsed_time = df.loc[df.index[-1],'elapsed_time'] - df.loc[df.index[0],'elapsed_time']
            self.Table1Widget.setItem(row, column_dict['total_elapsed_time'], 
                                      QtGui.QTableWidgetItem(format(total_elapsed_time,'.3f')))        
        
                   
def ElapsedTime(timestamp, units_t='sec', mode='start'):    
    """Calculate the elapsed time from a timestamp pandas Series.
        
    Arguments:
    timestamp : timestamp pandas Series
        Timestamp values
    units_d: string
        Units of the calculated time, e.g. 'sec' (default), 'min', or 'h'
    mode : string
        If 'start' calculate the elapsed time between all points of the array and the first point.
        If 'previous' calculate the elapsed time between all points of the array the previous point.
    
    Output:
    elapsed_time: float pandas Series
        Contains the calculated elapsed time in units of units_t
    """
    
    # The Garmin Forerunner 35 takes data every 1 second

    origin_time = np.empty(timestamp.shape, dtype=type(timestamp))
#    origin_time = timestamp
    if mode == 'start':
        origin_time[:] = timestamp[0]
    
    elif mode == 'previous':
        origin_time[0] = timestamp[0]
        for i, time in enumerate(timestamp[0:-1]):
            origin_time[i+1] = time
            
    else:
        raise ValueError('Unable to recognise the mode.')  

    timedelta = timestamp-origin_time
    elapsed_time = timedelta.astype('timedelta64[s]') # in seconds
    
    if units_t == 's':
        pass    
    elif units_t == 'sec':
        pass
    elif units_t == 'min':
        # Convert seconds to minutes
        elapsed_time = elapsed_time/60 
    elif units_t == 'h':
        # Convert seconds to hours
        elapsed_time = elapsed_time/60/60 
    else:
        raise ValueError('Unable to recognise the units for the time.')    
    return elapsed_time
        
def Distance(longitude, latitude, units_gps='semicircles', units_d='m',
             mode='start', fixed_lon=1601994.0, fixed_lat=622913929.0):
    """Calculate the great circle distance between two points
    on the earth using the Haversine formula.
        
    Arguments:
    longitude : float pandas Series
        Longitude values of GPS coordinates, in units of units_gps
    latitude : float pandas Series
        Latitude values of GPS coordinates, in units of units_gps        
    units_gps : string
        Units of longitude or latitude, e.g. 'semicircles' (default) or 'deg'
    units_d: string
        Units of the calculated distance, e.g. 'm' (default) or 'km'
    mode : string
        If 'start' calculate the distance between all points of the array and the first point.
        If 'previous' calculate the distance between all points of the array the previous point.
        If 'fixed' calculate the distance between all points of the array and a fixed point.
    fixed_lon: float
        Longitude value in units of units_gps to be used with mode='fixed'
    fixed_lat: float
        Latitude value in units of units_gps to be used with mode='fixed'        
    
    Output:
    distance: float pandas Series
        Contains the calculated distance in units of units_d
    """
    
    if units_gps == 'semicircles':
        # Convert semicircles to degrees
        longitude = longitude*180/2**31
        latitude = latitude*180/2**31
    elif units_gps == 'deg':
        pass
    else:
        raise ValueError('Unable to recognise the units for the longitude and latitude.')
    
    origin_lon = np.empty(longitude.shape)
    origin_lat = np.empty(latitude.shape)
    
    if mode == 'start':
        origin_lon[:] = longitude[0]
        origin_lat[:] = latitude[0]
    
    elif mode == 'previous':
        origin_lon[0] = longitude[0]
        origin_lat[0] = latitude[0]
        
        origin_lon[1:] = longitude[0:-1]
        origin_lat[1:] = latitude[0:-1]
        
    elif mode == 'fixed':
        if units_gps == 'semicircles':
            fixed_lon = fixed_lon*180/2**31
            fixed_lat = fixed_lat*180/2**31
            
        origin_lon[:] = fixed_lon
        origin_lat[:] = fixed_lat

    else:
        raise ValueError('Unable to recognise the mode.')  
    
    # Radius of the Earth in units of units_d
    if units_d == 'm':
        radius = 6371000
    elif units_d == 'km':
        radius = 6371
    else:
        raise ValueError('Unable to recognise the units for the distance.')
    
    delta_lon = np.radians(longitude-origin_lon)
    delta_lat = np.radians(latitude-origin_lat)
    # Haversine formula
    a = np.sin(delta_lat/2) * np.sin(delta_lat/2) + np.cos(np.radians(origin_lat)) \
        * np.cos(np.radians(latitude)) * np.sin(delta_lon/2) * np.sin(delta_lon/2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))    
    distance = radius * c # Same units as radius
    # TODO: check the validity of the Haversine formula
    # https://en.wikipedia.org/wiki/Geographical_distance

    return distance
    
if __name__ == '__main__':
    app = QtGui.QApplication([])
    gui = DataBaseGUI()
    gui.show()
    