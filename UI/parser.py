from models import TrafficState

def parse_uart_line(line: str):
    line = line.strip()
    if not line:
        return None

    parts = [p.strip() for p in line.split(",")]
    if len(parts) != 9:
        return None

    try:
        vals = list(map(int, parts))
    except ValueError:
        return None

    return TrafficState(
        mode=vals[0],
        red1=vals[1],
        yellow1=vals[2],
        green1=vals[3],
        countdown1=vals[4],
        red2=vals[5],
        yellow2=vals[6],
        green2=vals[7],
        countdown2=vals[8],
    )