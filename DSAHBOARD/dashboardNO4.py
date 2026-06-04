import math
import collections
import threading
import queue
import time

import serial  # pip install pyserial

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle

from kivy_garden.mapview import MapView, MapMarker
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from matplotlib.figure import Figure

print("GOAT-SAT dashboard starting...")

# ============================
#  SERIAL CONFIG – WINDOWS
# ============================
SERIAL_PORT = "COM21"   # <-- LoRa RX board on Windows
SERIAL_BAUD = 115200


# ============================
#  SERIAL READER THREAD
# ============================

class SerialReader(threading.Thread):
    """
    Reads lines from COM22 and pushes them into a queue.
    Expects lines that contain: LAT=...,LON=...
    e.g. 'RX Got 29 bytes (RSSI=-27, SNR=13): LAT=-36.853185,LON=174.769157'
    """

    def __init__(self, port, baudrate, line_queue):
        super().__init__(daemon=True)
        self.port = port
        self.baudrate = baudrate
        self.line_queue = line_queue
        self._stop_flag = threading.Event()

    def stop(self):
        self._stop_flag.set()

    def run(self):
        try:
            ser = serial.Serial(self.port, self.baudrate, timeout=1)
        except Exception as e:
            print(f"[SerialReader] Failed to open {self.port}: {e}")
            return

        print(f"[SerialReader] Listening on {self.port} @ {self.baudrate}")

        buffer = b""
        while not self._stop_flag.is_set():
            try:
                chunk = ser.read(128)
                if not chunk:
                    continue
                buffer += chunk
                # split on newlines
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    try:
                        text = line.decode(errors="ignore").strip()
                    except Exception:
                        continue
                    if text:
                        self.line_queue.put(text)
            except Exception as e:
                print(f"[SerialReader] Error: {e}")
                break

        try:
            ser.close()
        except Exception:
            pass

        print("[SerialReader] Stopped")


# ---------- Helper to give dark background to any layout ----------
class DarkPanel(BoxLayout):
    def __init__(self, bg_color=(0.05, 0.05, 0.08, 1), **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        with self.canvas.before:
            Color(*self.bg_color)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class Dashboard(DarkPanel):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", bg_color=(0.02, 0.02, 0.05, 1), **kwargs)

        # -----------------------------
        # COLORS / STYLE
        # -----------------------------
        self.accent = (0.0, 0.8, 0.6, 1)
        self.accent_soft = (0.2, 0.9, 0.8, 1)
        self.text_main = (0.9, 0.95, 1, 1)
        self.text_dim = (0.6, 0.7, 0.9, 1)

        # Queue for serial lines (from LoRa RX)
        self.serial_queue = queue.Queue()
        self.serial_last_fix_ts = 0.0
        self.current_lat = None
        self.current_lon = None

        # rolling history for smoothing
        self.lat_history = collections.deque(maxlen=10)
        self.lon_history = collections.deque(maxlen=10)

        # -----------------------------
        # TOP: MISSION HEADER
        # -----------------------------
        header = DarkPanel(
            orientation="horizontal",
            size_hint_y=0.08,
            bg_color=(0.05, 0.05, 0.12, 1),
        )

        self.title_label = Label(
            text="[b]GOAT-SAT • MISSION TELEMETRY[/b]",
            markup=True,
            color=self.text_main,
            font_size="22sp",
            halign="left",
            valign="middle",
        )

        self.mission_time_label = Label(
            text="[b]T+ 0.0 s[/b]",
            markup=True,
            color=self.accent_soft,
            font_size="18sp",
            halign="right",
            valign="middle",
        )

        header.add_widget(self.title_label)
        header.add_widget(self.mission_time_label)

        # -----------------------------
        # CENTER: MAIN BODY
        # -----------------------------
        body = DarkPanel(
            orientation="horizontal",
            bg_color=(0.02, 0.02, 0.05, 1),
        )

        # LEFT: Charts column
        charts_panel = DarkPanel(
            orientation="vertical",
            bg_color=(0.04, 0.04, 0.09, 1),
            size_hint_x=0.5,
            padding=5,
            spacing=8,
        )

        # RIGHT: Map + info
        right_panel = DarkPanel(
            orientation="vertical",
            bg_color=(0.03, 0.03, 0.07, 1),
            size_hint_x=0.5,
            padding=5,
            spacing=8,
        )

        body.add_widget(charts_panel)
        body.add_widget(right_panel)

        # -----------------------------
        # BOTTOM: STATUS BAR
        # -----------------------------
        status_bar = DarkPanel(
            orientation="horizontal",
            size_hint_y=0.08,
            bg_color=(0.05, 0.05, 0.12, 1),
            padding=[10, 2, 10, 2],
            spacing=20,
        )

        self.lat_label = Label(
            text="LAT: --",
            color=self.text_dim,
            font_size="14sp",
            halign="left",
        )
        self.lon_label = Label(
            text="LON: --",
            color=self.text_dim,
            font_size="14sp",
            halign="left",
        )
        self.alt_label = Label(
            text="ALT: -- m",
            color=self.text_dim,
            font_size="14sp",
            halign="left",
        )
        self.acc_label = Label(
            text="ACC: -- m/s²",
            color=self.text_dim,
            font_size="14sp",
            halign="left",
        )

        self.status_label = Label(
            text="[b]LORA RX: CONNECTING[/b]",
            markup=True,
            color=self.accent_soft,
            font_size="14sp",
            halign="right",
        )

        status_bar.add_widget(self.lat_label)
        status_bar.add_widget(self.lon_label)
        status_bar.add_widget(self.alt_label)
        status_bar.add_widget(self.acc_label)
        status_bar.add_widget(Widget())  # spacer
        status_bar.add_widget(self.status_label)

        # Add layout sections to root
        self.add_widget(header)
        self.add_widget(body)
        self.add_widget(status_bar)

        # =============================
        #   CHARTS SETUP (LEFT)
        # =============================

        # Accelerometer chart (fake)
        self.acc_fig = Figure(figsize=(5, 3), dpi=100)
        self._style_fig(self.acc_fig)
        self.acc_ax = self.acc_fig.add_subplot(111)
        self._style_axis(self.acc_ax)
        self.acc_ax.set_title("ACCELEROMETER", color=self.text_main[:3])
        self.acc_ax.set_ylim(-10, 10)
        self.acc_ax.set_ylabel("m/s²", color=self.text_dim[:3])
        self.acc_ax.set_xlabel("Time", color=self.text_dim[:3])

        self.acc_data = collections.deque(maxlen=50)
        (self.acc_line,) = self.acc_ax.plot([], [], color=self.accent)

        self.acc_canvas = FigureCanvasKivyAgg(self.acc_fig)
        charts_panel.add_widget(self.acc_canvas)

        # Altimeter chart (fake)
        self.alt_fig = Figure(figsize=(5, 3), dpi=100)
        self._style_fig(self.alt_fig)
        self.alt_ax = self.alt_fig.add_subplot(111)
        self._style_axis(self.alt_ax)
        self.alt_ax.set_title("ALTIMETER", color=self.text_main[:3])
        self.alt_ax.set_ylim(0, 500)
        self.alt_ax.set_ylabel("m", color=self.text_dim[:3])
        self.alt_ax.set_xlabel("Time", color=self.text_dim[:3])

        self.alt_data = collections.deque(maxlen=50)
        (self.alt_line,) = self.alt_ax.plot([], [], color=self.accent_soft)

        self.alt_canvas = FigureCanvasKivyAgg(self.alt_fig)
        charts_panel.add_widget(self.alt_canvas)

        # =============================
        #   MAP + INFO (RIGHT)
        # =============================

        # Initial fake base (Auckland-ish)
        self.base_lat = -36.8485
        self.base_lon = 174.7633
        self.radius = 0.001

        map_container = DarkPanel(
            orientation="vertical",
            bg_color=(0.02, 0.02, 0.06, 1),
            size_hint_y=0.85,
        )

        self.map_view = MapView(
            zoom=17,
            lat=self.base_lat,
            lon=self.base_lon,
        )
        map_container.add_widget(self.map_view)

        self.marker = MapMarker(lat=self.base_lat, lon=self.base_lon)
        self.map_view.add_marker(self.marker)

        right_panel.add_widget(map_container)

        # Telemetry info panel
        info_panel = DarkPanel(
            orientation="vertical",
            size_hint_y=0.15,
            bg_color=(0.03, 0.03, 0.09, 1),
            padding=[10, 4, 10, 4],
            spacing=2,
        )

        self.orbit_label = Label(
            text="[b]ORBIT: LOW EARTH (SIM)[/b]",
            markup=True,
            color=self.text_main,
            font_size="14sp",
            halign="left",
        )
        self.map_hint_label = Label(
            text="MAP: Real GPS from LoRa RX if available,\n"
                 "otherwise simulated circular track.",
            color=self.text_dim,
            font_size="12sp",
            halign="left",
        )

        info_panel.add_widget(self.orbit_label)
        info_panel.add_widget(self.map_hint_label)

        right_panel.add_widget(info_panel)

        # =============================
        #   STATE & TIMER
        # =============================

        self.t = 0
        self.elapsed_time = 0.0

        # Start serial reader thread
        self.serial_reader = SerialReader(
            port=SERIAL_PORT,
            baudrate=SERIAL_BAUD,
            line_queue=self.serial_queue,
        )
        self.serial_reader.start()

        # Update 10 times per second
        Clock.schedule_interval(self.update_telemetry, 0.1)

    # ---------- Matplotlib styling helpers ----------
    def _style_fig(self, fig):
        fig.patch.set_facecolor((0.02, 0.02, 0.06, 1))

    def _style_axis(self, ax):
        ax.set_facecolor((0.03, 0.03, 0.09, 1))
        ax.tick_params(colors=self.text_dim[:3])
        for spine in ax.spines.values():
            spine.set_color(self.text_dim[:3])

    # ---------- Parse lines from LoRa RX ----------
    def _consume_serial(self):
        """
        Pull all pending lines from the serial queue
        and update self.current_lat / self.current_lon
        when we see 'LAT=...,LON=...'.
        Handles lines like:
          'RX Got 29 bytes (RSSI=-27, SNR=13): LAT=-36.853185,LON=174.769157'
        """
        updated = False
        while not self.serial_queue.empty():
            line = self.serial_queue.get_nowait()
            # Debug so you can see what actually comes from COM22
            print("[RX LINE]", repr(line))

            if "LAT=" in line and "LON=" in line:
                try:
                    sub = line[line.index("LAT="):]  # keep from 'LAT=' onward
                    parts = sub.split(",")

                    lat_str = parts[0].split("=", 1)[1]
                    lon_str = parts[1].split("=", 1)[1]

                    lat = float(lat_str)
                    lon = float(lon_str)

                    # raw latest fix
                    self.current_lat = lat
                    self.current_lon = lon
                    self.serial_last_fix_ts = time.time()

                    # also feed history for smoothing
                    self.lat_history.append(lat)
                    self.lon_history.append(lon)

                    updated = True
                    print(f"[GPS PARSED] lat={lat}, lon={lon}")
                except Exception as e:
                    print(f"[Dashboard] Failed to parse GPS line '{line}': {e}")
        return updated

    # ---------- Main update loop ----------
    def update_telemetry(self, dt):
        self.t += 1
        self.elapsed_time += dt

        # 1) Check serial for new GPS fixes
        has_new_gps = self._consume_serial()

        # 2) Decide what lat/lon to display
        if (
            self.current_lat is not None
            and self.current_lon is not None
            and len(self.lat_history) > 0
        ):
            # Use smoothed GPS (average of last few fixes)
            lat = sum(self.lat_history) / len(self.lat_history)
            lon = sum(self.lon_history) / len(self.lon_history)
            self.status_label.text = "[b]LORA RX: ONLINE[/b]"
        else:
            # Fallback to simple circular simulation
            lat = self.base_lat + self.radius * math.sin(self.t / 100.0)
            lon = self.base_lon + self.radius * math.cos(self.t / 100.0)
            self.status_label.text = "[b]LORA RX: NO FIX[/b]"

        # 3) Fake accelerometer and altitude
        acc_val = 5 * math.sin(self.t / 20.0)
        alt_val = 250 + 150 * math.sin(self.t / 60.0)

        # --- Update map ---
        # If you want the map not to recenter every frame, comment next line
        self.map_view.center_on(lat, lon)
        self.marker.lat = lat
        self.marker.lon = lon

        # --- Update accel chart (fake) ---
        self.acc_data.append(acc_val)
        self.acc_line.set_data(range(len(self.acc_data)), list(self.acc_data))
        self.acc_ax.set_xlim(0, max(50, len(self.acc_data)))
        self.acc_canvas.draw()

        # --- Update alt chart (fake) ---
        self.alt_data.append(alt_val)
        self.alt_line.set_data(range(len(self.alt_data)), list(self.alt_data))
        self.alt_ax.set_xlim(0, max(50, len(self.alt_data)))
        self.alt_canvas.draw()

        # --- Update status labels ---
        self.lat_label.text = f"LAT: {lat:.6f}"
        self.lon_label.text = f"LON: {lon:.6f}"
        self.alt_label.text = f"ALT: {alt_val:6.1f} m"
        self.acc_label.text = f"ACC: {acc_val:5.2f} m/s²"

        self.mission_time_label.text = f"[b]T+ {self.elapsed_time:5.1f} s[/b]"

    def cleanup(self):
        try:
            if hasattr(self, "serial_reader") and self.serial_reader is not None:
                self.serial_reader.stop()
        except Exception:
            pass


class ESPDashboardApp(App):
    def build(self):
        self.title = "GOAT-SAT Mission Control"
        self.dashboard = Dashboard()
        return self.dashboard

    def on_stop(self):
        if hasattr(self, "dashboard"):
            self.dashboard.cleanup()


if __name__ == "__main__":
    ESPDashboardApp().run()

