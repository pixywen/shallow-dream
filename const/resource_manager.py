import importlib
from pathlib import Path

from airtest.core.cv import Template
from airtest.utils.transform import TargetPos

from model.points import point


def _path(p, name):
    return Path('resources').joinpath(p).joinpath(name)


class ResourceManager:
    """
    资源管理器
    """
    screen_resolution = None

    _cache = {}

    def __init__(self, sr):
        self.screen_resolution = sr
        _p = str(sr[0]) + "_" + str(sr[1])
        _config = importlib.import_module('resources.' + _p + '.config')

        if _config:
            _templates = _config.config['templates']
            for key in _templates:
                th = None
                rp = None
                tp = TargetPos.MID
                if "th" in _templates[key]:
                    th = _templates[key]['th']
                if "tp" in _templates[key]:
                    tp = _templates[key]['tp']
                if "rp" in _templates[key]:
                    rp = _templates[key]['rp']
                self._cache[key] = Template(_path(_p, _templates[key]['path']), record_pos=rp,
                                            resolution=_templates[key]['r'], threshold=th, target_pos=tp)
            _points = _config.config['points']
            for key in _points:
                self._cache[key] = point(xy=_points[key]['xy'],
                                         resolution=_points[key]['r'])

        # print(self._cache)

    def get(self, key):
        return self._cache.get(key)
