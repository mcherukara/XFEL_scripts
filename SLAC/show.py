import tifffile as tif
import matplotlib.pyplot as plt
a=tif.imread('run148.tiff')
plt.imshow(a[0,:,:],cmap=plt.cm.jet, vmin=10, vmax=10000)
