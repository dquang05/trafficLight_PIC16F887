import queue
import tkinter as tk
from tkinter import ttk

from models import TrafficState


ROAD_COLOR = "#0b1b2b"
LANE_COLOR = "white"
BG_COLOR = "#d9d9d9"


class LightGroup:
    def __init__(
        self,
        canvas: tk.Canvas,
        x: int,
        y: int,
        title: str,
        orientation: str = "south",   # south / north / east / west
        title_side: str = "top",      # top / bottom / left / right
        count_side: str = "bottom",   # top / bottom / left / right
    ):
        self.canvas = canvas
        self.orientation = orientation

        vertical = orientation in ("south", "north")

        if vertical:
            body_left, body_top = x - 28, y - 67
            body_right, body_bottom = x + 28, y + 67
        else:
            body_left, body_top = x - 67, y - 28
            body_right, body_bottom = x + 67, y + 28

        # Housing
        self.canvas.create_rectangle(
            body_left, body_top, body_right, body_bottom,
            fill="#1f2937", outline=""
        )

        def lamp(cx, cy, off_color):
            return self.canvas.create_oval(
                cx - 16, cy - 16, cx + 16, cy + 16,
                fill=off_color, outline=""
            )

        # Bulbs by orientation
        if orientation == "south":
            self.red = lamp(x, y - 38, "#4b0000")
            self.yellow = lamp(x, y, "#5a4a00")
            self.green = lamp(x, y + 38, "#003b14")

        elif orientation == "north":
            self.green = lamp(x, y - 38, "#003b14")
            self.yellow = lamp(x, y, "#5a4a00")
            self.red = lamp(x, y + 38, "#4b0000")

        elif orientation == "east":
            self.red = lamp(x - 38, y, "#4b0000")
            self.yellow = lamp(x, y, "#5a4a00")
            self.green = lamp(x + 38, y, "#003b14")

        elif orientation == "west":
            self.green = lamp(x - 38, y, "#003b14")
            self.yellow = lamp(x, y, "#5a4a00")
            self.red = lamp(x + 38, y, "#4b0000")

        else:
            raise ValueError(f"Unknown orientation: {orientation}")

        # Title position
        if title_side == "top":
            tx, ty, anchor = x, body_top - 18, "center"
        elif title_side == "bottom":
            tx, ty, anchor = x, body_bottom + 18, "center"
        elif title_side == "left":
            tx, ty, anchor = body_left - 16, y, "e"
        else:  # right
            tx, ty, anchor = body_right + 16, y, "w"

        self.canvas.create_text(
            tx, ty,
            text=title,
            font=("Segoe UI", 11, "bold"),
            fill="black",
            anchor=anchor
        )

        # Countdown box position
        if count_side == "top":
            x1, y1, x2, y2 = x - 34, body_top - 50, x + 34, body_top - 14
            cx, cy = x, body_top - 32
        elif count_side == "bottom":
            x1, y1, x2, y2 = x - 34, body_bottom + 14, x + 34, body_bottom + 50
            cx, cy = x, body_bottom + 32
        elif count_side == "left":
            x1, y1, x2, y2 = body_left - 78, y - 18, body_left - 10, y + 18
            cx, cy = body_left - 44, y
        else:  # right
            x1, y1, x2, y2 = body_right + 10, y - 18, body_right + 78, y + 18
            cx, cy = body_right + 44, y

        self.count_box = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill="#091226", outline=""
        )
        self.count_text = self.canvas.create_text(
            cx, cy,
            text="--",
            font=("Consolas", 18, "bold"),
            fill="#ff6666"
        )

    def update(self, red: int, yellow: int, green: int, countdown: int | None):
        self.canvas.itemconfig(self.red, fill="#ff2d2d" if red else "#4b0000")
        self.canvas.itemconfig(self.yellow, fill="#ffd21f" if yellow else "#5a4a00")
        self.canvas.itemconfig(self.green, fill="#2ee66b" if green else "#003b14")

        if countdown is None:
            self.canvas.itemconfig(self.count_text, text="")
        else:
            self.canvas.itemconfig(self.count_text, text=str(countdown))

class TrafficAppUI:
    def __init__(self, root: tk.Tk, event_queue: queue.Queue, serial_service):
        self.root = root
        self.event_queue = event_queue
        self.serial_service = serial_service

        self.root.title("Traffic Light Control & Monitor")
        self.root.geometry("1060x900")
        self.root.configure(bg=BG_COLOR)

        self.mode_var = tk.StringVar(value="MODE: ---")
        self.status_var = tk.StringVar(value="Disconnected")
        self.port_var = tk.StringVar(value="COM5")
        self.baud_var = tk.StringVar(value="9600")

        self._build_topbar()
        self._build_canvas()
        self._build_controls()

        self._poll_events()

    def _build_topbar(self):
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")

        ttk.Label(top, text="Port:").pack(side="left")
        ttk.Entry(top, textvariable=self.port_var, width=10).pack(side="left", padx=4)

        ttk.Label(top, text="Baud:").pack(side="left", padx=(10, 0))
        ttk.Entry(top, textvariable=self.baud_var, width=10).pack(side="left", padx=4)

        ttk.Button(top, text="Connect", command=self._on_connect).pack(side="left", padx=6)
        ttk.Button(top, text="Disconnect", command=self._on_disconnect).pack(side="left", padx=2)

        ttk.Label(
            top, textvariable=self.mode_var,
            font=("Segoe UI", 18, "bold")
        ).pack(side="right")

    def _build_canvas(self):
        self.canvas = tk.Canvas(
            self.root, width=1000, height=700,
            bg=BG_COLOR, highlightthickness=0
        )
        self.canvas.pack(pady=8)

        # Road bounds
        v_left, v_right = 420, 580
        v_top, v_bottom = 90, 610

        h_left, h_right = 80, 940
        h_top, h_bottom = 260, 420

        # Roads
        self.canvas.create_rectangle(v_left, v_top, v_right, v_bottom, fill=ROAD_COLOR, outline="")
        self.canvas.create_rectangle(h_left, h_top, h_right, h_bottom, fill=ROAD_COLOR, outline="")

        # Lane dashed lines
        mid_x = (v_left + v_right) // 2
        mid_y = (h_top + h_bottom) // 2

        self.canvas.create_line(mid_x, v_top, mid_x, h_top, fill=LANE_COLOR, width=3, dash=(16, 12))
        self.canvas.create_line(mid_x, h_bottom, mid_x, v_bottom, fill=LANE_COLOR, width=3, dash=(16, 12))
        self.canvas.create_line(h_left, mid_y, v_left, mid_y, fill=LANE_COLOR, width=3, dash=(16, 12))
        self.canvas.create_line(v_right, mid_y, h_right, mid_y, fill=LANE_COLOR, width=3, dash=(16, 12))

        # Crosswalks
        self._draw_crosswalk_vertical(v_left - 18, h_top, bars=14)
        self._draw_crosswalk_vertical(v_right - 2, h_top, bars=14)
        self._draw_crosswalk_horizontal(v_left, h_top - 18, bars=14)
        self._draw_crosswalk_horizontal(v_left, h_bottom - 2, bars=14)

        # Center guide box
        self.canvas.create_rectangle(v_left, h_top, v_right, h_bottom, outline="#6b7280")

        # Traffic lights
        # North: dọc bên trái, G-Y-R
        self.north = LightGroup(
            self.canvas,
            345, 130,
            "North",
            orientation="north",
            title_side="top",
            count_side="left"
        )

        # East: ngang phía trên, R-Y-G
        # đổi title sang right để không đè với count ở top
        self.east = LightGroup(
            self.canvas,
            815, 190,
            "East",
            orientation="east",
            title_side="right",
            count_side="top"
        )

        # South: dọc bên phải, R-Y-G
        self.south = LightGroup(
            self.canvas,
            655, 580,
            "South",
            orientation="south",
            title_side="bottom",
            count_side="right"
        )

        # West: ngang phía dưới, G-Y-R
        # đổi title sang left để không đè với count ở bottom
        self.west = LightGroup(
            self.canvas,
            215, 530,
            "West",
            orientation="west",
            title_side="left",
            count_side="bottom"
        )

    def _draw_crosswalk_vertical(self, x: int, y: int, bars: int = 14):
        for i in range(bars):
            self.canvas.create_rectangle(
                x, y + i * 12, x + 20, y + i * 12 + 7,
                fill="white", outline=""
            )

    def _draw_crosswalk_horizontal(self, x: int, y: int, bars: int = 14):
        for i in range(bars):
            self.canvas.create_rectangle(
                x + i * 12, y, x + i * 12 + 7, y + 20,
                fill="white", outline=""
            )

    def _build_controls(self):
        wrap = ttk.Frame(self.root, padding=10)
        wrap.pack(fill="x")

        left = ttk.LabelFrame(wrap, text="Mode Control", padding=10)
        left.pack(side="left", padx=10)

        ttk.Button(left, text="AUTO", width=12, command=lambda: self.serial_service.send_command("A")).pack(side="left", padx=4)
        ttk.Button(left, text="MANUAL", width=12, command=lambda: self.serial_service.send_command("N")).pack(side="left", padx=4)
        ttk.Button(left, text="FLASHING", width=12, command=lambda: self.serial_service.send_command("F")).pack(side="left", padx=4)
        ttk.Button(left, text="NEXT MODE", width=12, command=lambda: self.serial_service.send_command("M")).pack(side="left", padx=4)

        right = ttk.LabelFrame(wrap, text="Manual Control", padding=10)
        right.pack(side="left", padx=10)

        ttk.Button(right, text="ROAD 1 GO", width=14, command=lambda: self.serial_service.send_command("R1")).pack(side="left", padx=4)
        ttk.Button(right, text="ROAD 2 GO", width=14, command=lambda: self.serial_service.send_command("R2")).pack(side="left", padx=4)

        status = ttk.Frame(self.root, padding=10)
        status.pack(fill="x")
        ttk.Label(status, textvariable=self.status_var, font=("Segoe UI", 10)).pack()

    def _on_connect(self):
        port = self.port_var.get().strip()
        try:
            baud = int(self.baud_var.get().strip())
        except ValueError:
            self.status_var.set("Baud rate không hợp lệ")
            return

        self.serial_service.connect(port, baud)

    def _on_disconnect(self):
        self.serial_service.disconnect()

    def apply_state(self, state: TrafficState):
        self.mode_var.set(f"MODE: {state.mode_text}")

        # AUTO: hiện countdown
        if state.mode == 0:
            c1 = state.countdown1
            c2 = state.countdown2
        else:
            # MANUAL / FLASHING: tắt countdown như LED 7 đoạn thật
            c1 = None
            c2 = None

        # Road 1 -> North + South
        self.north.update(state.red1, state.yellow1, state.green1, c1)
        self.south.update(state.red1, state.yellow1, state.green1, c1)

        # Road 2 -> West + East
        self.west.update(state.red2, state.yellow2, state.green2, c2)
        self.east.update(state.red2, state.yellow2, state.green2, c2)

        self.status_var.set("Receiving UART data")

    def _poll_events(self):
        try:
            while True:
                kind, payload = self.event_queue.get_nowait()

                if kind == "state":
                    self.apply_state(payload)
                elif kind == "status":
                    self.status_var.set(payload)
                elif kind == "raw":
                    self.status_var.set(f"Ignored frame: {payload}")
        except queue.Empty:
            pass

        self.root.after(20, self._poll_events)