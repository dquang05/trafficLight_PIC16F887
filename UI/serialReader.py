import queue
import threading
import time
import serial

from parser import parse_uart_line


class SerialService:
    def __init__(self, event_queue: queue.Queue):
        self.event_queue = event_queue
        self._ser = None
        self._thread = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def connect(self, port: str, baudrate: int = 9600) -> bool:
        self.disconnect(silent=True)

        try:
            ser = serial.Serial(port, baudrate, timeout=0.2)
            time.sleep(1.0)
            ser.reset_input_buffer()
        except Exception as e:
            self.event_queue.put(("status", f"Serial error: {e}"))
            return False

        with self._lock:
            self._ser = ser

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._thread.start()

        self.event_queue.put(("status", f"Connected: {port} @ {baudrate}"))
        return True

    def disconnect(self, silent: bool = False):
        self._stop_event.set()

        with self._lock:
            ser = self._ser
            self._ser = None

        if ser is not None:
            try:
                ser.close()
            except Exception:
                pass

        if not silent:
            self.event_queue.put(("status", "Disconnected"))

    def send_command(self, cmd: str) -> bool:
        cmd = cmd.strip()
        if not cmd:
            return False

        with self._lock:
            if self._ser is None or not self._ser.is_open:
                self.event_queue.put(("status", "Not connected"))
                return False

            try:
                self._ser.write((cmd + "\n").encode())
                self.event_queue.put(("status", f"Sent command: {cmd}"))
                return True
            except Exception as e:
                self.event_queue.put(("status", f"Send error: {e}"))
                return False

    def _reader_loop(self):
        while not self._stop_event.is_set():
            with self._lock:
                ser = self._ser

            if ser is None:
                break

            try:
                raw = ser.readline()
                if not raw:
                    continue

                line = raw.decode(errors="ignore").strip()
                state = parse_uart_line(line)

                if state is not None:
                    self.event_queue.put(("state", state))
                else:
                    self.event_queue.put(("raw", line))

            except Exception as e:
                self.event_queue.put(("status", f"Read error: {e}"))
                break

    def close(self):
        self.disconnect()