import argparse
import json
import math
import random
import re

import cv2
import requests
from airtest.aircv import aircv
from airtest.core.android.touch_methods.base_touch import DownEvent, SleepEvent, MoveEvent, UpEvent
from airtest.core.api import connect_device, device, touch, sleep, exists, wait, keyevent
from airtest.core.helper import G
from airtest.utils.transform import TargetPos
from pytesseract import pytesseract

from common import constants
from common.utils import pre_process
from config.log import MainLogger
from const.resource_manager import ResourceManager
from exception.exception import TroopsNumLimitedError, MarchMonitorError, MarchTimeExceededError
from model.points import point


def send_card_notification(title="", content="验证告警", btn_title="保留", btn_url=""):
    webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=7981888b00d17ef3548ac9b8e7340d85476ed5797bb7c02376b553c7d430cfa2"
    headers = {'Content-Type': 'application/json'}
    data = {
        #'msgtype': 'actionCard',
        #"msgtype": "link",
        "msgtype": "text",
        "text": {
            "content": "[告警]" + content
        },
        # "link": {
        #     "text": "[告警]" + title + " @15811301691\n",
        #     "title": content,
        #     "picUrl": "https://img.36krcdn.com/20211015/v2_6383d28228d14f4eacef60b1fc1695bb_img_000",
        #     "messageUrl": "https://img.36krcdn.com/20211015/v2_6383d28228d14f4eacef60b1fc1695bb_img_000"
        # },
        # 'actionCard': {
        #     'title': title,
        #     'text': content,
        #     'btnOrientation': '1',
        #     "image": "https://img.36krcdn.com/20211015/v2_6383d28228d14f4eacef60b1fc1695bb_img_000",
        #     'btns': [
        #         {
        #             'title': btn_title,
        #             'actionURL': btn_url
        #         }
        #     ],
        #
        # },
        "at": {
            "atMobiles": ["15811301691"],
            #"isAtAll": True
        }
    }
    response = requests.post(webhook_url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print('Card notification sent successfully.')
    else:
        print('Failed to send card notification.')


def key_back():
    keyevent("BACK")


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

    _r = target_matching(constants.RM.get("ICON_TROOP_EXTEND"), cv_screen)

    if _r and _r['confidence'] > 0.90:
        MainLogger.info("检测到展开图标")
        _p = _r['result']

    else:
        MainLogger.info("获得出征队列数量失败，无派遣部队或未显示出征栏")
        return 0

    _p_x = point((_p[0] + 70, _p[1]), constants.SCREEN_RESOLUTION)
    _p_y = point((_p[0] + 88, _p[1] + 19), constants.SCREEN_RESOLUTION)

    _target = crop(_p_x, _p_y, cv_screen, resolution=constants.SCREEN_RESOLUTION)
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
            _p1 = wait(constants.RM.get("BTN_COLLECTION"))
            click(_p1)
            MainLogger.info("等待「创建部队」按钮")
            _p1 = wait(constants.RM.get('BTN_CREATE_TROOPS'))
            click(_p1)
            MainLogger.info("等待「行军」按钮")
            _p1 = wait(constants.RM.get('BTN_MARCH'))

            if max_time > 0:
                MainLogger.info("需进行行军时间检测")
                _screen = G.DEVICE.snapshot(filename=None, quality=1)
                _p_x = point((_p1[0] - 32, _p1[1] + 32), constants.SCREEN_RESOLUTION)
                _p_y = point((_p1[0] + 80, _p1[1] + 58), constants.SCREEN_RESOLUTION)

                _target = crop(_p_x, _p_y, _screen, resolution=constants.SCREEN_RESOLUTION)
                # cv2.imwrite('runtime/crop-temp-111.png', _target)
                # _i = pre_process(_target, True)
                # _i.save("runtime/crop-temp-2.png")
                num = pytesseract.image_to_string(_target, lang='chi_sim',
                                                  config='--psm 7 -c tessedit_char_whitelist=:1234567890')
                num = time_to_seconds(num)
                MainLogger.info(num)
                if num is not None and num > max_time:
                    MainLogger.info("行军时间超过设定值，取消行军")
                    _p1 = wait(constants.RM.get('BTN_CANCEL_MARCH'))
                    return False, MarchTimeExceededError

            MainLogger.info("点击行军")
            click(_p1)
            return True, None
        else:
            return False, TroopsNumLimitedError

    except Exception as e:
        return False, MarchMonitorError


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


def is_map_scene():
    MainLogger.info("地图场景检测")
    p = exists(constants.RM.get("BTN_HOME"))
    if p:
        MainLogger.info("地图场景检测: True")
        return p
    MainLogger.info("地图场景检测: False")
    return None


def is_city_scene():
    MainLogger.info("主城场景检测")
    p = exists(constants.RM.get("BTN_MAP"))
    if p:
        MainLogger.info("主城场景检测: True")
        return p
    MainLogger.info("主城场景检测: False")
    return None


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
    _p = exists(constants.RM.get("BTN_CANCEL"))
    if _p:
        MainLogger.info("遮挡检测(Cancel): True")
        key_back()
        sleep(1)
        return scene_map_reset(_try_times, max_try_time, True)
    MainLogger.info("遮挡检测(Cancel): False")

    # 若含关闭等面板
    MainLogger.info("遮挡检测(Close)")
    _p = exists(constants.RM.get("BTN_CLOSE"))
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


def init_env(adb_serial='emulator-5554', host='127.0.0.1', port='5037'):
    """
    AirTest 环境初始化
    :return:
    """
    # adb = ADB()
    # device_list = adb.devices()
    #
    # if len(device_list) < 1:
    #     MainLogger.error("无设备")
    #     exit()
    #
    # adb_serial = device_list[0][0]
    dev = connect_device("Android://" + host + ":" + port + "/" + adb_serial)
    _w, _h = device().get_current_resolution()

    constants.SCREEN_RESOLUTION = (_w, _h)
    constants.RM = ResourceManager(constants.SCREEN_RESOLUTION)

    return constants.SCREEN_RESOLUTION, constants.RM, dev


def swipe_with_salting(direction):
    """
    向目标方向平滑滑动
    :param direction:
    :return:
    """
    step = 16
    finger = None
    delta_x = None
    delta_y = None

    finger_left_middle = (
        (constants.SCREEN_RESOLUTION[1] - (constants.SCREEN_RESOLUTION[1] * 0.51 + random.uniform(-9, 9))),
        constants.SCREEN_RESOLUTION[0] * 0.28 + random.uniform(-9, 9))
    finger_right_middle = (
        (constants.SCREEN_RESOLUTION[1] - (constants.SCREEN_RESOLUTION[1] * 0.51 + random.uniform(-9, 9))),
        constants.SCREEN_RESOLUTION[0] * 0.72 + random.uniform(-9, 9))

    if direction == 0:
        # 向上
        finger = ((constants.SCREEN_RESOLUTION[1] - (constants.SCREEN_RESOLUTION[1] * 0.2 + random.uniform(-9, 9))),
                  finger_left_middle[1])
        delta_x = -80
        step = 10
        delta_y = 0
        # finger = finger_left_middle
    elif direction == 3:
        # 向右
        delta_x = 0
        delta_y = -100
        step = 16
        finger = finger_right_middle

    elif direction == 6:
        # 向下
        finger = ((constants.SCREEN_RESOLUTION[1] - (constants.SCREEN_RESOLUTION[1] * 0.8 + random.uniform(-9, 9))),
                  finger_right_middle[1])
        delta_x = 80
        delta_y = 0
        step = 10
        # finger = finger_right_middle
    elif direction == 9:
        # 向左
        delta_x = 0
        delta_y = 100
        step = 16
        finger = finger_left_middle

    swipe_event2 = [
        DownEvent(finger, 0, 1),
        SleepEvent(0.01)
    ]

    for i in range(step):
        # swipe_event2.append(MoveEvent((finger[0] + delta_x * i,
        #                                finger[1] + delta_y * i), 0, 1))
        swipe_event2.append(MoveEvent((finger[0] + delta_x * i + random.uniform(-3, 3),
                                       finger[1] + delta_y * i + random.uniform(-3, 3)), 0, 1))

        # swipe_event2.append(MoveEvent((fingerTop[0] - delta * i, fingerTop[1]), 1))
        swipe_event2.append(SleepEvent(0.1))

    swipe_event2.append(UpEvent(0))
    device().touch_proxy.perform(swipe_event2)


def zoom_with_salting():
    """
    平滑缩放
    :return:
    """
    MainLogger.info("<缩放>")
    delta = 50
    step = 16

    delta_x = delta / math.sqrt(1 + (constants.SCREEN_RESOLUTION[0] / constants.SCREEN_RESOLUTION[1]) ** 2)
    delta_y = (constants.SCREEN_RESOLUTION[0] / constants.SCREEN_RESOLUTION[1]) * delta_x

    # 此模式下坐标计算很奇怪，翻转 X|Y，且 Y 轴坐标为 Y-DY，待探究
    fingerBottom = ((constants.SCREEN_RESOLUTION[1] - (constants.SCREEN_RESOLUTION[1] * 0.85 + random.uniform(-5, 5))),
                    constants.SCREEN_RESOLUTION[0] * 0.28 + random.uniform(-5, 5))
    fingerTop = ((constants.SCREEN_RESOLUTION[1] - (constants.SCREEN_RESOLUTION[1] * 0.28 + random.uniform(-5, 5))),
                 constants.SCREEN_RESOLUTION[0] * 0.68 + random.uniform(-5, 5))

    swipe_event2 = [
        DownEvent(fingerBottom, 0, 1),
        DownEvent(fingerTop, 1, 1),
        SleepEvent(0.01)
    ]

    for i in range(step):
        swipe_event2.append(MoveEvent((fingerBottom[0] + delta_x * i + random.uniform(-5, 5),
                                       fingerBottom[1] + delta_y * i + random.uniform(-5, 5)), 0, 1))
        # swipe_event2.append(MoveEvent((fingerTop[0] - delta * i, fingerTop[1]), 1))
        swipe_event2.append(SleepEvent(0.1))

    swipe_event2.append(UpEvent(0))
    swipe_event2.append(UpEvent(1))

    device().touch_proxy.perform(swipe_event2)


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
    _r = target_matching(constants.RM.get("ICON_POSITION_SEARCH"), _screen)
    MainLogger.info(f"坐标图标匹配结果: {_r}")
    if _r and _r['confidence'] > 0.90:
        MainLogger.info("检测到目标图像")
        _p = _r['result']

    else:
        MainLogger.info("未检测到目标图像")
        return None, None, None

    _p_x = point((_p[0] - 170, _p[1] - 2), constants.SCREEN_RESOLUTION)
    _p_y = point((_p[0] - 8, _p[1] + 24), constants.SCREEN_RESOLUTION)

    # 根据相对坐标筛查
    _target = crop(_p_x, _p_y, _screen, resolution=constants.SCREEN_RESOLUTION)

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


def reg_fetch_pos(str):
    """
    正则提取坐标
    输入: X:123Y:123
    :param str:
    :return:
    """
    reg = re.compile('^X:(?P<X>\\d{1,4})Y:(?P<Y>\\d{1,4})')
    _result = None
    _match = reg.match(str)
    if _match:
        _dict = _match.groupdict()
        _result = (int(_dict['X']), int(_dict['Y']))

    return _result


def process_target_panel(screen):
    """
    处理分析目标矿点面板
    :param screen:当前帧
    :return:
    """
    try:
        MainLogger.info("<处理分析目标矿点面板>")
        # 是否已有人采集
        # _is_enable = not exists(R.get('ICON_MORE'))
        _is_enable = constants.RM.get('ICON_MORE').match_in(screen) is None
        MainLogger.info(f"无人采集: {_is_enable}")

        # 定位目标面板位置，选择特征点较多的分享按钮作为锚点
        # 划线标记
        # 此处进行绝对路径坐标及相对坐标的转换
        # Notice: 此处采用绝对偏移，未考虑分辨率差异

        _results = constants.RM.get('ICON_SHARE')._cv_match(screen)

        MainLogger.debug(f"查找分享按钮: {_results}")
        _p = _results['rectangle']
        cv2.circle(screen, _results['result'], 3, (0, 0, 255), -1)
        cv2.circle(screen, _results['result'], 25, (0, 0, 255), 2)
        cv2.rectangle(screen, _p[0], _p[2], (0, 0, 255), 2)
        _panel_top = (_p[3][0] - 695, _p[3][1])
        _panel_bottom = (_p[3][0], _p[3][1] + 516)

        # 截取目标面板
        _panel = aircv.crop_image(screen, (_panel_top[0], _panel_top[1], _panel_bottom[0], _panel_bottom[1]))
        cv2.rectangle(screen, _panel_top, _panel_bottom, (0, 0, 255), 2)
        _debug_panel = _panel.copy()

        # 提取面板中的矿点坐标信息
        # 截取并 OCR 识别
        # 示例 X:363Y:503
        _panel_pos = aircv.crop_image(_panel, (272, 9, 421, 40))
        cv2.rectangle(_debug_panel, (272, 9), (421, 40), (0, 0, 255), 2)

        _pos = pytesseract.image_to_string(_panel_pos, lang='eng',
                                           config='--psm 6 -c tessedit_char_whitelist=0123456789XY:')

        _pos = reg_fetch_pos(_pos)
        MainLogger.info(f"目标矿点坐标: {_pos}")

        # 提取矿点等级信息
        # 截取并 OCR 识别
        _panel_level = aircv.crop_image(_panel, (322, 87, 353, 122))
        cv2.rectangle(_debug_panel, (322, 87), (353, 122), (0, 0, 255), 2)
        _panel_level = pre_process(_panel_level, True)
        _level = pytesseract.image_to_string(_panel_level, lang='eng',
                                             config='--psm 6 -c tessedit_char_whitelist=123456789')

        MainLogger.info(f"目标矿点等级: {_level}")

        # 调试用
        # _panel_level.save("testing/temp." + str(randint(10000, 99999)) + ".png")
        # cv2.imwrite("testing/temp." + str(randint(10000, 99999)) + ".png", screen)
        # cv.imwrite("testing/temp." + str(randint(10000, 99999)) + ".png", _debug_panel)
        # 获取当前的年月日
        # timestamp = datetime.datetime.now().strftime("%Y%m%d")
        # 构建新的文件名
        # filename = f"testing/temp.{timestamp}.png"
        # 保存图像
        # cv2.imwrite(filename, _debug_panel)
        # 截取待识别区域
        # _c = aircv.crop_image(screen, (_p[0][0], _p[0][1], _p[0][0] + 687, _p[0][1] + 300))

        return _pos, _level, _is_enable

    except Exception as e:
        MainLogger.warn(f"处理分析目标矿点面板异常: {e}")
        return None, None, None


def tag_target(results, screen, path="testing/test"):
    _screen = screen.copy()
    # _screen = screen
    for _result in results:
        cv2.rectangle(_screen, _result['rectangle'][0], _result['rectangle'][2], (0, 0, 255), 2)
        cv2.circle(_screen, _result['result'], 40, (0, 0, 255), 1)
        cv2.circle(_screen, _result['result'], 9, (0, 0, 255), -1)
        cv2.putText(_screen, "gem", (_result['result'][0], _result['result'][1] + 70), cv2.FONT_HERSHEY_COMPLEX, 1,
                    (0, 0, 255))
        cv2.imshow('debug', _screen)

# def show_path(path):
#     # 创建图形和坐标轴
#     fig, ax = plt.subplots()
#
#     # 提取 x 和 y 坐标列表
#     x_coords = [position[0] for position in path]
#     y_coords = [position[1] for position in path]
#
#     # 绘制路径
#     ax.plot(x_coords, y_coords, marker='o')
#
#     # 设置坐标轴范围
#     ax.set_xlim(min(x_coords) - 1, max(x_coords) + 1)
#     ax.set_ylim(min(y_coords) - 1, max(y_coords) + 1)
#
#     # 显示方向箭头
#     for i in range(1, len(path)):
#         dx = path[i][0] - path[i - 1][0]
#         dy = path[i][1] - path[i - 1][1]
#         ax.annotate("", xy=(path[i][0], path[i][1]), xytext=(path[i - 1][0], path[i - 1][1]),
#                     arrowprops=dict(arrowstyle="->"))
#
#     # 显示图形
#     plt.show()

# def walk():
#     direction_array = [0, 3, 6, 9]
#     # 初始方向
#     initial_direction = random.choice(direction_array)
#     rotation_direction = random.choice([-1, 1])
#     step = 1
#     MainLogger.info("initial_direction: " + str(initial_direction))
#
#     path = [(0, 0)]
#
#     total_step = 0
#
#     direction = initial_direction
#
#     delta_step = 1
#     turn_step = delta_step
#     turn_round = 0
#
#     while action(total_step):
#
#         total_step = total_step + 1
#         # 更新方向
#
#         if total_step > 1:
#
#             turn_step = turn_step + 1
#
#             if turn_step >= delta_step:
#
#                 turn_round = turn_round + 1
#                 turn_step = 0
#
#                 if turn_round == 2:
#                     turn_round = 0
#                     delta_step = delta_step + 1
#
#                 if rotation_direction == 1:
#                     direction_index = direction_array.index(direction)
#                     direction = direction_array[(direction_index + 1) % len(direction_array)]  # 顺时针遍历数组
#                 else:
#                     direction_index = direction_array.index(direction)
#                     direction = direction_array[(direction_index - 1) % len(direction_array)]  # 逆时针遍历数组
#
#         # 行走到下一个方向
#         swipe_with_salting(direction)
#
#         # 获取当前位置
#         current_position = path[-1]
#
#         next_position = None
#         direction_str = None
#
#         # 根据当前方向和步长计算下一个位置
#         if direction == 0:
#             direction_str = "↑"
#             next_position = (current_position[0], current_position[1] + step)
#         elif direction == 3:
#             direction_str = "→"
#             next_position = (current_position[0] + step, current_position[1])
#         elif direction == 6:
#             direction_str = "↓"
#             next_position = (current_position[0], current_position[1] - step)
#         elif direction == 9:
#             direction_str = "←"
#             next_position = (current_position[0] - step, current_position[1])
#
#         MainLogger.info("direction: " + direction_str)
#
#         # 将下一个位置添加到路径
#         path.append(next_position)
#
#     # show_path(path)

# def find_color(screen):
#     start = time.time()
#     # _screen = G.DEVICE.snapshot(quality=1)
#     # cv.imwrite("testing/test.temp.find_color.3" + ".jpg", _screen)
#     # _screen = cv.imread("testing/cor1" + ".png")
#     hsv = cv.cvtColor(screen, cv.COLOR_BGR2HSV)
#
#     # Red color rangle  169, 100, 100 , 189, 255, 255
#
#     # blue = np.uint8([[[250, 161, 82]]])
#     # hsv_blue = cv.cvtColor(blue, cv.COLOR_BGR2HSV)
#     # print(hsv_blue)
#     # exit()
#     # # green
#     # lower_range = np.array([55, 250, 201])
#     # upper_range = np.array([60, 255, 255])
#
#     # blue
#     # lower_range = np.array([100, 200, 250])
#     # upper_range = np.array([120, 255, 255])
#
#     # white
#     # lower_range = np.array([0, 0, 200])
#     # upper_range = np.array([180, 70, 255])
#
#     lower_range = np.array([20, 15, 150])
#     upper_range = np.array([180, 80, 255])
#
#     mask = cv.inRange(hsv, lower_range, upper_range)
#
#     binary = cv.threshold(mask, 127, 255, cv.THRESH_BINARY)[1]
#     binary = cv.dilate(binary, None, iterations=2)
#     cnts, hiera = cv.findContours(binary.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
#     sum = 0
#     for c in cnts:
#         sum += cv.contourArea(c)
#
#     print(sum)
#     MainLogger.info("End " + str((time.time() - start) * 1000) + " ms")
#
#     # res = cv.bitwise_and(_screen, _screen, mask=mask)
#     res = cv.drawContours(screen, cnts, -1, (255, 0, 255), 3)
#
#     cv.imshow('pixy - image', screen)
#     cv.imshow('pixy - mask', res)
#     cv.imshow('pixy - res', mask)
#
#     cv.waitKey(0)
#     cv.destroyAllWindows()
