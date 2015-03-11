# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 15:13:03 2015

@author: Antoine
"""

import pandas as pd
import numpy as np

csv_name = 'noname.csv'

all_drivers = np.loadtxt('../data/drivers.txt', dtype=np.uint)

for driver_no in all_drivers:
    input_file = '../data/drivers/'+str(driver_no)+'/'+csv_name
    output_file = '../drivers/'+str(driver_no)+'/'+csv_name

    df = pd.read_csv(input_file, index_col=0)
    df['targ'] = 1
    labels = df['targ']
    df = df.drop('targ', 1)

    with open(output_file, 'w') as f:
        i = -1
        for row_index, row in df.iterrows():
            i += 1
            entry = str(labels[i]) + " '" + row_index + ' |'
            for col, value in row.iteritems():
                entry += col + ':' + str(value)
            f.write(entry + '\n')