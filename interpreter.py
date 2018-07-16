import ctypes
import os
import sys


class _CMark(ctypes.Structure):
    _fields_ = [
        ("sample", ctypes.c_int),
        ("type", ctypes.c_wchar_p)
    ]


class Mark(object):
    def __init__(self, cmark):
        self.sample = cmark.sample
        self.type = cmark.type


class EcgInterpreter(object):
    def __init__(self, rate, size):
        self.rate = ctypes.c_double(rate)
        self.size = ctypes.c_int(size)
        old_cwd = os.getcwd()
        new_cwd = os.path.dirname(sys.argv[0])
        dll_path = os.path.join(new_cwd, "LibEcgInterpreter.dll")
        os.chdir(new_cwd)
        # dll_path.replace("\\", "/")
        self.__handler = ctypes.windll.LoadLibrary(dll_path)
        os.chdir(old_cwd)
        self.__handler.Init(self.rate, self.size, ctypes.c_int(21))
        self.__handler.GetGlobalBorders.restype = ctypes.POINTER(_CMark)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__handler.Dispose()

    def add_signal(self, lead, resolution, signal):
        return self.__handler.AddSignal(ctypes.c_int(lead),
                                        ctypes.c_double(resolution),
                                        (ctypes.c_int * len(signal))(*signal))

    def calculate(self):
        return self.__handler.Calculate()

    def get_global_borders(self):
        count = ctypes.c_int()
        marks = self.__handler.GetGlobalBorders(ctypes.byref(count))
        return [Mark(x) for x in marks[:count.value]]

    def get_points(self):
        points_count = 5
        leads_count = 12
        table = []
        for lead in range(leads_count):
            table.append([])
            for point_id in range(points_count):
                point = self.__handler.GetPoint(ctypes.c_int(lead),
                                                ctypes.c_int(point_id))
                table[lead].append(point)
        return table

    def get_intervals(self):
        return [self.__handler.GetP(),
                self.__handler.GetPQ(),
                self.__handler.GetQrs(),
                self.__handler.GetQT()]

    @staticmethod
    def from_record(record):
        interpreter = EcgInterpreter(record.rate, record.size)
        for i, item in enumerate(record.signals):
            if item is None:
                continue
            interpreter.add_signal(i, record.mv_per_unit, item)
        interpreter.calculate()
        return interpreter
