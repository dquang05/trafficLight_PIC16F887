from dataclasses import dataclass

MODE_NAMES = {
    0: "AUTO",
    1: "MANUAL",
    2: "FLASHING",
}

@dataclass(slots=True)
class TrafficState:
    mode: int
    red1: int
    yellow1: int
    green1: int
    countdown1: int
    red2: int
    yellow2: int
    green2: int
    countdown2: int

    @property
    def mode_text(self) -> str:
        return MODE_NAMES.get(self.mode, f"UNKNOWN ({self.mode})")