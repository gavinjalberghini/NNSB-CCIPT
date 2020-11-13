"""
# Author: Gavin Alberghini
# Date: 12/1/2019
# File: gui.py
# Purpose: The function of this file is to collect input data from the user
"""

#!/usr/bin/python
from tkinter import *
from tkinter import messagebox
import process

# Click event for the Reset Button
def clicked_reset():
    year_slider.set(0)
    #storm_cat_slider.set(0)
    high_tide_radio.select()
    messagebox.showinfo('RESET', 'Input information has been reset!')


# Click event for the Apply Button
def clicked_apply():
    if selected.get() == 1:
        res_text.set(process.apply(year_slider.get(), "HIGH"))
    elif selected.get() == 2:
        res_text.set(process.apply(year_slider.get(), "LOW"))
    else:
        res_text.set(process.apply(year_slider.get(), "N/A"))


# Build the window
window = Tk()
window.title("NNSB_CCIPT")
window.geometry('250x300')

# Create buttons and labels
selected = IntVar()
res_text = StringVar()
apply_btn = Button(window, text="Apply", command=clicked_apply)
reset_btn = Button(window, text="Reset", command=clicked_reset)
high_tide_radio = Radiobutton(window, text="High Tide", value=1, variable=selected)
low_tide_radio = Radiobutton(window, text="Low Tide", value=2, variable=selected)
year_slider = Scale(window, from_=0, to=50, orient=HORIZONTAL)
#storm_cat_slider = Scale(window, from_=0, to=5, orient=HORIZONTAL)

res_text.set("Water Level Displacement 0.0ft")
blank_label = Label(window, text="")
blank_label_2 = Label(window, text="")
year_label = Label(window, text="Estimated Year")
#storm_label = Label(window, text="Storm Category")
elevation_label = Label(window, textvariable=res_text)

# Place buttons and lables on window
elevation_label.pack(anchor=N)
year_slider.pack(anchor=N)
year_label.pack(anchor=N)
#storm_cat_slider.pack(anchor=N)
#storm_label.pack(anchor=N)
blank_label.pack(anchor=N)
high_tide_radio.pack(anchor=N)
low_tide_radio.pack(anchor=N)
blank_label_2.pack(anchor=N)
reset_btn.pack(anchor=N)
apply_btn.pack(anchor=N)

# Set default positons and start gui thread
window.mainloop()
