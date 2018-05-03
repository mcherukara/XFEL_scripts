#Use to sort shots, normalize to diode and write to tiff for delay scans and rocking curves
#Mathew Cherukara, APS, Argonne
#Usage python sorttimingcube.py scan_number csvfile 
import h5py
import tifffile as tiff
import sys
sys.path.append('/Volumes/NTFS/Online_analysis/Apr2017/src')
import os
import numpy as np
import csv
import numpy as np
from lima_pickroi import roi_selector
from v5_delay import time_analysis
from rocking import rocking_analysis

run_type=sys.argv[1]
run_no=int(sys.argv[2])
nshots=int(sys.argv[3])
mult_factor=nshots/480.0 #Background has 480 shots

if(run_type=='delay'): col=4
elif(run_type=='rocking'): col=5
else: 
 print "Options are 'delay' or 'rocking'"
 exit()

f=h5py.File('/Volumes/NTFS/h5files/%d.h5' %run_no,'r')
#f=h5py.File('../%d_2.h5' %run_no,'r')
light_str='run_%d/event_info/acc/accelerator_status' %run_no
lstat=f[light_str].value #Light status
diode_str1='run_%d/event_info/bl_3/eh_2/photodiode/photodiode_user_4_in_volt' %run_no
diode_str2='run_%d/event_info/bl_3/eh_2/photodiode/photodiode_user_5_in_volt' %run_no
ipmvas=(f[diode_str1].value+f[diode_str2].value)/2 #Average of 2 photodiodes next to each other

img_size=np.array([1024,512])
thresh=5 #Threshold each shot, lesson from SLAC

#Read csv file for shots corresponding to each motor position
#if len(sys.argv[2])==6:
#  csvfile='/xdaq/work/share/Harder_20170403/scan_output/%d.csv' %run_no
#else:
csv_fname=sys.argv[2]
csvfile='/Volumes/NTFS/Online_analysis/Apr2017/xdaq/scan_output/%s' %csv_fname[2:]

#csvfile='/xdaq/work/share/Harder_20170403/scan_output/scan_x1.csv' %run_no
#csvfile='csvfiles/newformat.csv'
ifile=open(csvfile,'r')
reader=csv.reader(ifile)
shots=[]
steps=[]

next(reader, None) #skip header
for row in reader:
  shots.append(row[1]) #Copy the shot numbers and delay, don't need motor positions
  steps.append(row[col]) #Delay

init_tag=long(shots[0]) #Find the first and last shot tags
end_tag=long(shots[-1]) #Find the first and last shot tags
print init_tag, end_tag


#Throw out super bright flashes by counting photons in a small roi in a corner
#def roi(data):
#  tmp2=np.sum(np.sum(data[:10,:10]))
#  if(tmp2>1000):
#   print "flash check failed"
#   return 0
#  else:
#   return 1


#Think this is to sort cause Silke wrote in parallel
#all_pos=f['scan/var0'].value
#motor_pos, motor_idx =np.unique(all_pos, return_inverse=True) #Scan positions
#steps=f['scan/varStep'].value


#Store output array
npts=len(shots)/nshots
print "Total points:", npts
data3=np.zeros((npts,img_size[0],img_size[1]),float)

print data3.shape
mpi=0 
ipmsum=np.zeros(npts)

k=0
pt_ctr=0
rejects=0
for j in shots: #Iterate over shots for that point-ONLY EVEN SHOTS
   if(k%nshots==0 and k!=0):
    pt_ctr+=1
    print "Next point is:", pt_ctr+1
    print "Total shots:", k+1
   data_str='run_%d/detector_2d_1/tag_%s/detector_data' %(run_no,j)
   chk=data_str in f #Check if the h5 path exists
   if(chk):
    data=f[data_str].value #This is hopefully a 2D array
#    print lstat[k]
#    if(lstat[k] and roi(data)): #Only sum shots that have x-rays and are not bright flashes
    if(lstat[k]): #Only sum shots that have x-rays
     if(ipmvas[k]<1.0): #Musn't cross 1ev 
      data=np.where(data<thresh,0,data) #Threshold all shots, lesson from SLAC
      data3[pt_ctr,:,:]+=data[:,:]
      ipmsum[pt_ctr]+=ipmvas[k]
     else:
      rejects+=1
      print "Shot rejected, rejects so far:", rejects
#     print ipmsum[i]
    k+=1 #Update counter if shot exists whether used or no
print "Shots read:", pt_ctr+1
print "Scan points:", k 

#Normalize over diode, use average over point and not per shot
#for j in range(npts):
# if(ipmsum[j]>0):
#  data3[j,:,:]= 100*data3[j,:,:]/ipmsum[j]

#Read dark
dark=tiff.imread('dark.tiff')
for i in range(npts):
 data3[i,:,:]-=mult_factor*dark #Subtract background taking number of exposures into account

data4=data3.astype(np.int32)
d4dims=data4.shape
tiff.imsave('full_image.tiff', data4[:,:,:])


#Enter with much fanfare, Steven Leake's Python ROI selector
central_slice=d4dims[0]/2 #Time is first dimension
x1,x2=roi_selector(data4[central_slice,:,:])
print x1,x2
b=data4[:,x1[1]:x2[1],x1[0]:x2[0]] #Ordering is a bit weird
d4dims=b.shape
print "Cropped image is:", d4dims

if(run_type=='delay'):
 tiff.imsave('tiffs/timing_tiffs/run%d.tiff' %run_no, b[:,:,:])

 #Call the analysis function
 DelayPulsToPico = (1e-3)*20/3 #6.67 femtoseconds per pulse
 init_step=int(steps[0])*DelayPulsToPico #In ps
 step_size=(int(steps[nshots])-int(steps[0]))*DelayPulsToPico #In ps
 print "First time step and time step size", init_step, step_size
 time_analysis(b,step_size,init_step)

 if(os.path.isdir('tiffs/delay_%d' %run_no)):
  os.system('rm -r tiffs/delay_%d' %run_no)
 os.system('cp -r tiffs/plots_of_time_scans tiffs/delay_%d' %run_no)

else:
 if(not os.path.isdir('tiffs/reconstructions/run%d' %run_no)):
  os.mkdir('tiffs/reconstructions/run%d' %run_no)
 tiff.imsave('tiffs/reconstructions/run%d/tmp.tiff' %run_no, b[:,:,:])

 if(os.path.isdir('tiffs/rocking_%d' %run_no)):
  os.system('rm -r tiffs/rocking_%d' %run_no)
 os.system('cp -r tiffs/plots_of_rocking_curves tiffs/rocking_%d' %run_no)
 init_step=int(steps[0])
 step_size=(int(steps[nshots])-int(steps[0]))
 rocking_analysis(b,step_size,init_step)

#Phase it
# os.chdir('tiffs/reconstructions/run%d' %run_no)
# os.system('cp ../simple.m .')
# print "Starting reconstruction"
# os.system('matlab -nosplash -nodisplay -r "clear;simple;quit;">run.out')
# os.chdir('~/Apr2017/')

