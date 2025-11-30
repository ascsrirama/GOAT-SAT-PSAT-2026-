import customtkinter
import tkintermapview
import tkinter as tk
import serial
import threading

#serial stuff
SERIAL_PORT = "COM3"   # ← change this to your port
BAUD_RATE = 115200

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)



customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("blue")

root = customtkinter.CTk()
root.title("ESP32 GPS Tracker")
root.geometry("600x600")

# Map 
map_frame = customtkinter.CTkFrame(root)
map_frame.pack(fill="both", expand=True, padx=10, pady=10)

map_widget = tkintermapview.TkinterMapView(map_frame, width=600, height=600, corner_radius=0)
map_widget.pack(fill="both", expand=True)

map_widget.set_zoom(17)

marker = None



def update_marker(lat, lon):
    global marker

    map_widget.set_position(lat, lon)

    if marker:
        marker.set_position(lat, lon)
    else:
        marker = map_widget.set_marker(lat, lon, text="ESP32 Location")



# def read_serial():
#     while True:
#         line = ser.readline().decode().strip()

#         # Expecting format: "LAT,LON"
#         if "," in line:
#             try:
#                 lat_str, lon_str = line.split(",")
#                 lat = float(lat_str)
#                 lon = float(lon_str)

#                 root.after(0, update_marker, lat, lon)

#             except:
#                 pass

import random
import time

def fake_serial():
    lat, lon = -36.8485, 174.7633  # starting point
    while True:
        lat += random.uniform(-0.0001, 0.0001)
        lon += random.uniform(-0.0001, 0.0001)
        root.after(0, update_marker, lat, lon)
        time.sleep(0.5)

threading.Thread(target=fake_serial, daemon=True).start()



# Start serial thread
#threading.Thread(target=read_serial, daemon=True).start()

root.mainloop()
