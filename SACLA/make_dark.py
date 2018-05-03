#Use to sum dark 'shots' for background subtraction
#Mathew Cherukara, APS, Argonne
#Usage python sorttimingcube.py scan_number csvfile 
import h5py
import tifffile as tiff
import sys
import os
import numpy as np
import csv
import numpy as np
from lima_pickroi import roi_selector

run_no=int(sys.argv[1])

f=h5py.File('/work/rharder/h5files/%d.h5' %run_no,'r')
all_tags=f['run_%d/detector_2d_1/' %run_no].keys()
print "Total shots", len(all_tags)

data=np.zeros((1024,512),float)
for st in all_tags[1:]:
 data_str='run_%d/detector_2d_1/%s/detector_data' %(run_no,st)
 print data_str
 data+=f[data_str].value #This is hopefully a 2D array
#tiff.imsave('dark.tiff' %run_no, b[:d4dims[0]-1,:,:])

data2=data.astype(np.int32)
tiff.imsave('dark.tiff', data2[:,:])
