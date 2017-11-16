# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo
GUI which reads, analyses, plots, and updates the database CSV file and the activities' CSV files.
"""
# pyuic4 DataBaseGUIdesign.ui -o DataBaseGUIdesign.py


import sys
import gmplot
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from MatplotlibSettings import *

import DataBaseGUIdesign
from PyQt4 import QtGui, QtCore

# matplotlib.rcParams.update({'font.size': 50})

class DataBaseGUI(QtGui.QMainWindow, DataBaseGUIdesign.Ui_DataBaseGUI):
    """
    GUI which analyses and plots GPS and fitness data.
    """
    def __init__(self, parent=None):
        super(DataBaseGUI, self).__init__(parent)
        self.setupUi(self)
#        self.file_path = os.getcwd()        
        self.file_path = 'C:/Users/Ana Andres/Documents/Garmin/database/'   
#        self.file_path = QtGui.QFileDialog.getOpenFileName(self, 'Choose database .csv file to read.', self.file_path, "CSV files (*.csv)")
        self.ReadFilePathWidget.insert(self.file_path)
        self.MapFilePathWidget.insert('C:/Users/Ana Andres/Documents/Garmin/maps/mymap.html')        
        self.records_directory = 'C:/Users/Ana Andres/Documents/Garmin/csv/'    

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
        self.dataframe_units = {'elapsed_time':'min',
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
                                'enhanced_avg_speed':'m/s',
                                'event':None,
                                'event_type':None,
                                'file_name':None,
                                'first_lap_index	':None,
                                'gear':None,
                                'max_cadence':'rpm',
                                'max_heart_rate':'bpm',
                                'message_index':None,
                                'num_laps':None,
                                'sport':None,
                                'start_position_lat':'semicircle',
                                'start_position_long':'semicircles',
                                'end_position_lat':'semicircle',
                                'end_position_long':'semicircles',
                                'start_time':None,
                                'sub_sport':None,
                                'timestamp':None,
                                'timezone':'h',
                                'total_calories':'kcal',
                                'total_distance':'m/s',
                                'total_elapsed_time':'s',
                                'total_strides':'strides',
                                'total_timer_time':'s',
                                'trigger':None,
                                'weekday':'0 = Monday, 6 = Sunday'
                                }            
        
        # Connect GUI elements
        self.NewFilePushButton.clicked.connect(self.new_file)
        self.FilterPlotDatabasePushButton.clicked.connect(self.filter_and_plot_database)      
        self.PlotTracePushButton.clicked.connect(self.refresh_2)  
        self.SaveDataPushButton.clicked.connect(self.save_data)  
        self.SaveMapPushButton.clicked.connect(self.save_map)  
        self.ScatterPushButton.clicked.connect(self.plot_scatter)  
        self.HistogramPushButton.clicked.connect(self.plot_histogram)  
        self.PlotMapPushButton.clicked.connect(self.generate_map)  
        self.UpdateUnitsPushButton.clicked.connect(self.update_units)  
        self.SIUnitsPushButton.clicked.connect(self.set_SI_units)  
        
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
        
        legend_list = ['sport','activity','gear']
        for item in legend_list:
            self.ScatterLegendComboBox.addItem(item, 0)
            self.HistLegendComboBox.addItem(item, 0)
        index = self.ScatterLegendComboBox.findText('sport')
        self.ScatterLegendComboBox.setCurrentIndex(index)
        index = self.HistLegendComboBox.findText('sport')
        self.HistLegendComboBox.setCurrentIndex(index)
       
        colormap_list = ['CMRmap','Set1','Accent','jet']
        for item in colormap_list:
            self.HistCMapComboBox.addItem(item, 0)
            self.ScatterCMapComboBox.addItem(item, 0)
        index = self.HistCMapComboBox.findText('CMRmap')
        self.HistCMapComboBox.setCurrentIndex(index)
        index = self.ScatterCMapComboBox.findText('CMRmap')
        self.ScatterCMapComboBox.setCurrentIndex(index)
        
        # TODO: these options are wrong
        for key in np.sort(self.dataframe_units.keys()):
            self.XComboBox2.addItem(key, 0)
            self.YComboBox2.addItem(key, 0)
        index = self.XComboBox2.findText('elapsed_time')
        self.XComboBox2.setCurrentIndex(index)
        index = self.YComboBox2.findText('speed')
        self.YComboBox2.setCurrentIndex(index)
        
        for key in self.time_units.keys():
            self.TimeUnitsComboBox.addItem(key, 0)
        index = self.TimeUnitsComboBox.findText('s')
        self.TimeUnitsComboBox.setCurrentIndex(index)

        for key in self.position_units.keys():
            self.PositionUnitsComboBox.addItem(key, 0)
        index = self.PositionUnitsComboBox.findText('semicircles')
        self.PositionUnitsComboBox.setCurrentIndex(index)
        
        for key in self.distance_units.keys():
            self.DistanceUnitsComboBox.addItem(key, 0)
        index = self.DistanceUnitsComboBox.findText('m')
        self.DistanceUnitsComboBox.setCurrentIndex(index)

        for key in self.speed_units.keys():
            self.SpeedUnitsComboBox.addItem(key, 0)
        index = self.SpeedUnitsComboBox.findText('m/s')
        self.SpeedUnitsComboBox.setCurrentIndex(index)
    
        # Read file      
        self.new_file()

    
    def new_file(self):
        """Select a new Garmin DataBase CSV file and locations file.""" 
        self.location_list()
        file_path = self.ReadFilePathWidget.text()
        file_path = QtGui.QFileDialog.getOpenFileName(self, 'Choose database .csv file to read.', file_path, "CSV files (*.csv)")
        if len(file_path):
            self.file_path = file_path
            self.ReadFilePathWidget.clear()
            self.SaveFilePathWidget.clear()
            self.ReadFilePathWidget.insert(self.file_path)
            self.SaveFilePathWidget.insert(self.file_path)
            self.read_file()      
            # make a copy so the current_units can be modified independently from the SI_units
            self.current_units = dict(self.SI_units) 
            self.update_units()
            self.filter_and_plot_database()            
            self.refresh_2()
            # TODO: don't overwrite previous user input settings
        else:
            print "No file chosen. Choose another file to avoid errors.\n"            
        
    def read_file(self):
        """Read the CSV file."""
        print self.file_path + '\n'
        
        self.df = pd.read_csv(self.file_path, parse_dates=['start_time'], index_col='start_time', dayfirst=True)
        self.df['timezone'] = pd.to_timedelta(self.df['timezone'])
        # TODO: what if the dates column is not called start_time
        
        # Create a variable with the column names to use when saving the database
        self.database_columns_to_save = self.df.columns

        self.df = self.calculate_new_columns(self.df)                    
        self.df_selected = self.df.copy()
        
        
#        self.StartDateEdit.setDate(min(self.df.index))
#        self.EndDateEdit.setDate(max(self.df.index))
        self.sports = self.populate_list('sport', self.SportsListWidget)
        self.activities = self.populate_list('activity', self.ActivitiesListWidget)
        self.gear = self.populate_list('gear', self.GearListWidget)
        
        self.HistXComboBox.clear()
        self.ScatterXComboBox.clear()
        self.ScatterYComboBox.clear()        
        self.ScatterSizeComboBox.clear()      

        scatter_plot_variables = self.df.columns
        self.ScatterSizeComboBox.addItem('constant', 0)
        for item in np.sort(scatter_plot_variables):
#            if self.df.dtypes[item] == 'int64' or self.df.dtypes[item] == 'float64' or self.df.dtypes[item] == 'datetime.time':
#            if self.df.dtypes[item] != 'str':
            # TODO: disable unwanted options
#                print item                
#                print self.df.dtypes[item]
#                print
                self.HistXComboBox.addItem(item, 0)
                self.ScatterXComboBox.addItem(item, 0)
                self.ScatterYComboBox.addItem(item, 0)
                self.ScatterSizeComboBox.addItem(item, 0)             
        
        index = self.HistXComboBox.findText('avg_speed')
        self.HistXComboBox.setCurrentIndex(index)
        index = self.ScatterXComboBox.findText('avg_speed')
        self.ScatterXComboBox.setCurrentIndex(index)
        index = self.ScatterYComboBox.findText('avg_heart_rate')
        self.ScatterYComboBox.setCurrentIndex(index)
        index = self.ScatterSizeComboBox.findText('constant')
        self.ScatterSizeComboBox.setCurrentIndex(index)       
        
    def calculate_new_columns(self, df): 
        # take into account the timezone        
        temp =  df.index + df['timezone']
        # TODO: what if there is no timezone?       
        df['start_daytime'] = temp.dt.time.values
        # TODO: add end_daytime info when it's added in DatabaseWrite.py
        df['weekday'] = temp.dt.weekday
        df['start_time_local'] = temp.values
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
        self.fill_table(self.df_selected, self.Table1Widget, self.DatabaseRowsSpinBox.value())       
        # TODO: also convert units in the trace plot
    
    def convert_units(self, df, units, to_SI=False):
        # if to_SI = False: convert from SI_units to dataframe_units
        # if to_SI = True: convert from dataframe_units to SI_units
        if to_SI:
            factor = -1.
        else: 
            factor = 1.
    
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
        return df.loc[str(start_date) : str(end_date + pd.DateOffset(1))]
        
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
        
        file_path = 'C:/Users/Ana Andres/Documents/Garmin/database/Garmin-Locations.csv'        
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
        # TODO: allow several gear for the same activity
    
    def filter_database(self):
        df_dates = self.select_dates(self.df)
        
        self.selected_sports = self.list_selection(self.SportsListWidget)
        self.selected_activities = self.list_selection(self.ActivitiesListWidget)
        self.selected_gear = self.list_selection(self.GearListWidget)
        self.selected_start_locations = self.list_selection(self.StartLocationListWidget)
        self.selected_end_locations = self.list_selection(self.EndLocationListWidget)
        # TODO: add more selection options - speed, heart_rate, time, distance...
        
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
        self.EndTimeDoubleSpinBox.setValue(1000)
    
    def plot_scatter(self):
        df = self.df_selected
        
        x = self.ScatterXComboBox.currentText()
        y = self.ScatterYComboBox.currentText()
        size = self.ScatterSizeComboBox.currentText()
        
#        data_labels = [x,y,size]
#        print '\nstatistics:'
#        print df.loc[:,[x,y]].describe()
        
        self.figure_scatter.clear()
        ax = self.figure_scatter.add_subplot(111)

        legend_variable = self.ScatterLegendComboBox.currentText()
        if legend_variable == 'sport':
            selected_legend = self.selected_sports
        elif legend_variable == 'activity':
            selected_legend = self.selected_activities
        elif legend_variable == 'gear':
            selected_legend = self.selected_gear
        
        cmap_name = self.ScatterCMapComboBox.currentText()
        cmap = plt.get_cmap(cmap_name)
        colours = cmap(np.linspace(0,1,len(selected_legend)+1))          
        
        for i, label in enumerate(selected_legend):
            
            # select data according to the legend variable selected            
            df_plot = df.loc[df[legend_variable]==label]
            
            # generate size array
            if size == 'constant':
                size_data = 1
            else:
                size_data = df_plot[size]
                
            size_data = size_data - np.min(size_data)*0.8
            size_data = size_data / np.max(size_data)*800
            
            # TODO: fix error that shows when trying to plot timestamps
            if len(df_plot) > 0:
                # scatter plot
                df_plot.plot(kind='scatter', x=x, y=y, s = size_data, ax=ax,
                           color = [colours[i],] * len(df_plot),
                           # the RGB colour array is duplidated for every data points
                           # otherwise when having just 4 data points it gets confused
                           # due to a bug in matplotlib
                           label = label, 
                           alpha = 0.4, # edgecolors='face',                            
                           )
                
        
        xlabel = x.replace('_',' ')
        if self.dataframe_units[x]:
            xlabel = xlabel + ' (' + self.dataframe_units[x] + ')'
        
        ylabel = y.replace('_',' ')
        if self.dataframe_units[y]:
            ylabel = ylabel + ' (' + self.dataframe_units[y] + ')'
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.legend()
        self.canvas_scatter.draw()
        
            
    def plot_histogram(self):
        df = self.df_selected
        x = self.HistXComboBox.currentText()        
        self.figure_hist.clear()
        ax = self.figure_hist.add_subplot(111)

        legend_variable = self.HistLegendComboBox.currentText()
        if legend_variable == 'sport':
            selected_legend = self.selected_sports
        elif legend_variable == 'activity':
            selected_legend = self.selected_activities
        elif legend_variable == 'gear':
            selected_legend = self.selected_gear
        
        cmap_name = self.HistCMapComboBox.currentText()
        cmap = plt.get_cmap(cmap_name)
        colours = cmap(np.linspace(0,1,len(selected_legend)+1))  
        # generate colours after the plot in case there are empty sports or other
        
        try:
            bins = np.linspace(min(df[x]), max(df[x]), 20)
            histogram = True
            # TODO: what if it's start_time, daytime, or weekday?
        except:
            print "Cannot generate histogram.\n"
            histogram = False
        
        for i, label in enumerate(selected_legend):
#            data = []
#            for item in data_labels:
#                if item == 'constant':
#                    data_item = 1
#                else:
#                    data_item = df.loc[df[legend_variable]==label, item]
##                    print label
##                    print item
##                    print data_item.head()
##                    print
#                data.append(data_item)

                
            x_data = df.loc[df[legend_variable]==label, x]
            
            if len(x_data) > 1:                
                # histogram plot
                if histogram:
                    ax.hist(x_data, bins=bins,
                            color = colours[i], label = label, 
                            normed = True, alpha = 0.4,
                            )
                            
        
        xlabel = x.replace('_',' ')
        if self.dataframe_units[x]:
            xlabel = xlabel + ' (' + self.dataframe_units[x] + ')'        
        
        if histogram:
            ax.set_xlabel(xlabel)
            ax.set_ylabel('frequency')
            ax.legend()
            self.canvas_hist.draw()
        
        
        
    def fill_table(self, df, table, max_rows=50):    
        # TODO: add option for the user to select how many rows to print
        # TODO: make sure the default is often reset to 50    
        # TODO: organise by start time - with or without timezone?
        # TODO: use timestamp as column index or not?
        table.clear()
        table.setColumnCount(len(df.columns))
        table.setHorizontalHeaderLabels(df.columns)
            
        row = 0
        while row <= min(max_rows,len(df.index)-1):
            table.setRowCount(row+1)
            for col in range(len(df.columns)):                
                table.setItem(row,col,QtGui.QTableWidgetItem(str(df.iloc[row,col])))
                table.resizeColumnToContents(col)
            row = row + 1
        table.setVerticalHeaderLabels(df.index[0:row].strftime("%Y-%m-%d %H:%M:%S"))
#        if row == max_rows:
#            print "Only the first " + str(max_rows) + " rows are displayed in the table.\n"                         
#            table.setRowCount(row+1)
#            table.setItem(row,0,QtGui.QTableWidgetItem(str('And more...')))            
#            table.resizeColumnToContents(col)
    
    def read_table(self,table):
        rows = table.rowCount()
        columns = table.columnCount()

        column_names = []
        for column in range(columns):
            column_names.append(table.horizontalHeaderItem(column).text())

        index_values = []
        for row in range(rows):
            index_values.append(pd.to_datetime(table.verticalHeaderItem(row).text()))
            # TODO: what if the index is not a datetime?
        
        df = pd.DataFrame(columns=column_names, index=index_values)
        df.index.name = 'start_time'
        # TODO: what if the index is called 'timestamp' instead?
        
        for row, index in enumerate(index_values):
            for column_number, column_name in enumerate(column_names):
                df.loc[index,column_name] = table.item(row,column_number).data(0)
            
        # TODO: make this formatting more automatic
        # format data types
        for column_name in column_names:
            # format dates
            if column_name == 'start_time_local':
                df[column_name] = pd.to_datetime(df[column_name])
            elif 'position' in column_name:
                df[column_name] = pd.to_numeric(df[column_name], errors='coerce')
            # change strings to numbers
            elif column_name != 'file_name':
                df[column_name] = pd.to_numeric(df[column_name], errors='ignore')        
        return df
            

    
    def table_selection(self, widget):
        selected_rows = []
        for item in widget.selectedIndexes():
            selected_rows.append(item.row())
        selected_rows = np.unique(selected_rows)
        return selected_rows
    
    def read_records(self, file_path):
        df = pd.read_csv(file_path, parse_dates=['timestamp'], index_col='timestamp')
        df['elapsed_time'] = ElapsedTime(df.index.to_series(), units_t=self.dataframe_units['elapsed_time'])
        return df
        
    def select_times(self, df):
        start_time = self.StartTimeDoubleSpinBox.value()
        end_time = self.EndTimeDoubleSpinBox.value()
        mask_start = df['elapsed_time'] >= start_time
        mask_end = df['elapsed_time'] <= end_time
        return df.loc[mask_start & mask_end]
    
    def merge_dataframes(self,left,right):
        for row in right.index:
            for column in right.columns:
                left.loc[row,column] = right.loc[row,column]
        return left
    
    def save_data(self):
        # TODO: strange characters like ñ screw it up
        print 'Saving data...'
        # read data from Table 1
        df_widget = self.read_table(self.Table1Widget)
        self.temp = df_widget
        # combine df_widget with the rest of the activities not shown in Table 1
#        df_save = self.merge_dataframes(df_widget, self.df)
        df_save = self.merge_dataframes(self.df, df_widget)
        # TODO: remove the columns we added at the start
        self.df = df_save
        # TODO: check wether this is causing issues from the data formats
        
        # convert to SI units before saving
        df_save = self.convert_units(df_save, self.current_units, to_SI=True)
        
        file_path = self.SaveFilePathWidget.text()
#        file_path = QtGui.QFileDialog.getSaveFileName(self, 'Choose database .csv file to save.', file_path, "CSV files (*.csv)")
        self.SaveFilePathWidget.clear()
        self.SaveFilePathWidget.insert(file_path)
        self.ReadFilePathWidget.clear()
        self.ReadFilePathWidget.insert(file_path)
        df_save.to_csv(file_path, sep=',', header=True, index=True, columns=self.database_columns_to_save)
        
        
        for index, file_number in enumerate(self.record_file_numbers):
            file_path = self.records_directory + str(file_number) + '_record.csv'
            df = self.read_records(file_path)
            df = self.select_times(df)
            df['distance'] = df['distance'] - df.loc[df.index[0],'distance']
            df = df.drop('elapsed_time', axis=1)
            df.to_csv(file_path, sep=',', header=True, index=True)
        
        print 'Saving complete! \n'
    
    def generate_map(self):    
        number_of_activities = self.MapActivitiesSpinBox.value()             
        
#        selected_legend = self.selected_sports
#        cmap = plt.get_cmap('CMRmap')
#        colours = cmap(np.linspace(0,1,len(selected_legend)+1))  
#        colours_dict = dict(zip(selected_legend, colours))        
        
        self.figure_map.clear()
        # TODO: use this syntax? fig, axs = plt.subplots(2, 2)
        ax = self.figure_map.add_subplot(111)
        
        self.map_data = {}
        self.map_colours = {}
        avg_lat = []
        avg_long = []
        for index in self.df_selected.iloc[0:number_of_activities].index:
            file_number = self.df_selected.loc[index,'file_name']
#            sport = self.df_selected.loc[index,'sport']
            # TODO: use different colours for different sports
            
            file_path = self.records_directory + str(file_number) + '_record.csv'
            # read the csv file
            df = self.read_records(file_path)  
            df = self.convert_units(df, self.current_units)
            # Extract location information, remove missing data, convert to degrees
#            self.map_data[file_number] = df.loc[:,['position_lat','position_long']].dropna()*180/2**31
#            self.map_data[file_number] = df.loc[:,['position_lat','position_long']].dropna()*position_units_factor
            self.map_data[file_number] = df.loc[:,['position_lat','position_long']].dropna()
            self.map_colours[file_number] = 'k'
            
            avg_long.append(self.map_data[file_number]['position_long'].mean())
            avg_lat.append(self.map_data[file_number]['position_lat'].mean())
            
            # TODO: user option: line (faster) or scatter (better if many nan) plot
            ax.plot(self.map_data[file_number]['position_long'], 
                    self.map_data[file_number]['position_lat'],
                    label = file_number,
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
#        ax.set_xlabel('longitude (degrees)')
#        ax.set_ylabel('latitude (degrees)')        
#        ax.set_xlabel('longitude (' + position_units_name + ')')
#        ax.set_ylabel('latitude (' + position_units_name + ')')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        
        self.canvas_map.draw()
        
        # TODO: calculate the required zoom too
        # TODO: adjust histogram number of bins depending on the data
#        self.temp = avg_long
        temp = np.histogram(avg_long,bins=100)
        centre_long = (temp[1][np.argmax(temp[0])] + temp[1][np.argmax(temp[0])+1])/2
        temp = np.histogram(avg_lat,bins=100)
        centre_lat = (temp[1][np.argmax(temp[0])] + temp[1][np.argmax(temp[0])+1])/2
        self.map_centre = [centre_long, centre_lat]        
#        self.map_centre = [np.mean(avg_long), np.mean(avg_lat)]            
        
        
    def save_map(self):     
        # TODO: this will only work if the GPS units is set to "deg", allow other options
    
        gmap = gmplot.GoogleMapPlotter(self.map_centre[1], self.map_centre[0], 13)
#        gmap = gmplot.GoogleMapPlotter(52.202, 0.12, 13) # Cambridge 
#        gmap = gmplot.GoogleMapPlotter(43, -120, 5) # USA West Coast
#        gmap = gmplot.GoogleMapPlotter(46.36, 14.09, 11) # Lake Bled        
        
        for key in self.map_data:             
            # Add a line plot to the gmap object which will be save to an .html file
            # Use line instead of scatter plot for faster speed and smaller file size
            
            # TODO: user option: line (faster) or scatter (bery very slow) plot
            # so if there are nan, e.g. metro, separate the plots into several line plots
            gmap.plot(self.map_data[key]['position_lat'], 
                      self.map_data[key]['position_long'], 
                      color=self.map_colours[key], edge_width=3)
#            gmap.scatter(self.map_data[key]['position_lat'][0:-1:5], 
#                         self.map_data[key]['position_long'][0:-1:5], 
#                         color=self.map_colours[key], size=10, marker=False)
        
        file_path = self.MapFilePathWidget.text()
        file_path = QtGui.QFileDialog.getSaveFileName(self, 'Choose .html file to save map.', file_path, "HTML files (*.html)")
        self.MapFilePathWidget.clear()
        self.MapFilePathWidget.insert(file_path)        
        gmap.draw(file_path)
                

    def refresh_2(self):
        selected_rows = self.table_selection(self.Table1Widget)
        self.record_file_numbers = []
        self.record_sports = []
        self.record_timezone = []
        for row in selected_rows:
            self.record_file_numbers.append(self.df_selected.loc[self.df_selected.index[row],'file_name'])
            self.record_sports.append(self.df_selected.loc[self.df_selected.index[row],'sport'])
            self.record_timezone.append(self.df_selected.loc[self.df_selected.index[row],'timezone'])
        self.select_and_plot_trace() # this also fills Tables 1 and 2
        
            
    def select_and_plot_trace(self):
        x1 = self.XComboBox2.currentText()
        y1 = self.YComboBox2.currentText()
        x2 = 'position_long'
        y2 = 'position_lat'
        
        data_labels = [x1,y1,x2,y2]
        
        self.figure_trace.clear()
        # TODO: use this syntax? fig, axs = plt.subplots(2, 2)
        ax1 = self.figure_trace.add_subplot(211)
        ax2 = self.figure_trace.add_subplot(212)
    
        for index, file_number in enumerate(self.record_file_numbers):
            file_path = self.records_directory + str(file_number) + '_record.csv'
            # read the csv file
            df = self.read_records(file_path)
            # select data based on start and end values of elapsed_time
            df = self.select_times(df)
            # TODO: output the statistics to the GUI
            # TODO: fix error when a non-df column is selected by making all the options be part of the df
#            try:
#                print '\n' + str(file_number)
#                print df.loc[:,[x1,y1]].describe()
#            except:
#                pass
            # recalculate average and max values (heart_rate, speed, ...) and update Table 1
            self.recalculate_statistics(df,file_number)
            sport = self.record_sports[index]
            timezone = self.record_timezone[index]
            
            if index == 0:
                self.fill_table(df, self.Table2Widget)
            
            data = []
            for item in data_labels:
                if item == 'timestamp':
                    # take into account the timezone
                    data_item = df.index + timezone
                else:
                    data_item = df[item]
                data.append(data_item)
                
            (x1_data, y1_data, x2_data, y2_data) = data
#            x1_data = np.nan_to_num(x1_data)
#            y1_data = np.nan_to_num(y1_data)
#            x2_data = np.nan_to_num(x2_data)
#            y2_data = np.nan_to_num(y2_data)
            
            # TODO: use a different label - start_time instead of file_number?
            # TODO: use a different colour scheme
            # TODO: allow scatter plot option
            plot_label = str(file_number) + ': ' + sport;
            ax1.plot(x1_data, y1_data,
#                    c = sport_colours[sport],
                    label = plot_label,
                    )
                    
            ax2.plot(x2_data, y2_data,
#                    c = sport_colours[sport],
                    label = plot_label,
                    )
                    
        
        xlabel = x1.replace('_',' ')
        if self.dataframe_units[x1]:
            xlabel = xlabel + ' (' + self.dataframe_units[x1] + ')'
        
        ylabel = y1.replace('_',' ')
        if self.dataframe_units[y1]:
            ylabel = ylabel + ' (' + self.dataframe_units[y1] + ')'
        
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel(ylabel)
        if self.TraceLegendCheckBox.checkState():
            ax1.legend()
        
        xlabel = x2.replace('_',' ')
        if self.dataframe_units[x2]:
            xlabel = xlabel + ' (' + self.dataframe_units[x2] + ')'
        
        ylabel = y2.replace('_',' ')
        if self.dataframe_units[y2]:
            ylabel = ylabel + ' (' + self.dataframe_units[y2] + ')'
        
        # make sure x and y axis have the same spacing
        ax2.axis('equal')        
        ax2.set_xlabel(xlabel)
        ax2.set_ylabel(ylabel)
        if self.MapLegendCheckBox.checkState():
            ax2.legend()
        
        self.canvas_trace.draw()
            
    def recalculate_statistics(self,df,file_number):
        # TODO: take into account non SI units!!!
        row = self.Table1Widget.findItems(str(file_number),QtCore.Qt.MatchExactly)[0].row()
        
        number_of_columns = self.Table1Widget.columnCount()
        column_dict = {}
        for column in range(number_of_columns):
            column_name = self.Table1Widget.horizontalHeaderItem(column).text()
            column_dict[column_name] = column
               
        avg_speed = df['speed'].mean()
        self.Table1Widget.setItem(row, column_dict['avg_speed'], 
                                  QtGui.QTableWidgetItem(format(avg_speed,'.3f')))
                                                                   
        avg_heart_rate = df['heart_rate'].mean()
        self.Table1Widget.setItem(row, column_dict['avg_heart_rate'], 
                                  QtGui.QTableWidgetItem(format(avg_heart_rate,'.0f')))
                                 
        max_heart_rate = df['heart_rate'].max()
        self.Table1Widget.setItem(row, column_dict['max_heart_rate'], 
                                  QtGui.QTableWidgetItem(format(max_heart_rate,'.0f')))
                                  
        # TODO: fix the average cadence calculation because it decreases drastically for no apparent reason
#        avg_cadence = df['cadence'].mean()
#        self.Table1Widget.setItem(row, column_dict['avg_cadence'], 
#                                  QtGui.QTableWidgetItem(format(avg_cadence,'.1f')))
#                                 
#        max_cadence = df['cadence'].max()
#        self.Table1Widget.setItem(row, column_dict['max_cadence'], 
#                                  QtGui.QTableWidgetItem(format(max_cadence,'.1f')))
        
        start_position_lat = df['position_lat'].dropna().iloc[0]
        self.Table1Widget.setItem(row, column_dict['start_position_lat'], 
                                  QtGui.QTableWidgetItem(format(start_position_lat,'.0f')))
                                  # TODO: fix error when activity has no GPS data

        start_position_long = df['position_long'].dropna().iloc[0]
        self.Table1Widget.setItem(row, column_dict['start_position_long'], 
                                  QtGui.QTableWidgetItem(format(start_position_long,'.0f')))    
                                  
        end_position_lat = df['position_lat'].dropna().iloc[-1]
        self.Table1Widget.setItem(row, column_dict['end_position_lat'], 
                                  QtGui.QTableWidgetItem(format(end_position_lat,'.0f')))

        end_position_long = df['position_long'].dropna().iloc[-1]
        self.Table1Widget.setItem(row, column_dict['end_position_long'], 
                                  QtGui.QTableWidgetItem(format(end_position_long,'.0f')))        
        
        total_distance = df.loc[df.index[-1],'distance'] - df.loc[df.index[0],'distance']
        self.Table1Widget.setItem(row, column_dict['total_distance'], 
                                  QtGui.QTableWidgetItem(format(total_distance,'.2f')))        

        total_elapsed_time = df.loc[df.index[-1],'elapsed_time'] - df.loc[df.index[0],'elapsed_time']
        total_elapsed_time = total_elapsed_time * 60 # conversion from minutes to seconds
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
    
    app = QtGui.QApplication(sys.argv)
    gui = DataBaseGUI()
    gui.show()
    app.exec_()
    