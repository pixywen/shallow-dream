# coding=utf-8
from airtest.core.cv import Predictor


class point(Predictor):
    rs = None

    def __init__(self, xy=(), resolution=(), deviation=100):
        self.xy = xy
        self.resolution = resolution
        self.DEVIATION = deviation
        rx, ry = Predictor.count_record_pos(xy, resolution)
        self.rs = (rx, ry)
        #print(self.rs)

    def pos(self, target_resolution=()):
        # print(self.rs)
        return self.get_predict_point(self.rs, target_resolution)

    def record_pos(self):
        return self.rs
