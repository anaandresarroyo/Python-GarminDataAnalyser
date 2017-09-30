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
from PyQt4 import QtGui
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

sport_colours = {'walking':'g',
                 'cycling':'b',
                 'running':'r',
                 'driving':'b',
                 'train': 'm',
                 'water': 'c',
                 'training':'m',
                 'test':'g',
                 'lucia':'k',
                 }
                 
records_units = {'cadence':'rpm',
                 'distance':'m',
                 'enhanced_speed':'m/s',
                 'heart_rate':'bpm',
                 'position_lat':'semicircles',
                 'position_long	':'semicircles',
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
        self.file_path = 'C:/Users/Ana Andres/Documents/Garmin/database/Garmin-Ana-170930.csv'        
        self.new_file()
        self.location_list()
        
        
        # Connect GUI elements
        self.NewFilePushButton.clicked.connect(self.new_file)
        self.RefreshPlot1PushButton.clicked.connect(self.refresh_1)      
        
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
        # TODO: implement different legend options in plot 1
        
    
    def new_file(self):
        """Select a new CSV file.""" 
        file_path = QtGui.QFileDialog.getOpenFileName(self, 'Choose database .csv file.', self.file_path, "CSV files (*.csv)")
        if len(file_path):
            self.file_path = file_path
            self.FilePathWidget.insert(self.file_path)
            self.read_file()
        else:
            print "No file chosen. Choose another file to avoid errors."            
        
    def read_file(self):
        """Read the CSV file."""
        print self.file_path
        self.df = pd.read_csv(self.file_path, parse_dates='start_time', index_col='start_time', dayfirst=True)
        self.df['timezone'] = pd.to_timedelta(self.df['timezone'])
        print "File read."
        self.df_selected = self.df
        self.StartDateEdit.setDate(min(self.df.index))
        self.EndDateEdit.setDate(max(self.df.index))
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
            
        self.XComboBox1.setCurrentIndex(2)
        self.YComboBox1.setCurrentIndex(1)
        self.SizeComboBox.setCurrentIndex(0)
        
           
    def populate_list(self, column, widget):
        """Populate the tree widget with items from the dataframe column."""
        items = np.sort(self.df[column].unique())
        widget.clear()
        for row, item in enumerate(items):
            widget.addItem(item)
            widget.item(row).setSelected(True)
        print column + ' list updated.'
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
            print file_path
            self.df_locations = pd.read_csv(file_path)
            print "File read."
            
            for item in self.df_locations['name']:
                self.StartLocationListWidget.addItem(item)
                self.EndLocationListWidget.addItem(item)
            print "Location lists updated."        
        else:
            print "No file chosen. Choose another file to avoid errors."            
    
    def select_dates(self, df):
        start_date = self.StartDateEdit.date().toPyDate()
        end_date = self.EndDateEdit.date().toPyDate()
        return df.loc[str(start_date) : str(end_date + pd.DateOffset(1))]
        
    def read_selection(self, column, widget):
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
        
        self.selected_sports = self.read_selection('sport', self.SportsListWidget)
        self.selected_activities = self.read_selection('activity', self.ActivitiesListWidget)
        self.selected_gear = self.read_selection('gear', self.GearListWidget)
        
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

        for sport in self.selected_sports:            
            data = []
            for item in data_labels:
                if item == 'start_time':
                    # take into account the timezone
                    data_item = df.loc[df['sport']==sport].index + df.loc[df['sport']==sport, 'timezone']
                    data_item = data_item.values
                    
                    # TODO: implement end_time option too
                    
                elif item == 'daytime':
                    # take into account the timezone
                    data_item = df.loc[df['sport']==sport].index + df.loc[df['sport']==sport, 'timezone']
                    data_item = data_item.dt.time.values
                elif item == 'weekday':
                    # 0 = Monday, ... 6 = Sunday
                    data_item = df.loc[df['sport']==sport].index.weekday
                elif item == 'constant':
                    data_item = 1
                else:
                    data_item = df.loc[df['sport']==sport, item]
                data.append(data_item)
                
            (x_data,y_data,size_data) = data

            size_data = size_data - np.min(size_data)*0.8
            size_data = size_data / np.max(size_data)*500
            
            ax.scatter(x_data, y_data, s = size_data, 
                       c = sport_colours[sport], label = sport, 
                       edgecolors='face', alpha = 0.4)
        
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
        
        
    def fill_table(self, df, widget):            
        widget.clear()
        if len(df.index) < 100:
            widget.setColumnCount(len(df.columns))
            widget.setRowCount(len(df.index))
            widget.setHorizontalHeaderLabels(df.columns)
            widget.setVerticalHeaderLabels(df.index.strftime("%Y-%m-%d %H:%M"))
            # TODO: what if the index is not datetime?
            for i in range(len(df.index)):
                for j in range(len(df.columns)):                
                    widget.setItem(i,j,QtGui.QTableWidgetItem(str(df.iloc[i, j])))
                    widget.resizeColumnToContents(j)
        else:
            widget.setColumnCount(1)
            widget.setRowCount(1)             
            widget.setItem(0,0,QtGui.QTableWidgetItem('Too much data to display.'))
            widget.resizeColumnToContents(0)  
            
#      def fill_table(self):                
#        df = self.df_selected
#            
#        self.Table1Widget.clear()
#        if len(df.index) < 100:
#            self.Table1Widget.setColumnCount(len(df.columns))
#            self.Table1Widget.setRowCount(len(df.index))
#            self.Table1Widget.setHorizontalHeaderLabels(df.columns)
#            self.Table1Widget.setVerticalHeaderLabels(df.index.strftime("%Y-%m-%d %H:%M"))
#            for i in range(len(df.index)):
#                for j in range(len(df.columns)):                
#                    self.Table1Widget.setItem(i,j,QtGui.QTableWidgetItem(str(df.iloc[i, j])))
#                    self.Table1Widget.resizeColumnToContents(j)
#        else:
#            self.Table1Widget.setColumnCount(1)
#            self.Table1Widget.setRowCount(1)             
#            self.Table1Widget.setItem(0,0,QtGui.QTableWidgetItem('Too much data to display.'))
#            self.Table1Widget.resizeColumnToContents(0)  
#        
    
if __name__ == '__main__':
    
    app = QtGui.QApplication(sys.argv)
    GUI = DataBaseGUI()
    GUI.show()
    app.exec_()
    