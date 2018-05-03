import h5py
import tifffile as tiff
import sys
import os
import numpy as np

run_no=sys.argv[1]

f=h5py.File('ldat_xppm0416_Run%s.h5' %run_no)

#Read Tim's list of CSPAD array rotations
ifile=open('CSPADangle.txt', 'r')
tmp=ifile.readline()
rotvals=(tmp.split(','))
rotvals2=map(int, rotvals)

data=f['cspad/ROI'].value
print data.shape
thresh=25
data2=np.where(data<thresh,0,data)

dims=data2.shape
tmp2=np.sum(data2[:,:10,:10],axis=2)
roi=np.sum(tmp2,axis=1)


all_pos=f['scan/var0'].value
motor_pos, motor_idx =np.unique(all_pos, return_inverse=True) #Scan positions
steps=f['scan/varStep'].value
lstat=f['lightStatus/xray'].value #Light
ipmvas=f['ipm2/sum'].value #Ipm


#Store output array
data3=np.zeros([len(motor_pos),dims[1],dims[2]],int)

print data3.shape
mpi=0 
ipmsum=np.zeros(len(motor_pos))
for i in range(dims[0]):
  if(lstat[i] and roi[i]<1000): #Only sum shots that have x-rays and are not flashes
   data3[motor_idx[i],:,:]+=data2[i,:,:]
   ipmsum[motor_idx[i]]+=ipmvas[i]

for j in range(len(motor_pos)):
 data3[j,:,:]= 100*data3[j,:,:]/ipmsum[j]

#Find number of 90 degree rotations
data4=data3.astype(np.int32)

panel=int(f['UserDataCfg/cspad_ROI_bound'].value[0,0]) #Panel number
angle=rotvals2[panel] #Map file from Tim
if(angle==90):nrot=1
elif(angle==-90):nrot=3
elif(angle==180 or angle==-180):nrot=2
else:nrot=0
data4=np.transpose(data4,(1,2,0)) #Move Z-axis to end
print data4.shape
data4=np.rot90(data4,nrot) #Rotate X,Y as required
print data4.shape
data4=np.transpose(data4,(2,0,1)) #Move Z-axis back to front
print data4.shape
d4dims=data4.shape
tiff.imsave('tmp.tiff', data4[:d4dims[0]-1,:,:])

os.system('mkdir ../scratch/phasing/run%s' %run_no)
os.system('cp tmp.tiff ../scratch/phasing/run%s' %run_no)
#os.chdir('/reg/d/psdm/xpp/xppm0416/scratch/phasing/run%s' %run_no)
#os.system('cp ../simple.m .')
#os.system('cp ../GA.m .')
#os.system('/reg/common/package/matlab/R2016a/bin/matlab -nosplash -nodisplay -r "clear;params.files={%s};GA;quit;">ga.out' %(run_no))
#os.system('cp Rec*/Amp-Phase.vtk ../frames/Au%s.vtk' %run_no)
#os.system('cp Rec*GA*/Amp-Phase.vtk ../frames/Au%s.vtk' %run_no)
os.chdir('/reg/d/psdm/xpp/xppm0416/ftc')

