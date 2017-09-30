# -*- coding: utf-8 -*-
"""
@author: Ana Andres-Arroyo

Reads a Garmin .fit file and prints its information
"""
from fitparse import FitFile
from collections import Counter

from MatplotlibSettings import *
import FitBrowserGUIdesign
import sys
import os
from PyQt4 import QtGui
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

class FitBrowserGUI(QtGui.QMainWindow, FitBrowserGUIdesign.Ui_FitBrowserGUI):
    """
    GUI which displays the contents of a .fit file
    """
    def __init__(self, parent=None):
        super(FitBrowserGUI, self).__init__(parent)
        self.setupUi(self)
        self.file_path = os.getcwd()
        self.new_file()
        
        # Connect GUI elements
        self.NewFilePushButton.clicked.connect(self.new_file)
        self.PrintPushButton.clicked.connect(self.fill_table)
                      
        self.figure1 = Figure()
        self.canvas1 = FigureCanvas(self.figure1)
        self.toolbar1 = NavigationToolbar(self.canvas1, self)
        self.Plot1WidgetContainer.addWidget(self.toolbar1)
        self.Plot1WidgetContainer.addWidget(self.canvas1)    
       
    
    def new_file(self):
        """Select a new FIT file and populate the file contents table.""" 
        file_path = QtGui.QFileDialog.getOpenFileName(self, 'Choose .fit file.', self.file_path, "FIT files (*.fit)")
        if len(file_path):
            self.file_path = file_path
            self.open_file()
            self.FilePathWidget.insert(self.file_path)
        else:
            print "No file chosen. Choose another file to avoid errors."            
        
    def open_file(self):
        """Read the FIT file and populate the file contents table."""
        print self.file_path
        # Open .fit file    
        self.fitfile = FitFile(self.file_path)
        print "File open."
        self.message_list()
           
    def message_list(self):
        """Populate the file contents table."""
        # Initialise empty counter to count types of messages
        self.message_counter = Counter()

        # Get all data messages 
        print "Reading message types."
        for message in self.fitfile.get_messages():
            # Update the message_counter
            self.message_counter[message.name] += 1
        
        self.Table1Widget.clear()
        self.FileContentsTableWidget.clear()
        self.FileContentsTableWidget.setColumnCount(2)
        self.FileContentsTableWidget.setRowCount(len(self.message_counter))
        self.FileContentsTableWidget.setHorizontalHeaderLabels(['Message type','Quantity'])
        row = 0
        for key, val in self.message_counter.items():
            self.FileContentsTableWidget.setItem(row,0,QtGui.QTableWidgetItem(key))
            self.FileContentsTableWidget.setItem(row,1,QtGui.QTableWidgetItem(str(val)))
            row = row + 1
        self.FileContentsTableWidget.resizeColumnToContents(0)
        self.FileContentsTableWidget.resizeColumnToContents(1)
        self.FileContentsTableWidget.setCurrentCell(0,1)
        
        print "Message list updated."
    
    def fill_table(self):
        """Pupulate Table 1 with the contents of the desired message type and number."""
        message_type = self.FileContentsTableWidget.item(self.FileContentsTableWidget.currentRow(),0).text() 
        max_number = int(self.FileContentsTableWidget.item(self.FileContentsTableWidget.currentRow(),1).text())
        message_number = self.MessageNumberBox.value()
        if message_number > max_number:
            message_number = max_number
            self.MessageNumberBox.setValue(message_number)
               
        self.Table1Widget.clear()
        self.Table1Widget.setColumnCount(3)        
        self.Table1Widget.setHorizontalHeaderLabels(['Name','Value', 'Units'])
        
        # Get all data messages that are of type desired_messages
        for im, message in enumerate(self.fitfile.get_messages(message_type)):
            if im == message_number-1:
                # Go through all the data entries in this message and populate the table
                for row, message_data in enumerate(message):

                    self.Table1Widget.setRowCount(row+1)
                    self.Table1Widget.setItem(row,0,QtGui.QTableWidgetItem(message_data.name))
                    self.Table1Widget.setItem(row,1,QtGui.QTableWidgetItem(str(message_data.value)))

                    if message_data.units:
                        self.Table1Widget.setItem(row,2,QtGui.QTableWidgetItem(message_data.units))
                        
                self.Table1Widget.resizeColumnToContents(0)
                self.Table1Widget.resizeColumnToContents(1)
                self.Table1Widget.resizeColumnToContents(2)

    
if __name__ == '__main__':
        
    app = QtGui.QApplication(sys.argv)
    form = FitBrowserGUI()
    form.show()
    app.exec_()