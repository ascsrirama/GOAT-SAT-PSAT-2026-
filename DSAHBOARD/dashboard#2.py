
# import customtkinter
# import tkintermapview
# import tkinter as tk
# import random
# import time
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from matplotlib.figure import Figure
# #import serial
# import threading




#serial stuff
#SERIAL_PORT = "COM3"   # ← change this to your port
#BAUD_RATE = 115200

#ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)



# customtkinter.set_appearance_mode("system")
# customtkinter.set_default_color_theme("blue")

# root = customtkinter.CTk()
# root.title("FAKE ESP DATA TEST")
# root.geometry("1200x1000")

# # Map 
# map_frame = customtkinter.CTkFrame(root)
# map_frame.pack(fill="both", expand=True, padx=10, pady=10)

# map_widget = tkintermapview.TkinterMapView(map_frame, width=100, height=200, corner_radius=0)
# map_widget.pack(fill="both", expand=True)

# map_widget.set_zoom(17)

# marker = None



# def update_marker(lat, lon):
#     global marker

#     map_widget.set_position(lat, lon)

#     if marker:
#         marker.set_position(lat, lon)
#     else:
#         marker = map_widget.set_marker(lat, lon, text="ESP32 Location")



# # def read_serial():
# #     while True:
# #         line = ser.readline().decode().strip()

# #         # Expecting format: "LAT,LON"
# #         if "," in line:
# #             try:
# #                 lat_str, lon_str = line.split(",")
# #                 lat = float(lat_str)
# #                 lon = float(lon_str)

# #                 root.after(0, update_marker, lat, lon)

# #             except:
# #                 pass

# import random
# import time

# def fake_serial():
#     lat, lon = -36.8485, 174.7633  # starting point
#     while True:
#         lat += random.uniform(-0.0001, 0.0001)
#         lon += random.uniform(-0.0001, 0.0001)
#         root.after(0, update_marker, lat, lon)
#         time.sleep(0.5)

# threading.Thread(target=fake_serial, daemon=True).start()


# import customtkinter
# import tkinter as tk
# import tkintermapview
# import threading
# import random
# import time
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from matplotlib.figure import Figure

# customtkinter.set_appearance_mode("system")
# customtkinter.set_default_color_theme("blue")

# root = customtkinter.CTk()
# root.title("FAKE ESP DATA TEST")
# root.geometry("1200x1000")  # wide for dashboard


# #set up layout
# root.grid_rowconfigure(0, weight=1)
# root.grid_columnconfigure(0, weight=1)  # left side for charts
# root.grid_columnconfigure(1, weight=2)  # right side for map

# # Graphs and stuff
# charts_frame = customtkinter.CTkFrame(root)
# charts_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
# charts_frame.grid_rowconfigure(0, weight=1)
# charts_frame.grid_rowconfigure(1, weight=1)
# charts_frame.grid_columnconfigure(0, weight=1)

# # Accelerometer graoh
# fig_acc = Figure(figsize=(5, 3), dpi=100)
# ax_acc = fig_acc.add_subplot(111)
# ax_acc.set_title("Accelerometer")
# ax_acc.set_ylim(-10, 10)
# ax_acc.set_ylabel("m/s²")
# ax_acc.set_xlabel("Time")

# line_acc, = ax_acc.plot([], [], color='blue')
# acc_data = []

# canvas_acc = FigureCanvasTkAgg(fig_acc, master=charts_frame)
# canvas_acc.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

# # Altimeter graph
# fig_alt = Figure(figsize=(5, 3), dpi=100)
# ax_alt = fig_alt.add_subplot(111)
# ax_alt.set_title("Altimeter")
# ax_alt.set_ylim(0, 500) 
# ax_alt.set_ylabel("m")
# ax_alt.set_xlabel("Time")

# line_alt, = ax_alt.plot([], [], color='green')
# alt_data = []

# canvas_alt = FigureCanvasTkAgg(fig_alt, master=charts_frame)
# canvas_alt.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

# #==== MAP STUFF ===
# map_frame = customtkinter.CTkFrame(root)
# map_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

# map_widget = tkintermapview.TkinterMapView(map_frame, width=600, height=700, corner_radius=0)
# map_widget.pack(fill="both", expand=True)
# map_widget.set_zoom(17)

# marker = None

# def update_marker(lat, lon):
#     global marker
#     map_widget.set_position(lat, lon)
#     if marker:
#         marker.set_position(lat, lon)
#     else:
#         marker = map_widget.set_marker(lat, lon, text="GPS Location")


# # ==== FAKE DATA === 
# def update_fake_data():
#     lat, lon = -36.8485, 174.7633
#     t = 0
#     while True:
#         # Update GPS
#         lat += random.uniform(-0.0001, 0.0001)
#         lon += random.uniform(-0.0001, 0.0001)
#         root.after(0, update_marker, lat, lon)

#         # Update accelerometer
#         acc_val = random.uniform(-9, 9)
#         acc_data.append(acc_val)
#         if len(acc_data) > 50:
#             acc_data.pop(0)
#         line_acc.set_data(range(len(acc_data)), acc_data)
#         ax_acc.set_xlim(0, max(50, len(acc_data)))
#         canvas_acc.draw()

#         # Update altimeter
#         alt_val = random.uniform(0, 500)
#         alt_data.append(alt_val)
#         if len(alt_data) > 50:
#             alt_data.pop(0)
#         line_alt.set_data(range(len(alt_data)), alt_data)
#         ax_alt.set_xlim(0, max(50, len(alt_data)))
#         canvas_alt.draw()

#         time.sleep(0.05)
#         t += 1

# threading.Thread(target=update_fake_data, daemon=True).start()




# # Start serial thread
# #threading.Thread(target=read_serial, daemon=True).start()

# root.mainloop()



# import customtkinter
# import tkintermapview
# import tkinter as tk
# import serial
# import threading

# # -----------------------------
# # Serial setup
# # -----------------------------
# SERIAL_PORT = "COM15"  # Replace with your ESP32 COM port
# BAUD_RATE = 115200

# ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# # -----------------------------
# # GUI setup
# # -----------------------------
# customtkinter.set_appearance_mode("system")
# customtkinter.set_default_color_theme("blue")

# root = customtkinter.CTk()
# root.title("ESP32 GPS Tracker")
# root.geometry("800x600")

# map_frame = customtkinter.CTkFrame(root)
# map_frame.pack(fill="both", expand=True, padx=10, pady=10)

# map_widget = tkintermapview.TkinterMapView(map_frame, width=800, height=600, corner_radius=0)
# map_widget.pack(fill="both", expand=True)
# map_widget.set_zoom(17)

# marker = None

# def update_marker(lat, lon):
#     global marker
#     map_widget.set_position(lat, lon)
#     if marker:
#         marker.set_position(lat, lon)
#     else:
#         marker = map_widget.set_marker(lat, lon, text="ESP32 Location")

# # -----------------------------
# # Read ESP32 serial
# # -----------------------------
# def read_serial():
#     while True:
#         line = ser.readline().decode().strip()
#         if "," in line:
#             try:
#                 lat_str, lon_str = line.split(",")
#                 lat = float(lat_str)
#                 lon = float(lon_str)
#                 root.after(0, update_marker, lat, lon)
#             except:
#                 pass

# threading.Thread(target=read_serial, daemon=True).start()

# root.mainloop()


import customtkinter
import tkintermapview
import tkinter as tk
import serial
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import collections

# -----------------------------
# Serial setup
# -----------------------------
SERIAL_PORT = "COM7"  # Replace with your ESP32 COM port
BAUD_RATE = 115200

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# -----------------------------
# GUI setup
# -----------------------------
customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("blue")

root = customtkinter.CTk()
root.title("ESP32 Dashboard")
root.geometry("1200x800")

# Layout: 2 columns, left for charts, right for map
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)  # charts
root.grid_columnconfigure(1, weight=2)  # map

# -----------------------------
# Charts frame (left)
# -----------------------------
charts_frame = customtkinter.CTkFrame(root)
charts_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
charts_frame.grid_rowconfigure(0, weight=1)
charts_frame.grid_rowconfigure(1, weight=1)
charts_frame.grid_columnconfigure(0, weight=1)

# Accelerometer chart
fig_acc = Figure(figsize=(5, 3), dpi=100)
ax_acc = fig_acc.add_subplot(111)
ax_acc.set_title("Accelerometer")
ax_acc.set_ylim(-10, 10)
ax_acc.set_ylabel("m/s²")
ax_acc.set_xlabel("Time")
acc_data = collections.deque(maxlen=50)
line_acc, = ax_acc.plot([], [], color='blue')
canvas_acc = FigureCanvasTkAgg(fig_acc, master=charts_frame)
canvas_acc.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

# Altimeter chart
fig_alt = Figure(figsize=(5, 3), dpi=100)
ax_alt = fig_alt.add_subplot(111)
ax_alt.set_title("Altimeter")
ax_alt.set_ylim(0, 500)
ax_alt.set_ylabel("m")
ax_alt.set_xlabel("Time")
alt_data = collections.deque(maxlen=50)
line_alt, = ax_alt.plot([], [], color='green')
canvas_alt = FigureCanvasTkAgg(fig_alt, master=charts_frame)
canvas_alt.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

# -----------------------------
# Map frame (right)
# -----------------------------
map_frame = customtkinter.CTkFrame(root)
map_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
map_widget = tkintermapview.TkinterMapView(map_frame, width=800, height=800, corner_radius=0)
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

# -----------------------------
# Serial reading thread
# -----------------------------
def read_serial():
    while True:
        try:
            line = ser.readline().decode().strip()
            if line:
                # Expecting: LAT,LON,ACC,ALT
                parts = line.split(",")
                if len(parts) == 4:
                    lat, lon = float(parts[0]), float(parts[1])
                    acc_val, alt_val = float(parts[2]), float(parts[3])

                    # Update GUI safely
                    root.after(0, update_marker, lat, lon)

                    # Update charts
                    acc_data.append(acc_val)
                    alt_data.append(alt_val)

                    line_acc.set_data(range(len(acc_data)), acc_data)
                    ax_acc.set_xlim(0, max(50, len(acc_data)))
                    canvas_acc.draw()

                    line_alt.set_data(range(len(alt_data)), alt_data)
                    ax_alt.set_xlim(0, max(50, len(alt_data)))
                    canvas_alt.draw()
        except Exception as e:
            print("Error reading serial:", e)

threading.Thread(target=read_serial, daemon=True).start()

root.mainloop()
