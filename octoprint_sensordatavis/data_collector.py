import numpy as np
import threading

class Metric():
    def __init__(self, lims_field) -> None:
        self.values = []
        self.lims_field = lims_field
    
    def collect(self, reading) -> None:
        self.values.append(reading)
    
    def summarize(self):
        arr = np.array(self.values)
        print(len(self.values))
        return {
            "StandardDeviation": np.std(arr),
            "Average": np.mean(arr),
            "Value": arr[-1]
        }
    
    def clear(self):
        self.values = []


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
    
def record_bed_mesh_data(mesh, probe_points):
    """
        @mesh - (n, 1) z values at each probe point
        @probe_points - (n, 2) array of [[x_1, y_1], [x_2, y_2], ..., [x_n, y_n]]
    """

    from sklearn import linear_model

    probe_points = np.asarray(probe_points)
    mesh = np.asarray(mesh, dtype=np.float64)
    print(mesh)

    lr = linear_model.LinearRegression()
    lr.fit(probe_points, mesh.flatten())
    plane = lr.predict(probe_points).reshape(mesh.shape)
    flatness_mm = np.max(mesh - plane) - np.min(mesh - plane)

    with _metrics_lock:
        _metrics['mesh'] = mesh
        _metrics['flatness'] = flatness_mm
        print(_metrics)

def get_summarized_readings():
    data = {}
    with _metrics_lock:
        for lims_field in _metrics.keys():
            data[lims_field] = _metrics[lims_field].summarize()
            _metrics[lims_field].clear()
    return data