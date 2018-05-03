#Read 2 time scans with different steps, merge and account for different step sizes
import tifffile as tif
import sys
import numpy as np
import matplotlib.pyplot as plt

a=tif.imread(sys.argv[1])
b=tif.imread(sys.argv[2])

dim1=a.shape
dim2=b.shape
print dim1, dim2
#im1=np.zeros( [(dim1[0]+dim2[0]*2), dim1[1]])
#im2=np.zeros( [(dim1[0]+dim2[0]*2), dim2[2]])
im1=np.zeros( [(dim1[0]+dim2[0]*1), dim1[1]])
im2=np.zeros( [(dim1[0]+dim2[0]*1), dim2[2]])
#xvals=np.zeros(dim1[0]+dim2[0])
print a.shape, b.shape, im1.shape

for fr in range(dim1[0]-1):
  im1[fr,:] = np.mean(a[fr,:,:], 1)
  im1[fr+dim1[0]-1,:] = np.mean(b[fr,:,:], 1)
#  im1[fr*2+dim1[0]-1,:] = np.mean(b[fr,:,:], 1)
#  im1[fr*2-1+dim1[0]-1,:] = (np.mean(b[fr,:,:], 1)+(np.mean(b[fr-1,:,:], 1)))/2
  im2[fr,:] = np.mean(a[fr,:,:], 0)
  im2[fr+dim1[0]-1,:] = np.mean(b[fr,:,:], 0)
#  im2[fr*2+dim1[0]-1,:] = np.mean(b[fr,:,:], 0)
#  im2[fr*2-1+dim1[0]-1,:] =(np.mean(b[fr,:,:], 0)+(np.mean(b[fr-1,:,:], 0)))/2
#  xvals[fr],xvals[fr+dim1[0]-1]=-25+25*fr,1000+25*fr

im1=np.rot90(im1)
im2=np.rot90(im2)

f,(plt1,plt2)=plt.subplots(2,sharex=True)
plt1.imshow(im2 ,aspect='auto')
plt2.imshow(im1 ,aspect='auto')
plt2.set_xlabel('Scan point')
plt1.set_ylabel('Pixel')
plt2.set_ylabel('Pixel')
plt1.set_title('X deviation')
plt2.set_title('Y deviation')
plt.show()
