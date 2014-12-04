#!/Users/nimesh/anaconda/bin/python
from numpy import savetxt
from rtlsdr import *
from pylab import *
import numpy as np
import sys

N = int(sys.argv[1])
frequency = sys.argv[2]
gainvalue = sys.argv[3]
fname = sys.argv[4]

sdr = RtlSdr() 

sdr.sample_rate = 2.4e6
sdr.center_freq = float(frequency)*1.0e6
sdr.gain = float(gainvalue)
 
totalx = np.zeros(1024)
samples = sdr.read_samples(256*1024)
for i in range(N):
    samples = sdr.read_samples(256*1024)
    (x,f) = psd(samples, NFFT = 1024, Fs= sdr.sample_rate/1.0e6, Fc=\
              sdr.center_freq/1.0e6) 
    totalx = totalx + x   
 

averagex = totalx/float(N)
#xa = np.array(averagex)
#imax = np.unravel_index(xa.argmax(),xa.shape)
#print "Maximum:"
#print imax[0],f[imax[0]],totalx[imax[0]]
#deleteIndices = [imax[0]-1,imax[0],imax[0]+1]
#averagex=np.delete(averagex,deleteIndices)
totalpower = averagex.sum()
totalpowerdB = 10.0*log10(totalpower)
outdata = 10.0*log10(averagex)
#f=np.delete(f,deleteIndices)
figure(2)
plot(f,outdata)
output = column_stack((f,outdata))
savetxt(fname,output,fmt=('%.5f','%.5f'))
#print f
#print totalx
#print 10.0*log10(x)
print "Total Power=",totalpower,totalpowerdB
show()    
