#!/usr/bin/env pythonf
'''
3 functions that take 2 provided angles and rotate the component around both
angles. Therefore requires all 3 components as an imput as well as two angles.

Requires Obspy

S. Hicks, University of Southampton, May-July 2017
S. Goessen, Guralp Systems, April 2019
'''

from math import cos, sin
from obspy.core import Trace, Stream
import numpy as np



def rotateZaxis(e, n, z, rot_angle_n, rot_angle_e):
    '''
    Python function to rotate the vertical component accross both
    horizontal axes. First rotate about east, followed by north.
    Returns the modifed trace.
    '''
    Tr = Trace()
    # Get traces
    e_data = np.array(e[0].data, dtype='float64')
    n_data = np.array(n[0].data, dtype='float64')
    z_data = np.array(z[0].data, dtype='float64')

    # Rotate about east
    z_rot_1 = ((np.cos(np.arctan2(n_data, z_data) + np.deg2rad(rot_angle_n))) *
               np.sqrt(z_data**2 + n_data**2))

    # Rotate about north
    z_rot_2 = ((np.cos(np.arctan2(e_data, z_rot_1) + np.deg2rad(rot_angle_e))) *
               np.sqrt(z_rot_1**2 + e_data**2))

    # Get rotated vertical component back into obspy stream object
    Tr = Trace(data=z_rot_2, header=z[0].stats)
    Z_rot = Stream(traces=[Tr])

    return Z_rot
	
def rotateNaxis(e, n, z, rot_angle_n1, rot_angle_v1):
    '''
    Python function to rotate the north/south component accross both
    horizontal and vertical axes. First rotate about horizontal,
    followed by vertical.
    Returns the modifed trace.
    '''
    Tr = Trace()
    # Get traces and convert to np array
    e_data = np.array(e[0].data, dtype='float64')
    n_data = np.array(n[0].data, dtype='float64')
    z_data = np.array(z[0].data, dtype='float64')

    # Rotate along the horizontal azis
    N_rot_1 = ((np.cos(np.arctan2(e_data, n_data) + np.deg2rad(rot_angle_n1)))*
               np.sqrt(e_data**2 + n_data**2))

    #Rotate the horizontal along the vertical axis
    N_rot_2 = ((np.cos(np.arctan2(z_data, N_rot_1) + np.deg2rad(rot_angle_v1)))*
               np.sqrt(N_rot_1**2 + z_data**2))

    # Get rotated vertical component back into obspy stream object
    Tr = Trace(data=N_rot_2, header=n[0].stats)
    N_rot = Stream(traces=[Tr])

    return N_rot

def rotateEaxis(e, n, z, rot_angle_n2, rot_angle_v2):
    '''
    Python function to rotate the north/south component accross both
    horizontal and vertical axes. First rotate about horizontal,
    followed by vertical.
    Returns the modifed trace.
    '''
    Tr = Trace()
    # Get traces and convert to np array
    e_data = np.array(e[0].data, dtype='float64')
    n_data = np.array(n[0].data, dtype='float64')
    z_data = np.array(z[0].data, dtype='float64')

    # Rotate horizontal
    E_rot_1 = ((np.sin(np.arctan2(e_data, n_data) + np.deg2rad(rot_angle_n2)))*
               np.sqrt(e_data**2 + n_data**2))

    # Rotate the horizontal along the vertical axis
    E_rot_2 = ((np.sin(np.arctan2(E_rot_1, z_data) + np.deg2rad(rot_angle_v2)))*
               np.sqrt(E_rot_1 ** 2 + z_data ** 2))

    # Get rotated vertical component back into obspy stream object
    Tr = Trace(data=E_rot_2, header=e[0].stats)
    E_rot = Stream(traces=[Tr])

    return E_rot