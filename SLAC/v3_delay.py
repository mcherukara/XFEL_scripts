#Creates nice delay plots, automatically centering to brightest pixel at time0
#Calculates COM shift and Gaussian peak position and width shift
#Takes step size and initial time as inputs

import tifffile as tif
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import ndimage
from scipy.optimize import curve_fit

#Gaussian fit function
def twoD_Gaussian((x, y), amplitude, xo, yo, sigma_x, sigma_y, theta, offset):
    xo = float(xo)
    yo = float(yo)    
    a = (np.cos(theta)**2)/(2*sigma_x**2) + (np.sin(theta)**2)/(2*sigma_y**2)
    b = -(np.sin(2*theta))/(4*sigma_x**2) + (np.sin(2*theta))/(4*sigma_y**2)
    c = (np.sin(theta)**2)/(2*sigma_x**2) + (np.cos(theta)**2)/(2*sigma_y**2)
    g = offset + amplitude*np.exp( - (a*((x-xo)**2) + 2*b*(x-xo)*(y-yo) 
                            + c*((y-yo)**2)))
    return g.ravel()

a=tif.imread(sys.argv[1])

b=float(sys.argv[2]) #Step size
c=float(sys.argv[3]) #Init time
dim=a.shape
print dim
#im1=np.zeros( [dim[0], dim[1]])
#im2=np.zeros( [dim[0], dim[2]])
data1=np.zeros((dim[0],dim[1],3),float)
data2=np.zeros((dim[0],dim[2],3),float)

#initpix1=np.where(a[0,:,:]==a.max(axis=1))
initpix=np.where(a[0,:,:]==a[0,:,:].max())
print initpix[0],initpix[1], ndimage.measurements.center_of_mass(a[0,:,:])
coms=np.zeros((dim[0],3),float) #Stores time,  COMx and COMy of each frame

#Gaussian fit shit
gpos=np.zeros((dim[0],3),float) #Stores time gaussian centre X and Y
gw=np.zeros((dim[0],2),float) #Stores time, gaussian width
initial_guess = (1000,55,45,5,5,0,0)
# Create x and y indices
x = np.linspace(0, dim[1], dim[1])
y = np.linspace(0, dim[2], dim[2])
x,y = np.meshgrid(x, y)

#IF TIME 0 DOESN'T WORK, USE THE NEXT FRAME
try:
 popt, pcov = curve_fit(twoD_Gaussian, (x,y), a[0,:,:].ravel(), p0=initial_guess,maxfev=10000)
except:
 popt, pcov = curve_fit(twoD_Gaussian, (x,y), a[1,:,:].ravel(), p0=initial_guess,maxfev=10000)
print popt
gposinit=popt[1:3] #Initial positions and widths
print gposinit
#gwinit=(popt[4]+popt[5])/2 #Average width

initial_guess=popt
for fr in range(dim[0]):
  print fr
  data1[fr,:,0],data2[fr,:,0]=fr*b+c,fr*b+c #Time using init time and step size
  data1[fr,:,1],data2[fr,:,1]=np.arange(dim[1])-initpix[0],np.arange(dim[2])-initpix[1] #X and Y position at first point
  data1[fr,:,2],data2[fr,:,2]=np.mean(a[fr,:,:], 1),np.mean(a[fr,:,:], 0) #Colour map
  coms[fr,1:3]=np.array(ndimage.measurements.center_of_mass(a[fr,:,:]))-np.array(ndimage.measurements.center_of_mass(a[0,:,:]))
  try:
   popt, pcov = curve_fit(twoD_Gaussian, (x,y), a[fr,:,:].ravel(), p0=initial_guess, maxfev=10000)
  except:
   print fr, "failed"
   popt=temp_popt
  temp_popt=popt 
  gpos[fr,1:3]=popt[1:3]-gposinit #Copy X and Y from Gaussian fits 
  gw[fr,1]=(popt[3]+popt[4])/2 #Average width
  coms[fr,0]=fr*b+c
  gpos[fr,0]=fr*b+c
  gw[fr,0]=fr*b+c

f,(plt1,plt2)=plt.subplots(1,2,sharey=True)

f.patch.set_facecolor('white')
f.set_size_inches(12, 10,forward=True)
plt1.pcolormesh(data2[:,:,0],data2[:,:,1],data2[:,:,2],shading='gouraud')
plt2.pcolormesh(data1[:,:,0],data1[:,:,1],data1[:,:,2],shading='gouraud')
plt1.axis([data2[:,:,0].min(),data2[:,:,0].max(),-20,20])
plt2.axis([data1[:,:,0].min(),data1[:,:,0].max(),-20,20])
plt2.set_xlabel('Time (ps)',{'fontsize':20})
plt1.set_xlabel('Time (ps)',{'fontsize':20})
plt1.set_ylabel('Pixel',{'fontsize':20})
#plt2.set_ylabel('Pixel shift')
plt1.set_title('X deviation',{'fontsize':20})
plt2.set_title('Y deviation',{'fontsize':20})
matplotlib.rcParams.update({'font.size': 16})
plt.savefig('colour.png')

f2,(plt11,plt22)=plt.subplots(1,2,sharey=True)
f2.patch.set_facecolor('white')
f2.set_size_inches(12, 10,forward=True)
plt11.plot(coms[:,0],coms[:,2],'bo-',linewidth=3.0,ms=11.0)
plt22.plot(coms[:,0],coms[:,1],'bo-',linewidth=3.0,ms=11.0)
plt22.set_xlabel('Time (ps)',{'fontsize':20})
plt11.set_xlabel('Time (ps)',{'fontsize':20})
plt11.set_ylabel('COM shift',{'fontsize':20})
#plt2.set_ylabel('Pixel shift')
plt11.set_title('X deviation',{'fontsize':20})
plt22.set_title('Y deviation',{'fontsize':20})
matplotlib.rcParams.update({'font.size': 16})
plt.savefig('line.png')

f3,(plt111,plt222)=plt.subplots(1,2,sharey=True)
f3.patch.set_facecolor('white')
f3.set_size_inches(12, 10,forward=True)
plt111.plot(gpos[:,0],gpos[:,1],'bo-',linewidth=3.0,ms=11.0)
plt222.plot(gpos[:,0],gpos[:,2],'bo-',linewidth=3.0,ms=11.0)
plt222.set_xlabel('Time (ps)',{'fontsize':20})
plt111.set_xlabel('Time (ps)',{'fontsize':20})
plt111.set_ylabel('COM shift',{'fontsize':20})
#plt2.set_ylabel('Pixel shift')
plt111.set_title('X deviation',{'fontsize':20})
plt222.set_title('Y deviation',{'fontsize':20})
matplotlib.rcParams.update({'font.size': 16})
plt.savefig('gauss.png')

f3,(plt4)=plt.subplots(1,1,sharey=True)
f3.patch.set_facecolor('white')
f3.set_size_inches(12, 10,forward=True)
plt4.plot(gw[:,0],gw[:,1],'bo-',linewidth=3.0,ms=11.0)
plt4.set_ylim([min(gw[:,1])-1,max(gw[:,1])+1])
plt4.set_xlabel('Time (ps)',{'fontsize':20})
plt4.set_ylabel('Width',{'fontsize':20})
#plt2.set_ylabel('Pixel shift')
plt4.set_title('Gaussian width',{'fontsize':20})
matplotlib.rcParams.update({'font.size': 16})
plt.savefig('width.png')

