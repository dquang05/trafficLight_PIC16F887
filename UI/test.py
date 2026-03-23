import serial
import time

PORT = "COM5"      # đổi lại nếu cần
BAUD = 9600

ser = serial.Serial(PORT, BAUD, timeout=0.2)
time.sleep(2)  # chờ cổng ổn định
ser.reset_input_buffer()

print(f"Listening on {PORT} @ {BAUD}...")

while True:
    data = ser.read_all()
    if data:
        print("RAW:", repr(data))
    time.sleep(0.1)