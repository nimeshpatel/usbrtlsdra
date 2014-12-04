#!/Users/nimesh/anaconda/bin/python
"""
Acquires frequency-switched spectra.
Switching interval is fixed to 1 MHz.
Gain is fixed to 30.
This is a copy of freqsw2.py, with no arguments.
Only displays the spectrum- does not save to file.
Usage:
fs.py <N>
"""

from numpy import savetxt
from rtlsdr import *
from pylab import *
import numpy as np
import sys

N = int(sys.argv[1])
frequency = 1420.6

ion()

#gain = 42.
gain = 30.
deltaf=0.5

frequency1=float(frequency)-deltaf
frequency2=float(frequency)+deltaf

total=np.zeros(1024)

sdr = RtlSdr() 
sdr.sample_rate = 2.4e6
sdr.gain = gain

fig=figure(1)

for i in range(N):
    print N-i
    subplot(313)
    sdr.center_freq = float(frequency1)*1.0e6
    samples = sdr.read_samples(256*1024)
    average = sum(samples)/len(samples)
    nsamples = [(x-average) for x in samples]
    (power1,f1) = psd(nsamples, NFFT = 1024, Fs= sdr.sample_rate/1.0e6, Fc=\
                       sdr.center_freq/1.0e6)
    sdr.center_freq = float(frequency2)*1.0e6
    samples = sdr.read_samples(256*1024)
    average = sum(samples)/len(samples)
    nsamples = [(x-average) for x in samples]
    (power2,f2) = psd(nsamples, NFFT = 1024, Fs= sdr.sample_rate/1.0e6, Fc=\
              sdr.center_freq/1.0e6)
    diff=power1-power2
    diff2=np.roll(diff,428)
    final=(diff-diff2)/2.0
    total=total+final
    subaverage=total/float(i+1)
    if (i==0):
        ax = fig.add_subplot(312)
	line1, = ax.plot(f1,subaverage)
    line1.set_ydata(subaverage)
    fig.canvas.draw()

average=92000.0*(total/float(N))
subplot(311)
plot(f1,average)
#ioff()
draw()
figure(2)
plot(f1,average)
xlim([1419.5,1421.0])
xlabel('Frequency (MHz)')
ylabel('Antenna temperature (K)')
draw()
figure(3)
vel=(3.0e5*(1420.406-f1)/1420.406)
plot(vel,average)
xlim([-200,135])
xlabel('Velocity (km/s)')
ylabel('Antenna temperature (K)')
draw()
#output = column_stack((f1,average))
#savetxt(fname,output,fmt=('%.5f','%.7e'))
var = raw_input(" ")
close("all")
