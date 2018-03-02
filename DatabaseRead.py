# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo
GUI which reads, analyses, plots, and updates the database CSV file.
"""
import os
import gmplot
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from PyQt4 import QtGui, QtCore, uic


from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from MatplotlibSettings import *

import DatabaseSettings

# matplotlib.rcParams.update({'font.size': 50})

def fill_table(df, table, max_rows=50):   
    # TODO: threading

    # read indices of currently selected rows
    selected_indexes = table.selectedIndexes()
    selected_rows = []
    for item in selected_indexes:
        selected_rows.append(item.row())
    
    # initialise the GUI table columns
    table.clear()
    # disable sorting to solve issues with repopulating
    table.setSortingEnabled(False)        
    
    number_of_rows = min(max_rows, len(df.index))
    table.setRowCount(number_of_rows)
    table.setColumnCount(len(df.columns))
    table.setHorizontalHeaderLabels(df.columns)
                
    # fill the GUI table       
    for col in range(len(df.columns)):
        for row in range(number_of_rows):
            data = df.iloc[row,col]  
            item = QtGui.QTableWidgetItem()
            if isinstance(data, (float, np.float64)):
                # pad the floats so they'll be sorted correctly
                formatted_data = '{:.3f}'.format(data).rjust(15)
                item.setTextAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
            elif isinstance(data, (int, np.int64)):
                # pad the integers so they'll be sorted correctly
                formatted_data = '{:d}'.format(data).rjust(15)
                item.setTextAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
            else:
                formatted_data = str(data)
            item.setData(QtCore.Qt.EditRole, formatted_data)
            table.setItem(row, col, item)
            table.resizeColumnToContents(col)

    # enable table sorting by columns
    table.setSortingEnabled(True)
    
    # temporarily set MultiSelection
    table.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
    # reselect the prevously selected rows
    # TODO: reselect by filename instead of table row number
    for row in selected_rows:
        table.selectRow(row)            
    # revert MultiSelection to ExtendedSelection
    table.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

class DatabaseGUI(QtGui.QMainWindow):
    """
    GUI which analyses and plots GPS and fitness data.
    """
    def __init__(self, kind='gps', file_path=None):
        super(self.__class__, self).__init__()

        # Load GUI design
        ui_file = 'DatabaseGUIdesign.ui'
        uic.loadUi(ui_file, self)    
        
        # Maximise GUI window
#        self.showMaximized()
        
        # Set initial splitter sizes
        self.splitter.setSizes([50,6000])
        self.SummarySplitter.setSizes([50,6000])
        
        # Set initial tabs to display
        self.DatabaseTabsWidget.setCurrentIndex(2)   
        self.PlotTabsWidget.setCurrentIndex(0)
        self.SummaryTabsWidget.setCurrentIndex(0)
        
        # Connect GUI elements
        self.NewDatabasePushButton.clicked.connect(self.new_database)
        self.NewRecordsPathPushButton.clicked.connect(self.new_records)
        self.NewLocationsPathPushButton.clicked.connect(self.new_locations)
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
        
        # group widgets into dictionaries: comboboxes, lists, labels
        self.units_labels = {'elapsed_time':self.CurrentTimeUnitsLabel,
                             'position':self.CurrentPositionUnitsLabel,
                             'distance':self.CurrentDistanceUnitsLabel,
                             'speed':self.CurrentSpeedUnitsLabel,
                             }          
                             
        self.units_comboboxes = {'elapsed_time':self.TimeUnitsComboBox,
                                 'position':self.PositionUnitsComboBox,
                                 'distance':self.DistanceUnitsComboBox,
                                 'speed':self.SpeedUnitsComboBox,
                                 }
                                 
        self.plot_comboboxes = {'histogram_y':[self.HistYComboBox],
                                'legend_location':[self.LegendLocationComboBox],
                                'colormap':[self.CMapComboBox],
                                'kind_trace':[self.TraceTopKindComboBox, self.TraceBottomKindComboBox],
                                'kind_summary':[self.SummaryKindComboBox],
                                'stacked':[self.SummaryStackedComboBox],
                                'measure':[self.SummaryMeasureComboBox, self.HistMeasureComboBox],
                                'frequency':[self.HistFrequencyComboBox, self.SummaryFrequencyComboBox],
                                'sort':[self.SummarySortComboBox],
                                'location':[self.LocationComboBox]}

        self.column_comboboxes = {'category1':[self.SummaryCategory1ComboBox],
                                  'category2':[self.SummaryCategory2ComboBox],
                                  'quantity':[self.SummaryQuantityComboBox],
                                  'legend_variable':[self.LegendVariableComboBox]}

        self.numeric_comboboxes = {'histogram_x':[self.HistXComboBox],
                                   'scatter_x':[self.ScatterXComboBox],
                                   'scatter_y':[self.ScatterYComboBox]}
                                   
        self.trace_comboboxes = {'top_x':[self.TraceTopXComboBox],
                                 'top_y':[self.TraceTopYComboBox],
                                 'bottom_x':[self.TraceBottomXComboBox],
                                 'bottom_y':[self.TraceBottomYComboBox]}
        
        # TODO: change filter widgets and labels to more generic names                
        self.filters_widgets = {'sport':self.SportsListWidget,
                                'activity':self.ActivitiesListWidget,
                                'gear':self.GearListWidget,
                                'start_location':self.StartLocationListWidget,
                                'end_location':self.EndLocationListWidget,
                                'Account':self.StartLocationListWidget,
                                'Category':self.EndLocationListWidget,
                                'category':self.StartLocationListWidget}        
                                
        self.filters_labels = {'sport':self.SportsLabel,
                               'activity':self.ActivitiesLabel,
                               'gear':self.GearLabel,
                               'start_location':self.StartLocationLabel,
                               'end_location':self.EndLocationLabel,
                               'Account':self.StartLocationLabel,
                               'Category':self.EndLocationLabel,
                               'category':self.StartLocationLabel}  
             

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
        
        self.settings = DatabaseSettings.DatabaseSettings(kind=kind)
        self.ReadDatabasePathWidget.insert(self.settings.database_path)
        
        # Read file      
        self.new_database(file_path=file_path)
        
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
                               

    def populate_comboboxes(self):    
        # populate comboboxes based on the database columns DatabaseSettings.py

        for key in self.numeric_comboboxes.keys():
            options = []
            for item in self.settings.numeric_options[key]:
                if item in self.df.columns:
                    options.append(item)
            for column in self.df.columns:
                if self.df[column].dtype in ['float64', 'int64', 'datetime64[ns]']:
                    options.append(column)
            self.populate_combobox(np.sort(np.unique(options)),
                                   self.settings.numeric_default[key],
                                   self.numeric_comboboxes[key])
        
        for key in self.units_comboboxes.keys():
            self.populate_combobox(np.sort(self.settings.unit_factors[key].keys()), 
                                   self.settings.units_SI[key],
                                   [self.units_comboboxes[key]])
                                
        for key in self.plot_comboboxes.keys():        
            self.populate_combobox(self.settings.options[key], 
                                   self.settings.default[key], 
                                   self.plot_comboboxes[key])
                                
        for key in self.column_comboboxes.keys():        
            self.populate_combobox(np.sort(list(set(self.settings.column_options[key]) & set(self.df.columns))), 
                                   self.settings.column_default[key], 
                                   self.column_comboboxes[key])
                                   
        for key in self.trace_comboboxes.keys():        
            self.populate_combobox([self.settings.trace_default[key]], 
                                   self.settings.trace_default[key], 
                                   self.trace_comboboxes[key])
        
        trace_modes = ['Single sport', 'Multi sport']
        self.populate_combobox(trace_modes,
                               'Single sport',
                               [self.TraceModeComboBox])
                          

    def new_database(self, file_path=None):
        """Select a new Garmin DataBase CSV file and locations file.""" 
        if not file_path:
            file_path = self.ReadDatabasePathWidget.text()
            file_path = QtGui.QFileDialog.getOpenFileName(self, 'Choose database .csv file to read.', file_path, "CSV files (*.csv)")
            
        if len(file_path):
            self.file_path = file_path
            self.ReadDatabasePathWidget.clear()
            self.SaveDatabasePathWidget.clear()
            self.ReadDatabasePathWidget.insert(self.file_path)
            self.SaveDatabasePathWidget.insert(self.file_path)
            self.read_database()
            
            # disable some tabs
            self.RecordsTab.setEnabled(self.settings.RecordsTab)
            self.MapTab.setEnabled(self.settings.MapTab)
            self.TracesTab.setEnabled(self.settings.TracesTab)
            
            if self.RecordsTab.isEnabled():
                self.locations_path = self.settings.locations_path
                self.LocationsPathWidget.insert(self.locations_path)
                self.records_path = self.settings.records_path
                self.RecordsPathWidget.insert(self.records_path)
            if self.MapTab.isEnabled():
                self.MapFilePathWidget.insert(self.settings.map_path)     

            self.populate_dates()
            self.populate_comboboxes()            
            self.populate_filters()
                          
            # make a copy so the current_units can be modified independently from the SI_units
            self.current_units = dict(self.settings.units_SI) 
            self.update_units() # includes self.filter_and_plot_database()
            
        else:
            print "WARNING: No database file chosen. Choose another file to avoid errors.\n" 
                
    def new_records(self):
        file_path = self.RecordsPathWidget.text()
        file_path = QtGui.QFileDialog.getExistingDirectory(self, 'Choose directory containing .csv record files.', file_path)
        file_path = file_path + '\\'
        if len(file_path):
            self.records_path = file_path
            self.RecordsPathWidget.clear()
            self.RecordsPathWidget.insert(file_path)
        else:
            print "WARNING: No .csv records directory chosen. Choose another directory to avoid errors.\n"            
        
    def read_database(self):
        """Read the CSV file."""
        print self.file_path + '\n'
        
        self.df = pd.read_csv(self.file_path, dayfirst=True)
        # TODO: fix errors that appear when some activities have empty gear
        
        # rename columns to ignore white spaces at the start and end of the string
        self.df.rename(columns=lambda x: x.strip(), inplace=True) 
        
        if 'start_time' in self.df.columns:
            self.column_date = 'start_time'
            self.settings = DatabaseSettings.DatabaseSettings(kind='gps')
        elif 'Date' in self.df.columns:
            self.column_date = 'Date'
            self.settings = DatabaseSettings.DatabaseSettings(kind='expenses')
        elif 'meeting_time' in self.df.columns:
            self.column_date = 'meeting_time'
            self.settings = DatabaseSettings.DatabaseSettings(kind='late')
        else:
            self.column_date = False        
        
        # reformat the file_name column
        if 'file_name' in self.df.columns:
            self.df['file_name'] = self.df['file_name'].apply(str)
            
        # reformat the date column    
        if self.column_date in self.df.columns:
            self.df[self.column_date] = pd.to_datetime(self.df[self.column_date], dayfirst=True)        
                
        # create a variable with the column names to use when saving the database
        self.database_columns_to_save = self.df.columns

        self.df = self.calculate_new_columns(self.df)                    
        self.df_selected = self.df.copy()
           
            
    def populate_dates(self):
        if self.column_date_local in self.df.columns:
            self.StartDateEdit.setDate(self.df[self.column_date_local].min())
            self.EndDateEdit.setDate(self.df[self.column_date_local].max())
            
    def populate_filters(self):
        # clear all widgets and labels
        for item in self.filters_widgets.keys():
            self.filters_labels[item].setText('')
            self.filters_widgets[item].clear()
        
        # populate appropriate widgets and labels
        for item in self.settings.filters:        
            if item in self.df.columns:
                self.populate_list(item, self.filters_widgets[item])
                self.filters_labels[item].setText(item)
            else:
                self.filters_labels[item].setText('')
                self.filters_widgets[item].clear()
        
        if 'start_position_long' in self.df.columns:
            self.populate_locations()
            
    def new_locations(self):
        file_path = self.LocationsPathWidget.text()
        file_path = QtGui.QFileDialog.getOpenFileName(self, 'Choose .csv file with list of locations.', file_path, "CSV files (*.csv)")
        if len(file_path):
            self.locations_path = file_path
            self.LocationsPathWidget.clear()
            self.LocationsPathWidget.insert(file_path)
            self.populate_locations()
        else:
            print "WARNING: No locations file chosen. Choose another file to avoid errors.\n"            
                
        
    def populate_locations(self):      
        """Populate the start and end location tree widgets."""
        
        self.StartLocationLabel.setText('Start Location:')
        self.StartLocationListWidget.clear()
        self.StartLocationListWidget.addItem('any')  
        self.StartLocationListWidget.setCurrentRow(0) 
        
        self.EndLocationLabel.setText('End Location:')
        self.EndLocationListWidget.clear()
        self.EndLocationListWidget.addItem('any')  
        self.EndLocationListWidget.setCurrentRow(0)
        
        if len(self.locations_path):
            self.df_locations = pd.read_csv(self.locations_path)
            for item in self.df_locations['name']:
                self.StartLocationListWidget.addItem(item)
                self.EndLocationListWidget.addItem(item)      
        else:
            print "WARNING: No locations file chosen. Choose another file to avoid errors.\n"            

        
    def calculate_new_columns(self, df):         
        self.column_date_local = self.column_date
        
        if self.column_date in df.columns:
            if 'timezone' in df.columns:
                # take into account the timezone        
                self.df['timezone'] = pd.to_timedelta(self.df['timezone'])
                temp =  df[self.column_date] + df['timezone']
                df[self.column_date + '_local'] = temp
                
                df['start_daytime_local'] = temp.dt.time
                self.column_date_local = 'start_time_local'
                # TODO: automate the self.column_date_local column name
            else:
                temp =  df[self.column_date]                         
                # TODO: if self.column_date also has time info calculate temp.dt.time
                # then it won't be needed to add a timezone column full of zeros (eg John's data)
            
            # TODO: add end_daytime and end_time_local info when it's added in DatabaseWrite.py
            df['weekday'] = temp.dt.weekday+1 # numeric: 1 = Monday, 7 = Sunday     
            df['weekday_name'] = (temp.dt.weekday+1).apply(str) + ': ' + temp.dt.weekday_name # string
            df['week'] = temp.dt.week
            df['year_week'] = temp.dt.year.apply(str) + '-' + temp.dt.week.apply(str).str.pad(2,fillchar='0')
            df['month'] = temp.dt.month
            df['year_month'] = temp.dt.year.apply(str) + '-' + temp.dt.month.apply(str).str.pad(2,fillchar='0')
            df['year_month_day'] = df['year_month'] + '-' + temp.dt.day.apply(str).str.pad(2,fillchar='0')
            df['year'] = temp.dt.year
        
        if 'Amount' in df.columns:
            df.sort_values(self.column_date, inplace=True)
            df['Balance'] = df['Amount'].cumsum()

        return df
    
    def set_SI_units(self):   
        print "Setting database units to SI..."        
        for key in self.units_comboboxes.keys():
            index = self.units_comboboxes[key].findText(self.settings.units_SI[key])
            self.units_comboboxes[key].setCurrentIndex(index)        
        # update the units
        self.update_units()
    
    def read_units(self):
        """Read units from GUI comboboxes."""
        units = dict()
        for key in self.units_comboboxes.keys():
            units[key] = self.units_comboboxes[key].currentText()
        return units
        
    def display_units(self, units):
        """Display units on the GUI labels."""
        for key in self.units_labels.keys():
            self.units_labels[key].setText(units[key])
        
        
    def update_units(self):
        # dataframes to update: df, df_selected
        print "Updating database units..."     
        
        # convert from current_units to SI_units       
        self.df, self.settings.units = self.convert_units(self.df, self.settings.units, self.current_units, to_SI=True)
        self.df_selected, self.settings.units = self.convert_units(self.df_selected, self.settings.units, self.current_units, to_SI=True)       

        # read desired units from the GUI into self.current_units
        self.current_units = self.read_units()
                
        # convert from SI_units to current_units
        self.df, self.settings.units = self.convert_units(self.df, self.settings.units, self.current_units, to_SI=False)
        self.df_selected, self.settings.units = self.convert_units(self.df_selected, self.settings.units, self.current_units, to_SI=False)
        
        self.display_units(self.current_units)
        print "Finished updating datatabase units!\n"
        
        # re-filter the database
        self.filter_and_plot_database()
        
    
    def convert_units(self, df, dataframe_units, desired_units, to_SI=False):
        # if to_SI = False: convert from SI_units to dataframe_units
        # if to_SI = True: convert from dataframe_units to SI_units
        if to_SI:
            factor = -1.
        else: 
            factor = 1.
            
        # TODO: automate this more
        for column_name in df.columns:
            if 'elapsed_time' in column_name:
                dataframe_units[column_name] = desired_units['elapsed_time']
                df[column_name] = df[column_name] * (self.settings.unit_factors['elapsed_time'][desired_units['elapsed_time']] ** factor)
            if 'position' in column_name:
                dataframe_units[column_name] = desired_units['position']
                df[column_name] = df[column_name] * (self.settings.unit_factors['position'][desired_units['position']] ** factor)
            if 'distance' in column_name:
                dataframe_units[column_name] = desired_units['distance']
                df[column_name] = df[column_name] * (self.settings.unit_factors['distance'][desired_units['distance']] ** factor)
            if 'speed' in column_name:
                dataframe_units[column_name] = desired_units['speed']                
                if 'min/' in desired_units['speed']:
                    if to_SI:
                        df[column_name] = 60 / df[column_name]
                        df[column_name] = df[column_name] * (self.settings.unit_factors['speed'][desired_units['speed']] ** factor)
                    else:
                        df[column_name] = df[column_name] * (self.settings.unit_factors['speed'][desired_units['speed']] ** factor)
                        df[column_name] = 60 / df[column_name]
                else:
                    df[column_name] = df[column_name] * (self.settings.unit_factors['speed'][desired_units['speed']] ** factor)
        return df, dataframe_units
           
    def populate_list(self, column, widget):
        """Populate the list widget with items from the dataframe column."""
        items = np.sort(self.df[column].unique())
        widget.clear()
        for row, item in enumerate(items):
            widget.addItem(item)
            widget.item(row).setSelected(True)             
    
    def select_dates(self, df):
        start_date = self.StartDateEdit.date().toPyDate()
        end_date = self.EndDateEdit.date().toPyDate()
        df_copy = df.copy()
        df_copy.set_index(self.column_date_local, inplace=True)
        df_selected = df_copy.loc[str(start_date) : str(end_date + pd.DateOffset(1))]
        df_selected.reset_index(inplace=True)
        return df_selected
        
    def list_selection(self, widget):
        selected_options = []
        for item in widget.selectedItems():
            selected_options.append(item.text())
        return selected_options       
            
    def location_mask(self, df, when, selected_options):
        # TODO: fix error with weird characters such as "ñ" in "Logroño"
        if 'any' in selected_options:
            mask = True
        else:
            mask = [False]*len(df)
            for option in selected_options:
                radius = self.df_locations.loc[self.df_locations['name'] == option, 'radius'].values[0]
                lon_deg = self.df_locations.loc[self.df_locations['name'] == option, 'position_long']
                lat_deg = self.df_locations.loc[self.df_locations['name'] == option, 'position_lat']
                distance = Distance(df[when+'_position_long'], df[when+'_position_lat'],                                     
                                    units_gps=self.current_units['position'], units_d='m', mode='fixed', 
                                    fixed_lon=lon_deg*self.settings.unit_factors['position'][self.current_units['position']]/0.00000008381903171539306640625, 
                                    fixed_lat=lat_deg*self.settings.unit_factors['position'][self.current_units['position']]/0.00000008381903171539306640625,
                                    )
                option_mask = distance.abs() <= radius
                mask = mask | option_mask                                    
        return mask
        
    def generate_mask(self, df, column, selected_options):       
        mask = [False]*len(df)
        for option in selected_options:
            option_mask = df[column] == option
            mask = mask | option_mask
        return mask
        # TODO: what if some rows are empy in this column?
        # TODO: allow several gear for the same activity - maybe?
    
    def filter_database(self):        
        print "Filtering database..."            
        if self.column_date_local:        
            df_dates = self.select_dates(self.df)      
        else:
            df_dates = self.df
        
        total_mask = [True]*len(df_dates)
        for key in self.filters_widgets.keys():
            if key in self.df.columns:
                selected_items = self.list_selection(self.filters_widgets[key])
                mask = self.generate_mask(df_dates, key, selected_items)
                total_mask = total_mask & mask   
        
        # filtering by start and end location
        if 'start_position_long' in self.df.columns:
            selected_items = self.list_selection(self.StartLocationListWidget)
            mask_start = self.location_mask(df_dates, 'start', selected_items)
            
            selected_items = self.list_selection(self.EndLocationListWidget)
            mask_end = self.location_mask(df_dates, 'end', selected_items)
            
            if self.LocationComboBox.currentText() == 'and':
                mask_location = mask_start & mask_end
            elif self.LocationComboBox.currentText() == 'or':
                mask_location = mask_start | mask_end
                
            total_mask = total_mask & mask_location
            
        self.df_selected = df_dates[total_mask]
            
        print "Finished filtering database!\n"
        
    def filter_and_plot_database(self):
        self.filter_database()
        self.DatabaseSizeSpinBox.setValue(len(self.df_selected))
        fill_table(self.df_selected, self.Table1Widget, self.DatabaseRowsSpinBox.value())
        
        print "Updating figures (summary, scatter, histogram, map)..."
        self.plot_summary()
        self.plot_scatter()
        self.plot_histogram()        
        if self.MapCheckBox.checkState() and self.MapCheckBox.isEnabled():
            self.generate_map()
        print "Figures updated!\n"
        
        self.StartTimeDoubleSpinBox.setValue(0)
        self.EndTimeDoubleSpinBox.setValue(999999)    
    
    def generate_colours(self, df, column, cmap_name):
        # TODO: they get generated a little different than what pandas does automatically
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
        legend = self.LegendVariableComboBox.currentText()
        kind = 'line' # fake scatter plot made from a line plot with markers
            
        if x == y:
            print "WARNING: choose different X and Y variables for the scatter plot!!!"
        else:
            
            self.figure_scatter.clear()
            ax = self.figure_scatter.add_subplot(111)
            
            colour_dict = self.generate_colours(df, legend, cmap_name)
            for label in np.sort(colour_dict.keys()):
                # select data according to the desired legend variable
                df_plot = df.loc[df[legend]==label][[x,y]]           
                if len(df_plot) > 0:
                     df_plot.plot(x=x, y=y,
                                  ax=ax,
                                  kind=kind,
                                  label=label, 
                                  alpha=alpha, 
                                  c=colour_dict[label],
                                  marker='.',
                                  markersize=50,
                                  linestyle='None',
                                  ) 
            
            ax.autoscale(enable=True, axis='both', tight='False')
            ax.margins(0.1,0.1)
                    
            xlabel = x.replace('_',' ')
            if x in self.settings.units.keys():
                if self.settings.units[x]:
                    xlabel = xlabel + ' (' + self.settings.units[x] + ')'
            
            ylabel = y.replace('_',' ')
            if y in self.settings.units.keys():
                if self.settings.units[y]:
                    ylabel = ylabel + ' (' + self.settings.units[y] + ')'
            
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            legend = ax.legend(loc=self.LegendLocationComboBox.currentText(), numpoints=1)
            if legend:
                legend.set_visible(self.LegendCheckBox.checkState())
            
            ax.set_title(self.PlotTitleTextWidget.text())
            self.canvas_scatter.draw()
        
            
    def plot_histogram(self):  
        df = self.df_selected
        x = self.HistXComboBox.currentText()
        y = self.HistYComboBox.currentText()
        measure = self.HistMeasureComboBox.currentText()  
        frequency = self.HistFrequencyComboBox.currentText()  
        legend = self.LegendVariableComboBox.currentText()
        cmap_name = self.CMapComboBox.currentText()
        alpha = self.TransparencyDoubleSpinBox.value()
                
        self.figure_hist.clear()
        ax = self.figure_hist.add_subplot(111)
        
        if y == 'frequency':
            normed = True
        elif y == 'counts':
            normed = False

#        if self.HistogramBinsSheckBox.checkState():
#            bins = 'auto'
#            histogram = True
#        else:
#            try:
#                bins = np.linspace(min(df[x]), max(df[x]), 30)
#                histogram = True
#            except:
#                # TODO: try/except is a temporary solution: fix it
#                print "Cannot generate histogram.\n"
#                histogram = False
            
        colour_dict = self.generate_colours(df, legend, cmap_name)
        for label in np.sort(colour_dict.keys()):                
            df_hist = df[df[legend]==label]         
            
            if frequency != 'all' and self.column_date_local in df_hist.columns:                
                if measure == 'sum':
                    x_data = df_hist.set_index(self.column_date_local).resample(frequency).sum().reset_index()
                if measure == 'mean':
                    x_data = df_hist.set_index(self.column_date_local).resample(frequency).mean().reset_index()
                if measure == 'count':
                    x_data = df_hist.set_index(self.column_date_local).resample(frequency).count().reset_index()
                if measure == 'last':
                    x_data = df_hist.set_index(self.column_date_local).resample(frequency).last().reset_index()
            else:
                x_data = df_hist
            
            if self.HistogramNanCheckBox.checkState():
                x_data = x_data.fillna(0)
                
            if self.HistogramBinsCheckBox.checkState():
                bins = 'auto'
                histogram = True
            else:
                try:
                    bins = np.linspace(min(x_data[x]), max(x_data[x]), 30)
                    histogram = True
                except:
                    # TODO: try/except is a temporary solution: fix it
                    print "Cannot generate histogram.\n"
                    histogram = False
            
            if len(x_data) > 1:                
                if histogram:
                    ax.hist(x_data[x].dropna(), 
                            bins=bins,
                            color=colour_dict[label],
                            label=label, 
                            normed=normed, 
                            alpha=alpha,
                            )
                            
        
        xlabel = x.replace('_',' ')
        if x in self.settings.units.keys():
            if self.settings.units[x]:
                xlabel = xlabel + ' (' + self.settings.units[x] + ')'        
        if frequency != 'all':
            xlabel = measure + ' ' + xlabel + ' / ' + frequency
        
        if histogram:
            ax.set_xlabel(xlabel)
            ax.set_ylabel(y)
            legend = ax.legend(loc=self.LegendLocationComboBox.currentText())
            if legend:
                legend.set_visible(self.LegendCheckBox.checkState())
            
            ax.set_title(self.PlotTitleTextWidget.text())
            self.canvas_hist.draw()

        
    def populate_plot_options(self, kind, alpha, cmap_name, df=pd.DataFrame(), 
                              index=False, legend=False, stacked=True):
        plot_options = dict()   
        plot_options['kind'] = kind    
        plot_options['alpha'] = alpha

        if not df.empty:
            colour_dict = self.generate_colours(df, legend, cmap_name)
            label = df.loc[index,legend]
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
            plot_options['stacked'] = stacked
            plot_options['edgecolor'] = 'none'                
        
        return plot_options   
            
    def plot_summary(self):
        summary_quantity_list = [self.SummaryQuantityComboBox.itemText(i) for i in range(self.SummaryQuantityComboBox.count())]
        summary_category_list = [self.SummaryCategory1ComboBox.itemText(i) for i in range(self.SummaryCategory1ComboBox.count())]
        summary_list = np.unique(summary_category_list + summary_quantity_list)

        df = self.df_selected[summary_list]        
        
        measure = self.SummaryMeasureComboBox.currentText()
        quantity = self.SummaryQuantityComboBox.currentText()
        category1 = self.SummaryCategory1ComboBox.currentText()
        category2 = self.SummaryCategory2ComboBox.currentText()
        frequency = self.SummaryFrequencyComboBox.currentText()
        kind = self.SummaryKindComboBox.currentText()
        cmap_name = self.CMapComboBox.currentText()     
        alpha = self.TransparencyDoubleSpinBox.value()        
        if self.SummaryStackedComboBox.currentText() == 'yes':
            stacked = True
        elif self.SummaryStackedComboBox.currentText() == 'no':
            stacked = False
        
        if measure == 'sum':
            self.df_summary_single = df.groupby([category1]).sum()
            self.df_summary_double = df.groupby([category1,category2]).sum()
        elif measure == 'last':
            self.df_summary_single = df.groupby([category1]).last()
            self.df_summary_double = df.groupby([category1,category2]).last()
        elif measure == 'mean':
            self.df_summary_single = df.groupby([category1]).mean()
            self.df_summary_double = df.groupby([category1,category2]).mean()
        elif measure == 'count':
            self.df_summary_single = df.groupby([category1]).count()
            self.df_summary_double = df.groupby([category1,category2]).count()
        
        
        if self.SummarySortComboBox.currentText() == 'category':
            # this is how df.groupby sorts it by default
            sorted_indices = self.df_summary_single.index
        if self.SummarySortComboBox.currentText() == 'quantity':
            sorted_indices = self.df_summary_single.sort_values(quantity).index
            
        fill_table(self.df_summary_single[quantity].reset_index(), self.SummarySingleTableWidget)
        if category1 == category2:
            df_summary_plot = self.df_summary_single[quantity].loc[sorted_indices]
        else:
            df_summary_plot = self.df_summary_double[quantity].unstack(level=1).loc[sorted_indices]
            fill_table(self.df_summary_double[quantity].reset_index(), self.SummaryDoubleTableWidget)

        if frequency != 'all':  
            timedelta = self.df_selected[self.column_date_local].max() - self.df_selected[self.column_date_local].min()
            # this is not very precise but it should be enough to get an idea
            df_summary_plot = df_summary_plot / timedelta.days * self.settings.timedelta_factors[frequency]            
            
        self.figure_summary.clear()
        ax = self.figure_summary.add_subplot(111)

        plot_options = self.populate_plot_options(kind=kind, alpha=alpha, 
                                                  cmap_name=cmap_name, stacked=stacked)
        df_summary_plot.plot(ax=ax, **plot_options)
            
        legend = ax.legend(loc=self.LegendLocationComboBox.currentText())
        legend.set_visible(self.LegendCheckBox.checkState())
        
        label_quantity = quantity.replace('_',' ')
        label_quantity = measure + ' ' + label_quantity
        if quantity in self.settings.units.keys():
            if self.settings.units[quantity]:
                label_quantity = label_quantity + ' (' + self.settings.units[quantity] + ')' 
        if frequency != 'all':
            label_quantity = label_quantity + ' / ' + frequency

        label_category1 = category1.replace('_',' ')
        if category1 in self.settings.units.keys():
            if self.settings.units[category1]:
                label_category1 = label_category1 + ' (' + self.settings.units[category1] + ')' 

        if kind == 'barh':
            ax.set_xlabel(label_quantity)
            ax.set_ylabel(label_category1)
        else:
            ax.set_xlabel(label_category1)
            ax.set_ylabel(label_quantity)            
        
        ax.set_title(self.PlotTitleTextWidget.text())
        self.canvas_summary.draw() 
                
    
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
#            elif column_name != 'file_name':
#                df[column_name] = pd.to_numeric(df[column_name], errors='ignore')        
        
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
        
        df['elapsed_time'] = ElapsedTime(df['timestamp'], units_t='s')
        
        self.populate_combobox(np.sort(df.columns), self.TraceTopXComboBox.currentText(),
                          [self.TraceTopXComboBox])
        self.populate_combobox(np.sort(df.columns), self.TraceTopYComboBox.currentText(),
                          [self.TraceTopYComboBox])   
        self.populate_combobox(np.sort(df.columns), self.TraceBottomXComboBox.currentText(),
                          [self.TraceBottomXComboBox])
        self.populate_combobox(np.sort(df.columns), self.TraceBottomYComboBox.currentText(),
                          [self.TraceBottomYComboBox]) 
                          
        return df # output in SI units
        
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
        df_save = self.merge_dataframes(self.df, df_widget, 'start_time_local')
        # TODO: merge by file_name instead of start_time_local
        self.df = df_save.copy()       
        
        # convert to SI units before saving
        df_save, useless_units = self.convert_units(df_save, self.settings.units, self.current_units, to_SI=True)      
        
        # save database
        df_save.to_csv(file_path, sep=',', header=True, index=False, columns=self.database_columns_to_save)
        print 'Database saved! \n'
        
        # read selected rows from the database
        self.df_trace = self.read_selected_table_rows(self.Table1Widget)
        print 'Saving record files...'
        for index in self.df_trace.index:
            file_name = self.df_trace.loc[index,'file_name']
            # read records file
            file_path = self.records_path + str(file_name) + '_record.csv'
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
        # TODO: what if records do not have GPS data?
        number_of_activities = self.MapActivitiesSpinBox.value()  
        legend = self.LegendVariableComboBox.currentText()
        cmap_name = self.CMapComboBox.currentText()  
        colour_dict = self.generate_colours(self.df_selected, legend, cmap_name)           
        
        self.figure_map.clear()
        ax = self.figure_map.add_subplot(111)
        
        self.map_data = {}
        self.map_colours = {}
        avg_lat = []
        avg_long = []
        for index in self.df_selected.iloc[0:number_of_activities].index:
            file_name = self.df_selected.loc[index,'file_name']
            
            file_path = self.records_path + str(file_name) + '_record.csv'
            # read the csv file
            df = self.read_records(file_path)  
            df, self.settings.units = self.convert_units(df, self.settings.units, self.current_units)
            # Extract location information, remove missing data, convert to degrees
            self.map_data[file_name] = df.loc[:,['position_lat','position_long']].dropna()
#            self.map_colours[file_name] = 'k'
            self.map_colours[file_name] = colour_dict[self.df_selected.loc[index,legend]]
            
            avg_long.append(self.map_data[file_name]['position_long'].mean())
            avg_lat.append(self.map_data[file_name]['position_lat'].mean())
            
            # TODO: user option: line (faster) or scatter (better if many nan) plot
            ax.plot(self.map_data[file_name]['position_long'], 
                    self.map_data[file_name]['position_lat'],
                    label = file_name,
                    c=self.map_colours[file_name],
                    )     
#            ax.scatter(self.map_data[file_name]['position_long'], 
#                       self.map_data[file_name]['position_lat'],
#                       label = file_name,
#                       )     
                
              
        # make sure x and y axis have the same spacing
        ax.axis('equal')        
        
        # label axes        
        xlabel = 'position_long (' + self.settings.units['position_long'] + ')'
        ylabel = 'position_lat (' + self.settings.units['position_lat'] + ')'  
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        
        ax.set_title(self.PlotTitleTextWidget.text())
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
            color = '#%02x%02x%02x' % (self.map_colours[key][0]*255, 
                                       self.map_colours[key][1]*255, 
                                       self.map_colours[key][2]*255),
            if self.MapBlackCheckBox.checkState():
                color = 'k'
            
            # Add a line plot to the gmap object which will be save to an .html file
            # Use line instead of scatter plot for faster speed and smaller file size
            
            # TODO: user option: line (faster) or scatter (very very slow) plot
            # so if there are nan, e.g. metro, separate the plots into several line plots
            gmap.plot(self.map_data[key]['position_lat'], 
                      self.map_data[key]['position_long'], 
                      color=color,                       
                      edge_width=3,
                      )
#            gmap.scatter(self.map_data[key]['position_lat'][0:-1:5], 
#                         self.map_data[key]['position_long'][0:-1:5], 
#                         color=self.map_colours[key], size=10, marker=False)
        
        file_path = self.MapFilePathWidget.text()
        file_path = QtGui.QFileDialog.getSaveFileName(self, 'Choose .html file to save map.', file_path, "HTML files (*.html)")
        if len(file_path):
            self.MapFilePathWidget.clear()
            self.MapFilePathWidget.insert(file_path)        
            gmap.draw(file_path)
            print "Finished HTML map!\n"
        else:
            print "WARNING: No .html path chosen. Choose another path to save the map.\n"  
        
            
    def select_and_plot_trace(self):
        # TODO: threading
        print "Starting trace plots..."
        self.df_trace = self.read_selected_table_rows(self.Table1Widget)    
        
        self.figure_trace.clear()
        
        if self.TraceTopCheckBox.checkState() and self.TraceBottomCheckBox.checkState():
            ax1 = self.figure_trace.add_subplot(211)
            ax2 = self.figure_trace.add_subplot(212)
            ax = ax1
        elif self.TraceTopCheckBox.checkState():
            ax1 = self.figure_trace.add_subplot(111)
            ax = ax1
        elif self.TraceBottomCheckBox.checkState():
            ax2 = self.figure_trace.add_subplot(111)
            ax = ax2
                    
        if len(self.df_trace) > 20:
            print "WARNING: " + str(len(self.df_trace)) + " trace plots might take a long time!"
            
        for index in self.df_trace.index:
            file_name = self.df_trace.loc[index,'file_name']
            file_path = self.records_path + str(file_name) + '_record.csv'
            # read the csv file
            df = self.read_records(file_path)
            # conver to current_units
            df, self.settings.units = self.convert_units(df, self.settings.units, self.current_units, to_SI=False)
            # select data based on start and end values of elapsed_time
            df = self.select_times(df)

            # recalculate mean and max values (heart_rate, speed, ...) and update Table 1
            self.recalculate_statistics(df,file_name)
            
            if index == self.df_trace.index[0]:
                fill_table(df, self.Table2Widget)   

            x1 = self.TraceTopXComboBox.currentText()
            y1 = self.TraceTopYComboBox.currentText()
            x2 = self.TraceBottomXComboBox.currentText()
            y2 = self.TraceBottomYComboBox.currentText()
        
            if self.TraceTopCheckBox.checkState():
                trace_top_plot_options = self.populate_plot_options(df=self.df_trace,
                        index=index,
                        legend=self.LegendVariableComboBox.currentText(),
                        cmap_name=self.CMapComboBox.currentText(),
                        kind=self.TraceTopKindComboBox.currentText(), 
                        alpha=self.TransparencyDoubleSpinBox.value())
                        
                df.plot(x=x1, y=y1, 
                        ax=ax1, 
                        **trace_top_plot_options)
                        
                xlabel = x1.replace('_',' ')
                if x1 in self.settings.units.keys():
                    if self.settings.units[x1]:
                        xlabel = xlabel + ' (' + self.settings.units[x1] + ')'
                
                ylabel = y1.replace('_',' ')
                if y1 in self.settings.units.keys():
                    if self.settings.units[y1]:
                        ylabel = ylabel + ' (' + self.settings.units[y1] + ')'
                
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
                        legend=self.LegendVariableComboBox.currentText(),
                        cmap_name=self.CMapComboBox.currentText(),
                        kind=self.TraceBottomKindComboBox.currentText(), 
                        alpha=self.TransparencyDoubleSpinBox.value())
                    
                df.plot(x=x2, y=y2, 
                        ax=ax2, 
                        **trace_bottom_plot_options)
        
                xlabel = x2.replace('_',' ')
                if x2 in self.settings.units.keys():
                    if self.settings.units[x2]:
                        xlabel = xlabel + ' (' + self.settings.units[x2] + ')'
                
                ylabel = y2.replace('_',' ')
                if y2 in self.settings.units.keys():
                    if self.settings.units[y2]:
                        ylabel = ylabel + ' (' + self.settings.units[y2] + ')'
                
                if self.TraceBottomAxesEqualCheckBox.checkState():
                    # set x and y axis to have the same spacing - good for GPS coordinates
                    ax2.axis('equal')    
                
                ax2.set_xlabel(xlabel)
                ax2.set_ylabel(ylabel)
                ax2.autoscale(enable=True, axis='both', tight='False')
                ax2.margins(0.1,0.1)
                legend = ax2.legend(loc=self.LegendLocationComboBox.currentText())
                legend.set_visible(self.LegendCheckBox.checkState())
        
        ax.set_title(self.PlotTitleTextWidget.text())
        self.canvas_trace.draw()
        print "Finished trace plots!\n"
        
            
    def recalculate_statistics(self,df,file_name):
        # df is the records dataframe
    
        row = self.Table1Widget.findItems(str(file_name),QtCore.Qt.MatchExactly)[0].row()
        
        number_of_columns = self.Table1Widget.columnCount()
        column_dict = {}
        for column in range(number_of_columns):
            column_name = self.Table1Widget.horizontalHeaderItem(column).text()
            column_dict[column_name] = column
               
        if 'speed' in df.columns:
            if 'avg_speed' in column_dict.keys():
                value = df['speed'].mean()
                self.Table1Widget.setItem(row, column_dict['avg_speed'], 
                                          QtGui.QTableWidgetItem(format(value,'.3f')))
            if 'max_speed' in column_dict.keys():
                value = df['speed'].max()
                self.Table1Widget.setItem(row, column_dict['max_speed'], 
                                          QtGui.QTableWidgetItem(format(value,'.3f')))
                                          
        if 'heart_rate' in df.columns:
            if 'avg_heart_rate' in column_dict.keys():
                value = df['heart_rate'].mean()
                self.Table1Widget.setItem(row, column_dict['avg_heart_rate'], 
                                          QtGui.QTableWidgetItem(format(value,'.2f')))
            if 'max_heart_rate' in column_dict.keys():
                value = df['heart_rate'].max()
                self.Table1Widget.setItem(row, column_dict['max_heart_rate'], 
                                          QtGui.QTableWidgetItem(format(value,'.2f')))
                                          
        if 'cadence' in df.columns:
            if 'avg_cadence' in column_dict.keys():
                # remove zeros, which are like missing cadence data
                value = df[df['cadence']!=0]['cadence'].dropna().mean()
                self.Table1Widget.setItem(row, column_dict['avg_cadence'], 
                                          QtGui.QTableWidgetItem(format(value,'.2f')))
            if 'max_cadence' in column_dict.keys():
                value = df['cadence'].max()
                self.Table1Widget.setItem(row, column_dict['max_cadence'], 
                                          QtGui.QTableWidgetItem(format(value,'.2f')))

        if 'position_lat' in df.columns:
            if 'start_position_lat' in column_dict.keys():
                position = df['position_lat'].dropna()
                if not position.empty:
                    value = position.iloc[0]
                    self.Table1Widget.setItem(row, column_dict['start_position_lat'], 
                                              QtGui.QTableWidgetItem(format(value,'.4f')))
            if 'end_position_lat' in column_dict.keys():
                position = df['position_lat'].dropna()
                if not position.empty:
                    value = position.iloc[-1]
                    self.Table1Widget.setItem(row, column_dict['end_position_lat'], 
                                              QtGui.QTableWidgetItem(format(value,'.4f')))
                                          
        if 'position_long' in df.columns:
            if 'start_position_long' in column_dict.keys():
                position = df['position_long'].dropna()
                if not position.empty:
                    value = position.iloc[0]
                    self.Table1Widget.setItem(row, column_dict['start_position_long'], 
                                              QtGui.QTableWidgetItem(format(value,'.4f')))
            if 'end_position_long' in column_dict.keys():
                position = df['position_long'].dropna()
                if not position.empty:
                    value = position.iloc[-1]
                    self.Table1Widget.setItem(row, column_dict['end_position_long'], 
                                              QtGui.QTableWidgetItem(format(value,'.4f')))   
                                          
        if 'distance' in df.columns:
            if 'total_distance' in column_dict.keys():
                value = df.loc[df.index[-1],'distance'] - df.loc[df.index[0],'distance']
                self.Table1Widget.setItem(row, column_dict['total_distance'], 
                                          QtGui.QTableWidgetItem(format(value,'.4f')))
        if 'elapsed_time' in df.columns:
            if 'total_elapsed_time' in column_dict.keys():
                value = df.loc[df.index[-1],'elapsed_time'] - df.loc[df.index[0],'elapsed_time']
                self.Table1Widget.setItem(row, column_dict['total_elapsed_time'], 
                                          QtGui.QTableWidgetItem(format(value,'.4f')))
        
                   
def ElapsedTime(timestamp, units_t='sec', mode='start', fixed_timestamp=None):    
    """Calculate the elapsed time from a timestamp pandas Series.
        
    Arguments:
    timestamp : timestamp pandas Series
        Timestamp values
    units_d: string
        Units of the calculated time, e.g. 'sec' (default), 'min', or 'h'
    mode : string
        If 'start' calculate the elapsed time between all points of the array and the first point.
        If 'previous' calculate the elapsed time between all points of the array the previous point.
        If 'fixed' calculate the elapsed time between all points of the array the fixed_timestamp.
    fixed_timestamp : one timestamp value
        Fixed timestamp value to be used as a reference to calculate the elapsed time.
    Output:
    elapsed_time: float pandas Series
        Contains the calculated elapsed time in units of units_t
    """
    
    # The Garmin Forerunner 35 takes data every 1 second

    origin_time = np.empty(timestamp.shape, dtype=type(timestamp))
    if mode == 'start':
        origin_time[:] = timestamp[0]
    
    elif mode == 'previous':
        origin_time[0] = timestamp[0]
        for i, time in enumerate(timestamp[0:-1]):
            origin_time[i+1] = time
            # TODO: change to origin_time.append(time)
    elif mode == 'fixed':
        origin_time[:] = fixed_timestamp
            
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
    
#class QCustomTableWidgetItem (QtGui.QTableWidgetItem):
#    def __init__ (self, value):
##        super(QCustomTableWidgetItem, self).__init__(QtCore.QString('%s' % value))
#        super(QCustomTableWidgetItem, self).__init__(str('%s' % value))
#
#    def __lt__ (self, other):
#        if (isinstance(other, QCustomTableWidgetItem)):
#            selfDataValue  = float(self.data(QtCore.Qt.EditRole).toString())
#            otherDataValue = float(other.data(QtCore.Qt.EditRole).toString())
#            return selfDataValue < otherDataValue
#        else:
#            return QtGui.QTableWidgetItem.__lt__(self, other)
    
if __name__ == '__main__':
    app = QtGui.QApplication([])
    file_path = 'C:/Users/Ana Andres/Documents/Garmin/Ana/database/Garmin-Ana-180226-1.csv'
    gui = DatabaseGUI(kind='gps', file_path=file_path)
    gui.show()
    