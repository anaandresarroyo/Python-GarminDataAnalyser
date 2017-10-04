# Use Python to analyse GPS and fitness data recorded with a Garmin Forerunner 35 watch.

--- FitBrowser.py ---

GUI which displays the contents of a Garmin FIT file.

--- FitToCsv.py ---

Reads many Garmin FIT files and saves the desired data into many .CSV files.

--- DatabaseWrite.py ---

Creates/updates CSV database entries from information extracted from FIT files.

--- DatabaseRead.py ---

GUI which reads, analyses, plots, and updates the database CSV file and the activities' CSV files.

- Select data by: sport, activity, gear, location, date.
- Display data from tables: database, and individual activities.
- Plot types: scatter plot, histogram, line plot
- Custom x and y axis options: date, time, position, speed, heart rate, cadence, calories, etc.
- Save data to: original/new database CSV file, update individual activities' CSV files, HTML file with trajectories.