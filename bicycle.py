import csv
import datetime
from collections import defaultdict
import matplotlib.pylab as plt

velicites_list = []
stations_lat_long_dictionary = {}
duration_dictionary = defaultdict(int)
distance_dictionary = defaultdict(float)

file_name_input1 = 'inputs/hubway_trips.csv'
file_name_input2 = 'inputs/hubway_stations.csv'
file_name_input3 = 'inputs/hubway_station_distances.csv'

file_name_output1 = 'output/hubway_velocities.csv'


# this is a function that aggregates all hubway trips by trip start station, end station and time of the day
# the input is hubway_trips.csv file that can be downloaded from http://files.hubwaydatachallenge.org/hubway_2011_07_through_2013_11.zip
# the output is a dictionary with the shortest distance for every start_station, end_station and hour_in_day (0,..,24)
def find_trip_duration():
    
    file_ = open(file_name_input1,'rb')
    file_.readline()                                        # read the first header line

    try:
        for i_ in range(200):
            lines = file_.readlines(i_*10000)
            for line in lines:
                
                try:
                    list_of_strings = line.split(',')
                    duration_trip = int(list_of_strings[3]) # in seconds
                    start_station = int(list_of_strings[5])
                    end_station = int(list_of_strings[7])
                    start_time = datetime.datetime.strptime(list_of_strings[4], "%m/%d/%Y %H:%M:%S")
                   
                    if duration_trip > 0:                       
                        current_duration_trip = duration_dictionary[start_station, end_station, start_time.hour]                      
                        if start_station != end_station and (current_duration_trip > duration_trip or current_duration_trip == 0):
                                duration_dictionary[start_station, end_station, start_time.hour] = duration_trip
                       
                except Exception as e:                      # catch and print out casting Errors
                    print e, line
    except EOFError:
        pass  


# this is a function that creates a dictionary with lat long coordinates for every hubway station
# the input is hubway_stations.csv file that can be downloaded from http://files.hubwaydatachallenge.org/hubway_2011_07_through_2013_11.zip
# the output is a dictionary with lat long coordinates for every hubway station
def find_stations_lat_long():
    
    file_ = open(file_name_input2,'rb')
    file_.readline()                                        # read the first header line
    
    try:
        for i_ in range(200):
            lines = file_.readlines(i_*10000)
            for line in lines:
                list_of_strings = line.split(',')
                station_id = int(list_of_strings[0])
                station_lat = float(list_of_strings[4])
                station_long = float(list_of_strings[5])
    
                stations_lat_long_dictionary[station_id] = (station_lat, station_long)           
               
    except EOFError:
        pass     
      
      
# this is a function that creates a dictionary with distances (in meters) for every two connected hubway stations
# the input is hubway_station_distances.csv file that was made using ArcGIS
# the output is a dictionary with distances (in meters) for every two connected hubway stations
def find_trip_distance():
    
    file_ = open(file_name_input3,'rb')
    file_.readline()                                        # read the first header line
    
    try:
        for i_ in range(200):
            lines = file_.readlines(i_*10000)
            for line in lines:
                list_of_strings = line.split(',')
                start_station = int(list_of_strings[2]) - 140   # different id station names
                end_station = int(list_of_strings[3]) + 2       # different id station names
                distance = float(list_of_strings[5])
    
                if start_station != end_station:
                    distance_dictionary[start_station, end_station] = distance             
               
    except EOFError:
        pass
          
    
# this is a function that calculates velocities for every two stations that are connected
# the inputs are three previously created dictionaries
# the output is hubway_velocities.csv file where velocity between two stations is assigned to the point that is between those two stations
def calculate_trip_velocity(): 
    
    with open(file_name_output1, 'wb') as f:
        writer = csv.writer(f)
        
        writer.writerow(["strt_statn,end_statn,time,velocity,middle_station_lat,middle_station_long"])
        
        for key, value in duration_dictionary.items():        
            distance = float(distance_dictionary[int(key[0]), int(key[1])])
            duration = int(value)
            
            if duration != 0:
                velocity = float(distance/duration)
            
                if velocity > 1 and velocity < 11:              # we are filtering only feasible velocities
                    start_station_lat = float(stations_lat_long_dictionary[int(key[0])][0])        
                    start_station_long = float(stations_lat_long_dictionary[int(key[0])][1])
                    
                    end_station_lat = float(stations_lat_long_dictionary[int(key[1])][0])        
                    end_station_long = float(stations_lat_long_dictionary[int(key[1])][1])
                    
                    middle_station_lat = float((start_station_lat + end_station_lat) / 2)           # calculating mid point lat
                    middle_station_long = float((start_station_long + end_station_long) / 2)        # calculating mid point long
                    
                    writer.writerow([key[0], key[1], key[2], velocity, middle_station_lat, middle_station_long])
                                    
                    velicites_list.append(velocity)
                    
        plt.hist(velicites_list, bins = 100)    # show velocities distribution
        plt.show()
        
          
find_trip_duration()
find_trip_distance()
find_stations_lat_long()
calculate_trip_velocity()
