import os
import gmplot
import pandas as pd
import numpy as np
import configparser

from PyQt5 import QtCore, uic, QtWidgets

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

from database.gui import fill_table, populate_combobox, populate_comboboxes, populate_dates, read_units, set_labels_text, \
    list_selection, populate_list, read_table, read_selected_table_rows, get_labels_text
from database.plot import generate_colours, populate_plot_options
from fitness.analysis import convert_units, select_dates, generate_mask, location_mask
from fitness.time import calculate_elapsed_time, select_times


class DatabaseGUI(QtWidgets.QMainWindow):
    """
    GUI which analyses and plots GPS and fitness data.
    """

    def __init__(self):
        super(self.__class__, self).__init__()

        # Load GUI design
        ui_file = 'DatabaseGUIdesign.ui'
        uic.loadUi(ui_file, self)

        # Maximise GUI window
        #        self.showMaximized()

        # Set initial splitter sizes
        self.splitter.setSizes([50, 6000])
        self.SummarySplitter.setSizes([50, 6000])

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

        self.units = {'elapsed time': 's',
                      'total elapsed time': 's',
                      'total timer time': 's',

                      'timezone': 'h',
                      'weekday': '1 = Monday, 7 = Sunday',

                      'distance': 'm',
                      'altitude': 'm',
                      'total distance': 'm',
                      'total ascent': 'm',
                      'total descent': 'm',

                      'position lat': 'semicircles',
                      'position long': 'semicircles',
                      'start position lat': 'semicircle',
                      'start position long': 'semicircles',
                      'end position lat': 'semicircle',
                      'end position long': 'semicircles',

                      'cadence': 'rpm',
                      'avg cadence': 'rpm',
                      'max cadence': 'rpm',

                      'total strides': 'strides',

                      'heart rate': 'bpm',
                      'avg heart rate': 'bpm',
                      'max heart rate': 'bpm',

                      'speed': 'm/s',
                      'avg speed': 'm/s',
                      'max speed': 'm/s',
                      'enhanced speed': 'm/s',
                      'enhanced avg speed': 'm/s',

                      'total calories': 'kcal',
                      }

        # group widgets into dictionaries: comboboxes, lists, labels
        self.units_labels = {'elapsed time': self.CurrentTimeUnitsLabel,
                             'position': self.CurrentPositionUnitsLabel,
                             'distance': self.CurrentDistanceUnitsLabel,
                             'speed': self.CurrentSpeedUnitsLabel,
                             }

        self.units_comboboxes = {'elapsed time': self.TimeUnitsComboBox,
                                 'position': self.PositionUnitsComboBox,
                                 'distance': self.DistanceUnitsComboBox,
                                 'speed': self.SpeedUnitsComboBox,
                                 }

        self.comboboxes = {'histogram y': [self.HistYComboBox],
                           'legend location': [self.LegendLocationComboBox],
                           'colormap': [self.CMapComboBox],
                           'kind trace': [self.TraceTopKindComboBox, self.TraceBottomKindComboBox],
                           'kind summary': [self.SummaryKindComboBox],
                           'stacked': [self.SummaryStackedComboBox],
                           'measure': [self.SummaryMeasureComboBox, self.HistMeasureComboBox],
                           'frequency': [self.HistFrequencyComboBox, self.SummaryFrequencyComboBox],
                           'sort': [self.SummarySortComboBox],
                           'location': [self.LocationComboBox],
                           'category 1': [self.SummaryCategory1ComboBox],
                           'category 2': [self.SummaryCategory2ComboBox],
                           'quantity': [self.SummaryQuantityComboBox],
                           'legend variable': [self.LegendVariableComboBox],
                           'trace mode': [self.TraceModeComboBox]}

        self.numeric_comboboxes = {'histogram x': [self.HistXComboBox],
                                   'scatter x': [self.ScatterXComboBox],
                                   'scatter y': [self.ScatterYComboBox]}

        self.trace_comboboxes = {'top x': [self.TraceTopXComboBox],
                                 'top y': [self.TraceTopYComboBox],
                                 'bottom x': [self.TraceBottomXComboBox],
                                 'bottom y': [self.TraceBottomYComboBox]}

        # TODO: change filter widgets and labels to more generic names                
        self.filters_widgets = {'sport': self.SportsListWidget,
                                'activity': self.ActivitiesListWidget,
                                'gear': self.GearListWidget,
                                'start location': self.StartLocationListWidget,
                                'end location': self.EndLocationListWidget,
                                'Account': self.StartLocationListWidget,
                                'Category': self.EndLocationListWidget,
                                'category': self.StartLocationListWidget}

        self.filters_labels = {'sport': self.SportsLabel,
                               'activity': self.ActivitiesLabel,
                               'gear': self.GearLabel,
                               'start location': self.StartLocationLabel,
                               'end location': self.EndLocationLabel,
                               'Account': self.StartLocationLabel,
                               'Category': self.EndLocationLabel,
                               'category': self.StartLocationLabel}

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

        self.config = configparser.ConfigParser()
        self.config.read('user_config.ini')
        file_path = os.path.join(self.config['DIRECTORIES']['database'],
                                 self.config['FILE NAMES']['database'])
        self.ReadDatabasePathWidget.insert(file_path)

        # Read file      
        self.new_database(file_path=file_path)

    def new_database(self, file_path=None):
        # TODO: fix errors that happen when selecting a new database
        """Select a new Garmin DataBase CSV file and locations file."""
        if file_path is None:
            file_path = self.ReadDatabasePathWidget.text()
            print(file_path)
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose database .csv file to read.',
                                                                 file_path, 'CSV files (*.csv)')
            print(file_path)
            self.ReadDatabasePathWidget.clear()
            self.SaveDatabasePathWidget.clear()
            self.ReadDatabasePathWidget.insert(file_path)
            self.SaveDatabasePathWidget.insert(file_path)
            print(self.ReadDatabasePathWidget.text())

        if len(file_path):
            self.read_database()

            # disable some tabs
            # TODO: Turn the tabs into a dictionary
            self.RecordsTab.setEnabled(self.config['GUI OPTIONS']['enable records tab'].lower() == 'yes')
            self.MapTab.setEnabled(self.config['GUI OPTIONS']['enable map tab'].lower() == 'yes')
            self.TracesTab.setEnabled(self.config['GUI OPTIONS']['enable traces tab'].lower() == 'yes')

            if self.RecordsTab.isEnabled():
                locations_path = os.path.join(self.config['DIRECTORIES']['locations'],
                                              self.config['FILE NAMES']['locations'])
                self.LocationsPathWidget.clear()
                self.LocationsPathWidget.insert(locations_path)
                records_path = os.path.abspath(self.config['DIRECTORIES']['csv files'])
                self.RecordsPathWidget.clear()
                self.RecordsPathWidget.insert(records_path)
            if self.MapTab.isEnabled():
                self.MapFilePathWidget.insert(os.path.join(self.config['DIRECTORIES']['map'],
                                                           self.config['FILE NAMES']['map']))

            populate_dates(self.column_date_local, self.df, self.StartDateEdit, self.EndDateEdit)
            populate_comboboxes(self.config, self.df, self.numeric_comboboxes, self.units_comboboxes,
                                self.trace_comboboxes, self.comboboxes)
            self.populate_filters()

            self.update_units()  # includes self.filter_and_plot_database()

        else:
            print("WARNING: No database file chosen. Choose another file to avoid errors.\n")

    def new_records(self):
        file_path = self.RecordsPathWidget.text()
        file_path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Choose directory containing .csv record files.',
                                                               file_path)
        # file_path = file_path + '\\'
        if len(file_path):
            self.RecordsPathWidget.clear()
            self.RecordsPathWidget.insert(file_path)
        else:
            print("WARNING: No .csv records directory chosen. Choose another directory to avoid errors.\n")

    def read_database(self):
        """Read the CSV file."""
        print(self.file_path + '\n')

        self.df = pd.read_csv(self.file_path, dayfirst=True)
        # TODO: fix errors that appear when some activities have empty gear

        # rename columns to ignore white spaces at the start and end of the string
        self.df.rename(columns=lambda x: x.strip(), inplace=True)

        if 'start time' in self.df.columns:
            self.column_date = 'start time'
        else:
            self.column_date = False

            # reformat the file_name column
        if 'file name' in self.df.columns:
            self.df['file name'] = self.df['file name'].apply(str)

        # reformat the date column
        # TODO: what if there is more than one date column: convert them all to datetime
        if self.column_date in self.df.columns:
            self.df[self.column_date] = pd.to_datetime(self.df[self.column_date], dayfirst=True)

        # create a variable with the column names to use when saving the database
        self.database_columns_to_save = self.df.columns

        self.df = self.calculate_new_columns(self.df)
        self.df_selected = self.df.copy()

    def populate_filters(self):
        # clear all widgets and labels
        for item in self.filters_widgets.keys():
            self.filters_labels[item].setText('')
            self.filters_widgets[item].clear()

        # populate appropriate widgets and labels
        for item in ['sport', 'activity', 'gear']:
            if item in self.df.columns:
                populate_list(self.df, item, self.filters_widgets[item])
                self.filters_labels[item].setText(item)
            else:
                self.filters_labels[item].setText('')
                self.filters_widgets[item].clear()

        if 'start position long' in self.df.columns:
            self.populate_locations()

    def new_locations(self):
        file_path = self.LocationsPathWidget.text()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose .csv file with list of locations.',
                                                             file_path, "CSV files (*.csv)")
        if len(file_path):
            self.LocationsPathWidget.clear()
            self.LocationsPathWidget.insert(file_path)
            self.populate_locations()
        else:
            print("WARNING: No locations file chosen. Choose another file to avoid errors.\n")

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

        locations_path = self.LocationsPathWidget.text()
        if len(locations_path):
            self.df_locations = pd.read_csv(locations_path)
            for item in self.df_locations['name']:
                self.StartLocationListWidget.addItem(item)
                self.EndLocationListWidget.addItem(item)
        else:
            print("WARNING: No locations file chosen. Choose another file to avoid errors.\n")

    def calculate_new_columns(self, df):
        self.column_date_local = self.column_date

        if self.column_date in df.columns:
            if 'timezone' in df.columns:
                # take into account the timezone
                self.df['timezone'] = pd.to_timedelta(self.df['timezone'])
                # TODO: fix errors when timezone is blank
                temp = df[self.column_date] + df['timezone']
                df[self.column_date + ' local'] = temp

                df['start daytime local'] = temp.dt.time
                self.column_date_local = 'start time local'
                # TODO: automate the self.column_date_local column name
            else:
                temp = df[self.column_date]
                # TODO: if self.column_date also has time info calculate temp.dt.time
                # then it won't be needed to add a timezone column full of zeros (eg John's data)

            # TODO: add end_daytime and end_time_local info when it's added in DatabaseWrite.py
            df['weekday'] = temp.dt.weekday + 1  # numeric: 1 = Monday, 7 = Sunday
            df['weekday week'] = (temp.dt.weekday + 1).apply(str) + ': ' + temp.dt.weekday_name  # string
            df['week'] = temp.dt.week
            df['year week'] = temp.dt.year.apply(str) + '-' + temp.dt.week.apply(str).str.pad(2, fillchar='0')
            df['month'] = temp.dt.month
            df['year month'] = temp.dt.year.apply(str) + '-' + temp.dt.month.apply(str).str.pad(2, fillchar='0')
            df['year month day'] = df['year month'] + '-' + temp.dt.day.apply(str).str.pad(2, fillchar='0')
            df['year'] = temp.dt.year
            df['date'] = temp.dt.date

        if 'Amount' in df.columns:
            df.sort_values(self.column_date, inplace=True)
            df['Balance'] = df['Amount'].cumsum()

        return df

    def set_SI_units(self):
        print("Setting database units to SI...")
        units_SI = dict()
        sections = self.config.sections()
        for section in sections:
            if 'UNIT FACTORS' in section:
                quantity = section.replace(' UNIT FACTORS', '').lower()
                # TODO: choose the one with value 1, in case it's not the first
                units_SI[quantity] = list(self.config.items(section))[0][0]

        for key in self.units_comboboxes.keys():
            index = self.units_comboboxes[key].findText(units_SI[key])
            self.units_comboboxes[key].setCurrentIndex(index)
            # update the units
        self.update_units()

    def update_units(self):
        # dataframes to update: df, df_selected
        print("Updating database units...")

        current_units = get_labels_text(self.units_labels)

        # convert from current_units to SI_units       
        self.df, self.units = convert_units(self.config, self.df, self.units, current_units, to_SI=True)
        self.df_selected, self.units = convert_units(self.config, self.df_selected, self.units, current_units, to_SI=True)

        # read desired units from the GUI into current_units
        current_units = read_units(self.units_comboboxes)

        # convert from SI_units to current_units
        self.df, self.units = convert_units(self.config, self.df, self.units, current_units, to_SI=False)
        self.df_selected, self.units = convert_units(self.config, self.df_selected, self.units, current_units, to_SI=False)

        set_labels_text(self.units_labels, current_units)
        print("Finished updating datatabase units!\n")

        # re-filter the database
        self.filter_and_plot_database()

    def filter_database(self):
        print("Filtering database...")
        current_units = get_labels_text(self.units_labels)

        if self.column_date_local:
            df_dates = select_dates(self.StartDateEdit, self.EndDateEdit, self.column_date_local, self.df)
        else:
            df_dates = self.df

        total_mask = [True] * len(df_dates)
        for key in self.filters_widgets.keys():
            if key in self.df.columns:
                selected_items = list_selection(self.filters_widgets[key])
                mask = generate_mask(df_dates, key, selected_items)
                total_mask = total_mask & mask

                # filtering by start and end location
        if 'start position long' in self.df.columns:
            selected_items = list_selection(self.StartLocationListWidget)
            mask_start = location_mask(self.df_locations, current_units, self.config, df_dates, 'start',
                                       selected_items)

            selected_items = list_selection(self.EndLocationListWidget)
            mask_end = location_mask(self.df_locations, current_units, self.config, df_dates, 'end',
                                     selected_items)

            if self.LocationComboBox.currentText() == 'and':
                mask_location = mask_start & mask_end
            elif self.LocationComboBox.currentText() == 'or':
                mask_location = mask_start | mask_end

            total_mask = total_mask & mask_location

        self.df_selected = df_dates[total_mask]

        print("Finished filtering database!\n")

    def filter_and_plot_database(self):
        self.filter_database()
        self.DatabaseSizeSpinBox.setValue(len(self.df_selected))
        fill_table(self.df_selected, self.Table1Widget, self.DatabaseRowsSpinBox.value())

        print("Updating figures (summary, scatter, histogram, map)...")
        self.plot_summary()
        self.plot_scatter()
        self.plot_histogram()
        if self.MapCheckBox.checkState() and self.MapCheckBox.isEnabled():
            self.generate_map()
            # pass
        print("Figures updated!\n")

        self.StartTimeDoubleSpinBox.setValue(0)
        self.EndTimeDoubleSpinBox.setValue(999999)

    def plot_scatter(self):
        df = self.df_selected
        x = self.ScatterXComboBox.currentText()
        y = self.ScatterYComboBox.currentText()
        cmap_name = self.CMapComboBox.currentText()
        alpha = self.TransparencyDoubleSpinBox.value()
        legend = self.LegendVariableComboBox.currentText()
        kind = 'line'  # fake scatter plot made from a line plot with markers

        if x == y:
            print("WARNING: choose different X and Y variables for the scatter plot!!!")
        else:

            self.figure_scatter.clear()
            ax = self.figure_scatter.add_subplot(111)

            colour_dict = generate_colours(df, legend, cmap_name)
            for label in sorted(colour_dict.keys()):
                # select data according to the desired legend variable
                df_plot = df.loc[df[legend] == label][[x, y]]
                if len(df_plot) > 0:
                    df_plot.plot(x=x, y=y,
                                 ax=ax,
                                 kind=kind,
                                 label=label,
                                 alpha=alpha,
                                 c=colour_dict[label],
                                 marker='.',
                                 markersize=12,
                                 linestyle='None',
                                 )

            ax.autoscale(enable=True, axis='both', tight='False')
            ax.margins(0.1, 0.1)

            xlabel = x.replace('_', ' ')
            if x in self.units.keys():
                if self.units[x]:
                    xlabel = xlabel + ' (' + self.units[x] + ')'

            ylabel = y.replace('_', ' ')
            if y in self.units.keys():
                if self.units[y]:
                    ylabel = ylabel + ' (' + self.units[y] + ')'

            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            legend = ax.legend(loc=self.LegendLocationComboBox.currentText(), numpoints=1)
            if legend:
                legend.set_visible(self.LegendCheckBox.checkState())

            ax.set_title(self.PlotTitleTextWidget.text())
            ax.grid(c='k', alpha=0.5)
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
            density = True
        elif y == 'counts':
            density = False

        colour_dict = generate_colours(df, legend, cmap_name)
        for label in sorted(colour_dict.keys()):
            df_hist = df[df[legend] == label]

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
                    print("Cannot generate histogram.\n")
                    histogram = False

            if len(x_data) > 1:
                if histogram:
                    ax.hist(x_data[x].dropna(),
                            bins=bins,
                            color=colour_dict[label],
                            label=label,
                            density=density,
                            alpha=alpha,
                            )

        xlabel = x.replace('_', ' ')
        if x in self.units.keys():
            if self.units[x]:
                xlabel = xlabel + ' (' + self.units[x] + ')'
        if frequency != 'all':
            xlabel = measure + ' ' + xlabel + ' / ' + frequency

        if histogram:
            ax.set_xlabel(xlabel)
            ax.set_ylabel(y)
            legend = ax.legend(loc=self.LegendLocationComboBox.currentText())
            if legend:
                legend.set_visible(self.LegendCheckBox.checkState())

            ax.set_title(self.PlotTitleTextWidget.text())
            ax.grid(c='k', alpha=0.5)
            self.canvas_hist.draw()

    def plot_summary(self):
        summary_quantity_list = [self.SummaryQuantityComboBox.itemText(i) for i in
                                 range(self.SummaryQuantityComboBox.count())]
        summary_category_list = [self.SummaryCategory1ComboBox.itemText(i) for i in
                                 range(self.SummaryCategory1ComboBox.count())]
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
            self.df_summary_double = df.groupby([category1, category2]).sum()
        elif measure == 'last':
            self.df_summary_single = df.groupby([category1]).last()
            self.df_summary_double = df.groupby([category1, category2]).last()
        elif measure == 'mean':
            self.df_summary_single = df.groupby([category1]).mean()
            self.df_summary_double = df.groupby([category1, category2]).mean()
        elif measure == 'count':
            self.df_summary_single = df.groupby([category1]).count()
            self.df_summary_double = df.groupby([category1, category2]).count()

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
            timedelta_factors = {'D': 1, 'W': 7, 'Y': 365,
                                 'M': 365 / 12}  # this is not very precise but it should be enough to get an idea
            df_summary_plot = df_summary_plot / timedelta.days * timedelta_factors[frequency]

        self.figure_summary.clear()
        ax = self.figure_summary.add_subplot(111)

        plot_options = populate_plot_options(kind=kind, alpha=alpha,
                                             cmap_name=cmap_name, stacked=stacked)
        df_summary_plot.plot(ax=ax, **plot_options)

        legend = ax.legend(loc=self.LegendLocationComboBox.currentText())
        legend.set_visible(self.LegendCheckBox.checkState())

        label_quantity = quantity.replace('_', ' ')
        label_quantity = measure + ' ' + label_quantity

        if quantity in self.units.keys():
            if self.units[quantity]:
                label_quantity = label_quantity + ' (' + self.units[quantity] + ')'
        if frequency != 'all':
            label_quantity = label_quantity + ' / ' + frequency

        label_category1 = category1.replace('_', ' ')
        if category1 in self.units.keys():
            if self.units[category1]:
                label_category1 = label_category1 + ' (' + self.units[category1] + ')'

        if kind == 'barh':
            ax.set_xlabel(label_quantity)
            ax.set_ylabel(label_category1)
        else:
            ax.set_xlabel(label_category1)
            ax.set_ylabel(label_quantity)

        ax.set_title(self.PlotTitleTextWidget.text())
        ax.grid(c='k', alpha=0.5)
        self.canvas_summary.draw()

    def read_records(self, file_path):
        df = pd.read_csv(file_path, parse_dates=['timestamp'])
        self.records_columns_to_save = df.columns

        # use these lines if we want to eliminate columns titled 'Unnamed'
        #        self.records_columns_to_save = []
        #        for item in df.columns:
        #            if not 'Unnamed' in item:
        #                self.records_columns_to_save.append(item)

        df['elapsed time'] = calculate_elapsed_time(df['timestamp'], units_t='s')

        populate_combobox(sorted(df.columns), self.TraceTopXComboBox.currentText(),
                          [self.TraceTopXComboBox])
        populate_combobox(sorted(df.columns), self.TraceTopYComboBox.currentText(),
                          [self.TraceTopYComboBox])
        populate_combobox(sorted(df.columns), self.TraceBottomXComboBox.currentText(),
                          [self.TraceBottomXComboBox])
        populate_combobox(sorted(df.columns), self.TraceBottomYComboBox.currentText(),
                          [self.TraceBottomYComboBox])

        return df  # output in SI units

    def merge_dataframes(self, left, right, index):
        left.set_index(index, inplace=True)
        right.set_index(index, inplace=True)
        for row in right.index:
            for column in right.columns:
                left.loc[row, column] = right.loc[row, column]
        left.reset_index(inplace=True)
        return left

    def save_data(self):
        # read file name
        file_path = self.SaveDatabasePathWidget.text()
        #        file_path = QtWidgets.QFileDialog.getSaveFileName(self, 'Choose database .csv file to save.', file_path, "CSV files (*.csv)")
        self.SaveDatabasePathWidget.clear()
        self.SaveDatabasePathWidget.insert(file_path)
        self.ReadDatabasePathWidget.clear()
        self.ReadDatabasePathWidget.insert(file_path)

        # TODO: strange characters like ñ screw it up
        print('Saving database...')
        # read data from Table 1
        df_widget = read_table(self.Table1Widget)
        # combine df_widget with the rest of the activities not shown in Table 1
        df_save = self.merge_dataframes(self.df, df_widget, 'start time local')
        # TODO: merge by file_name instead of start_time_local
        self.df = df_save.copy()

        # convert to SI units before saving
        current_units = get_labels_text(self.units_labels)
        df_save, useless_units = convert_units(self.config, df_save, self.units, current_units,
                                               to_SI=True)

        # save database
        df_save.to_csv(file_path, sep=',', header=True, index=False, columns=self.database_columns_to_save)
        print('Database saved! \n')

        # read selected rows from the database
        self.df_trace = read_selected_table_rows(self.Table1Widget)
        print('Saving record files...')
        for index in self.df_trace.index:
            file_name = self.df_trace.loc[index, 'file name']
            # read records file
            file_path = os.path.join(self.RecordsPathWidget.text(), str(file_name) + '_record.csv')
            df = self.read_records(file_path)
            # crop records by time
            # TODO: crop by database time and not start and end time from the GUI
            df = select_times(self.StartTimeDoubleSpinBox, self.EndTimeDoubleSpinBox, df)
            # recalculate distance
            df['distance'] = df['distance'] - df.loc[df.index[0], 'distance']
            #            df = df.drop('elapsed time', axis=1)
            # save records
            df.to_csv(file_path, sep=',', header=True, index=False, columns=self.records_columns_to_save)
        print('Record files saved! \n')

    def generate_map(self):
        # TODO: what if records do not have GPS data?
        number_of_activities = self.MapActivitiesSpinBox.value()
        legend = self.LegendVariableComboBox.currentText()
        cmap_name = self.CMapComboBox.currentText()
        colour_dict = generate_colours(self.df_selected, legend, cmap_name)
        current_units = get_labels_text(self.units_labels)

        self.figure_map.clear()
        ax = self.figure_map.add_subplot(111)

        self.map_data = {}
        self.map_colours = {}
        avg_lat = []
        avg_long = []
        for index in self.df_selected.iloc[0:number_of_activities].index:
            file_name = self.df_selected.loc[index, 'file name']

            file_path = os.path.join(self.RecordsPathWidget.text(), str(file_name) + '_record.csv')
            # read the csv file
            df = self.read_records(file_path)
            df, self.units = convert_units(self.config, df, self.units, current_units)
            # Extract location information, remove missing data, convert to degrees
            self.map_data[file_name] = df.loc[:, ['position lat', 'position long']].dropna()
            #            self.map_colours[file_name] = 'k'
            self.map_colours[file_name] = colour_dict[self.df_selected.loc[index, legend]]

            avg_long.append(self.map_data[file_name]['position long'].mean())
            avg_lat.append(self.map_data[file_name]['position lat'].mean())

            # TODO: user option: line (faster) or scatter (better if many nan) plot
            ax.plot(self.map_data[file_name]['position long'],
                    self.map_data[file_name]['position lat'],
                    label=file_name,
                    c=self.map_colours[file_name],
                    )
        #            ax.scatter(self.map_data[file_name]['position long'],
        #                       self.map_data[file_name]['position lat'],
        #                       label = file_name,
        #                       )

        # make sure x and y axis have the same spacing
        ax.axis('equal')

        # label axes        
        xlabel = 'position long (' + self.units['position long'] + ')'
        ylabel = 'position lat (' + self.units['position lat'] + ')'
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        ax.set_title(self.PlotTitleTextWidget.text())
        ax.grid(c='k', alpha=0.5)
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
        print("Saving HTML map...")
        print("WARNING: HTML map saving will only work if the GPS units is set to 'deg'!")
        # TODO: this will only work if the GPS units is set to "deg", allow other options

        gmap = gmplot.GoogleMapPlotter(self.map_centre[1], self.map_centre[0], 13)
        #        gmap = gmplot.GoogleMapPlotter(52.202, 0.12, 13) # Cambridge
        #        gmap = gmplot.GoogleMapPlotter(43, -120, 5) # USA West Coast
        #        gmap = gmplot.GoogleMapPlotter(46.36, 14.09, 11) # Lake Bled

        for key in self.map_data:
            color = '#%02x%02x%02x' % (self.map_colours[key][0] * 255,
                                       self.map_colours[key][1] * 255,
                                       self.map_colours[key][2] * 255),
            if self.MapBlackCheckBox.checkState():
                color = 'k'

            # Add a line plot to the gmap object which will be save to an .html file
            # Use line instead of scatter plot for faster speed and smaller file size

            # TODO: user option: line (faster) or scatter (very very slow) plot
            # so if there are nan, e.g. metro, separate the plots into several line plots
            gmap.plot(self.map_data[key]['position lat'],
                      self.map_data[key]['position long'],
                      color=color,
                      edge_width=3,
                      )
        #            gmap.scatter(self.map_data[key]['position lat'][0:-1:5],
        #                         self.map_data[key]['position long'][0:-1:5],
        #                         color=self.map_colours[key], size=10, marker=False)

        file_path = self.MapFilePathWidget.text()
        file_path = QtWidgets.QFileDialog.getSaveFileName(self, 'Choose .html file to save map.', file_path,
                                                          "HTML files (*.html)")
        if len(file_path):
            self.MapFilePathWidget.clear()
            self.MapFilePathWidget.insert(file_path)
            gmap.draw(file_path)
            print("Finished HTML map!\n")
        else:
            print("WARNING: No .html path chosen. Choose another path to save the map.\n")

    def select_and_plot_trace(self):
        # TODO: threading
        print("Starting trace plots...")

        current_units = get_labels_text(self.units_labels)

        self.df_trace = read_selected_table_rows(self.Table1Widget)

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
            print("WARNING: " + str(len(self.df_trace)) + " trace plots might take a long time!")

        for index in self.df_trace.index:
            file_name = self.df_trace.loc[index, 'file name']
            file_path = os.path.join(self.RecordsPathWidget.text(), str(file_name) + '_record.csv')
            # read the csv file
            df = self.read_records(file_path)
            # convert to current_units
            df, self.units = convert_units(self.config, df, self.units, current_units,
                                                    to_SI=False)
            # select data based on start and end values of elapsed time
            df = select_times(self.StartTimeDoubleSpinBox, self.EndTimeDoubleSpinBox, df)

            # recalculate mean and max values (heart_rate, speed, ...) and update Table 1
            self.recalculate_statistics(df, file_name)

            if index == self.df_trace.index[0]:
                fill_table(df, self.Table2Widget)

            x1 = self.TraceTopXComboBox.currentText()
            y1 = self.TraceTopYComboBox.currentText()
            x2 = self.TraceBottomXComboBox.currentText()
            y2 = self.TraceBottomYComboBox.currentText()

            if self.TraceTopCheckBox.checkState() and x1 != y1:
                trace_top_plot_options = populate_plot_options(df=self.df_trace,
                                                               index=index,
                                                               legend=self.LegendVariableComboBox.currentText(),
                                                               cmap_name=self.CMapComboBox.currentText(),
                                                               kind=self.TraceTopKindComboBox.currentText(),
                                                               alpha=self.TransparencyDoubleSpinBox.value())

                df.plot(x=x1, y=y1,
                        ax=ax1,
                        **trace_top_plot_options)

                xlabel = x1.replace('_', ' ')
                if x1 in self.units.keys():
                    if self.units[x1]:
                        xlabel = xlabel + ' (' + self.units[x1] + ')'

                ylabel = y1.replace('_', ' ')
                if y1 in self.units.keys():
                    if self.units[y1]:
                        ylabel = ylabel + ' (' + self.units[y1] + ')'

                if self.TraceTopAxesEqualCheckBox.checkState():
                    # set x and y axis to have the same spacing - good for GPS coordinates
                    ax1.axis('equal')

                ax1.set_xlabel(xlabel)
                ax1.set_ylabel(ylabel)
                ax1.autoscale(enable=True, axis='both', tight=False)
                ax1.margins(0.1, 0.1)
                legend = ax1.legend(loc=self.LegendLocationComboBox.currentText())
                legend.set_visible(self.LegendCheckBox.checkState())
                ax1.grid(c='k', alpha=0.5)

            if self.TraceBottomCheckBox.checkState() and x2 != y2:
                trace_bottom_plot_options = populate_plot_options(df=self.df_trace,
                                                                  index=index,
                                                                  legend=self.LegendVariableComboBox.currentText(),
                                                                  cmap_name=self.CMapComboBox.currentText(),
                                                                  kind=self.TraceBottomKindComboBox.currentText(),
                                                                  alpha=self.TransparencyDoubleSpinBox.value())

                df.plot(x=x2, y=y2,
                        ax=ax2,
                        **trace_bottom_plot_options)

                xlabel = x2.replace('_', ' ')
                if x2 in self.units.keys():
                    if self.units[x2]:
                        xlabel = xlabel + ' (' + self.units[x2] + ')'

                ylabel = y2.replace('_', ' ')
                if y2 in self.units.keys():
                    if self.units[y2]:
                        ylabel = ylabel + ' (' + self.units[y2] + ')'

                if self.TraceBottomAxesEqualCheckBox.checkState():
                    # set x and y axis to have the same spacing - good for GPS coordinates
                    ax2.axis('equal')

                ax2.set_xlabel(xlabel)
                ax2.set_ylabel(ylabel)
                ax2.autoscale(enable=True, axis='both', tight='False')
                ax2.margins(0.1, 0.1)
                legend = ax2.legend(loc=self.LegendLocationComboBox.currentText())
                legend.set_visible(self.LegendCheckBox.checkState())
                ax2.grid(c='k', alpha=0.5)

        ax.set_title(self.PlotTitleTextWidget.text())
        ax.grid(c='k', alpha=0.5)
        self.canvas_trace.draw()
        print("Finished trace plots!\n")

    def recalculate_statistics(self, df, file_name):
        # TODO: instead of placing the values in the table, place the values in the df then update the table
        # df is the records dataframe

        row = self.Table1Widget.findItems(str(file_name), QtCore.Qt.MatchExactly)[0].row()

        number_of_columns = self.Table1Widget.columnCount()
        column_dict = {}
        for column in range(number_of_columns):
            column_name = self.Table1Widget.horizontalHeaderItem(column).text()
            column_dict[column_name] = column

        if 'speed' in df.columns:
            if 'avg speed' in column_dict.keys():
                value = df['speed'].mean()
                self.Table1Widget.setItem(row, column_dict['avg speed'],
                                          QtWidgets.QTableWidgetItem(format(value, '.3f')))
            if 'max speed' in column_dict.keys():
                value = df['speed'].max()
                self.Table1Widget.setItem(row, column_dict['max speed'],
                                          QtWidgets.QTableWidgetItem(format(value, '.3f')))

        if 'heart rate' in df.columns:
            if 'avg heart rate' in column_dict.keys():
                value = df['heart rate'].mean()
                self.Table1Widget.setItem(row, column_dict['avg heart rate'],
                                          QtWidgets.QTableWidgetItem(format(value, '.2f')))
            if 'max heart rate' in column_dict.keys():
                value = df['heart rate'].max()
                self.Table1Widget.setItem(row, column_dict['max heart rate'],
                                          QtWidgets.QTableWidgetItem(format(value, '.2f')))

        if 'cadence' in df.columns:
            if 'avg cadence' in column_dict.keys():
                # remove zeros, which are like missing cadence data
                value = df[df['cadence'] != 0]['cadence'].dropna().mean()
                self.Table1Widget.setItem(row, column_dict['avg cadence'],
                                          QtWidgets.QTableWidgetItem(format(value, '.2f')))
            if 'max cadence' in column_dict.keys():
                value = df['cadence'].max()
                self.Table1Widget.setItem(row, column_dict['max cadence'],
                                          QtWidgets.QTableWidgetItem(format(value, '.2f')))

        if 'position lat' in df.columns:
            if 'start position lat' in column_dict.keys():
                position = df['position lat'].dropna()
                if not position.empty:
                    value = position.iloc[0]
                    self.Table1Widget.setItem(row, column_dict['start position lat'],
                                              QtWidgets.QTableWidgetItem(format(value, '.4f')))
            if 'end position lat' in column_dict.keys():
                position = df['position lat'].dropna()
                if not position.empty:
                    value = position.iloc[-1]
                    self.Table1Widget.setItem(row, column_dict['end position lat'],
                                              QtWidgets.QTableWidgetItem(format(value, '.4f')))

        if 'position long' in df.columns:
            if 'start position long' in column_dict.keys():
                position = df['position long'].dropna()
                if not position.empty:
                    value = position.iloc[0]
                    self.Table1Widget.setItem(row, column_dict['start position long'],
                                              QtWidgets.QTableWidgetItem(format(value, '.4f')))
            if 'end position long' in column_dict.keys():
                position = df['position long'].dropna()
                if not position.empty:
                    value = position.iloc[-1]
                    self.Table1Widget.setItem(row, column_dict['end position long'],
                                              QtWidgets.QTableWidgetItem(format(value, '.4f')))

        if 'distance' in df.columns:
            if 'total distance' in column_dict.keys():
                value = df.loc[df.index[-1], 'distance'] - df.loc[df.index[0], 'distance']
                self.Table1Widget.setItem(row, column_dict['total distance'],
                                          QtWidgets.QTableWidgetItem(format(value, '.4f')))
        if 'elapsed time' in df.columns:
            if 'total elapsed time' in column_dict.keys():
                value = df.loc[df.index[-1], 'elapsed time'] - df.loc[df.index[0], 'elapsed time']
                self.Table1Widget.setItem(row, column_dict['total elapsed time'],
                                          QtWidgets.QTableWidgetItem(format(value, '.4f')))


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    gui = DatabaseGUI()
    gui.show()
    app.exec_()
