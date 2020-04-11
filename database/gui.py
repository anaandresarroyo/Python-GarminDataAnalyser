import numpy as np
import pandas as pd
from PyQt5 import QtWidgets, QtCore


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
            data = df.iloc[row, col]
            item = QtWidgets.QTableWidgetItem()
            if isinstance(data, (float, np.float64)):
                # pad the floats so they'll be sorted correctly
                formatted_data = '{:.3f}'.format(data).rjust(15)
                item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            elif isinstance(data, (int, np.int64)):
                # pad the integers so they'll be sorted correctly
                formatted_data = '{:d}'.format(data).rjust(15)
                item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            else:
                formatted_data = str(data)
            item.setData(QtCore.Qt.EditRole, formatted_data)
            table.setItem(row, col, item)
            table.resizeColumnToContents(col)

    # enable table sorting by columns
    table.setSortingEnabled(True)

    # temporarily set MultiSelection
    table.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
    # reselect the prevously selected rows
    # TODO: reselect by filename instead of table row number
    for row in selected_rows:
        table.selectRow(row)
    # revert MultiSelection to ExtendedSelection
    table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)


def populate_combobox(items_list, item_default, combobox_list):
    # populate comboboxes
    for combobox in combobox_list:
        combobox.clear()
        for item in items_list:
            combobox.addItem(item, 0)
        if item_default in items_list:
            index = combobox.findText(item_default)
        else:
            index = 0
        combobox.setCurrentIndex(index)


def populate_comboboxes(config, df, numeric_comboboxes, units_comboboxes, trace_comboboxes, comboboxes):
    default_value_keys = [x[0] for x in config.items('DEFAULT VALUES')]

    # TODO: also include datetime.time values
    options = df.select_dtypes(include=['float64', 'int64', 'datetime64[ns]']).columns.values
    for key, value in numeric_comboboxes.items():
        if key in default_value_keys:
            default_value = config['DEFAULT VALUES'][key]
        else:
            default_value = options[0]
        populate_combobox(sorted(np.unique(options)),
                          default_value,
                          value)

    for key, value in units_comboboxes.items():
        options = [x[0] for x in config.items('%s UNIT FACTORS' % key.upper())]
        populate_combobox(options,
                          options[0],  # TODO: choose the one with value 1, in case it's not the first
                          [value])

    for key, value in trace_comboboxes.items():
        if key in default_value_keys:
            default_value = config['DEFAULT VALUES'][key]
        else:
            default_value = None
        populate_combobox([default_value],
                          default_value,
                          value)

    for key, value in comboboxes.items():
        options = list(filter(None, [x.strip() for x in config['GUI OPTIONS'][key].splitlines()]))
        if key in default_value_keys:
            default_value = config['DEFAULT VALUES'][key]
        else:
            default_value = options[0]
        populate_combobox(options,
                          default_value,
                          value)


def populate_dates(column_date_local, df, start_date_edit, end_date_edit):
    if column_date_local in df.columns:
        start_date_edit.setDate(df[column_date_local].min())
        end_date_edit.setDate(df[column_date_local].max())


def read_units(units_comboboxes):
    """Read units from GUI comboboxes."""
    units = dict()
    for key in units_comboboxes.keys():
        units[key] = units_comboboxes[key].currentText()
    return units





def list_selection(widget):
    selected_options = []
    for item in widget.selectedItems():
        selected_options.append(item.text())
    return selected_options


def populate_list(df, column, widget):
    """Populate the list widget with items from the dataframe column."""
    items = np.sort(df[column].unique())
    widget.clear()
    for row, item in enumerate(items):
        widget.addItem(item)
        widget.item(row).setSelected(True)


def read_table(table, rows=None):
    # read GUI table size
    if rows is None:
        rows = []
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
            df.loc[row, column_name] = table.item(row, column_number).data(0)

    # TODO: make this formatting more automatic
    # format data types
    datetime_column_names = ['start time', 'start time local', 'end time', 'end time local', 'timestamp']
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


def read_selected_table_rows(table):
    selected_rows = []
    for item in table.selectedIndexes():
        selected_rows.append(item.row())
    selected_rows = np.unique(selected_rows)
    # read the selected_rows from the table
    df = read_table(table, selected_rows)
    # return the dataframe
    return df


def get_labels_text(labels):
    text = dict()
    for key, value in labels.items():
        text[key] = value.text()
    return text


def set_labels_text(labels, text):
    for key in labels.keys():
        labels[key].setText(text[key])