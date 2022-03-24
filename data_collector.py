import numpy as np
import threading

import lims

_logger = None


class Metric():
    def __init__(self, lims_field) -> None:
        self.values = []
        self.lims_field = lims_field
    
    def collect(self, reading) -> None:
        self.values.append(reading)
    
    def summarize(self, data):
        arr = np.array(self.values)
        data[f'{self.lims_field}.StandardDeviation'] = np.std(arr)
        data[f'{self.lims_field}.Average'] = np.mean(arr)
        data[f'{self.lims_field}.Value'] = arr[-1]
        # return {
        #     "StandardDeviation": np.std(arr),
        #     "Average": np.mean(arr),
        #     "Value": arr[-1]
        # }
    
    def clear(self):
        self.values = []

class BedMeshMetrics():
    def __init__(self, lims_field, mesh, flatness, normal, theta, phi) -> None:
        self.lims_field = lims_field
        self.mesh = mesh
        self.flatness = flatness
        self.normal = normal
        self.theta = theta
        self.phi = phi
    
    def clear(self):
        pass

    def summarize(self, data):
        data[f'{self.lims_field}.Mesh'] = str(self.mesh)
        data[f'{self.lims_field}.Flatness'] = self.flatness
        data[f'{self.lims_field}.NormalX'] = self.normal[0]
        data[f'{self.lims_field}.NormalY'] = self.normal[1]
        data[f'{self.lims_field}.NormalZ'] = self.normal[2]
        data[f'{self.lims_field}.Theta'] = self.theta
        data[f'{self.lims_field}.Phi'] = self.phi

class GCodeMetrics():
    def __init__(self, lims_field, line_number):
        self.lims_field = lims_field
        self.line_number = line_number
    
    def clear(self):
        pass

    def summarize(self, data):
        data[f'{self.lims_field}.GCODE.LineNumber'] = self.line_number


_metrics_lock = threading.Lock()
_metrics = {}

def record_metric(lims_field, readings):
    with _metrics_lock:
        metric = None
        if lims_field in _metrics.keys():
            metric = _metrics[lims_field]
        else:
            _metrics[lims_field] = Metric(lims_field)
            metric = _metrics[lims_field]
        
        metric.collect(readings)

def record_gcode_line(lims_field, line_number):
    with _metrics_lock:
        metric = None
        if lims_field in _metrics.keys():
            metric = _metrics[lims_field]
        else:
            _metrics[lims_field] = GCodeMetrics(lims_field, line_number)
            metric = _metrics[lims_field]
    
def record_bed_mesh_data(mesh, probe_points):
    """
        @mesh - (n, 1) z values at each probe point
        @probe_points - (n, 2) array of [[x_1, y_1], [x_2, y_2], ..., [x_n, y_n]]
    """

    from sklearn import linear_model

    probe_points = np.asarray(probe_points)
    mesh = np.asarray(mesh, dtype=np.float64)

    lr = linear_model.LinearRegression()
    lr.fit(probe_points, mesh.flatten())
    plane = lr.predict(probe_points).reshape(mesh.shape)
    flatness_mm = np.abs(np.max(mesh - plane) - np.min(mesh - plane))

    n = np.array([-lr.coef_[0], -lr.coef_[1], 1])
    n = n / np.linalg.norm(n)
    
    theta = np.rad2deg(np.arctan2(n[0], n[1]))
    phi = np.rad2deg(np.arccos(np.dot([0,0,1],n)))

    with _metrics_lock:
        _metrics["Facility.PrusaMK3.Bed"] = BedMeshMetrics("Facility.PrusaMK3.Bed", mesh, flatness_mm, n, theta, phi)

def get_summarized_readings():
    data = {}
    with _metrics_lock:
        _logger.debug(f'[DATA_COLLECTOR] Metrics keys: {_metrics.keys()}')
        for lims_field in _metrics.keys():
            _metrics[lims_field].summarize(data)
        # for lims_field in _metrics.keys():
        #     # # data[lims_field] = _metrics[lims_field].summarize()
        #     # summaries = _metrics[lims_field].summarize()
        #     # for summary in summaries:
        #     #     data[f'{lims_field}.{summary["lims_field"]}'] = summary["value"]
        #     # # _metrics[lims_field].clear()
        _metrics.clear()
    return data
