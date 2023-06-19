import argparse
import datetime
import random
import re
import time
from math import sqrt

from airtest.aircv import aircv
from airtest.core.android.touch_methods.base_touch import DownEvent, SleepEvent, MoveEvent, UpEvent
from airtest.core.api import device, exists, wait, sleep
from airtest.core.cv import Template
from airtest.utils.transform import TargetPos

from common.utils import init_env, crop, pre_process, scene_map_reset, gem_searching, deploy_gem_squad, \
    deploy_gem_squad_ex, get_troop_num_ex, get_current_coordinates, coordinate_parser
from config.log import MainLogger
from pytesseract import pytesseract
from airtest.core.helper import G
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt

from model.mine import MineStack, Mine
from common.utils import click, get_troop_num


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

    finger_left_middle = ((CR[1] - (CR[1] * 0.51 + random.uniform(-9, 9))), CR[0] * 0.28 + random.uniform(-9, 9))
    finger_right_middle = ((CR[1] - (CR[1] * 0.51 + random.uniform(-9, 9))), CR[0] * 0.72 + random.uniform(-9, 9))

    if direction == 0:
        # 向上
        finger = ((CR[1] - (CR[1] * 0.2 + random.uniform(-9, 9))), finger_left_middle[1])
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
        finger = ((CR[1] - (CR[1] * 0.8 + random.uniform(-9, 9))), finger_right_middle[1])
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
    delta = 50
    step = 16

    delta_x = delta / sqrt(1 + (CR[0] / CR[1]) ** 2)
    delta_y = (CR[0] / CR[1]) * delta_x

    # 此模式下坐标计算很奇怪，翻转 X|Y，且 Y 轴坐标为 Y-DY，待探究
    fingerBottom = ((CR[1] - (CR[1] * 0.85 + random.uniform(-5, 5))), CR[0] * 0.28 + random.uniform(-5, 5))
    fingerTop = ((CR[1] - (CR[1] * 0.28 + random.uniform(-5, 5))), CR[0] * 0.68 + random.uniform(-5, 5))

    print(fingerBottom)

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


def zoom_1():
    MID_X = int(CR[1] / 2)

    swipe_event2 = [
        DownEvent((400, MID_X), 0),
        DownEvent((1700, MID_X), 1),
        SleepEvent(5)
    ]

    for i in range(9):
        swipe_event2.append(MoveEvent((400 + 60 * i, MID_X), 0))
        swipe_event2.append(MoveEvent((1700 - 60 * i, MID_X), 1))
        swipe_event2.append(SleepEvent(1))

    swipe_event2.append(UpEvent(0))
    swipe_event2.append(UpEvent(1))

    device().touch_proxy.perform(swipe_event2)


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


def tag_target(results, screen, path="testing/test"):
    _screen = screen.copy()
    # _screen = screen
    for _result in results:
        cv.rectangle(_screen, _result['rectangle'][0], _result['rectangle'][2], (0, 0, 255), 2)
        cv.circle(_screen, _result['result'], 40, (0, 0, 255), 1)
        cv.circle(_screen, _result['result'], 9, (0, 0, 255), -1)
        cv.putText(_screen, "gem", (_result['result'][0], _result['result'][1] + 70), cv.FONT_HERSHEY_COMPLEX, 1,
                   (0, 0, 255))
        cv.imshow('debug', _screen)


def process(cor):
    """
    对目标进行进一步操作
    a.记录矿点位置
    b.若满足条件，派遣队伍
    :return:
    """
    try:
        MainLogger.info("点击矿点(缩略): " + str(cor))
        click(cor, rand_offset=(0, 0))
        # 识别是否已拉近至矿点
        p = wait(R.get("ICON_GEM_BIG"), interval=1, timeout=30)
        # 若已拉近
        if p:
            MainLogger.info("点击矿点(缩略图标): " + str(p))
            click(p)
            time.sleep(0.5)
            MainLogger.info("等待展开面板 : \n")

            _p1 = wait(R.get("BTN_COLLECTION"), timeout=15)
            if not _p1:
                MainLogger.info("无法展开或无采集选项")
                return False

            MainLogger.info("分析矿点信息 : \n")
            _screen = G.DEVICE.snapshot(quality=1)
            pos, level, is_enable = process_target_panel(_screen)
            if not is_enable:
                MainLogger.info("无法采集")
                return False

            STACK.push(Mine(pos))
            MainLogger.info("矿点入栈，全部矿点信息 : \n")
            MainLogger.info(STACK)

            TARGET_STACK.expire_elements()
            if TARGET_STACK.contains_element(Mine(pos)):
                MainLogger.info("已派出部队采集该矿点 \n")
                return False

            MainLogger.info("尝试派遣队列 : \n")
            if not deploy_gem_squad_ex(5):
                MainLogger.info("派遣失败")
                return False

            TARGET_STACK.push(Mine(pos))

        return False

    except Exception as e:
        MainLogger.error(e)
        return False


def action(step):
    time.sleep(1)
    _screen = G.DEVICE.snapshot(quality=1)
    x, y, d = get_current_coordinates(_screen, CITY)
    MainLogger.info(f"坐标: ({x}, {y}), 距离: {d} KM")
    # _gem_template = Template(r"testing/gem_small.png")
    _gem_template = R.get("ICON_GEM_SMALL")
    _r = target_matching(template=_gem_template, screen=_screen)
    print(_r)
    if _r and len(_r) > 0 and _r['confidence'] > 0.90:
        # 矿点匹配
        gem_cor = (_r['result'][0], _r['result'][1])
        MainLogger.info("找到待选钻石矿: " + str(gem_cor))
        tag_target([_r], _screen)
        return process(gem_cor)

    if step >= 100:
        return False

    return True


def walk_random():
    direction_array = [0, 3, 6, 9]
    # 初始方向
    initial_direction = random.choice(direction_array)
    rotation_direction = random.choice([-1, 1])
    step = 1
    MainLogger.info("initial_direction: " + str(initial_direction))

    path = [(0, 0)]

    total_step = 0

    direction = initial_direction

    delta_step = 5
    turn_step = delta_step
    turn_round = 0

    while action(total_step):

        total_step = total_step + 1
        # 更新方向

        if total_step > 1:

            turn_step = turn_step + 1

            if turn_step >= delta_step:

                turn_round = turn_round + 1
                turn_step = 0

                delta_step = random.randint(2, 5)

                if rotation_direction == 1:
                    direction_index = direction_array.index(direction)
                    direction = direction_array[(direction_index + 1) % len(direction_array)]  # 顺时针遍历数组
                else:
                    direction_index = direction_array.index(direction)
                    direction = direction_array[(direction_index - 1) % len(direction_array)]  # 逆时针遍历数组

        # 行走到下一个方向
        swipe_with_salting(direction)

        # 获取当前位置
        current_position = path[-1]

        next_position = None
        direction_str = None

        # 根据当前方向和步长计算下一个位置
        if direction == 0:
            direction_str = "↑"
            next_position = (current_position[0], current_position[1] + step)
        elif direction == 3:
            direction_str = "→"
            next_position = (current_position[0] + step, current_position[1])
        elif direction == 6:
            direction_str = "↓"
            next_position = (current_position[0], current_position[1] - step)
        elif direction == 9:
            direction_str = "←"
            next_position = (current_position[0] - step, current_position[1])

        MainLogger.info("direction: " + direction_str)

        # 将下一个位置添加到路径
        path.append(next_position)

    # show_path(path)


def walk():
    direction_array = [0, 3, 6, 9]
    # 初始方向
    initial_direction = random.choice(direction_array)
    rotation_direction = random.choice([-1, 1])
    step = 1
    MainLogger.info("initial_direction: " + str(initial_direction))

    path = [(0, 0)]

    total_step = 0

    direction = initial_direction

    delta_step = 1
    turn_step = delta_step
    turn_round = 0

    while action(total_step):

        total_step = total_step + 1
        # 更新方向

        if total_step > 1:

            turn_step = turn_step + 1

            if turn_step >= delta_step:

                turn_round = turn_round + 1
                turn_step = 0

                if turn_round == 2:
                    turn_round = 0
                    delta_step = delta_step + 1

                if rotation_direction == 1:
                    direction_index = direction_array.index(direction)
                    direction = direction_array[(direction_index + 1) % len(direction_array)]  # 顺时针遍历数组
                else:
                    direction_index = direction_array.index(direction)
                    direction = direction_array[(direction_index - 1) % len(direction_array)]  # 逆时针遍历数组

        # 行走到下一个方向
        swipe_with_salting(direction)

        # 获取当前位置
        current_position = path[-1]

        next_position = None
        direction_str = None

        # 根据当前方向和步长计算下一个位置
        if direction == 0:
            direction_str = "↑"
            next_position = (current_position[0], current_position[1] + step)
        elif direction == 3:
            direction_str = "→"
            next_position = (current_position[0] + step, current_position[1])
        elif direction == 6:
            direction_str = "↓"
            next_position = (current_position[0], current_position[1] - step)
        elif direction == 9:
            direction_str = "←"
            next_position = (current_position[0] - step, current_position[1])

        MainLogger.info("direction: " + direction_str)

        # 将下一个位置添加到路径
        path.append(next_position)

    # show_path(path)


def show_path(path):
    # 创建图形和坐标轴
    fig, ax = plt.subplots()

    # 提取 x 和 y 坐标列表
    x_coords = [position[0] for position in path]
    y_coords = [position[1] for position in path]

    # 绘制路径
    ax.plot(x_coords, y_coords, marker='o')

    # 设置坐标轴范围
    ax.set_xlim(min(x_coords) - 1, max(x_coords) + 1)
    ax.set_ylim(min(y_coords) - 1, max(y_coords) + 1)

    # 显示方向箭头
    for i in range(1, len(path)):
        dx = path[i][0] - path[i - 1][0]
        dy = path[i][1] - path[i - 1][1]
        ax.annotate("", xy=(path[i][0], path[i][1]), xytext=(path[i - 1][0], path[i - 1][1]),
                    arrowprops=dict(arrowstyle="->"))

    # 显示图形
    plt.show()


_results = []


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


def find_color(screen):
    start = time.time()
    # _screen = G.DEVICE.snapshot(quality=1)
    # cv.imwrite("testing/test.temp.find_color.3" + ".jpg", _screen)
    # _screen = cv.imread("testing/cor1" + ".png")
    hsv = cv.cvtColor(screen, cv.COLOR_BGR2HSV)

    # Red color rangle  169, 100, 100 , 189, 255, 255

    # blue = np.uint8([[[250, 161, 82]]])
    # hsv_blue = cv.cvtColor(blue, cv.COLOR_BGR2HSV)
    # print(hsv_blue)
    # exit()
    # # green
    # lower_range = np.array([55, 250, 201])
    # upper_range = np.array([60, 255, 255])

    # blue
    # lower_range = np.array([100, 200, 250])
    # upper_range = np.array([120, 255, 255])

    # white
    # lower_range = np.array([0, 0, 200])
    # upper_range = np.array([180, 70, 255])

    lower_range = np.array([20, 15, 150])
    upper_range = np.array([180, 80, 255])

    mask = cv.inRange(hsv, lower_range, upper_range)

    binary = cv.threshold(mask, 127, 255, cv.THRESH_BINARY)[1]
    binary = cv.dilate(binary, None, iterations=2)
    cnts, hiera = cv.findContours(binary.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    sum = 0
    for c in cnts:
        sum += cv.contourArea(c)

    print(sum)
    MainLogger.info("End " + str((time.time() - start) * 1000) + " ms")

    # res = cv.bitwise_and(_screen, _screen, mask=mask)
    res = cv.drawContours(screen, cnts, -1, (255, 0, 255), 3)

    cv.imshow('pixy - image', screen)
    cv.imshow('pixy - mask', res)
    cv.imshow('pixy - res', mask)

    cv.waitKey(0)
    cv.destroyAllWindows()


def process_target_panel(screen):
    """
    处理分析目标面板
    :return:
    """
    try:

        # 是否已有人采集
        __template_more_btn = Template(r"testing/more.png", resolution=CR, threshold=0.95)
        _is_enable = not exists(__template_more_btn)

        MainLogger.debug("is enable: " + str(_is_enable))

        # 定位目标面板位置
        # 选择特征点较多的分享按钮作为锚点
        __template_location = Template(r"testing/panel_share_button.png", resolution=CR)
        _results = __template_location._cv_match(screen)

        _p = _results['rectangle']
        cv.circle(screen, _results['result'], 3, (0, 0, 255), -1)
        cv.circle(screen, _results['result'], 25, (0, 0, 255), 2)
        cv.rectangle(screen, _p[0], _p[2], (0, 0, 255), 2)

        MainLogger.debug("panel_share_button, pos: " + str(_results))

        _panel_top = (_p[3][0] - 695, _p[3][1])
        _panel_bottom = (_p[3][0], _p[3][1] + 516)

        # 矿点面板坐标
        # 此处进行绝对路径坐标及相对坐标的转换
        # Notice: 此处采用绝对偏移，未考虑分辨率差异
        _panel = aircv.crop_image(screen, (_panel_top[0], _panel_top[1], _panel_bottom[0], _panel_bottom[1]))
        cv.rectangle(screen, _panel_top, _panel_bottom, (0, 0, 255), 2)
        _debug_panel = _panel.copy()

        # 矿点坐标截图及 OCR
        _panel_pos = aircv.crop_image(_panel, (272, 9, 421, 40))
        cv.rectangle(_debug_panel, (272, 9), (421, 40), (0, 0, 255), 2)
        _pos = pytesseract.image_to_string(_panel_pos, lang='eng',
                                           config='--psm 6 -c tessedit_char_whitelist=0123456789XY:')

        # 正则提取
        # 示例 X:363Y:503

        _pos = reg_fetch_pos(_pos)

        MainLogger.debug("target, pos: " + str(_pos))

        # 矿点等级截图及 OCR
        _panel_level = aircv.crop_image(_panel, (322, 87, 353, 122))
        cv.rectangle(_debug_panel, (322, 87), (353, 122), (0, 0, 255), 2)
        _panel_level = pre_process(_panel_level, True)
        _level = pytesseract.image_to_string(_panel_level, lang='eng',
                                             config='--psm 6 -c tessedit_char_whitelist=123456789')

        MainLogger.debug("target, level:" + _level)
        # _panel_level.save("testing/temp." + str(randint(10000, 99999)) + ".png")

        # cv2.imwrite("testing/temp." + str(randint(10000, 99999)) + ".png", screen)
        # cv.imwrite("testing/temp." + str(randint(10000, 99999)) + ".png", _debug_panel)
        # 获取当前的年月日
        timestamp = datetime.datetime.now().strftime("%Y%m%d")

        # 构建新的文件名
        filename = f"testing/temp.{timestamp}.png"

        # 保存图像
        cv.imwrite(filename, _debug_panel)

        # 截取待识别区域
        # _c = aircv.crop_image(screen, (_p[0][0], _p[0][1], _p[0][0] + 687, _p[0][1] + 300))

        return _pos, _level, _is_enable

    except Exception as e:
        print(e)
        return None, None, None


def test():
    # swipe_with_salting(9)

    _gem_template = Template(r"testing/gem_small.png")
    cv.namedWindow('plate', cv.WINDOW_NORMAL)
    # cv.resizeWindow('plate', 500, 500)
    # cv.waitKey(1)

    while True:

        time.sleep(0.01)

        s1 = time.time()
        _screen = G.DEVICE.snapshot(quality=1)
        cv.imshow('image', _screen)
        MainLogger.info("FrameSnapShot Time: " + str((time.time() - s1) * 1000) + " ms")

        s2 = time.time()
        MainLogger.info("coordinates: " + str(get_current_coordinates(_screen)))
        MainLogger.info("Coordinates Time: " + str((s2 - s1) * 1000) + " ms")

        s3 = time.time()
        _r = target_matching(_gem_template, _screen)
        if _r and len(_r) > 0:
            print(_r)
            if _r['confidence'] > 0.9:
                MainLogger.info("找到待选钻石矿")
                tag_target([_r], _screen)
            # break

        MainLogger.info("TargetMatching Time:  " + str((s3 - s2) * 1000) + " ms")

        cv.imshow('image', _screen)
        # cv.waitKey(16)


def sentinel(sleep_time=0.01, need_reset=False):
    """
    哨兵函数
    :param need_reset:
    :param sleep_time:
    :return:
    """
    MainLogger.info("休眠时间: " + str(sleep_time) + " 秒")
    sleep(sleep_time)

    try:

        # 判定是否到了休眠时间(或活跃时间段)
        _screen = G.DEVICE.snapshot(quality=1)
        _troop_num = get_troop_num_ex(_screen)

        if _troop_num == 0 and not need_reset:
            # 主地图界面判断(重置)
            scene_map_reset()
            return sentinel(0.05, True)

        # 判定是否有空余队列
        MainLogger.info("部队数量: " + str(_troop_num))
        if _troop_num >= 5:
            MainLogger.info("部队已满")
            sleep_time = 60 * random.randint(3, 5)
            return sentinel(sleep_time)

        else:
            MainLogger.info("有空闲队列")
            scene_map_reset()
            return True

    except Exception as e:
        MainLogger.error("哨兵异常: ", e)
        return False


def greedy_miner(adb_serial, host, port):
    MainLogger.info("I'm a greedy miner...")

    global CR, R, Dev
    global STACK, TARGET_STACK

    STACK = MineStack()
    TARGET_STACK = MineStack()

    try:
        CR, R, Dev = init_env(adb_serial, host, port)
        MainLogger.info(f"屏幕 分辨率: {CR}")
    except Exception as e:
        MainLogger.error("环境初始化失败 : ", e)
        exit(1)

    # 判断是否满足激活条件
    while sentinel():
        zoom_with_salting()
        sleep(1)
        walk_random()


if __name__ == '__main__':
    global CITY

    parser = argparse.ArgumentParser(description='Greedy Miner Script')
    parser.add_argument('--adb_serial', type=str, default='ab44f833', help='ADB serial number of the device')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host IP address')
    parser.add_argument('--port', type=str, default='5037', help='Port number')
    parser.add_argument('--city', type=coordinate_parser, default=(0, 0), help='City coordinates')

    args = parser.parse_args()

    adb_serial = args.adb_serial
    host = args.host
    port = args.port
    CITY = args.city

    MainLogger.info("ADB Serial: " + adb_serial)
    MainLogger.info("Host: " + host)
    MainLogger.info("Port: " + port)

    # adb_serial = "192.168.1.68:5555"
    # host = "127.0.0.1"
    # port = "5555"

    greedy_miner(adb_serial, host, port)
