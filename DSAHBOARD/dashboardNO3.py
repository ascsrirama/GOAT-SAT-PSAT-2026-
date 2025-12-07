
import math
import collections
import os 
import tempfile
## TRYING TO COMMIT

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle

from kivy_garden.mapview import MapView, MapMarker
import kivy_garden.mapview.view as mapview
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

from matplotlib.figure import Figure

print("HI THIS DASHBOARD WORKS")
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
        self.accent = (0.0, 0.8, 0.6, 1)      # teal-ish
        self.accent_soft = (0.2, 0.9, 0.8, 1)
        self.text_main = (0.9, 0.95, 1, 1)
        self.text_dim = (0.6, 0.7, 0.9, 1)

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
            text="[b]FAKE ESP: ONLINE[/b]",
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

        # Accelerometer chart
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

        # Altimeter chart
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

        # Map
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
            text="MAP: Centered on current ground track\nMODE: FAKE ESP STREAM",
            color=self.text_dim,
            font_size="12sp",
            halign="left",
        )

        info_panel.add_widget(self.orbit_label)
        info_panel.add_widget(self.map_hint_label)

        right_panel.add_widget(info_panel)

        # =============================
        #   FAKE ESP STATE & TIMER
        # =============================

        self.t = 0
        self.elapsed_time = 0.0

        # Update 10 times per second
        Clock.schedule_interval(self.update_fake_esp, 0.1)

    # ---------- Matplotlib styling helpers ----------
    def _style_fig(self, fig):
        fig.patch.set_facecolor((0.02, 0.02, 0.06, 1))

    def _style_axis(self, ax):
        ax.set_facecolor((0.03, 0.03, 0.09, 1))
        ax.tick_params(colors=self.text_dim[:3])
        for spine in ax.spines.values():
            spine.set_color(self.text_dim[:3])

    # ---------- Main fake ESP update loop ----------
    def update_fake_esp(self, dt):
        self.t += 1
        self.elapsed_time += dt

        # Smooth circular GPS motion
        lat = self.base_lat + self.radius * math.sin(self.t / 100.0)
        lon = self.base_lon + self.radius * math.cos(self.t / 100.0)

        # Smooth accelerometer signal
        acc_val = 5 * math.sin(self.t / 20.0)

        # Smooth altitude wave between ~100 and ~400 m
        alt_val = 250 + 150 * math.sin(self.t / 60.0)

        # --- Update map ---
        self.map_view.center_on(lat, lon)
        self.marker.lat = lat
        self.marker.lon = lon

        # --- Update accel chart ---
        self.acc_data.append(acc_val)
        self.acc_line.set_data(range(len(self.acc_data)), list(self.acc_data))
        self.acc_ax.set_xlim(0, max(50, len(self.acc_data)))
        self.acc_canvas.draw()

        # --- Update alt chart ---
        self.alt_data.append(alt_val)
        self.alt_line.set_data(range(len(self.alt_data)), list(self.alt_data))
        self.alt_ax.set_xlim(0, max(50, len(self.alt_data)))
        self.alt_canvas.draw()

        # --- Update status labels ---
        self.lat_label.text = f"LAT: {lat:.5f}"
        self.lon_label.text = f"LON: {lon:.5f}"
        self.alt_label.text = f"ALT: {alt_val:6.1f} m"
        self.acc_label.text = f"ACC: {acc_val:5.2f} m/s²"

        self.mission_time_label.text = f"[b]T+ {self.elapsed_time:5.1f} s[/b]"


class ESPDashboardApp(App):
    def build(self):
        self.title = "GOAT-SAT Mission Control"
        return Dashboard()


if __name__ == "__main__":
    ESPDashboardApp().run()
