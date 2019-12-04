# selfnoisePDF
# SELF-NOISE Probability Density Function

S. Hicks, University of Southampton, May-July 2017

S. Goessen, Guralp Systems, November 2019

This software can be used to evaluate the self-noise of a seismometer using 3 triaxial sensors.

The output is a probability density plot, of similar nature to the PPSD plot in the standard Obspy toolset. The difference being the Sleeman method has been applied to the 3 sensors, removing the common signal so only the self-noise of the sensor remains.

The software is designed to process large data sets of many days (Minimum 24 hours). It requires 2 or 3 seperate sample rates, allowing good resolution at both high and low frequncies.
There is a sample data; https://www.cloud.guralp.com/index.php/s/HivF4AtFxxZxXx5?path=%2F, by entering multiple lines in the daylist.txt file one can process multiple days.

Runs on Windows - will run on linux with modification to the filename format.

## Prerequisites:

Python 3.5.X

Obspy

# Example output:
![Example output](https://raw.githubusercontent.com/sgoessen/selfnoisePDF/master/3T_360s-50Hz%20%2B%20Affinity%20Vertical_5692_20190505_20190505.png)

## calc_selfnoise_pdfs.py
**********************

Main program to be executed.

3 lines the user will need to modify;
path = r'c:\data' 		# Path to waveform directorys by day, directorys here should be listed in daylist.txt
pathRESULTS = r'c:\RESULTS' 	# Path to write results
sensors = ['56C9', '5692', '5750'] # Sensors to analyse must match SEED station name

Starts by downloading sample data with the associated resp files.
Requires data from 3 x sensors, has been tested with miniseed. Requires associated resp file - can be modified to use dataless.

Reads in the first day/directory low sample rate only. Measures the angle at which the coherence is at a maximum using the function rotateAll in file measureRotation.py

Reads in the data from one day/directory at a time. Applies the rotation using the functions; rotateZaxis, rotateNaxis, rotateEaxis from the file rotateFunctions.py

For each day it then calculates the self-noise and produces a temp file in the results directory using class SelfNoise from file self_noise_pdf.py



## measureRotation.py
******************
This file used by calc_selfnoise_pdfs.py measures the rotation.
It takes the 3 components from 2 sensors and rotates the components of the second sensor independently for maximum coherence.
It returns the angle required to adjust for maximum coherence of the 3 components.
For example if the sensor is rotated 5 degrees clockwise and horizontally from the reference it will return 0 for the vertical, 5 for the north south and 5 for the east west.
Because they are done independently it provides an indication of non-orthogonality but this is not 100% accurate because orthogonality is assumed when applying rotation.


## rotateFunctions.py
******************
Takes all 3 axes data from a single sensor and rotates by the provided angles.
rotateZaxis(E,N,Z,angle1,angle2).
Angle 1 is the N/S axis for the rotateZaxis function (rotating the vertical)
Angle 2 is the E/W axis for the rotateZaxis function (rotating the vertical)

Angle 1 is the horizontal axis for the rotateNaxis function (rotating the north south)
Angle 2 is the vertical axis for the rotateNaxis function (rotating the north south)

Angle 1 is the horizontal axis for the rotateEaxis function (rotating the east west)
Angle 2 is the vertical axis for the rotateEaxis function (rotating the east west)

The output is the rotated data for the component specified by the function, ie. vertical data from the 'rotateZaxis'.


## daylist.txt
***********
This file contains a list of directories’ containing the data. Each directory should contain all the data for a single day. The example has the data for a 1 day from 3 x Guralp 3T with 3 x Guralp Affinity.


## firstRotate.py
### ************** EXPERIMENTAL **************  
Some triaxial seismometers can work at any angle. This code is intended to rotate the first (reference) sensor until it has the minimum noise on the vertical channel.
In a 'normal' vault installation it is expected that at 30 seconds and longer the vertical axis is the quietest.
input; rotatefirst(Z,N,E) where Z,N,E are the 3 components from a single sensor.
It returns the 2 angles to rotate the vertical for minimum noise.







