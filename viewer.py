import os
import pickle
from matplotlib import pyplot as plt
from matplotlib.widgets import CheckButtons
import cal_points
import reader
from interpreter import EcgInterpreter

_LEADS = ["I", "II", "III", "aVR", "aVL", "aVF",
          "V1", "V2", "V3", "V4", "V5", "V6"]
_LABEL_MEASURES = "Global Intervals"
_LABEL_REFERENCES = "Reference Intervals"
_LABEL_POINTS = "Local Peak points"


def show_cts(filename):
    plt.subplots_adjust(left=0.04, top=0.99, bottom=0.03, wspace=0.12,
                        hspace=0.23, right=0.86)
    record = reader.read_cts(filename, 10)
    with EcgInterpreter.from_record(record) as interpreter:
        borders = interpreter.get_global_borders()
        points = interpreter.get_points()
        measures = interpreter.get_intervals()
    borders = [x.sample for x in borders if x.sample > 0]
    onset = int(borders[0] - 0.02 * record.rate)
    offset = int(borders[-1] + 0.02 * record.rate)
    empty_count = 0
    local_points = []
    measurements = []
    references = []
    name = _record_name(filename)
    for i, item in enumerate(record.signals):
        if item is None:
            empty_count += 1
            continue
        chunk = item[onset:offset]
        plot_index = (i - empty_count) * 2
        if plot_index > 7:
            plot_index -= 7
        plt.subplot(421 + plot_index)
        plt.ylabel("Lead " + _LEADS[i] + ". Voltage, mV.")
        plt.xlabel("Time, s.")
        plt.plot(chunk)
        measurements += _plot_borders(onset, borders)
        local_points += _plot_local_points(onset, points[i], chunk)
        references += _plot_references(name, onset, offset)
    legend_items = {
        _LABEL_MEASURES: measurements[0],
        _LABEL_POINTS: local_points[0]
    }
    if references:
        legend_items[_LABEL_REFERENCES] = references[0]
    plt.figlegend(legend_items.values(), legend_items.keys(), "upper right")
    triggers = CheckButtons(plt.axes([0.87, 0.8, 0.12, 0.10]),
                            legend_items.keys(),
                            [True] * len(legend_items))

    def switch(label):
        lines = None
        if label == _LABEL_MEASURES:
            lines = measurements
        elif label == _LABEL_POINTS:
            lines = local_points
        elif label == _LABEL_REFERENCES:
            lines = references
        for item in lines:
            item.set_visible(not item.get_visible())
        plt.draw()

    triggers.on_clicked(switch)
    _result_table(measures, name, ((10, 8), (10, 8), (6, 5), (12, 10)),
                  "durations.pkl")
    plt.get_current_fig_manager().window.state("zoomed")
    plt.gcf().canvas.set_window_title("CTS-ECG: " + name)
    plt.show()


def show_cse(filename):
    plt.subplots_adjust(left=0.04, top=0.99, bottom=0.03, wspace=0.12,
                        hspace=0.23, right=0.86)
    record = reader.read_cse(filename)
    with EcgInterpreter.from_record(record) as interpreter:
        borders = interpreter.get_global_borders()
        points = interpreter.get_points()
        measures = interpreter.get_intervals()
    borders = [x.sample for x in borders if x.sample > 0]
    onset = int(borders[0] - 0.02 * record.rate)
    offset = int(borders[-1] + 0.02 * record.rate)
    empty_count = 0
    local_points = []
    measurements = []
    name = _record_name(filename)
    for i, item in enumerate(record.signals):
        if 2 <= i <= 5:
            empty_count += 1
            continue
        chunk = item[onset:offset]
        plot_index = (i - empty_count) * 2
        if plot_index > 7:
            plot_index -= 7
        plt.subplot(421 + plot_index)
        plt.ylabel("Lead " + _LEADS[i] + ". Voltage, mV.")
        plt.xlabel("Time, s.")
        plt.plot(chunk)
        measurements += _plot_borders(onset, borders)
        local_points += _plot_local_points(onset, points[i], chunk)
    legend_items = {
        _LABEL_POINTS: local_points[0]
    }
    if measurements:
        legend_items[_LABEL_MEASURES] = measurements[0]
    plt.figlegend(legend_items.values(), legend_items.keys(), "upper right")
    triggers = CheckButtons(plt.axes([0.87, 0.8, 0.12, 0.10]),
                            legend_items.keys(),
                            [True] * len(legend_items))

    def switch(label):
        lines = None
        if label == _LABEL_MEASURES:
            lines = measurements
        elif label == _LABEL_POINTS:
            lines = local_points
        for item in lines:
            item.set_visible(not item.get_visible())
        plt.draw()

    triggers.on_clicked(switch)
    _result_table(measures, name, ((10, 15), (10, 10), (10, 10), (25, 30)),
                  "ref_dict.pkl")
    plt.get_current_fig_manager().window.state("zoomed")
    plt.gcf().canvas.set_window_title("CSE Miltilead: " + name)
    plt.show()


def _result_table(measures, name, bounds, dict_name):
    ref_file = os.path.join(os.path.dirname(__file__), dict_name)
    with open(ref_file, "rb") as ref_file:
        ref_dict = pickle.load(ref_file)
    references = ref_dict[name]
    cells = []
    colors = []
    for i in range(4):
        if abs(measures[i] - references[i]) > sum(bounds[i]):
            colors.append("r")
        else:
            colors.append("g")
        cells.append([str(measures[i]), str(references[i])])
    plt.table(cellText=cells,
              rowLabels=["P", "PQ", "QRS", "QT"],
              colLabels=["Measure", "Reference"],
              colWidths=[0.3, 0.3],
              rowColours=colors)


def _record_name(filename):
    return os.path.basename(filename)[:-4].upper()


def _plot_references(name, onset, offset):
    if offset - onset < 1000:
        complex_size = 500
    else:
        complex_size = 1000
    shift = complex_size - onset % complex_size - 1
    points = cal_points.CAL_POINTS.get(name)
    if points is None:
        return []
    return [plt.axvline(x=(x + shift), color="y", ls="--") for x in points]


def _plot_local_points(onset, points, chunk):
    local_points = []
    for point in points:
        if point == 0:
            continue
        x = point - onset
        local_points += plt.plot(x, chunk[x], "ro", markersize=2.5)
    return local_points


def _plot_borders(onset, borders):
    intervals = []
    for point in borders:
        intervals.append(plt.axvline(x=(point - onset), color="g"))
    return intervals
