# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo

Reads Garmin database entries.
"""
# pyuic4 DataBaseGUIdesign.ui -o DataBaseGUIdesign.py

from MatplotlibSettings import *
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import DataBaseGUIdesign
import sys
import os
from PyQt4 import QtGui, QtCore
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

#matplotlib.rcParams.update({'font.size': 50})

sport_colours = {'walking':'g',
                 'cycling':'b',
                 'running':'r',
                 'driving':'k',
                 'train':'y',
                 'punting':'c',
                 'training':'m',
                 'test':'g',
                 'lucia':'k',
                 'mixed':'y',
                 'squash':'m',
                 'yoga':'c',
                 }
# TODO: generate unique colours for all sports
                 
record_units = {'elapsed_time':'min',
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
                }
                 
session_units = {'activity':None,
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


class DataBaseGUI(QtGui.QMainWindow, DataBaseGUIdesign.Ui_DataBaseGUI):
    """
    GUI which analyses and plots the expenses data from a csv file
    """
    def __init__(self, parent=None):
        super(DataBaseGUI, self).__init__(parent)
        self.setupUi(self)
        #self.file_path = os.getcwd()
        self.file_path = 'C:/Users/Ana Andres/Documents/Garmin/database/Garmin-Ana-171001-1.csv'   
        self.ReadFilePathWidget.insert(self.file_path)
        self.records_directory = 'C:/Users/Ana Andres/Documents/Garmin/csv/all/'
        self.new_file()
        self.location_list()
                
        
        # Connect GUI elements
        self.NewFilePushButton.clicked.connect(self.new_file)
        self.RefreshPlot1PushButton.clicked.connect(self.refresh_1)      
        self.RefreshPlot2PushButton.clicked.connect(self.refresh_2)  
        self.SaveDataPushButton.clicked.connect(self.save_data)  
        
        self.figure1 = Figure()
        self.canvas1 = FigureCanvas(self.figure1)
        self.toolbar1 = NavigationToolbar(self.canvas1, self)
        self.Plot1WidgetContainer.addWidget(self.toolbar1)
        self.Plot1WidgetContainer.addWidget(self.canvas1)    

        self.figure2 = Figure()
        self.canvas2 = FigureCanvas(self.figure2)
        self.toolbar2 = NavigationToolbar(self.canvas2, self)
        self.Plot2WidgetContainer.addWidget(self.toolbar2)
        self.Plot2WidgetContainer.addWidget(self.canvas2)  
        
        self.LegendComboBox.addItem('sport', 0)
        self.LegendComboBox.addItem('activity', 0)
        self.LegendComboBox.addItem('gear', 0)
        self.LegendComboBox.setCurrentIndex(0)
        # TODO: implement different legend options in plot 1
        
        for key in record_units:
            self.XComboBox2.addItem(key, 0)
            self.YComboBox2.addItem(key, 0)
        index = self.XComboBox2.findText('elapsed_time')
        self.XComboBox2.setCurrentIndex(index)
        index = self.YComboBox2.findText('speed')
        self.YComboBox2.setCurrentIndex(index)
    
    
        # Initial plot
        self.refresh_1()
        self.refresh_2()
        
    
    def new_file(self):
        """Select a new CSV file.""" 
        file_path = self.ReadFilePathWidget.text()
#        file_path = QtGui.QFileDialog.getOpenFileName(self, 'Choose database .csv file to read.', file_path, "CSV files (*.csv)")
        if len(file_path):
            self.file_path = file_path
            self.ReadFilePathWidget.clear()
            self.SaveFilePathWidget.clear()
            self.ReadFilePathWidget.insert(self.file_path)
            self.SaveFilePathWidget.insert(self.file_path)
            self.read_file()
            # TODO: don't overwrite previous user input settings
        else:
            print "No file chosen. Choose another file to avoid errors."            
        
    def read_file(self):
        """Read the CSV file."""
        print self.file_path
        self.df = pd.read_csv(self.file_path, parse_dates='start_time', index_col='start_time', dayfirst=True)
        self.df['timezone'] = pd.to_timedelta(self.df['timezone'])
        #print "File read."
        self.df_selected = self.df
#        self.StartDateEdit.setDate(min(self.df.index))
#        self.EndDateEdit.setDate(max(self.df.index))
        self.sports = self.populate_list('sport', self.SportsListWidget)
        self.activities = self.populate_list('activity', self.ActivitiesListWidget)
        self.gear = self.populate_list('gear', self.GearListWidget)
        
        self.XComboBox1.clear()
        self.YComboBox1.clear()        
        self.SizeComboBox.clear()      

        self.SizeComboBox.addItem('constant', 0)
        for item in np.sort(self.df.columns):
            if self.df.dtypes[item] == 'int64' or self.df.dtypes[item] == 'float64':
                self.XComboBox1.addItem(item, 0)
                self.YComboBox1.addItem(item, 0)
                self.SizeComboBox.addItem(item, 0)
        
        datetime_options = ['daytime', 'weekday', 'start_time']
        # TODO: datetime_options = ['daytime', 'weekday', 'start_time', 'end_time']
        for item in datetime_options:
            self.XComboBox1.addItem(item, 0)
            self.YComboBox1.addItem(item, 0)
        self.SizeComboBox.addItem('weekday', 0)
            
        index = self.XComboBox1.findText('avg_speed')
        self.XComboBox1.setCurrentIndex(index)
        index = self.YComboBox1.findText('avg_heart_rate')
        self.YComboBox1.setCurrentIndex(index)
        index = self.SizeComboBox.findText('constant')
        self.SizeComboBox.setCurrentIndex(index)
        
           
    def populate_list(self, column, widget):
        """Populate the tree widget with items from the dataframe column."""
        items = np.sort(self.df[column].unique())
        widget.clear()
        for row, item in enumerate(items):
            widget.addItem(item)
            widget.item(row).setSelected(True)
        #print column + ' list updated.'
        return items        

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
            #print file_path
            self.df_locations = pd.read_csv(file_path)
            #print "File read."
            
            for item in self.df_locations['name']:
                self.StartLocationListWidget.addItem(item)
                self.EndLocationListWidget.addItem(item)
            #print "Location lists updated."        
        else:
            print "No file chosen. Choose another file to avoid errors."            
    
    def select_dates(self, df):
        start_date = self.StartDateEdit.date().toPyDate()
        end_date = self.EndDateEdit.date().toPyDate()
        return df.loc[str(start_date) : str(end_date + pd.DateOffset(1))]
        
    def list_selection(self, widget):
        selected_options = []
        for item in widget.selectedItems():
            selected_options.append(item.text())
        return selected_options
    
       
    def generate_mask(self, df, column, selected_options):       
        mask = df[column] == 'nothing'
        for index, option in enumerate(selected_options):
            option_mask = df[column] == option
            mask = mask | option_mask
        return mask
        # TODO: what if some rows are empy in this column?
    
    def df_selection(self):
        df_dates = self.select_dates(self.df)
        
        self.selected_sports = self.list_selection(self.SportsListWidget)
        self.selected_activities = self.list_selection(self.ActivitiesListWidget)
        self.selected_gear = self.list_selection(self.GearListWidget)
        
        mask_sports = self.generate_mask(df_dates, 'sport', self.selected_sports)
        mask_activities = self.generate_mask(df_dates, 'activity', self.selected_activities)
        mask_gear = self.generate_mask(df_dates, 'gear', self.selected_gear)
        
        mask = mask_sports & mask_activities & mask_gear
        self.df_selected = df_dates.loc[mask]
        
    def refresh_1(self):
        self.df_selection()
        self.fill_table(self.df_selected, self.Table1Widget)
        self.plot1()
    
    def plot1(self):
        df = self.df_selected
        
        x = self.XComboBox1.currentText()
        y = self.YComboBox1.currentText()
        size = self.SizeComboBox.currentText()
        
        data_labels = [x,y,size]
        
        self.figure1.clear()
        ax = self.figure1.add_subplot(111)

        legend_variable = self.LegendComboBox.currentText()
        if legend_variable == 'sport':
            selected_legend = self.selected_sports
        elif legend_variable == 'activity':
            selected_legend = self.selected_activities
        elif legend_variable == 'gear':
            selected_legend = self.selected_gear
                   
        cmap = plt.get_cmap('CMRmap')
        colours = cmap(np.linspace(0,1,len(selected_legend)+1))  
        
        for i, label in enumerate(selected_legend):
            data = []
            for item in data_labels:
                if item == 'start_time':
                    # take into account the timezone
                    data_item = df.loc[df[legend_variable]==label].index + df.loc[df[legend_variable]==label, 'timezone']
                    data_item = data_item.values                    
                    # TODO: implement end_time option too
                    
                elif item == 'daytime':
                    # take into account the timezone
                    data_item = df.loc[df[legend_variable]==label].index + df.loc[df[legend_variable]==label, 'timezone']
                    # TODO: fix error that appears when data_item is empty
                    data_item = data_item.dt.time.values
                elif item == 'weekday':
                    # 0 = Monday, ... 6 = Sunday
                    data_item = df.loc[df[legend_variable]==label].index.weekday
                elif item == 'constant':
                    data_item = 1
                else:
                    data_item = df.loc[df[legend_variable]==label, item]
                data.append(data_item)
                
            (x_data,y_data,size_data) = data

            size_data = size_data - np.min(size_data)*0.8
            size_data = size_data / np.max(size_data)*800
            
            if len(x_data) > 0:
                ax.scatter(x_data, y_data, s = size_data, 
                           c = colours[i],
    #                       c = sport_colours[label], 
                           label = label, 
    #                       edgecolors='face', 
                           alpha = 0.4,
                           )
        
        xlabel = x.replace('_',' ')
        if session_units[x]:
            xlabel = xlabel + ' (' + session_units[x] + ')'
        
        ylabel = y.replace('_',' ')
        if session_units[y]:
            ylabel = ylabel + ' (' + session_units[y] + ')'
        
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.legend()
        self.canvas1.draw()
        
        
    def fill_table(self, df, table, max_rows=50):            
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
        table.setVerticalHeaderLabels(df.index[0:row].strftime("%Y-%m-%d %H:%M"))
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
            
        return df
            
    def refresh_2(self):
        selected_rows = self.table_selection(self.Table1Widget)
        self.record_file_numbers = []
        self.record_sports = []
        self.record_timezone = []
        for row in selected_rows:
            self.record_file_numbers.append(self.df_selected.loc[self.df_selected.index[row],'file_name'])
            self.record_sports.append(self.df_selected.loc[self.df_selected.index[row],'sport'])
            self.record_timezone.append(self.df_selected.loc[self.df_selected.index[row],'timezone'])
        self.plot2() # this also fills Tables 1 and 2
        
        # TODO: update Table 1 with new values of heart rate, speed, distance, ...
    
    def table_selection(self, widget):
        selected_rows = []
        for item in widget.selectedIndexes():
            selected_rows.append(item.row())
        selected_rows = np.unique(selected_rows)
        return selected_rows
    
    def read_records(self, file_path):
        df = pd.read_csv(file_path, parse_dates='timestamp', index_col='timestamp')
        df['elapsed_time'] = ElapsedTime(df.index.to_series(), units_t=record_units['elapsed_time'])
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
        print 'saving data...'
        # read data from Table 1
        self.df_widget = self.read_table(self.Table1Widget)
        # combine df_widget with the rest of the activities not shown in Table 1
        df_save = self.merge_dataframes(self.df, self.df_widget)
        self.df = df_save
        # TODO: check wether this is causing issues from the data formats
        
        file_path = self.SaveFilePathWidget.text()
#        file_path = QtGui.QFileDialog.getSaveFileName(self, 'Choose database .csv file to save.', file_path, "CSV files (*.csv)")
        self.SaveFilePathWidget.clear()
        self.SaveFilePathWidget.insert(file_path)
        df_save.to_csv(file_path, sep=',', header=True, index=True)
        
        
        for index, file_number in enumerate(self.record_file_numbers):
            file_path = self.records_directory + str(file_number) + '_record.csv'
            df = self.read_records(file_path)
            df = self.select_times(df)
            df['distance'] = df['distance'] - df.loc[df.index[0],'distance']
            df = df.drop('elapsed_time', axis=1)
            df.to_csv(file_path, sep=',', header=True, index=True)
        
        print 'saving complete \n'
                
    def recalculate_statistics(self,df,file_number):
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
        
        start_position_lat = df.loc[df.index[0],'position_lat']
        self.Table1Widget.setItem(row, column_dict['start_position_lat'], 
                                  QtGui.QTableWidgetItem(format(start_position_lat,'.0f')))

        start_position_long = df.loc[df.index[0],'position_long']
        self.Table1Widget.setItem(row, column_dict['start_position_long'], 
                                  QtGui.QTableWidgetItem(format(start_position_long,'.0f')))        
        
        total_distance = df.loc[df.index[-1],'distance'] - df.loc[df.index[0],'distance']
        self.Table1Widget.setItem(row, column_dict['total_distance'], 
                                  QtGui.QTableWidgetItem(format(total_distance,'.2f')))        

        total_elapsed_time = df.loc[df.index[-1],'elapsed_time'] - df.loc[df.index[0],'elapsed_time']
        total_elapsed_time = total_elapsed_time * 60 # conversion from minutes to seconds
        self.Table1Widget.setItem(row, column_dict['total_elapsed_time'], 
                                  QtGui.QTableWidgetItem(format(total_elapsed_time,'.3f')))        
        
        
    
    def plot2(self):
        x1 = self.XComboBox2.currentText()
        y1 = self.YComboBox2.currentText()
        x2 = 'position_long'
        y2 = 'position_lat'
        
        data_labels = [x1,y1,x2,y2]
        
        self.figure2.clear()
        ax1 = self.figure2.add_subplot(211)
        ax2 = self.figure2.add_subplot(212)
    
        for index, file_number in enumerate(self.record_file_numbers):
            file_path = self.records_directory + str(file_number) + '_record.csv'
            # read the csv file
            df = self.read_records(file_path)
            # select data based on start and end values of elapsed_time
            df = self.select_times(df)
            # recalculate average and max values (heart_rate, speed, ...) and update Table 1
            self.recalculate_statistics(df,file_number)
            sport = self.record_sports[index]
            timezone = self.record_timezone[index]
            # TODO: what if the file contains mixed sports?
            
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
            
            ax1.plot(x1_data, y1_data,
#                    c = sport_colours[sport],
                    label = str(file_number) + ': ' + sport,
                    )
                    
            ax2.plot(x2_data, y2_data,
#                    c = sport_colours[sport],
                    label = str(file_number) + ': ' + sport,
                    )
                    
        
        xlabel = x1.replace('_',' ')
        if record_units[x1]:
            xlabel = xlabel + ' (' + record_units[x1] + ')'
        
        ylabel = y1.replace('_',' ')
        if record_units[y1]:
            ylabel = ylabel + ' (' + record_units[y1] + ')'
        
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel(ylabel)
        if len(self.record_file_numbers) > 0 and len(self.record_file_numbers) <= 5:
            ax1.legend()
        
        xlabel = x2.replace('_',' ')
        if record_units[x2]:
            xlabel = xlabel + ' (' + record_units[x2] + ')'
        
        ylabel = y2.replace('_',' ')
        if record_units[y2]:
            ylabel = ylabel + ' (' + record_units[y2] + ')'
        
        ax2.set_xlabel(xlabel)
        ax2.set_ylabel(ylabel)
#        if len(self.record_file_numbers) > 0 and len(self.record_file_numbers) <= 5:
#            ax2.legend()
        
        self.canvas2.draw()
            
            
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

    origin_time =  np.empty(timestamp.shape, dtype=type(timestamp))
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
        
    
if __name__ == '__main__':
    
    app = QtGui.QApplication(sys.argv)
    GUI = DataBaseGUI()
    GUI.show()
    app.exec_()
    