#!/usr/bin/env pythonf
'''
Script to read in continuous data from 3 sensors, rotate, and calculate
PSD probability density functions. Uses two or three sample rates.
Has been tested with 500 and 1sps, 200 and 1sps, 100 and 1sps

Requires Obspy

Sample data available on;
https://www.cloud.guralp.com/index.php/s/HivF4AtFxxZxXx5?path=%2F

The sample data is from 3 x Guralp 3T and 3 x Guralp Affinity
The resp text files are in the resps directry
S. Hicks, University of Southampton, May-July 2017
S. Goessen, Guralp Systems, November 2019
'''

from self_noise_pdf import SelfNoise
from rotateFunctions import rotateZaxis, rotateNaxis, rotateEaxis
from measureRotation import rotateAll
from firstRotate import rotatefirst
from obspy.core import Stream, UTCDateTime, read
from obspy import read_inventory
import os


pwd = os.getcwd()

'''
file format should be in 'serialnumber_az4*.msd' in a directory in daylist.txt
    serialnumber = The varible 'sensors' defined below
    z = z,n,e depending on channel
    4 = 0 or 4, 4 for the low sample rate, 0 for the higher sample rate
    * = Can be anything, day hour, minute for example
'''
path = r'c:\data' # Path to waveform directorys by day
pathRESULTS = r'c:\RESULTS' # Path to write results
sensors = ['56C9', '5692', '5750'] # Sensors to analyse must match SEED station name
components = ['Z','N','E']  # Only used for reading resp files below
sampling_ratesFR = [4, 0] # Only used for reading resp files below

dless = []
for n, sensor in enumerate(sensors):
    for n1, comp in enumerate(components):
            for n2, sps in enumerate(sampling_ratesFR):
                dless += read_inventory(r'{0}\resps\{1}_a{2}{3}.resp'
                                        .format(path,sensor,comp,sps))


sensor_model = '3T_360s-50Hz + Affinity'  # String describing sensor
daylistfile = r'{0}\daylist.txt'.format(pwd) # File containing list of
                                             # days/directorys format = YYYYMMDD


ppsd_length = (16320, 4600) # Number of SECONDS to use per psd
sampling_rates = [1, 100] # Sample rates (minimum 2, maximum 3)
components = ['Z','N','E'] # Used to identify differnt resp files for each comp
dBmax = -120 # Top of output graph
dBmin = -200 # Bottom of output graph


# The following section is for the reading in the resp files.
# This will need to be mofified.




if not os.path.exists(pathRESULTS):
    os.makedirs(pathRESULTS)

# Set up self-noise function
SNZ = SelfNoise(sampling_rates=sampling_rates, path=pathRESULTS,
                db_bins=(dBmin, dBmax, 1.0), ppsd_length=ppsd_length)

SNN = SelfNoise(sampling_rates=sampling_rates, path=pathRESULTS,
                db_bins=(dBmin, dBmax, 1.0), ppsd_length=ppsd_length)
                
SNE = SelfNoise(sampling_rates=sampling_rates, path=pathRESULTS,
                db_bins=(dBmin, dBmax, 1.0), ppsd_length=ppsd_length)

def removeResponse(streamIn , sensor):
    '''
    Function removes response from time series using Obspy
    You can modify the stream station, network, location to match the resp file
    Returns modifed stream.
    '''
    streamIn.merge()
    streamIn[0].stats.station = 'A'
    streamIn[0].stats.network = sensor
    #print(streamIn)
    streamIn.remove_response(dless) #Obspy function removing sensor response
    return streamIn

def applyRotation(sensor, rot_ang, day):
    '''
    Function Reads in the all the data from day directory and applies rotation.
    Returns 6 streams low and high sample rates.
    '''    
    stLowZ = read(r'{0}\{1}\{2}_az4*.msd'.format(path, day, sensor))
    stLowE = read(r'{0}\{1}\{2}_ae4*.msd'.format(path, day, sensor))
    stLowN = read(r'{0}\{1}\{2}_an4*.msd'.format(path, day, sensor))
    
    stHighZ = read(r'{0}\{1}\{2}_az0*.msd'.format(path, day, sensor))
    stHighE = read(r'{0}\{1}\{2}_ae0*.msd'.format(path, day, sensor))
    stHighN = read(r'{0}\{1}\{2}_an0*.msd'.format(path, day, sensor))

    print('Removing response from low rate streams on sensor ', sensor)
    stLowZ =  removeResponse(stLowZ,sensor)
    stLowE =  removeResponse(stLowE,sensor)
    stLowN =  removeResponse(stLowN,sensor)
    
    print('Removing response from High rate streams on sensor ', sensor)
    stHighZ = removeResponse(stHighZ,sensor)
    stHighE = removeResponse(stHighE,sensor)
    stHighN = removeResponse(stHighN,sensor)

    print('Applying rotation to low rate channels on sensor ', sensor)
    stLowZresult = rotateZaxis(stLowE,stLowN,stLowZ,rot_ang[0],rot_ang[1])
    stLowNresult = rotateNaxis(stLowE,stLowN,stLowZ,rot_ang[2],rot_ang[3])
    stLowEresult = rotateEaxis(stLowE,stLowN,stLowZ,rot_ang[4],rot_ang[5])
    
    print('Applying rotation to high rate channels on sensor ', sensor)
    stHighZresult = rotateZaxis(stHighE,stHighN,stHighZ,rot_ang[0],rot_ang[1])
    stHighNresult = rotateNaxis(stHighE,stHighN,stHighZ,rot_ang[2],rot_ang[3])
    stHighEresult = rotateEaxis(stHighE,stHighN,stHighZ,rot_ang[4],rot_ang[5])
    
    return (stLowZresult,stLowNresult,stLowEresult, 
           stHighZresult,stHighNresult,stHighEresult)

def appendX(in1,in2,in3):
    x = []
    x.append(in1)
    x.append(in2)
    x.append(in3)
    return x

with open(daylistfile) as f:  #Open daylist file and read in the first line.
    day = f.readline()

day = day[:8]

print('Read in low sample rate data for day {}'.format(day))
# Read in ONLY low sample rate data for measuring the rotation
stLowZRef = read(r'{0}\{1}\{2}_az4*.msd'.format(path,day,sensors[0]))
stLowERef = read(r'{0}\{1}\{2}_ae4*.msd'.format(path,day,sensors[0]))
stLowNRef = read(r'{0}\{1}\{2}_an4*.msd'.format(path,day,sensors[0]))
stLowZSen1 = read(r'{0}\{1}\{2}_az4*.msd'.format(path,day,sensors[1]))
stLowESen1 = read(r'{0}\{1}\{2}_ae4*.msd'.format(path,day,sensors[1]))
stLowNSen1 = read(r'{0}\{1}\{2}_an4*.msd'.format(path,day,sensors[1]))
stLowZSen2 = read(r'{0}\{1}\{2}_az4*.msd'.format(path,day,sensors[2]))
stLowESen2 = read(r'{0}\{1}\{2}_ae4*.msd'.format(path,day,sensors[2]))
stLowNSen2 = read(r'{0}\{1}\{2}_an4*.msd'.format(path,day,sensors[2]))

# Remove response from low sample rate data
stLowZRef = removeResponse(stLowZRef,sensors[0])
stLowERef = removeResponse(stLowERef,sensors[0])
stLowNRef = removeResponse(stLowNRef,sensors[0])
stLowZSen1 = removeResponse(stLowZSen1,sensors[1])
stLowESen1 = removeResponse(stLowESen1,sensors[1])
stLowNSen1 = removeResponse(stLowNSen1,sensors[1])
stLowZSen2 = removeResponse(stLowZSen2,sensors[2])
stLowESen2 = removeResponse(stLowESen2,sensors[2])
stLowNSen2 = removeResponse(stLowNSen2,sensors[2])

print('Now measuring rotation....')

sen0RotRes = [0, 0, 0, 0, 0, 0]
'''
The directly below (currently commented out) can rotate the first (sen0) 
(reference sensor) to find the Minimum noise
The Theory being if vertical will be most vertical when it is measuring the
lowest noise.
Not being used at the moment as it is not conventional
'''
#firstRotateResult1, firstRotateResult2 = rotatefirst(stLowZRef,stLowNRef, stLowERef)
#stLowZRef = rotateZaxis(stLowERef, stLowNRef, stLowZRef, firstRotateResult1, firstRotateResult2)
#sen0RotRes = [firstRotateResult1, firstRotateResult2, 0, 0, 0, 0]

sen1RotRes = rotateAll(stLowZRef, stLowNRef, stLowERef,
                             stLowZSen1, stLowNSen1, stLowESen1)
sen2RotRes = rotateAll(stLowZRef, stLowNRef, stLowERef,
                             stLowZSen2, stLowNSen2, stLowESen2)
a = ' rotated by '
b = ' degrees on the '
print('{0} Z  {1}{2:.6f}{3}N/S axis'.format(sensors[0],a,sen0RotRes[0],b))
print('{0} Z  {1}{2:.6f}{3}E/W axis'.format(sensors[0],a,sen0RotRes[1],b))
print('{0} NS{1}{2:.6f}{3}horizontal axis'.format(sensors[0],a,sen0RotRes[2],b))
print('{0} NS{1}{2:.6f}{3}vertical axis'.format(sensors[0],a,sen0RotRes[3],b))
print('{0} EW{1}{2:.6f}{3}horizontal axis'.format(sensors[0],a,sen0RotRes[4],b))
print('{0} EW{1}{2:.6f}{3}vertical axis'.format(sensors[0],a,sen0RotRes[5],b))
print('')
print('{0} Z  {1}{2:.6f}{3}N/S axis'.format(sensors[1],a,sen1RotRes[0],b))
print('{0} Z  {1}{2:.6f}{3}E/W axis'.format(sensors[1],a,sen1RotRes[1],b))
print('{0} NS{1}{2:.6f}{3}horizontal axis'.format(sensors[1],a,sen1RotRes[2],b))
print('{0} NS{1}{2:.6f}{3}vertical axis'.format(sensors[1],a,sen1RotRes[3],b))
print('{0} EW{1}{2:.6f}{3}horizontal axis'.format(sensors[1],a,sen1RotRes[4],b))
print('{0} EW{1}{2:.6f}{3}vertical axis'.format(sensors[1],a,sen1RotRes[5],b))
print('')
print('{0} Z  {1}{2:.6f}{3}N/S axis'.format(sensors[2],a,sen2RotRes[0],b))
print('{0} Z  {1}{2:.6f}{3}E/W axis'.format(sensors[2],a,sen2RotRes[1],b))
print('{0} NS{1}{2:.6f}{3}horizontal axis'.format(sensors[2],a,sen2RotRes[2],b))
print('{0} NS{1}{2:.6f}{3}vertical axis'.format(sensors[2],a,sen2RotRes[3],b))
print('{0} EW{1}{2:.6f}{3}horizontal axis'.format(sensors[2],a,sen2RotRes[4],b))
print('{0} EW{1}{2:.6f}{3}vertical axis'.format(sensors[2],a,sen2RotRes[5],b))
print('')


# Loop over each line(day) in daylistfile and apply rotation
# then send data to self noise function.
daylist = []
dates = open((daylistfile), 'r')
for line in dates:
    day = line.split()[0]
    daylist.append(day)
    print('Now processing data from : {}'.format(day))
    LZ1,LN1,LE1,HZ1,HN1,HE1 = applyRotation(sensors[0],sen0RotRes, day)
    LZ2,LN2,LE2,HZ2,HN2,HE2 = applyRotation(sensors[1],sen1RotRes, day)
    LZ3,LN3,LE3,HZ3,HN3,HE3 = applyRotation(sensors[2],sen2RotRes, day)
    
    stLowZ_all = appendX(LZ1, LZ2, LZ3) # Merge verticals into one list
    stLowN_all = appendX(LN1, LN2, LN3) # Merge North/Souths into one list 
    stLowE_all = appendX(LE1, LE2, LE3) # Merge East/Wests into one list 
    
    stHighZ_all = appendX(HZ1, HZ2, HZ3) # Merge verticals into one list 
    stHighN_all = appendX(HN1, HN2, HN3) # Merge North/Souths into one list
    stHighE_all = appendX(HE1, HE2, HE3) # Merge East/Wests into one list

    SNZ.SNadd([stLowZ_all, stHighZ_all]) #Push data to Self-noise function
    SNN.SNadd([stLowN_all, stHighN_all]) #Push data to Self-noise function
    SNE.SNadd([stLowE_all, stHighE_all]) #Push data to Self-noise function

    # Make temporary plot after each day, this file will appear in the results
    # directory and good for checking all is working OK whilst code is running

    SNZ.SNplot(percentiles=[], cmap='hot_r', show_mode=False,
              sensors=sensors, sampling_rates=sampling_rates,
              sensor_model='{0}Vertical'.format(sensor_model),
              start_date=daylist[0], end_date=daylist[-1])
    SNN.SNplot(percentiles=[], cmap='hot_r', show_mode=False,
              sensors=sensors, sampling_rates=sampling_rates,
              sensor_model='{0}NorthSouth'.format(sensor_model),
              start_date=daylist[0], end_date=daylist[-1])
    SNE.SNplot(percentiles=[], cmap='hot_r', show_mode=False,
              sensors=sensors, sampling_rates=sampling_rates,
              sensor_model='{0}EastWest'.format(sensor_model),
              start_date=daylist[0], end_date=daylist[-1])
    print('done day ', day)
dates.close()

# Make final PDF plot
SNZ.SNplot(percentiles=[], cmap='hot_r', show_mode=True,
          sensors=sensors, sampling_rates=sampling_rates,
          sensor_model='{0} Vertical'.format(sensor_model),
          start_date=daylist[0], end_date=daylist[-1])

SNE.SNplot(percentiles=[], cmap='hot_r', show_mode=True,
          sensors=sensors, sampling_rates=sampling_rates,
          sensor_model='{0} NorthSouth'.format(sensor_model),
          start_date=daylist[0], end_date=daylist[-1])

SNE.SNplot(percentiles=[], cmap='hot_r', show_mode=True,
          sensors=sensors, sampling_rates=sampling_rates,
          sensor_model='{0} EastWest'.format(sensor_model),
          start_date=daylist[0], end_date=daylist[-1])
