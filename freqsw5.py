#!/home/nimesh/anaconda/bin/python
"""
Acquires frequency-switched spectra.

Usage:
freqsw.py <N> <fc> <delta-f> <filename>

N: No. of spectra to average
fc: center frequency (sw. by +/-deltaf MHz from fc)
delta-f: frequency switching amount (1/2)  in MHz 
filename: filename for final spectrum
"""

from numpy import savetxt
from rtlsdr import *
from pylab import *
import numpy as np
import sys
from matplotlib.mlab import psd

N = int(sys.argv[1])
frequency = float(sys.argv[2])
deltaf = float(sys.argv[3])
fname = sys.argv[4]

gain = 30.
calFactor = 92000.

frequency1=frequency-deltaf
frequency2=frequency+deltaf

total=np.zeros(1024)

sdr = RtlSdr() 
sdr.sample_rate = 2.4e6
sdr.gain = gain

for i in range(N):
    sdr.center_freq = float(frequency1)*1.0e6
    samples = sdr.read_samples(256*1024)
    (power1,f1) = psd(samples, NFFT = 1024, Fs= sdr.sample_rate/1.0e6,scale_by_freq=True) 
    sdr.center_freq = float(frequency2)*1.0e6
    samples = sdr.read_samples(256*1024)
    (power2,f2) = psd(samples, NFFT = 1024, Fs= sdr.sample_rate/1.0e6,scale_by_freq=True)

    diff=power1-power2

    total=total+diff

average=calFactor*(total/float(N))

flabel = f1+frequency
#output = column_stack((f1+float(frequency1),average))
output = column_stack((flabel,average))
savetxt(fname,output,fmt=('%.5f','%.7e'))
