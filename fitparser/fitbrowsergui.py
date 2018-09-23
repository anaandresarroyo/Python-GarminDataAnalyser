from fitparse import FitFile
from collections import Counter
import os
from PyQt5 import QtWidgets, uic

# TODO: without this the GUI doesn't load properly. fix it.
import matplotlib


class FitBrowserGUI(QtWidgets.QMainWindow):
    """
    GUI which displays the contents of a .fit file
    """

    def __init__(self, parent=None):
        super(FitBrowserGUI, self).__init__(parent)
        ui_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'FitBrowserGUIdesign.ui')
        uic.loadUi(ui_file_path, self)

        self.fit_file = None
        self.message_counter = None

        self.file_path = os.getcwd()
        self.new_file()

        # Connect GUI elements
        self.NewFilePushButton.clicked.connect(self.new_file)
        self.PrintPushButton.clicked.connect(self.fill_table)

        # Set initial splitter size
        self.splitter.setSizes([50, 650])

    def new_file(self):
        """Select a new FIT file and populate the file contents table."""
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose .fit file.',
                                                          self.file_path, "FIT files (*.fit)")[0]
        if len(file_path):
            self.file_path = file_path
            self.open_file()
            self.FilePathWidget.insert(self.file_path)
        else:
            print("No file chosen. Choose another file to avoid errors.")

    def open_file(self):
        """Read the FIT file and populate the file contents table."""
        print(self.file_path)
        # Open .fit file
        self.fit_file = FitFile(self.file_path)
        print("File open.")
        self.populate_file_contents_table()

    def populate_file_contents_table(self):
        """Populate the file contents table."""
        # Initialise empty counter to count types of messages
        self.message_counter = Counter()

        # Get all data messages 
        print("Reading message types.")
        for message in self.fit_file.get_messages():
            # Update the message_counter
            self.message_counter[message.name.replace('_', ' ')] += 1

        self.Table1Widget.clear()
        self.FileContentsTableWidget.clear()
        self.FileContentsTableWidget.setColumnCount(2)
        self.FileContentsTableWidget.setRowCount(len(self.message_counter))
        self.FileContentsTableWidget.setHorizontalHeaderLabels(['Message type', 'Quantity'])
        row = 0
        for key, val in self.message_counter.items():
            self.FileContentsTableWidget.setItem(row, 0, QtWidgets.QTableWidgetItem(key))
            self.FileContentsTableWidget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(val)))
            row = row + 1
        self.FileContentsTableWidget.resizeColumnToContents(0)
        self.FileContentsTableWidget.resizeColumnToContents(1)
        self.FileContentsTableWidget.setCurrentCell(0, 1)

        print("Message list updated.")

    def fill_table(self):
        """Populate Table 1 with the contents of the desired message type and number."""
        message_type = self.FileContentsTableWidget.item(self.FileContentsTableWidget.currentRow(), 0).text()
        max_number = int(self.FileContentsTableWidget.item(self.FileContentsTableWidget.currentRow(), 1).text())
        message_number = self.MessageNumberBox.value()
        if message_number > max_number:
            message_number = max_number
            self.MessageNumberBox.setValue(message_number)

        self.Table1Widget.clear()
        self.Table1Widget.setColumnCount(3)
        self.Table1Widget.setHorizontalHeaderLabels(['Name', 'Value', 'Units'])

        # Get all data messages that are of type desired_messages
        for im, message in enumerate(self.fit_file.get_messages(message_type)):
            if im == message_number - 1:
                # Go through all the data entries in this message and populate the table
                for row, message_data in enumerate(message):

                    self.Table1Widget.setRowCount(row + 1)
                    self.Table1Widget.setItem(row, 0, QtWidgets.QTableWidgetItem(message_data.name.replace('_', ' ')))
                    self.Table1Widget.setItem(row, 1, QtWidgets.QTableWidgetItem(str(message_data.value)))

                    if message_data.units:
                        self.Table1Widget.setItem(row, 2, QtWidgets.QTableWidgetItem(message_data.units))

                self.Table1Widget.resizeColumnToContents(0)
                self.Table1Widget.resizeColumnToContents(1)
                self.Table1Widget.resizeColumnToContents(2)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    gui = FitBrowserGUI()
    gui.show()
