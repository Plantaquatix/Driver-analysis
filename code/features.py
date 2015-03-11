# -*- coding: utf-8 -*-
"""
Created on Sun Feb 22 21:56:04 2015

@author: Antoine
"""

import numpy as np
import os
import pandas as pd
import random

def file_to_array(file_name):
    f = open(file_name,'r')
    f.readline()

    x, y = [], []
    for line in f:
        field = line.split(',')
        x.append(float(field[0]))
        y.append(float(field[1]))
    return [np.array(x), np.array(y)]


def smooth(x,window_len=5,window='hanning'): # http://wiki.scipy.org/Cookbook/SignalSmooth
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal

    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    see also:

    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """
    if x.ndim != 1:
        raise(ValueError, "smooth only accepts 1 dimension arrays.")
    if x.size < window_len:
        raise(ValueError, "Input vector needs to be bigger than window size.")
    if window_len<3:
        return x
    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise(ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")
    s=np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')
    y=np.convolve(w/w.sum(),s,mode='valid')
    return y

def trip_to_features(positions):
    """
    Here are my ideas for the features

    The acceleration should count. A driver who accelerates and breaks strongly can be distinguished.
    The speed in turns should count. A driver who goes fast in turns is more dangerous.
    The curvature maybe useful to determine if the driver prefers to take small roads or highway.
    The standard deviation of the behaviour. A driver might not have a stable driving style or may be several drivers for the same car (don't know).
    The global shape of the trip. Some people may prefer go in straight lines, other make a detour to take express roads, other go to places they know...
    The number of stops, and the duration of stops can be useful.
    """
    features = {}
    position_x, position_y = positions[0], positions[1]
    position_x = smooth(position_x)
    position_y = smooth(position_y)

    departure = np.array([position_x[0], position_y[0]])
    arrival = np.array([position_x[-1], position_y[-1]])
    delta_x, delta_y = np.diff(position_x), np.diff(position_y)

    distance = np.sum(np.sqrt(delta_x**2+delta_y**2))
    manhattan_distance = np.linalg.norm(arrival - departure, ord=1)
    euclidian_distance = np.linalg.norm(arrival - departure, ord=2)

    velocity_x, velocity_y = np.gradient(position_x), np.gradient(position_y)
    velocity = np.sqrt(velocity_x**2 + velocity_y**2)

    acceleration_x, acceleration_y = np.gradient(velocity_x), np.gradient(velocity_y)
    acceleration = np.sqrt(acceleration_x**2 + acceleration_y**2)

    curvature = (velocity_x*acceleration_y - velocity_y*acceleration_x) / velocity**3
    curvature[np.isinf(curvature)] = np.nan # Replace Inf by NaN if no velocity
    curvature = abs(curvature)

    centrifuge = velocity**2 * curvature

    speed_turn = velocity * curvature # speed / ray of curvature

    # Compute stops features
    stops = []
    stops_durations = []
    stopped = False
    for i,v_t in enumerate(velocity):
        if v_t < 0.1:
            if stopped == True:
                stops_durations[-1] += 1
            else:
                stops.append(i)
                stops_durations.append(1)
                stopped = True
        else:
            stopped = False

    #############################################
    ### Features based on the driver attitude ###
    #############################################

    # Features based on speed
    features['speed_min'] = np.nanmin(velocity)
    features['speed_max'] = np.nanmax(velocity)
    features['speed_mean'] = np.nanmean(velocity)
    features['speed_std'] = np.nanstd(velocity)
    for i in np.arange(5, 105, 5):
        features['speed_q_'+str(i)] = np.percentile(velocity, i)

    # Features based on acceleration
    features['acc_min'] = np.nanmin(acceleration)
    features['acc_max'] = np.nanmax(acceleration)
    features['acc_mean'] = np.nanmean(acceleration)
    features['acc_std'] = np.nanstd(acceleration)
    for i in np.arange(5, 105, 5):
        features['acc_q_'+str(i)] = np.percentile(acceleration, i)

    # Feature based on curvature
    features['curv_min'] = np.nanmin(curvature)
    features['curv_max'] = np.nanmax(curvature)
    features['curv_mean'] = np.nanmean(curvature)
    features['curv_std'] = np.nanstd(curvature)

    # Features based on the speed in turns
    features['speedturn_min'] = np.nanmin(speed_turn)
    features['speedturn_max'] = np.nanmax(speed_turn)
    features['speedturn_mean'] = np.nanmean(speed_turn)
    features['speedturn_std'] = np.nanstd(speed_turn)

    # Features based on Newton forces
    features['centrifuge_mean'] = np.nanmean(centrifuge) # v²/r
    features['centrifuge_std'] = np.nanstd(centrifuge)

    #############################################
    ### Features based on the trip properties ###
    #############################################

    # Features based on the shape of the trip
    features['distance'] = distance
    features['detour_manhattan'] = (distance / manhattan_distance) if manhattan_distance > 0 else 0. # detour relative to Manhattan distance
    features['detour_euclidian'] = (distance / euclidian_distance) if euclidian_distance > 0 else 0. # detour relative to Euclidian distance

    # Duration of the trip
    features['duration'] = len(position_x)

    # Features based on stops
    features['stops_n'] = len(stops)
    features['stops_duration'] = np.mean(stops_durations) if len(stops) > 0 else 0

    return features

def file_to_features(file):
    return trip_to_features(file_to_array(file))

def to_pandas():
    all_drivers = get_all_drivers()
    row_list = []
    row_indices = []

    for driver in all_drivers:
        print('Loading driver '+str(driver))
        files = os.listdir('../data/drivers/'+str(driver)+'/')
        for file in files:
            trip_no = file[:-4] # remove .csv
            row_indices.append(str(driver)+'_'+str(trip_no))
            values = file_to_features('../data/drivers/'+str(driver)+'/'+file)
#            values['#driver'] = driver
#            values['#trip'] = trip_no
            row_list.append(values)

    df = pd.DataFrame(row_list, index=row_indices)
    # Incorporate trip matching
    df['trip_id'] = get_trips_ids()
    return df

def to_csv(file_name):
    to_pandas().to_csv(file_name, index_label='driver_trip')

def get_all_drivers():
    return np.loadtxt('../data/drivers.txt', dtype=np.uint)[:3]


def get_driver_trips_ids(driver):
    m=np.loadtxt('../data/mats/'+str(int(driver))+'_similarityMatrix.csv', delimiter=',')

    trip_ids = []
    for i in np.arange(1,m.shape[0]):
        b_found = False
        for j in np.arange(i):
            if m[i,j] == 1:
                trip_ids.append(trip_ids[j])
                b_found = True
                break
        if b_found == False:
            trip_ids.append(str(driver)+'_'+str(i))
    return pd.DataFrame(trip_ids, index=np.array([str(driver)+'_'+str(i) for i in np.arange(1,m.shape[0])]))

def get_trips_ids(all_drivers=None):
    if all_drivers == None:
        all_drivers = get_all_drivers()

    trips_ids = pd.DataFrame()
    for driver in all_drivers:
        trips_ids = trips_ids.append(get_driver_trips_ids(driver))
    return trips_ids

def get_all_trips_from_driver(df):

    for key in df.index.values:
        [driver, trip] = key.split('_')


# Ignore warning when dividing by zero
np.seterr(divide='ignore', invalid='ignore')

if __name__ == '__main__':
    #to_csv('../data/Dataset.csv')
    print(to_pandas())
    #to_vw()
