usbrtlsdra
==========
This repository contains python code for using the rtl-sdr usb dongle receiver to acquire 21 cm hydrogen line spectra.
These codes require the librtlsdr and rtl-sdr packages to be installed, as well as the python wrapper installed.
URLs for both these:
1) rtl-sdr:
Please see "Building the software" section on this webpage:
http://sdr.osmocom.org/trac/wiki/rtl-sdr

2) A python wrapper for the librtlsdr:
https://github.com/roger-/pyrtlsdr

acquireSpectrum.py (also, as.py): acquires a total power spectrum without any switching.
Usage:
The code as.py simply acquires a total power spectrum and writes it to a file.
Usage: 
as.py <N> <freq> <gain> <fname>
N: number of spectra to average.
freq: tuning frequency in MHz.
gain: gain value of the LNA inside the dongle- typically 30

The code fs.py acquires a frequency-switched (and folded) spectrum and shows a plot- but does not write to a file.
fs.py <N>
(N: number of spectra to average; each one is about 1 sec I think).

The codes freqsw5.py and freqsw6.py are variants of fs.py, to avoid folding, and instead write out on-off to a 
file (also avoid plotting).

Here is the usage info on these two codes:

freqsw5.py: acquires a frequency-switched spectrum and writes out a two column (freq in MHz, power in dB) ascii 
file with filename given on command line.
Usage: 
freqsw5.py <N> <Fc> <delta-F> <filename>
e.g.:
freqsw5.py 10 1420.4 0.5 testspectrum

freqsw6.py: same as freqsw5.py but it does not take a filename. It writes out the data into a file called 
"spectrum_YYMMDD_HHMMSS" with appended time stamp.

Note that gain value is hard-coded to 30, but you can change it if you want.
The additional parameter delta-f is the switching amount in MHz. It is actually half of the value you want to
switch by; the two spectra are acquired with tunings of fcenter-delta and fcenter+delta.

These programs write out On-Off instead of the folded spectrum as before, so you should see the usual signature 
of frequency switched spectra with a negative signal followed by a positive signal.

To repeat these commands in a loop, it is very easy to do it either via a shell script or the following one-line
commands in bash (I assume you are using the bash shell- this is the default shell on Ubuntu).
E.g., to acquire 10 spectra in a succession, with file names as test1, test2, ... test10:

Enter the following command:

for i in {1..10}; do ./freqsw5.py 10 1420.4 0.5 test$i; done

To acquire time stamped spectra:

for i in {1..10}; do ./freqsw6.py 10 1420.4 0.5; done

To acquire spectra indefinitely, 

while(true); do ./freqsw6.py 10 1420.4 0.5; done

I found that ctrl-C does not quit the infinite loop! Instead you must do: ctrl-Z, followed by:
kill -9 %1


