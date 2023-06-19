# coding=utf-8


class ProgressError(Exception):
    def __init__(self, message, status):
        super().__init__(message, status)
        self.message = message
        self.status = status


class SceneError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


class AppStartError(Exception):

    def __init__(self):
        self.message = '应用启动失败'

    def __str__(self):
        return self.message


class AppStopError(Exception):

    def __init__(self):
        self.message = '应用退出失败'

    def __str__(self):
        return self.message


class TroopsNumLimitedError(Exception):

    def __init__(self):
        self.message = '部队数量超限'

    def __str__(self):
        return self.message


class MarchTimeExceededError(Exception):

    def __init__(self):
        self.message = '行军时间超过设定值，取消行军'

    def __str__(self):
        return self.message

class MarchMonitorError(Exception):

    def __init__(self):
        self.message = '行军检测异常'

    def __str__(self):
        return self.message


class CaptchaProcessError(Exception):

    def __init__(self):
        self.message = '验证码识别异常'

    def __str__(self):
        return self.message


class DispatchError(Exception):
    def __init__(self, message, status):
        super().__init__(message, status)
        self.message = message
        self.status = status

    def __str__(self):
        return self.message
