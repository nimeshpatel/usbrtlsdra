#!/Users/nimesh/anaconda/bin/python
from numpy import savetxt
from rtlsdr import *
from pylab import *
import numpy as np
import sys

N = int(sys.argv[1])
frequency1 = sys.argv[2]
frequency2 = sys.argv[3]
gain = sys.argv[4]
fname = sys.argv[5]

def acquirespectrum(frequency,gain):
    sdr = RtlSdr() 
    sdr.sample_rate = 2.4e6
    sdr.center_freq = float(frequency)*1.0e6
    sdr.gain = float(gain)
    totalx = np.zeros(1024)
    samples = sdr.read_samples(256*1024)
    (power,f) = psd(samples, NFFT = 1024, Fs= sdr.sample_rate/1.0e6, Fc=\
              sdr.center_freq/1.0e6) 
    return f,power


total=np.zeros(1024)
for i in range(N):
    (f1,power1)=acquirespectrum(frequency1,gain)
    (f2,power2)=acquirespectrum(frequency2,gain)
    diff=power1-power2
    diff2=np.roll(diff,428)
    final=(diff-diff2)/2.0
    total=total+final
average=total/float(N)
figure(2)
plot(f1,average)
show()
averagedb= 10.0*log10(average)
output = column_stack((f1,average,averagedb))
savetxt(fname,output,fmt=('%.5f','%.5e','%.5f'))

