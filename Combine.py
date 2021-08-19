globals().clear()

import sys
import os
import pyrsktools
import itertools
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import pyproj
import matplotlib.pyplot as plt

from copy import copy, deepcopy
from scipy import signal
import gsw
import xarray as xr
from matplotlib import pyplot as plt
import glob
from datetime import datetime
from datetime import timedelta
from decimal import Decimal
import random
import pycnv


dest_dir = '/Users/tylerzhang/Desktop/Finished/'

files = os.listdir(dest_dir)  # list all the files in dest_dir

files = list(filter(lambda f: f.endswith('.DTA'), files)) # keep the csv files only by passing a list of files and filter out all item end with .DTA




Final_File = open('compiled.DTA' , 'w')

for i in range(len(files)):
    input_filename = str(dest_dir) + str(files[i])
    DTA_Data = open(input_filename , 'r')
    data_hold = DTA_Data.read()
    Final_File.write(data_hold)
    Final_File.write('\n')
    Final_File.write('\n')



