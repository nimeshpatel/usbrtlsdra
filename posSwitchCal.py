import numpy as np
from numpy import savetxt, loadtxt
from rtlsdr import *
from matplotlib.pylab import *
import matplotlib.pyplot as plt
import datetime
import sys
import argparse

# Hydrogen ground state hyperfine spin-flip transition frequency
hline_rest_freq = 1420.40575180  # MHz
f0 = hline_rest_freq

# Speed of light in km/s
c = 2.998e5

# Calibration temperature in K
Tamb = 300

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Acquire and calibrate spectrum from RTL-SDR.')
parser.add_argument('-n', type=int, default=100, help='number of samples (default: 100)')
parser.add_argument('-f', type=float, default=1420.406, help='frequency in MHz (default: 1420.406)')
parser.add_argument('-g', type=float, default=30, help='gain (default: 30)')
parser.add_argument('-c', action='store_true', help='perform calibration')
args = parser.parse_args()

# number of samples
N = args.n

# in MHz
frequency = args.f

# gain value
gainvalue = args.g

sdr = RtlSdr()

sdr.sample_rate = 2.4e6
sdr.center_freq = float(frequency) * 1.0e6
sdr.gain = float(gainvalue)

def acquire_spectrum(N):
    totalx = np.zeros(1024)
    for i in range(N):
        samples = sdr.read_samples(256 * 1024)
        samples = samples - np.mean(samples)
        (x, f) = psd(samples, NFFT=1024, Fs=sdr.sample_rate / 1.0e6, Fc=sdr.center_freq / 1.0e6)
        totalx = totalx + x
    averagex = totalx / float(N)
    return f, averagex

if args.c:
    input("Show the hot load and hit return...")
    f, hotSpectrum = acquire_spectrum(N)
    savetxt("hotSpectrum", np.column_stack((f, f, hotSpectrum)), fmt=('%.12f', '%.12f', '%.12f'))
    
    input("Show the (off) sky position and hit return...")
    f, skySpectrum = acquire_spectrum(N)
    savetxt("skySpectrum", np.column_stack((f, f, skySpectrum)), fmt=('%.12f', '%.12f', '%.12f'))
    
    input("Show the (on) source position and hit return...")
    f, outdata = acquire_spectrum(N)
else:
    f, outdata = acquire_spectrum(N)
    skySpectrum = loadtxt("skySpectrum")[:, 2]  # Extract the third column
    hotSpectrum = loadtxt("hotSpectrum")[:, 2]  # Extract the third column

# Perform calibration if required
if args.c:
    skySpectrum = skySpectrum  # Already extracted correctly
    hotSpectrum = hotSpectrum  # Already extracted correctly
    calibrated_signal = (outdata - skySpectrum) / (hotSpectrum - skySpectrum) * Tamb
else:
    calibrated_signal = outdata

totalpower = outdata.sum()
totalpowerdB = 10.0 * np.log10(totalpower)

# convert freq to velocity
velocity = c * (f0 - f) / f0

fig, ax1 = plt.subplots()

# Plotting frequency vs calibrated signal
ax1.plot(f, calibrated_signal)
ax1.set_xlabel('Frequency (MHz)')
ax1.set_ylabel('Calibrated Intensity (K)' if args.c else 'Intensity')
ax1.ticklabel_format(useOffset=False, style='plain')

# Creating a second x-axis for velocity
ax2 = ax1.twiny()
ax2.set_xlabel('Velocity (km/s)')
ax2.set_xlim(ax1.get_xlim())

# Create custom tick locations and labels for velocity in steps of 40 km/s
velocity_ticks = np.arange(-200, 200 + 1, 40)  # from -200 km/s to 200 km/s in steps of 40 km/s
frequency_ticks = f0 - (velocity_ticks / c) * f0

ax2.set_xticks(frequency_ticks)
ax2.set_xticklabels([f"{v:.0f}" for v in velocity_ticks])

# Draw a vertical dashed line at 0 km/s velocity
zero_velocity_freq = f0  # Frequency corresponding to 0 km/s velocity
ax1.axvline(x=zero_velocity_freq, color='r', linestyle='--')

# Save the calibrated spectrum
fname = "calibrated_spectrum_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
output = np.column_stack((f, velocity, calibrated_signal))
savetxt(fname, output, fmt=('%.12f', '%.12f', '%.12f'))

print("Total Power=", totalpower, totalpowerdB)
print(sdr.center_freq)
plt.show()

