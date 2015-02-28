# -*- coding: utf-8 -*-
"""
Created on Sun Feb 22 21:56:04 2015

@author: Antoine
"""

import numpy as np
import os
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import pylab as plt # For visualisation

def file_to_array(file_name):
    f = open(file_name,'r')
    f.readline()

    x, y = [], []
    for line in f:
        field = line.split(',')
        x.append(float(field[0]))
        y.append(float(field[1]))
    return [np.array(x), np.array(y)]


def trip_to_features(positions):
    """
    Here are my ideas for the features

    The speed should not matter because the trips are not on the same kind of road.
    The acceleration should count. A driver who accelerates and breaks strongly can be distinguished.
    The speed in turns should count. A driver who goes fast in turns is more dangerous.
    The curvature maybe useful to determine if the driver prefers to take small roads or highway.
    The standard deviation of the behaviour. A driver might not have a stable driving style or may be several drivers for the same car (don't know).
    The global shape of the trip. Some people may prefer go in straight lines, other make a detour to take express roads, other go to places they know...
    The number of stops, and the duration of stops can be useful.
    """
    features = {}
    position_x, position_y = positions[0], positions[1]
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

    # Features based on acceleration
    features['min_acc'] = np.nanmin(acceleration)
    features['max_acc'] = np.nanmax(acceleration)
    features['mean_acc'] = np.nanmean(acceleration)
    features['std_acc'] = np.nanstd(acceleration)

    # Feature based on curvature
    features['min_curv'] = np.nanmin(curvature)
    features['max_curv'] = np.nanmax(curvature)
    features['mean_curv'] = np.nanmean(curvature)
    features['std_curv'] = np.nanstd(curvature)

    # Features based on the speed in turns
    #features['speedturn_min'] = np.nanmin(speed_turn)
    features['speedturn_max'] = np.nanmax(speed_turn)
    features['speedturn_mean'] = np.nanmean(speed_turn)
    features['speedturn_std'] = np.nanstd(speed_turn)

    # Features based on the shape of the trip
    features['dist'] = distance
    features['detour_1'] = (distance / manhattan_distance) if manhattan_distance > 0 else 0. # detour relative to Manhattan distance
    features['detour_2'] = (distance / euclidian_distance) if euclidian_distance > 0 else 0. # detour relative to Euclidian distance

    # Features based on Newton forces
    features['centrifuge_mean'] = np.nanmean(velocity**2 * curvature) # v²/r

    # Features based on stops
    features['stops_n'] = len(stops)
    features['stops_duration'] = np.mean(stops_durations) if len(stops) > 0 else 0

    return features


def file_to_features(file):
    return trip_to_features(file_to_array(file))

def directory_to_data_set(directory):
    files = os.listdir(directory)
    features = file_to_features(directory + files[0]).keys()

    dataset = np.zeros((len(files), len(features)))

    for i,file in enumerate(files):
        kv_pairs = file_to_features(directory + file)
        for j,key in enumerate(features):
            dataset[i,j] = kv_pairs[key]

    return list(features), dataset, [file[:-4] for file in files]



def driver_analysis(driver_directory):
    """
        Returns the probability (hard assignments at the moment) that the driver
        is actually doing each trip in the directory.
    """
    feature_names, dataset, trip_names = directory_to_data_set(driver_directory)

    # Apply PCA keeping 70% of the variance (can be changed if more features)
    reduced_dataset = PCA(0.7).fit_transform(dataset)
    # Normalise data (not sure it is necessary)
    reduced_dataset = StandardScaler().fit_transform(reduced_dataset)
    # Clustering
    labels = DBSCAN(eps=0.9, min_samples=1).fit_predict(reduced_dataset)
    # Visualisation in 1D
#    plt.hist(reduced_dataset)
#    plt.figure()
#    plt.hist(labels)

    # Get number of drivers
    clusters = np.unique(labels)
    # Get cluster sizes
    cluster_sizes = np.zeros((len(clusters)))
    for i,label in enumerate(clusters):
        cluster_sizes[i] = np.sum(labels == label)
    # Cluster no. of the main driver
    main_driver = clusters[np.argmax(cluster_sizes)]
    # "Probabilities" is here just cluster assignment to the main driver
    lr = LogisticRegression()
    lr.fit(reduced_dataset, labels == main_driver)
    probabilities = lr.predict_proba(reduced_dataset)

    return trip_names, probabilities[:,1]


if __name__ == '__main__':
	# Ignore warning when dividing by zero
    np.seterr(divide='ignore', invalid='ignore')

    drivers_directory = '../data/drivers/'
    submission_file = '../data/submission.csv'

    #drivers = [directory[0][len(drivers_directory):] for directory in os.walk(drivers_directory)][1:]
    drivers = np.loadtxt('../data/drivers.txt', dtype=np.uint) # improved caching
    drivers = drivers[:5] # subsample

    f = open(submission_file, 'w')
    f.write('driver_trip,prob\n')

    for i,driver in enumerate(drivers):
        print('%4d/%d - Analysing driver no.%u' % (i, len(drivers), driver))
        trips, probabilities = driver_analysis(drivers_directory + str(driver) + '/')
        for j,trip in enumerate(trips):
            f.write(str(driver) + '_' + trip + ',' + str(1*probabilities[j]) + '\n')
    f.close()
