import argparse
import base64
import json
import logging
import math
import re
import subprocess
import random
import requests

from io import BytesIO
from PIL import Image, ImageOps, ImageEnhance
from airtest.core.android.adb import ADB
from airtest.core.android.touch_methods.base_touch import DownEvent, MoveEvent, SleepEvent, UpEvent
from airtest.core.api import *
from airtest.core.api import sleep
from airtest.aircv import *
from airtest.core.api import start_app
from airtest.utils.transform import TargetPos
from pytesseract import pytesseract

from common import constants
from config.log import MainLogger
from const.resource_manager import ResourceManager
from exception.exception import *
from const.params import *

global CR
CR = (0, 0)

R = None

pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'


def time_to_seconds(time_str):
    try:
        hours, minutes, seconds = map(int, time_str.split(':'))
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds
    except ValueError:
        return None


def coordinate_parser(value):
    pattern = r'\((-?\d+),(-?\d+)\)'
    match = re.match(pattern, value)
    if match:
        x = int(match.group(1))
        y = int(match.group(2))
        return x, y
    else:
        raise argparse.ArgumentTypeError("Invalid coordinate format. Expected (x, y).")


def calculate_distance(point, city_origin=(0, 0)):
    """
    计算两点之间的距离
    :param point: 目标坐标点 (x, y)
    :param city_origin: 城市原点坐标 (x1, y1)
    :return: 距离的整数值
    """

    if city_origin == (0, 0):
        MainLogger.info("未正确初始化城市坐标")
        return None

    K = 1.667
    x1, y1 = point
    x2, y2 = city_origin
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) / K
    rounded_distance = round(distance)  # 四舍五入取整
    return int(rounded_distance)


def get_current_coordinates(_screen, city_origin=(0, 0)):
    """
    获得当前帧的坐标
    使用相对于坐标图标的定位获取坐标数字位置
    :param _screen:
    :return:
    """
    # _target = crop(R.get("POINT_CD_NUM_X1"), R.get("POINT_CD_NUM_Y2"), _screen, resolution=CR)
    MainLogger.info("尝试获得当前帧坐标")
    _r = target_matching(R.get("ICON_POSITION_SEARCH"), _screen)
    print(_r)

    if _r and _r['confidence'] > 0.90:
        MainLogger.info("检测到目标图像")
        _p = _r['result']

    else:
        MainLogger.info("未检测到目标图像")
        return None, None, None

    _p_x = point((_p[0] - 170, _p[1] - 2), CR)
    _p_y = point((_p[0] - 8, _p[1] + 24), CR)

    # 根据相对坐标筛查
    _target = crop(_p_x, _p_y, _screen, resolution=CR)

    # 掩码处理，但相对来说，似乎什么都不做效果最好
    # # HSV 色度、饱和度、亮度
    # hsv = cv2.cvtColor(_target, cv2.COLOR_BGR2HSV)
    # lower_range = np.array([20, 15, 150])
    # #lower_range = np.array([0, 0, 200])
    # # upper_range = np.array([185, 80, 255])
    # upper_range = np.array([180, 80, 255])
    # mask = cv2.inRange(hsv, lower_range, upper_range)

    num_str = pytesseract.image_to_string(_target, lang='eng',
                                          config='--psm 7 --oem 1 -c tessedit_char_whitelist=0123456789XY')

    MainLogger.info("coordinates: " + num_str)
    coordinates = re.findall(r'[XY](\d+)', num_str)

    if len(coordinates) != 2:
        return None, None, None

    x, y = map(int, coordinates)
    if x < 0 or x > 1200 or y < 0 or y > 1200:
        return None, None, None
    d = calculate_distance((x, y), city_origin)

    # cv2.imshow('target', _target)
    # cv2.putText(_screen, f"({x}, {y}), {d} KM", (500, 500), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    # cv2.imshow('main', _screen)

    if d is not None:
        return x, y, d

        # 窗口显示(仅调试)

    return x, y, None


def target_matching(template, screen):
    """
    模板匹配(改)，返回完整的匹配结果
    :param template:
    :param screen:
    :return:
    """
    _result = template._cv_match(screen)
    if not _result:
        return None
    focus_pos = TargetPos().getXY(_result, template.target_pos)
    _result['result'] = focus_pos
    # _result = template.match_in(screen)
    # template.match_in()
    return _result


def deploy_gem_squad_ex(max_troop_num=5, max_time=-1):
    """
    派遣宝石部队
    max_troop_num: 最大部队数量
    :return: (True, None) 表示成功部署部队，(False, 错误信息) 表示部署失败
    """
    # _screen = G.DEVICE.snapshot(filename=None, quality=10)
    try:
        MainLogger.info("<派遣部队>")
        # 此部分注释，默认至此页面时，已知必然派遣部队满足条件，无需重复检查
        # _troop_num = get_troop_num_ex(_screen)
        # MainLogger.info("当前已派遣数量: " + str(_troop_num))
        _troop_num = 0

        if _troop_num < max_troop_num:
            _p1 = wait(R.get("BTN_COLLECTION"))
            click(_p1)
            MainLogger.info("等待「创建部队」按钮")
            _p1 = wait(R.get('BTN_CREATE_TROOPS'))
            click(_p1)
            MainLogger.info("等待「行军」按钮")
            _p1 = wait(R.get('BTN_MARCH'))

            if max_time > 0:
                MainLogger.info("需进行行军时间检测")
                _screen = G.DEVICE.snapshot(filename=None, quality=1)
                _p_x = point((_p1[0] - 32, _p1[1] + 32), CR)
                _p_y = point((_p1[0] + 80, _p1[1] + 58), CR)

                _target = crop(_p_x, _p_y, _screen, resolution=CR)
                # cv2.imwrite('runtime/crop-temp-111.png', _target)
                # _i = pre_process(_target, True)
                # _i.save("runtime/crop-temp-2.png")
                num = pytesseract.image_to_string(_target, lang='chi_sim',
                                                  config='--psm 7 -c tessedit_char_whitelist=:1234567890')
                num = time_to_seconds(num)
                MainLogger.info(num)
                if num is not None and num > max_time:
                    MainLogger.info("行军时间超过设定值，取消行军")
                    _p1 = wait(R.get('BTN_CANCEL_MARCH'))
                    return False, MarchTimeExceededError

            MainLogger.info("点击行军")
            click(_p1)
            return True, None
        else:
            return False, TroopsNumLimitedError

    except Exception as e:
        return False, MarchMonitorError


def deploy_gem_squad(max_troop_num=5):
    """
    部署宝石部队
    max_troop_num: 最大部队数量
    :return:
    """
    _screen = G.DEVICE.snapshot(filename=None, quality=1)
    try:

        _troop_num = get_troop_num(_screen)
        MainLogger.info("当前部队数量: " + str(_troop_num))
        if _troop_num < max_troop_num:
            _p1 = wait(R.get("BTN_COLLECTION"))
            click(_p1)
            MainLogger.info("等待「创建部队」按钮")
            # print("等待创建部队")
            # 等待创建部队
            _p1 = wait(R.get('BTN_CREATE_TROOPS'))
            click(_p1)
            MainLogger.info("等待「行军」按钮")
            # print("行军")
            # 默认队列
            _p1 = wait(R.get('BTN_MARCH'))
            click(_p1)
            return True
        else:
            raise TroopsNumLimitedError

    except TroopsNumLimitedError as e:
        raise e
    except Exception as e:
        raise MarchMonitorError


def scene_map_reset(_try_times=0, max_try_time=5, confirm=False):
    """

    :param _try_times: 当前已重试次数
    :param max_try_time: 最大重试次数
    :confirm 重新点击一次归位
    :return:
    """

    if _try_times > max_try_time:
        MainLogger.info("场景重置超限")
        return False, None

    _p = is_map_scene()

    if _p:
        if not confirm:
            MainLogger.info("处于地图场景，待归位: " + str(_p))
            click(_p)
            sleep(1)
            return scene_map_reset(_try_times, max_try_time)

        else:
            MainLogger.info("处于地图场景, 已归位")
            return True, None

    # 若非地图场景，进行场景监测

    # 若处于主城界面，进行点后重新检测
    _p = is_city_scene()

    if _p:
        MainLogger.info("处于城市场景，待归位: " + str(_p))
        click(_p)
        sleep(1)
        return scene_map_reset(_try_times, max_try_time, True)

    # 若含取消等面板
    MainLogger.info("遮挡检测(Cancel)")
    _p = exists(R.get("BTN_CANCEL"))
    if _p:
        MainLogger.info("遮挡检测(Cancel): True")
        key_back()
        sleep(1)
        return scene_map_reset(_try_times, max_try_time, True)
    MainLogger.info("遮挡检测(Cancel): False")

    # 若含关闭等面板
    MainLogger.info("遮挡检测(Close)")
    _p = exists(R.get("BTN_CLOSE"))
    if _p:
        MainLogger.info("遮挡检测(Close): True")
        key_back()
        sleep(1)
        return scene_map_reset(_try_times, max_try_time, True)
    MainLogger.info("遮挡检测(Close): False")

    MainLogger.info("无匹配项，尝试回退")
    key_back()
    sleep(1)
    return scene_map_reset(_try_times, max_try_time, True)


def reset_scene(_try_times, max_try_time=5):
    """
    @deprecated
    :param _try_times:
    :param max_try_time:
    :return:
    """
    MainLogger.info("场景重置: " + str(_try_times))
    if _try_times > max_try_time:
        MainLogger.info("场景重置超限")
        raise SceneError
    _try_times = _try_times + 1
    key_back()
    _p = exists(R.get("BTN_CANCEL"))
    if _p:
        key_back()
        if is_map_scene():
            MainLogger.info("场景重置成功")
            return True

    return reset_scene(_try_times, max_try_time)


def is_app_starting():
    pass


def key_back():
    keyevent("BACK")


def app_start():
    start_app("com.lilithgames.rok.offical.cn")


def app_stop():
    stop_app("com.lilithgames.rok.offical.cn")


def cmd(command):
    """
    执行操作系统命令
    :param command:
    :return:
    """
    sub_process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   encoding="utf-8")
    sub_process.wait(10)
    if sub_process.poll() == 0:
        return sub_process.communicate()

    else:
        return False


def init_adb():
    """
    Adb 环境初始化
    :return:
    """
    ADB_PATH = sysconfig.get_paths()['platlib'] + os.sep + "airtest/core/android/static/adb/mac/adb"
    cmd(ADB_PATH + " kill-server")
    result = cmd(ADB_PATH + " start-server")
    if result and re.search(r'daemon started successfully', result[1]):
        return True
    return False


def init_env(adb_serial='emulator-5554', host='127.0.0.1', port='5037'):
    """
    AirTest 环境初始化
    :return:
    """
    adb = ADB(adb_path='adb')
    # device_list = adb.devices()
    #
    # if len(device_list) < 1:
    #     MainLogger.error("无设备")
    #     exit()
    #
    # adb_serial = device_list[0][0]
    dev = connect_device("Android://" + host + ":" + port + "/" + adb_serial)
    _w, _h = device().get_current_resolution()
    global CR, R
    CR = (_w, _h)
    R = ResourceManager(CR)
    constants.RM = R
    print(constants.RM)

    return CR, R, dev


def init_airtest(adb_serial='emulator-5554', host='127.0.0.1', port='5037'):
    """
    AirTest 环境初始化
    :return:
    """

    # auto_setup(__file__, logdir=True, devices=[
    #     "Android:///",
    # ])

    #
    logger = logging.getLogger("airtest")
    logger.setLevel(logging.NOTSET)

    connect_device("Android://" + host + ":" + port + "/" + adb_serial)
    _w, _h = device().get_current_resolution()
    global CR
    CR = (_w, _h)
    global R
    R = ResourceManager(CR)

    return CR, R


# def start_app(timeout=60):
#     """
#     启动 APP
#     :return:
#     """
#     try:
#
#         MainLogger.info("检测应用是否开启")
#         if exists(BTN_MENU):
#             MainLogger.info("应用已开启")
#             return True
#
#         MainLogger.info("应用未开启，尝试开启应用")
#
#         _p = wait(APP_ICON)
#         click(_p)
#
#         MainLogger.info("发现应用图标，尝试开启")
#
#         _m = wait(v=BTN_MENU, timeout=timeout)
#         # click(_m)
#
#     except Exception as e:
#         MainLogger.exception(e)
#         raise AppStartError
#
#     return True


def is_phone_home():
    """
    判断是否位于主屏幕
    :return:
    """
    return exists(APP_ICON)


def is_map_scene():
    MainLogger.info("地图场景检测")
    p = exists(R.get("BTN_HOME"))
    if p:
        MainLogger.info("地图场景检测: True")
        return p
    MainLogger.info("地图场景检测: False")
    return None


def is_city_scene():
    MainLogger.info("主城场景检测")
    p = exists(R.get("BTN_MAP"))
    if p:
        MainLogger.info("主城场景检测: True")
        return p
    MainLogger.info("主城场景检测: False")
    return None


def wait_city_scene():
    MainLogger.info("主城场景检测")
    p = wait(R.get("BTN_MAP"), interval=5, timeout=60)
    if p:
        MainLogger.info("主城场景检测: True")
        return p
    MainLogger.info("主城场景检测: False")
    return None


def to_map_scene():
    """
    跳转至地图界面
    :return:
    """

    _p = is_map_scene()
    if _p:
        return True

    _p = is_city_scene()
    if _p:
        click(_p)
        try:
            wait(R.get("BTN_HOME"))
        except Exception as e:
            raise SceneError("无法跳转至地图界面")

    return True


def cxy(x, y):
    """
    X,Y 坐标转换
    :param x:
    :param y:
    :return:
    """
    return (x, y)


def click(point, rand_sleep=(100, 200), rand_offset=(-1, 1)):
    """
    模拟点击
    :param point:
    :param rand_sleep:
    :param rand_offset:
    :return:
    """
    # print(rand_sleep)
    rs = random.randint(rand_sleep[0], rand_sleep[1]) / 1000
    # print(rs)
    sleep(rs)
    rp = random.randint(rand_offset[0], rand_offset[1])
    # print(rp)
    p = cxy(point[0] + rp, point[1] + rp)
    # print(p)
    touch(p)
    MainLogger.debug("点击 原始坐标: " + str(point) + ", 实际坐标: " + str(p))


def scroll_click(max_point, inc_point, max_size, target, inc=1):
    """
    派遣滑动条处理
    :param max_point:
    :param inc_point:
    :param max_size:
    :param target:
    :param inc:
    :return:
    """
    MainLogger.info("部队派遣界面")
    MainLogger.info("点击「最大值」按钮")
    # print('点击最大值')
    click(max_point, (100, 200), (0, 0))
    # sleep(0.3)
    # for i in range(target, max_size):
    cur = max_size
    while cur > target:
        MainLogger.info("点击「-」")
        # print('点击减号')
        click(inc_point, (100, 200), (0, 0))
        cur = cur - inc
        # print(cur)


def get_current_coordinate(cv_screen):
    """
    获得当前坐标
    :param cv_screen:
    :return:
    """
    MainLogger.debug("尝试获得出征队列数量")
    _target = crop(R.get("POINT_CD_NUM_X1"), R.get("POINT_CD_NUM_Y1"), cv_screen, resolution=CR)

    # _target = pre_process(_target, True)
    # cv2.imshow('plate', _target)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    _target = cv2image(_target)
    _target.save("runtime/collection/coordinate_x.png")
    num_x = pytesseract.image_to_string(_target, lang='eng',
                                        config='--psm 6 -c tessedit_char_whitelist=0123456789')

    if num_x is None or num_x.strip() == '' or int(num_x) < 0 or int(num_x) > 1200:
        MainLogger.warn("获得当前坐标失败 " + num_x)
        screen = cv2image(_target)
        # screen.save('runtime/collection/error.x.' + str(num_x) + ".jpg")
        return None

    MainLogger.debug("X: " + str(num_x))

    _target = crop(R.get("POINT_CD_NUM_X2"), R.get("POINT_CD_NUM_Y2"), cv_screen, resolution=CR)

    # _target = pre_process(_target, True)
    _target = cv2image(_target)
    _target.save("runtime/collection/coordinate_y.png")
    num_y = pytesseract.image_to_string(_target, lang='eng',
                                        config='--psm 6 -c tessedit_char_whitelist=0123456789')

    if num_y is None or num_y.strip() == '' or int(num_y) < 0 or int(num_y) > 1200:
        MainLogger.warn("获得当前坐标失败 " + num_y)
        screen = cv2image(_target)
        # screen.save('runtime/collection/error.y.' + str(num_y) + ".jpg")
        return None

    MainLogger.debug("Y: " + str(num_y))

    return int(num_x), int(num_y)


def get_troop_num(cv_screen):
    """
    获得出征队列数量
    :param cv_screen:
    :return:
    """
    cv2.imwrite('runtime/crop-temp-0.png', cv_screen)
    MainLogger.info("尝试获得出征队列数量")
    _target = crop(R.get("POINT_TROOP_NUM_X"), R.get("POINT_TROOP_NUM_Y"), cv_screen, resolution=CR)
    cv2.imwrite('runtime/crop-temp-1.png', _target)
    _i = pre_process(_target, True)
    _i.save("runtime/crop-temp-2.png")
    num = pytesseract.image_to_string(_i, lang='chi_sim',
                                      config='--psm 10 -c tessedit_char_whitelist=12345')

    if num is None or num.strip() == '':
        MainLogger.info("获得出征队列数量失败")
        return 0

    MainLogger.info("获得出征队列数量: " + str(num))
    return int(num)


def get_troop_num_ex(cv_screen=None):
    """
    获得出征队列数量(增强)
    根据展开图标进行相对位置定位
    :param cv_screen:
    :return:
    """
    # cv2.imwrite('runtime/crop-temp-0.png', cv_screen)
    # cv_screen = cv2.imread('runtime/crop-temp-0.png')

    MainLogger.info("尝试获得出征队列数量")
    MainLogger.info("检测展开图标")

    _r = target_matching(R.get("ICON_TROOP_EXTEND"), cv_screen)

    if _r and _r['confidence'] > 0.90:
        MainLogger.info("检测到展开图标")
        _p = _r['result']

    else:
        MainLogger.info("获得出征队列数量失败，无派遣部队或未显示出征栏")
        return 0

    _p_x = point((_p[0] + 70, _p[1]), CR)
    _p_y = point((_p[0] + 88, _p[1] + 19), CR)

    _target = crop(_p_x, _p_y, cv_screen, resolution=CR)
    # cv2.imwrite('runtime/crop-temp-1.png', _target)
    _i = pre_process(_target, True)
    # _i.save("runtime/crop-temp-2.png")
    num = pytesseract.image_to_string(_i, lang='chi_sim',
                                      config='--psm 10 -c tessedit_char_whitelist=12345')

    if num is None or num.strip() == '':
        MainLogger.info("获得出征队列数量失败")
        return 0

    MainLogger.info("获得出征队列数量: " + str(num))
    return int(num)


def march_monitor(interval=5):
    """
    行军检测
    :return:
    """

    try:
        MainLogger.info("行军检测")
        # print("行军检测..")
        sleep(1)
        click(R.get('POINT_FIRST_TROOP').pos(CR))
        sleep(0.5)
        click(R.get('POINT_FIRST_TROOP').pos(CR))
        wait(BTN_MARCH_STAY)

        while exists(R.get('ICON_MARCHING')):
            MainLogger.info("行军中...")
            sleep(interval)

        MainLogger.info("到达...")
        return True
    except Exception as e:
        raise MarchMonitorError


def zoom():
    MID_X = int(CR[1] / 2)

    swipe_event2 = [
        DownEvent((400, MID_X), 0),
        DownEvent((1700, MID_X), 1),
        SleepEvent(5)
    ]

    for i in range(5):
        swipe_event2.append(MoveEvent((400 + 60 * i, MID_X), 0))
        swipe_event2.append(MoveEvent((1700 - 60 * i, MID_X), 1))
        swipe_event2.append(SleepEvent(0.2))

    swipe_event2.append(UpEvent(0))
    swipe_event2.append(UpEvent(1))

    device().touch_proxy.perform(swipe_event2)


def screen_scroll(direction, reverse=True):
    # MainLogger.debug(CR)
    MainLogger.info("方向: " + direction)

    if reverse:
        MID_X = int(CR[1] / 2)
        MID_Y = int(CR[0] / 2)
        if direction == "up":
            direction = "right"
        elif direction == "down":
            direction = "left"
        elif direction == "right":
            direction = "down"
        elif direction == "left":
            direction = "up"

    else:
        MID_X = int(CR[0] / 2)
        MID_Y = int(CR[1] / 2)

    DELTA_X = int((MID_X - 100) / 2)
    DELTA_Y = int((MID_Y - 50) / 2)

    # MainLogger.debug("MDD X: " + str(MID_X))
    # MainLogger.debug("MDD Y: " + str(MID_Y))

    # print(device().touch_method)
    # print(device().cap_method)

    scroll_event = []
    if direction == "up":
        scroll_event.append(DownEvent([MID_X, MID_Y]))
        scroll_event.append(SleepEvent(0.1))
        for _i in range(3):
            scroll_event.append(MoveEvent([MID_X, MID_Y + _i * DELTA_Y]))
            scroll_event.append(SleepEvent(0.2))
        scroll_event.append(UpEvent())

    elif direction == "down":
        scroll_event.append(DownEvent([MID_X, MID_Y]))
        scroll_event.append(SleepEvent(0.1))
        for _i in range(3):
            scroll_event.append(MoveEvent([MID_X, MID_Y - _i * DELTA_Y]))
            scroll_event.append(SleepEvent(0.2))
        scroll_event.append(UpEvent())

    elif direction == "left":
        scroll_event.append(DownEvent([MID_X, MID_Y]))
        scroll_event.append(SleepEvent(0.1))
        for _i in range(2):
            scroll_event.append(MoveEvent([MID_X + DELTA_X * _i, MID_Y]))
            scroll_event.append(SleepEvent(0.2))
        scroll_event.append(UpEvent())

    elif direction == "right":
        scroll_event.append(DownEvent([MID_X + DELTA_X * 2, MID_Y]))
        scroll_event.append(SleepEvent(0.1))
        for _i in range(2):
            scroll_event.append(MoveEvent([MID_X + DELTA_X * 2 - DELTA_X * _i, MID_Y]))
            scroll_event.append(SleepEvent(0.2))
        scroll_event.append(UpEvent())

    device().touch_proxy.perform(scroll_event)


def gem_searching():
    try:
        MainLogger.info("查找宝石矿")
        _pl = find_all(R.get('ICON_GEM'))
        if _pl:
            MainLogger.info("存在宝石矿点-列表")
            for _p in _pl:
                MainLogger.info("存在宝石矿点-遍历")
                MainLogger.info(_p)
                gem_collection(_p['result'])
    except Exception as e:
        MainLogger.info("当前矿点采集失败")


def common_collection(_p):
    """
    :param _p: 坐标
    :return:
    """
    _screen = G.DEVICE.snapshot(filename=None, quality=10)
    try:

        # _troop_num = get_troop_num(_screen)
        _troop_num = 1
        MainLogger.info("当前部队数量: " + str(_troop_num))
        if _troop_num < 5:
            click(_p, (0, 0))
            _p1 = wait(R.get("BTN_COLLECTION"))
            click(_p1)
            MainLogger.info("等待「创建部队」按钮")
            # print("等待创建部队")
            # 等待创建部队
            _p1 = wait(R.get('BTN_CREATE_TROOPS'))
            click(_p1)
            MainLogger.info("等待「行军」按钮")
            # print("行军")
            # 默认队列
            _p1 = wait(R.get('BTN_MARCH'))
            click(_p1)
            return True
        else:
            raise TroopsNumLimitedError

    except TroopsNumLimitedError as e:
        raise e
    except Exception as e:
        raise MarchMonitorError


def gem_collection(_p):
    """
    宝石
    :param _p:
    :return:
    """
    _screen = G.DEVICE.snapshot(filename=None, quality=10)

    try:

        _troop_num = get_troop_num_ex(_screen)

        MainLogger.info("当前部队数量: " + str(_troop_num))
        if _troop_num < 5:
            click(_p, (0, 0))
            _p1 = wait(R.get("BTN_COLLECTION"))
            click(_p1)
            MainLogger.info("等待「创建部队」按钮")
            # print("等待创建部队")
            # 等待创建部队
            _p1 = wait(R.get('BTN_CREATE_TROOPS'))
            click(_p1)
            MainLogger.info("等待「行军」按钮")
            # print("行军")
            # 默认队列
            _p1 = wait(R.get('BTN_MARCH'))
            click(_p1)
            return True
        else:
            raise TroopsNumLimitedError

    except TroopsNumLimitedError as e:
        raise e
    except Exception as e:
        raise MarchMonitorError


def dispatch_collection(target_type, level, max_level=6):
    """
    采集派遣
    :param target_type:
    :param level:
    :param max_level:
    :return:
    """

    # 点击搜索
    _p = wait(R.get('BTN_SEARCH'))
    click(_p)
    # 等待「探索种类」面板展开
    MainLogger.info("等待「派遣类型界面展开」按钮")

    # 等待「野蛮人等级选择」面板展开
    MainLogger.info("等待「采集目标搜索展开」按钮")
    sleep(1)
    if target_type == DISPATCH_TYPE_FARMLAND:
        _p = R.get("POINT_FARMLAND").pos(CR)
        # _p_max = POINT_SCROLL_MAX_PROGRESS_FARMLAND
        # _p_dec = POINT_SCROLL_DEC_BTN_FARMLAND

    elif target_type == DISPATCH_TYPE_SAWMILL:
        _p = R.get("POINT_SAWMILL").pos(CR)
        # _p_max = POINT_SCROLL_MAX_PROGRESS_SAWMILL
        # _p_dec = POINT_SCROLL_DEC_BTN_SAWMILL

    elif target_type == DISPATCH_TYPE_QUARRY:
        _p = R.get("POINT_QUARRY").pos(CR)
        # _p_max = POINT_SCROLL_MAX_PROGRESS_QUARRY
        # _p_dec = POINT_SCROLL_DEC_BTN_QUARRY

    elif target_type == DISPATCH_TYPE_GOLD_MINE:
        _p = R.get("POINT_GOLD").pos(CR)
        # _p_max = POINT_SCROLL_MAX_PROGRESS_GOLD_MINE
        # _p_dec = POINT_SCROLL_DEC_BTN_GOLD_MINE

    click(_p, (0, 0), (0, 0))
    click(_p, (0, 0), (0, 0))
    sleep(0.5)

    _p = wait(BTN_SEARCH_1)

    MainLogger.info("点击「搜索」按钮")
    # print("点击搜索")
    sleep(1)
    click(_p)

    MainLogger.info("等待「目标」箭头")
    # print("等待目标箭头")
    # 等待目标箭头
    wait(R.get('ICON_TARGET_ARROW'))
    sleep(2)

    MainLogger.info("点击「中心」目标位置")
    # print("点击中心")
    # 点击中心(目标野蛮人位置)
    click(point(xy=(830, 526), resolution=(1664, 1040)).pos(CR))

    MainLogger.info("等待「采集」按钮")
    # print("等待攻击按钮")
    # 等待攻击按钮
    _p = wait(R.get('BTN_COLLECTION'))

    click(_p)

    MainLogger.info("等待「创建部队」按钮")
    # print("等待创建部队")
    # 等待创建部队
    _p = wait(R.get('BTN_CREATE_TROOPS'))

    click(_p)

    MainLogger.info("等待「行军」按钮")
    # print("行军")
    # 默认队列
    _p = wait(R.get('BTN_MARCH'))

    click(_p)

    pass


def dispatch_savage_bsp_troop(level, max_level=0):
    """
    派遣「野蛮人」
    :param max_level:
    :param level:
    :return:
    """

    # 点击搜索

    _p = wait(R.get('BTN_SEARCH'))

    click(_p)

    # 等待「探索种类」面板展开
    MainLogger.info("等待「派遣类型界面展开」按钮")
    # print("等待「派遣类型界面展开」按钮")
    _p = wait(R.get('BTN_SAVAGE'))
    click(_p)
    sleep(1)

    # 等待「野蛮人等级选择」面板展开
    MainLogger.info("等待「野蛮人等级选择」按钮")
    # print("等待「野蛮人等级选择」按钮")
    _p = wait(BTN_SEARCH_1)

    if max_level != 0:
        # 选择目标等级
        MainLogger.info("选择目标等级")
        # print("选择目标等级")
        scroll_click(POINT_SCROLL_MAX_PROGRESS_SAVAGE.pos(CR), POINT_SCROLL_DEC_BTN_SAVAGE.pos(CR), max_level, level,
                     1)

    MainLogger.info("点击「搜索」按钮")
    # print("点击搜索")
    sleep(1)
    click(_p)

    MainLogger.info("等待「目标」箭头")
    # print("等待目标箭头")
    # 等待目标箭头
    wait(R.get('ICON_TARGET_ARROW'))
    sleep(2)

    MainLogger.info("点击「中心」目标位置")
    # print("点击中心")
    # 点击中心(目标野蛮人位置)
    click(point(xy=(830, 526), resolution=(1664, 1040)).pos(CR))

    MainLogger.info("等待「攻击」按钮")
    # print("等待攻击按钮")
    # 等待攻击按钮
    _p = wait(R.get('BTN_ATTACK'))

    click(_p)

    MainLogger.info("等待「创建部队」按钮")
    # print("等待创建部队")
    # 等待创建部队
    _p = wait(R.get('BTN_CREATE_TROOPS'))

    click(_p)

    MainLogger.info("等待「预置部队」按钮")
    # print("等待预置部队")
    _p = wait(R.get('BTN_TROOP_1'))

    click(_p)
    sleep(0.1)
    click(_p)

    MainLogger.info("等待「行军」按钮")
    # print("行军")
    # 默认队列
    _p = wait(R.get('BTN_MARCH'))

    click(_p)


# 图像识别

def cv2image(cv_image):
    return Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))


def crop(p1, p2, image, resolution=()):
    """
    图片截取
    :param p1:
    :param p2:
    :param image:
    :param resolution:
    :return:
    """
    _p1 = p1.pos(resolution)
    _p2 = p2.pos(resolution)
    _rect = (_p1[0], _p1[1], _p2[0], _p2[1])
    MainLogger.debug("图片截取: " + str(_rect))

    _s = aircv.crop_image(image, (_p1[0], _p1[1], _p2[0], _p2[1]))
    return _s


def crop_xy(p1, p2, image):
    """
    图片截取
    :param p1:
    :param p2:
    :param image:
    :return:
    """
    _rect = (p1[0], p1[1], p2[0], p2[1])
    MainLogger.debug("图片截取: " + str(_rect))

    _s = aircv.crop_image(image, (p1[0], p1[1], p2[0], p2[1]))
    return _s


threshold = 150

TABLE = []
for i in range(256):
    if i < threshold:
        TABLE.append(0)
    else:
        TABLE.append(1)


# 去掉二值化处理后的图片中的噪声点
def cut_noise(image):
    rows, cols = image.size  # 图片的宽度和高度
    change_pos = []  # 记录噪声点位置

    # 遍历图片中的每个点，除掉边缘
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            # pixel_set用来记录该店附近的黑色像素的数量
            pixel_set = []
            # 取该点的邻域为以该点为中心的九宫格
            for m in range(i - 1, i + 2):
                for n in range(j - 1, j + 2):
                    if image.getpixel((m, n)) != 1:  # 1为白色,0位黑色
                        pixel_set.append(image.getpixel((m, n)))

            # 如果该位置的九宫内的黑色数量小于等于4，则判断为噪声
            if len(pixel_set) <= 4:
                change_pos.append((i, j))

    # 对相应位置进行像素修改，将噪声处的像素置为1（白色）
    for pos in change_pos:
        image.putpixel(pos, 1)

    return image  # 返回修改后的图片


def pre_process(cv_image, invert=True, table=None, process_type=2):
    """
    预处理， 对目标图片执行灰度、二值化、降噪处理
    :param cv_image:
    :param invert:
    :param table:
    :param process_type:
    :return:
    """

    if process_type == 1:
        return pre_process_1(cv_image, invert, table)
    else:
        return pre_process_2(cv_image, invert)


def pre_process_1(cv_image, invert=True, table=None):
    """

    :param cv_image:
    :param invert:
    :param table:
    :return:
    """

    if table is None:
        table = TABLE

    pil_image = Image.fromarray(cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB))
    pil_image.save('1.jpg')
    # pil_image.save('test_0.jpg')
    # 调整对比对
    enhancer = ImageEnhance.Contrast(pil_image)
    pil_image = enhancer.enhance(10)
    # enh_sha = ImageEnhance.Sharpness(pil_image)
    # pil_image = enh_sha.enhance(10)

    # 转化为灰度图
    pil_image = pil_image.convert('L')

    # 反色
    if invert:
        pil_image = ImageOps.invert(pil_image)

    # 将图片进行二值化处理
    # 获取图片中的出现次数最多的像素，即为该图片的背景
    # max_pixel = get_threshold(pil_image)
    # table = get_bin_table(threshold=max_pixel)
    pil_image = pil_image.point(table, '1')

    # 去掉图片中的噪声（孤立点）
    pil_image = cut_noise(pil_image)

    return pil_image


def pre_process_2(cv_image, invert=True):
    """

    :param cv_image:
    :param invert:



    :return:
    """

    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    gray = cv2.medianBlur(gray, 3)

    if invert:
        pil_image = Image.fromarray(255 - gray)
    else:
        pil_image = Image.fromarray(gray)

    return pil_image


# 联众打码

def image_to_base64(image_path):
    # img = Image.open(image_path)
    img = image_path
    output_buffer = BytesIO()
    img.save(output_buffer, format='JPEG')
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data).decode()
    return base64_str


def lj_captcha(image_path, user_name, pwd, captcha_type=1303):
    """
    联众打码
    :param image_path:
    :param user_name:
    :param pwd:
    :param captcha_type:
    :return:
    """

    print("联众打码")
    api = "https://v2-api.jsdama.com/upload"
    headers = {'content-target_type': 'application/json'}

    # user_name = 'pixywen'
    # pwd = 'WEn$1016l'
    payload = {

        'softwareId': 22385,
        'softwareSecret': 'C8mcx1dWSdDzrC274qDlwfiTg7OILAZP2niL7r9N',
        'username': user_name,
        'password': pwd,
        'captchaType': captcha_type,
        'captchaMinLength': 0,
        'captchaMaxLength': 0,
        'workerTipsId': 0,
        'captchaData': image_to_base64(image_path),

    }

    ret = requests.post(api, data=json.dumps(payload), headers=headers)
    # print(ret.json)
    print(ret.status_code)
    print(ret.text)
    return lj_captcha_result(ret.text)


def lj_captcha_result(json_str):
    """
    联众打码结果解析
    :param json_str:
    :return:
    """

    # json_str = '{"code":0,"data":{"recognition":"394,407|526,658|606,407",' \
    #           '"captchaId":"20201204:000000000048599777848"},"message":""} '

    result = []
    captcha_id = None

    try:
        data = json.loads(json_str)
        if data['code'] == 0 and data['data']['recognition'] != "":
            for item in data['data']['recognition'].split('|'):
                result.append(tuple(item.split(',')))

        captcha_id = data['data']['captchaId']

    except Exception as e:
        print(e)

    return result, captcha_id


def lj_captcha_error_report(user_name, pwd, captcha_id):
    print("联众打码异常上报")

    api = "https://v2-api.jsdama.com/upload"
    headers = {'content-target_type': 'application/json'}

    # user_name = 'pixywen'
    # pwd = 'WEn$1016l'
    payload = {

        'softwareId': 22385,
        'softwareSecret': 'C8mcx1dWSdDzrC274qDlwfiTg7OILAZP2niL7r9N',
        'username': user_name,
        'password': pwd,
        'captchaId': captcha_id
    }

    ret = requests.post(api, data=json.dumps(payload), headers=headers)
    print(ret.text)
    print(ret.status_code)
    return True


def request_captcha_error_report_api(captcha_id):
    """

    :param captcha_id:
    :return:
    """

    print("打码识别异常上报 API 调用")

    results = lj_captcha_error_report(LJ_CAPTCHA_USERNAME, LJ_CAPTCHA_PWD, captcha_id)
    print(results)


def request_captcha_api(image_path, offset=(0, 0)):
    """

    :param image_path:
    :param offset:
    :return:
    """
    print("打码识别 API 调用")

    results, id = lj_captcha(image_path, LJ_CAPTCHA_USERNAME, LJ_CAPTCHA_PWD)

    r = []

    if results is not None:
        for val in results:
            print(val)
            r.append((int(val[0]) + offset[0], int(val[1]) + offset[1]))
        id = results
    else:
        return None

    return r, id


def captcha_process():
    """
    验证码监测及处理
    :return:
    """

    try:

        # if exists(BTN_VERIFICATION) is False:
        #     return True

        # # 点击宝箱按钮
        # _p = wait(BTN_VERIFICATION)
        # click(_p)
        #
        # 点击验证按钮
        _p = wait(BTN_VERIFICATION_X)
        click(_p)

        # 等待验证码展开， 标志为 刷新按钮
        p = wait(BTN_CAPTCHA_REFRESH)

        # 截屏 ， 取验证码区间
        screen = G.DEVICE.snapshot('mma.temp.1.jpg', 'SnapShot', 99)
        screen = crop(R.get("POINT_CAPTCHA_X"), R.get("POINT_CAPTCHA_Y"), screen, CR)
        # try_log_screen(screen,quality=99)
        screen = cv2image(screen)
        screen.save('mma.temp.2.jpg')

        # 调用识别 API
        result, cid = request_captcha_api(screen, R.get("POINT_CAPTCHA_X").pos(CR))

        print("MMA Results: ")
        print(result)

        if result is not None:

            for val in result:
                click(val)

            sleep(1)
            keyevent('Enter')
            # click(R.get("BTN_CAPTCHA_CONFIRM").pos(CR))

        sleep(1)

        if exists(BTN_VERIFICATION) is False:
            return True

        if cid is not None:
            request_captcha_error_report_api(cid)

    except Exception as e:
        raise

    return False
