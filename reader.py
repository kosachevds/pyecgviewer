import struct
import math


class Record(object):
    def __init__(self, signals, rate, mv_per_unit):
        self.signals = signals
        self.mv_per_unit = mv_per_unit
        self.rate = rate
        self.count = len(signals)
        self.size = len(signals[0])


def read_cts(filename, duration=None):
    if duration is None:
        duration = 1
    with open(filename) as record_file:
        lines = record_file.readlines()
    size = len(lines)
    signals = [[] for _ in range(8)]
    for line in lines:
        for i, item in enumerate(line.split()):
            signals[i].append(int(item))
    rate = 1000
    multiplier = int(math.ceil(duration * rate / size))
    signals = [(item * multiplier)[:duration * rate] for item in signals]
    for i in range(2, 6):
        signals.insert(i, None)
    return Record(signals, rate, 1e-3)


def read_cse(filename):
    with open(filename, "rb") as record_file:
        record_file.seek(25, 0)
        if record_file.read() == ord("6"):
            count = 6
        else:
            count = 12
        record_file.seek(36, 0)
        size = int(record_file.read(4).decode("ascii"))
        record_file.seek(3000, 0)
        values = struct.unpack(">" + "h" * (size * count),
                               record_file.read(size * count * 2))
    signals = [[] for _ in range(count)]
    index = 0
    for i in range(0, count, 3):
        for _ in range(size):
            for k in range(3):
                signals[i + k].append(values[index])
                index += 1
    return Record(signals, 500, 1e-3)
