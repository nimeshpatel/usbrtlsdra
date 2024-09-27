import numpy as np
from numpy import savetxt, loadtxt
from rtlsdr import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import ttk, messagebox
import datetime

# Constants
hline_rest_freq = 1420.40575180  # MHz
f0 = hline_rest_freq
c = 2.998e5  # Speed of light in km/s
Tamb = 300  # Calibration temperature in K

sdr = RtlSdr()
sdr.sample_rate = 2.4e6

def acquire_spectrum(N):
    totalx = np.zeros(1024)
    for i in range(N):
        samples = sdr.read_samples(256 * 1024)
        samples = samples - np.mean(samples)
        (x, f) = plt.psd(samples, NFFT=1024, Fs=sdr.sample_rate / 1.0e6, Fc=sdr.center_freq / 1.0e6)
        totalx = totalx + x
    averagex = totalx / float(N)
    return f, averagex

def start_acquisition():
    try:
        N = int(entry_N.get())
        frequency = float(entry_frequency.get())
        gainvalue = float(entry_gain.get())
        perform_calibration = calibrate_var.get()

        sdr.center_freq = frequency * 1.0e6
        sdr.gain = gainvalue

        if perform_calibration:
            # Prompt for hot load spectrum
            messagebox.showinfo("Calibration", "Show the hot load and hit OK to continue...")
            f, hotSpectrum = acquire_spectrum(N)
            savetxt("hotSpectrum", np.column_stack((f, f, hotSpectrum)), fmt=('%.12f', '%.12f', '%.12f'))

            # Prompt for off-sky spectrum
            messagebox.showinfo("Calibration", "Show the (off) sky position and hit OK to continue...")
            f, skySpectrum = acquire_spectrum(N)
            savetxt("skySpectrum", np.column_stack((f, f, skySpectrum)), fmt=('%.12f', '%.12f', '%.12f'))

        else:
            # Read existing hotSpectrum and skySpectrum files
            skySpectrum = loadtxt("skySpectrum")[:, 2]  # Extract the third column
            hotSpectrum = loadtxt("hotSpectrum")[:, 2]  # Extract the third column

        # Acquire the on-source spectrum regardless of the calibration option
        messagebox.showinfo("Calibration", "Show the (on) source position and hit OK to continue...")
        f, outdata = acquire_spectrum(N)

        # Perform calibration using the acquired or loaded spectra
        calibrated_signal = (outdata - skySpectrum) / (hotSpectrum - skySpectrum) * Tamb

        velocity = c * (f0 - f) / f0
        
        # Plotting
        fig, ax1 = plt.subplots()
        ax1.plot(f, calibrated_signal)
        ax1.set_xlabel('Frequency (MHz)')
        ax1.set_ylabel('Calibrated Intensity (K)')
        ax1.ticklabel_format(useOffset=False, style='plain')

        # Creating a second x-axis for velocity
        ax2 = ax1.twiny()
        ax2.set_xlabel('Velocity (km/s)')
        ax2.set_xlim(ax1.get_xlim())

        # Create custom tick locations and labels for velocity in steps of 40 km/s
        velocity_ticks = np.arange(-200, 200 + 1, 40)
        frequency_ticks = f0 - (velocity_ticks / c) * f0
        ax2.set_xticks(frequency_ticks)
        ax2.set_xticklabels([f"{v:.0f}" for v in velocity_ticks])

        # Draw a vertical dashed line at 0 km/s velocity
        zero_velocity_freq = f0
        ax1.axvline(x=zero_velocity_freq, color='r', linestyle='--')

        # Save the calibrated spectrum
        fname = "calibrated_spectrum_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output = np.column_stack((f, velocity, calibrated_signal))
        savetxt(fname, output, fmt=('%.12f', '%.12f', '%.12f'))

        # Display the plot in the GUI
        for widget in plot_frame.winfo_children():
            widget.destroy()  # Clear the frame before adding a new plot

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Add the navigation toolbar for zoom, pan, etc.
        toolbar = NavigationToolbar2Tk(canvas, plot_frame)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        print("Total Power:", outdata.sum(), "dB:", 10.0 * np.log10(outdata.sum()))
        print("Center Frequency:", sdr.center_freq)

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to quit the application
def quit_program():
    window.quit()   # Stops the mainloop
    window.destroy()  # This is necessary to close the window

# Setting up the GUI
window = tk.Tk()
window.title("Spectrum Acquisition and Calibration")

# Adjust window size to fit Raspberry Pi touchscreen display
window.geometry("800x480")

# Frame for input cells
input_frame = ttk.Frame(window, padding="5")
input_frame.pack(fill=tk.X)

# Input fields in one row
ttk.Label(input_frame, text="Samples (N):").grid(column=0, row=0, sticky=tk.W)
entry_N = ttk.Entry(input_frame, width=5)
entry_N.insert(0, "100")  # Default value
entry_N.grid(column=1, row=0, sticky=tk.W)

ttk.Label(input_frame, text="Frequency (MHz):").grid(column=2, row=0, sticky=tk.W)
entry_frequency = ttk.Entry(input_frame, width=10)
entry_frequency.insert(0, "1420.406")  # Default value
entry_frequency.grid(column=3, row=0, sticky=tk.W)

ttk.Label(input_frame, text="Gain:").grid(column=4, row=0, sticky=tk.W)
entry_gain = ttk.Entry(input_frame, width=5)
entry_gain.insert(0, "30")  # Default value
entry_gain.grid(column=5, row=0, sticky=tk.W)

# Frame for buttons
button_frame = ttk.Frame(window, padding="5")
button_frame.pack(fill=tk.X)

# Checkbox for calibration option
calibrate_var = tk.BooleanVar()
calibrate_check = ttk.Checkbutton(button_frame, text="Perform Calibration", variable=calibrate_var)
calibrate_check.grid(column=0, row=0, padx=5, sticky=tk.W)

# Start button
start_button = ttk.Button(button_frame, text="Start Acquisition", command=start_acquisition)
start_button.grid(column=1, row=0, padx=5, sticky=tk.W)

# Quit button
quit_button = ttk.Button(button_frame, text="Quit", command=quit_program)
quit_button.grid(column=2, row=0, padx=5, sticky=tk.W)

# Frame for plotting
plot_frame = ttk.Frame(window, padding="5")
plot_frame.pack(fill=tk.BOTH, expand=True)

# Start the GUI loop
window.mainloop()
