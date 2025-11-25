# import tkinter as tk
# from tkinter import ttk
# import requests
# import threading
# import time

# ESP_URL = "http://192.168.1.100/temperature"     # <-- change this to your ESP8266 IP

# class TempDashboard:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("ESP8266 Temperature Dashboard")
#         self.root.geometry("400x250")
#         self.root.configure(bg="#1e1e1e")

#         style = ttk.Style()
#         style.theme_use("clam")

#         # Title Label
#         self.title_label = tk.Label(
#             root, 
#             text="ESP8266 Temperature Monitor", 
#             font=("Segoe UI", 16, "bold"), 
#             fg="white", 
#             bg="#1e1e1e"
#         )
#         self.title_label.pack(pady=10)

#         # Temperature display
#         self.temp_var = tk.StringVar(value="--- °C")
#         self.temp_label = tk.Label(
#             root,
#             textvariable=self.temp_var,
#             font=("Segoe UI", 40),
#             fg="#00ff7f",
#             bg="#1e1e1e"
#         )
#         self.temp_label.pack(pady=10)

#         # Status label
#         self.status_var = tk.StringVar(value="Waiting for update...")
#         self.status_label = tk.Label(root, textvariable=self.status_var, fg="gray", bg="#1e1e1e")
#         self.status_label.pack()

#         # Refresh interval
#         self.interval = 2  # seconds

#         # Start background update thread
#         self.update_thread = threading.Thread(target=self.update_temp_loop, daemon=True)
#         self.update_thread.start()

#     def get_temperature(self):
#         try:
#             r = requests.get(ESP_URL, timeout=2)
#             data = r.text.strip()

#             # If ESP sends JSON → uncomment:
#             # data = r.json()["temperature"]

#             return float(data)

#         except Exception as e:
#             self.status_var.set(f"Error: {e}")
#             return None

#     def update_temp_loop(self):
#         while True:
#             temp = self.get_temperature()
#             if temp is not None:
#                 self.temp_var.set(f"{temp:.1f} °C")
#                 self.status_var.set("Last update: ok")

#             time.sleep(self.interval)


# root = tk.Tk()
# app = TempDashboard(root)
# root.mainloop()


import tkinter as tk
import requests
import threading
import time

ESP_URL = "http://192.168.4.1/data"   # ESP8266 Access Point IP

class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP8266 DHT22 Monitor")
        self.root.geometry("350x220")
        self.root.configure(bg="#1e1e1e")

        # Temperature
        self.temp_var = tk.StringVar(value="-- °C")
        tk.Label(root, text="Temperature", font=("Arial", 14), fg="white", bg="#1e1e1e").pack()
        tk.Label(root, textvariable=self.temp_var, font=("Arial", 36), fg="#00ff88", bg="#1e1e1e").pack()

        # Humidity
        self.hum_var = tk.StringVar(value="-- %")
        tk.Label(root, text="Humidity", font=("Arial", 14), fg="white", bg="#1e1e1e").pack()
        tk.Label(root, textvariable=self.hum_var, font=("Arial", 36), fg="#00aaff", bg="#1e1e1e").pack()

        # Background update
        threading.Thread(target=self.update_loop, daemon=True).start()

    def update_loop(self):
        while True:
            try:
                r = requests.get(ESP_URL, timeout=2)
                data = r.json()

                self.temp_var.set(f"{data['temperature']:.1f} °C")
                self.hum_var.set(f"{data['humidity']:.1f} %")

            except Exception as e:
                self.temp_var.set("ERR")
                self.hum_var.set("ERR")

            time.sleep(2)

root = tk.Tk()
Dashboard(root)
root.mainloop()
