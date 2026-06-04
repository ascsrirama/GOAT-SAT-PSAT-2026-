# import re
# import glob
# import threading
# import queue
# import time
# import serial

# from kivy.app import App
# from kivy.clock import Clock
# from kivy.uix.boxlayout import BoxLayout
# from kivy_garden.mapview import MapView, MapMarker


# SERIAL_BAUD = 115200
# GPS_RE = re.compile(r"LAT=([+-]?\d+\.\d+),LON=([+-]?\d+\.\d+)")


# def find_serial_port(prefer=None):
#     if prefer:
#         return prefer
#     cands = sorted(glob.glob("/dev/ttyUSB*")) + sorted(glob.glob("/dev/ttyACM*"))
#     return cands[0] if cands else None


# SERIAL_PORT = find_serial_port("/dev/ttyUSB0")  # change to None to auto-detect
# print("[MAIN] SERIAL_PORT =", SERIAL_PORT)


# class SerialReader(threading.Thread):
#     def __init__(self, port, baudrate, out_q):
#         super().__init__(daemon=True)
#         self.port = port
#         self.baudrate = baudrate
#         self.out_q = out_q
#         self.stop_flag = threading.Event()

#     def stop(self):
#         self.stop_flag.set()

#     def run(self):
#         print(f"[SER] opening {self.port} @ {self.baudrate}")
#         if not self.port:
#             print("[SER] no port found")
#             return
#         try:
#             ser = serial.Serial(self.port, self.baudrate, timeout=1)
#             ser.reset_input_buffer()
#             print("[SER] opened OK")
#         except Exception as e:
#             print("[SER] open failed:", repr(e))
#             return

#         while not self.stop_flag.is_set():
#             try:
#                 line = ser.readline()
#                 if not line:
#                     continue
#                 s = line.decode(errors="ignore").strip()
#                 if s:
#                     self.out_q.put(s)
#             except Exception as e:
#                 print("[SER] read error:", repr(e))
#                 break

#         try:
#             ser.close()
#         except Exception:
#             pass
#         print("[SER] closed")


# class RXMap(BoxLayout):
#     def __init__(self, **kwargs):
#         super().__init__(orientation="vertical", **kwargs)
#         self.q = queue.Queue()
#         self.last_fix_ts = 0.0
#         self.lat = None
#         self.lon = None

#         self.map = MapView(zoom=16, lat=-36.8485, lon=174.7633)
#         self.marker = MapMarker(lat=-36.8485, lon=174.7633)
#         self.map.add_marker(self.marker)
#         self.add_widget(self.map)

#         self.reader = SerialReader(SERIAL_PORT, SERIAL_BAUD, self.q)
#         self.reader.start()

#         Clock.schedule_interval(self.update, 0.1)

#     def update(self, dt):
#         updated = False
#         while not self.q.empty():
#             s = self.q.get_nowait()
#             if "OnRxTimeout" in s:
#                 continue

#             m = GPS_RE.search(s)
#             if m:
#                 self.lat = float(m.group(1))
#                 self.lon = float(m.group(2))
#                 self.last_fix_ts = time.time()
#                 updated = True
#                 print("[GPS]", self.lat, self.lon)

#         fresh = (time.time() - self.last_fix_ts) < 5.0
#         if updated and self.lat is not None and self.lon is not None and fresh:
#             self.marker.lat = self.lat
#             self.marker.lon = self.lon
#             self.map.center_on(self.lat, self.lon)

#     def cleanup(self):
#         try:
#             self.reader.stop()
#         except Exception:
#             pass


# class GoatSatMapApp(App):
#     def build(self):
#         self.ui = RXMap()
#         return self.ui

#     def on_stop(self):
#         if hasattr(self, "ui"):
#             self.ui.cleanup()


# if __name__ == "__main__":
#     GoatSatMapApp().run()

import re
import glob
import threading
import queue
import time
from collections import deque

import serial

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle, Line

from kivy_garden.mapview import MapView, MapMarker


SERIAL_BAUD = 115200

GPS_RE = re.compile(r"LAT=([+-]?\d+\.\d+),LON=([+-]?\d+\.\d+)")
RSSI_RE = re.compile(r"RSSI=([+-]?\d+)")
SNR_RE  = re.compile(r"SNR=([+-]?\d+)")


def find_serial_port(prefer=None):
    if prefer:
        return prefer
    cands = sorted(glob.glob("/dev/ttyUSB*")) + sorted(glob.glob("/dev/ttyACM*"))
    return cands[0] if cands else None


SERIAL_PORT = find_serial_port("/dev/ttyUSB1")  # set None to auto-detect first port
print("[MAIN] SERIAL_PORT =", SERIAL_PORT)


class SerialReader(threading.Thread):
    def __init__(self, port, baudrate, out_q):
        super().__init__(daemon=True)
        self.port = port
        self.baudrate = baudrate
        self.out_q = out_q
        self.stop_flag = threading.Event()

    def stop(self):
        self.stop_flag.set()

    def run(self):
        print(f"[SER] opening {self.port} @ {self.baudrate}")
        if not self.port:
            print("[SER] no port found")
            return
        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=1)
            ser.reset_input_buffer()
            print("[SER] opened OK")
        except Exception as e:
            print("[SER] open failed:", repr(e))
            return

        while not self.stop_flag.is_set():
            try:
                line = ser.readline()
                if not line:
                    continue
                s = line.decode(errors="ignore").strip()
                if s:
                    self.out_q.put(s)
            except Exception as e:
                print("[SER] read error:", repr(e))
                break

        try:
            ser.close()
        except Exception:
            pass
        print("[SER] closed")


class Card(BoxLayout):
    def __init__(self, bg, radius=18, pad=12, **kwargs):
        super().__init__(**kwargs)
        self.bg = bg
        self.radius = radius
        self.padding = [dp(pad), dp(pad), dp(pad), dp(pad)]
        with self.canvas.before:
            Color(*self.bg)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(self.radius)])
        self.bind(pos=self._upd, size=self._upd)

    def _upd(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class TrailOverlay(Widget):
    def __init__(self, max_pts=120, **kwargs):
        super().__init__(**kwargs)
        self.pts = deque(maxlen=max_pts)

    def add_point(self, x, y):
        self.pts.append((x, y))
        self.redraw()

    def redraw(self):
        self.canvas.clear()
        if len(self.pts) < 2:
            return
        with self.canvas:
            Color(0.0, 0.85, 0.65, 0.55)
            flat = []
            for x, y in self.pts:
                flat += [x, y]
            Line(points=flat, width=dp(2))


class RXMapMission(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(10), padding=dp(10), **kwargs)

        # Theme
        self.bg = (0.03, 0.035, 0.05, 1)      # window bg
        self.card = (0.06, 0.07, 0.10, 1)     # panels
        self.card2 = (0.05, 0.055, 0.09, 1)   # header/footer
        self.text = (0.92, 0.95, 1.0, 1)
        self.dim = (0.62, 0.70, 0.85, 1)
        self.accent = (0.0, 0.85, 0.65, 1)
        self.warn = (1.0, 0.55, 0.25, 1)

        with self.canvas.before:
            Color(*self.bg)
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[0])
        self.bind(pos=self._upd_bg, size=self._upd_bg)

        # State
        self.q = queue.Queue()
        self.last_fix_ts = 0.0
        self.lat = None
        self.lon = None
        self.rssi = None
        self.snr = None

        self.lat_hist = deque(maxlen=8)
        self.lon_hist = deque(maxlen=8)

        # UI
        self._build_ui()

        # Serial
        self.reader = SerialReader(SERIAL_PORT, SERIAL_BAUD, self.q)
        self.reader.start()

        Clock.schedule_interval(self.update, 0.1)
        Clock.schedule_interval(self.update_clock, 0.25)

    def _upd_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _build_ui(self):
        # Header
        header = Card(bg=self.card2, radius=18, pad=14, size_hint_y=None, height=dp(68))
        header.orientation = "horizontal"
        header.spacing = dp(12)

        title = Label(
            text="[b]TEAM PLONK • MISSION CONTROL[/b]",
            markup=True,
            color=self.text,
            font_size="20sp",
            halign="left",
            valign="middle",
        )
        title.bind(size=lambda *_: setattr(title, "text_size", title.size))

        self.clock_label = Label(
            text="--:--:--",
            color=self.accent,
            font_size="16sp",
            halign="right",
            valign="middle",
        )
        self.clock_label.bind(size=lambda *_: setattr(self.clock_label, "text_size", self.clock_label.size))

        header.add_widget(title)
        header.add_widget(Widget())
        header.add_widget(self.clock_label)

        # Body: map + HUD overlay
        body = Card(bg=self.card, radius=18, pad=10)
        body.orientation = "vertical"

        container = FloatLayout()

        self.map = MapView(zoom=16, lat=-36.8485, lon=174.7633)
        container.add_widget(self.map)

        self.marker = MapMarker(lat=-36.8485, lon=174.7633)
        self.map.add_marker(self.marker)

        self.trail = TrailOverlay()
        container.add_widget(self.trail)

        # HUD overlay (top-left)
        hud = Card(bg=(0.02, 0.02, 0.03, 0.75), radius=16, pad=12,
                   size_hint=(None, None), size=(dp(360), dp(140)),
                   pos_hint={"x": 0.02, "top": 0.98})
        hud.orientation = "vertical"
        hud.spacing = dp(6)

        self.status_label = Label(
            text="[b]LORA RX: CONNECTING[/b]",
            markup=True,
            color=self.dim,
            font_size="14sp",
            halign="left",
            valign="middle",
        )
        self.status_label.bind(size=lambda *_: setattr(self.status_label, "text_size", self.status_label.size))

        self.latlon_label = Label(
            text="LAT: --\nLON: --",
            color=self.text,
            font_size="18sp",
            halign="left",
            valign="middle",
        )
        self.latlon_label.bind(size=lambda *_: setattr(self.latlon_label, "text_size", self.latlon_label.size))

        self.radio_label = Label(
            text="RSSI: -- dBm   SNR: -- dB   AGE: -- s",
            color=self.dim,
            font_size="13sp",
            halign="left",
            valign="middle",
        )
        self.radio_label.bind(size=lambda *_: setattr(self.radio_label, "text_size", self.radio_label.size))

        hud.add_widget(self.status_label)
        hud.add_widget(self.latlon_label)
        hud.add_widget(self.radio_label)

        container.add_widget(hud)
        body.add_widget(container)

        # Footer
        footer = Card(bg=self.card2, radius=18, pad=12, size_hint_y=None, height=dp(66))
        footer.orientation = "horizontal"
        footer.spacing = dp(12)

        self.footer_left = Label(
            text="PORT: --",
            color=self.dim,
            font_size="13sp",
            halign="left",
            valign="middle",
        )
        self.footer_left.bind(size=lambda *_: setattr(self.footer_left, "text_size", self.footer_left.size))

        self.footer_right = Label(
            text="[b]READY[/b]",
            markup=True,
            color=self.accent,
            font_size="13sp",
            halign="right",
            valign="middle",
        )
        self.footer_right.bind(size=lambda *_: setattr(self.footer_right, "text_size", self.footer_right.size))

        footer.add_widget(self.footer_left)
        footer.add_widget(Widget())
        footer.add_widget(self.footer_right)

        self.add_widget(header)
        self.add_widget(body)
        self.add_widget(footer)

        self.footer_left.text = f"PORT: {SERIAL_PORT or 'NONE'}  •  BAUD: {SERIAL_BAUD}"

    def update_clock(self, dt):
        self.clock_label.text = time.strftime("%H:%M:%S")

    def _consume(self):
        updated = False
        while not self.q.empty():
            s = self.q.get_nowait()
            if "OnRxTimeout" in s:
                continue

            m = GPS_RE.search(s)
            if not m:
                continue

            self.lat = float(m.group(1))
            self.lon = float(m.group(2))
            self.last_fix_ts = time.time()

            rm = RSSI_RE.search(s)
            sm = SNR_RE.search(s)
            self.rssi = int(rm.group(1)) if rm else self.rssi
            self.snr = int(sm.group(1)) if sm else self.snr

            self.lat_hist.append(self.lat)
            self.lon_hist.append(self.lon)
            updated = True
            print("[GPS]", self.lat, self.lon, "RSSI", self.rssi, "SNR", self.snr)
        return updated

    def update(self, dt):
        self._consume()

        age = time.time() - self.last_fix_ts if self.last_fix_ts else 9999.0
        online = age < 5.0

        if online and self.lat_hist:
            lat = sum(self.lat_hist) / len(self.lat_hist)
            lon = sum(self.lon_hist) / len(self.lon_hist)

            self.marker.lat = lat
            self.marker.lon = lon
            self.map.center_on(lat, lon)

            # trail uses marker pixel pos
            try:
                px, py = self.map.get_window_xy_from(lat, lon, self.map.zoom)
                self.trail.add_point(px, py)
            except Exception:
                pass

            self.status_label.text = "[b]LORA RX: ONLINE[/b]"
            self.status_label.color = self.accent
            self.latlon_label.text = f"LAT: {lat:.6f}\nLON: {lon:.6f}"
        else:
            self.status_label.text = "[b]LORA RX: NO FIX[/b]"
            self.status_label.color = self.warn
            if self.lat is not None and self.lon is not None:
                self.latlon_label.text = f"LAT: {self.lat:.6f}\nLON: {self.lon:.6f}"
            else:
                self.latlon_label.text = "LAT: --\nLON: --"

        rssi_txt = f"{self.rssi} dBm" if self.rssi is not None else "-- dBm"
        snr_txt = f"{self.snr} dB" if self.snr is not None else "-- dB"
        self.radio_label.text = f"RSSI: {rssi_txt}   SNR: {snr_txt}   AGE: {age:0.1f} s"

        self.footer_right.text = "[b]RX OK[/b]" if online else "[b]WAITING...[/b]"
        self.footer_right.color = self.accent if online else self.warn

    def cleanup(self):
        try:
            self.reader.stop()
        except Exception:
            pass


class PlonkMissionApp(App):
    def build(self):
        self.title = "TEAM PLONK Mission Control"
        self.ui = RXMapMission()
        return self.ui

    def on_stop(self):
        if hasattr(self, "ui"):
            self.ui.cleanup()


if __name__ == "__main__":
    PlonkMissionApp().run()

