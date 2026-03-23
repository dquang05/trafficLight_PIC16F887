import queue
import tkinter as tk

from serialReader import SerialService
from ui import TrafficAppUI


def main():
    event_queue = queue.Queue()
    serial_service = SerialService(event_queue)

    root = tk.Tk()
    app = TrafficAppUI(root, event_queue, serial_service)

    def on_close():
        serial_service.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()