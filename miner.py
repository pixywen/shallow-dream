import argparse
import random
import time

from airtest.core.api import wait, sleep, device

from common import constants
from common.tools import process_target_panel, swipe_with_salting, zoom_with_salting, init_env, click, scene_map_reset, \
    deploy_gem_squad_ex, get_troop_num_ex, get_current_coordinates, \
    coordinate_parser, send_card_notification
from config.log import MainLogger
from airtest.core.helper import G
from model.mine import MineStack, Mine


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
        p = wait(constants.RM.get("ICON_GEM_BIG"), interval=0.5, timeout=10)
        # 若已拉近
        if p:
            MainLogger.info("点击矿点(放大): " + str(p))
            click(p)
            time.sleep(0.5)
            MainLogger.info("等待展开面板")
            _p1 = wait(constants.RM.get("BTN_COLLECTION"), interval=0.5, timeout=10)
            if not _p1:
                MainLogger.info("无法展开或无采集选项")
                return False

            MainLogger.info("分析矿点信息")
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
    """
    移动间的动作
    1、查找矿点缩略图
    2、矿点分析及采集流程
    :param step:
    :return:
    False: 完成派遣动作，或因一场导致本次搜索路径中断，重新归位
    True: 未完找到目标矿点，或其他情况，继续搜索
    """

    # 等待屏幕稳定
    time.sleep(1)

    _screen = device().snapshot(quality=1)
    x, y, d = get_current_coordinates(_screen, CITY)
    MainLogger.info(f"坐标: ({x}, {y}), 距离: {d} KM")

    # 若首轮，则不作任何动作(等同于初始一屏随机移动，防止城市的矿点反复影响判定)
    if step <= 2:
        return True

    if step >= 100:
        return False

    _gem_template = constants.RM.get("ICON_GEM_SMALL")
    # _r = target_matching(template=_gem_template, screen=_screen)
    _r = _gem_template.match_in(_screen)
    if _r:
        MainLogger.info(f"找到待选钻石矿, 坐标 {_r} ")
        process(_r)
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

                delta_step = random.randint(3, 5)

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

        # 判定是否有验证
        verify = constants.RM.get("BTN_VERIFY").match_in(_screen)
        if verify:
            MainLogger.info("验证界面")
            return False

        _troop_num = get_troop_num_ex(_screen)

        if _troop_num == 0 and not need_reset:
            # 主地图界面判断(重置)
            scene_map_reset()
            return sentinel(0.05, True)

        # 判定是否有空余队列
        MainLogger.info("部队数量: " + str(_troop_num))
        if _troop_num >= 5:
            MainLogger.info("部队已满")
            sleep_time = 60 * random.randint(1, 3)
            return sentinel(sleep_time)

        else:
            MainLogger.info("有空闲队列")
            scene_map_reset()
            return True

    except Exception as e:
        MainLogger.error("哨兵异常: ", e)
        return False


def stop_greedy_miner():
    global GREEDY_MINER_RUNNING
    GREEDY_MINER_RUNNING = False


def init_miner(adb_serial, host, port, city=(0, 0)):
    global STACK, TARGET_STACK, CITY, GREEDY_MINER_RUNNING

    CITY = city

    STACK = MineStack()
    TARGET_STACK = MineStack()

    try:
        CR, R, Dev = init_env(adb_serial, host, port)
        MainLogger.info(f"屏幕 分辨率: {CR}")
    except Exception as e:
        MainLogger.error("环境初始化失败 : ", e)


def greedy_miner_ex():

    MainLogger.info("I'm a greedy miner...")

    try:

        GREEDY_MINER_RUNNING = True

        while GREEDY_MINER_RUNNING and sentinel():
            sleep(5)
            zoom_with_salting()
            sleep(5)
            walk_random()
            sleep(5)

    except Exception as e:
        MainLogger.info(e)

    MainLogger.info("greedy miner exit...")
    send_card_notification("", "哨兵下线，请检查")


def greedy_miner(adb_serial, host, port, city=(0, 0)):
    MainLogger.info("I'm a greedy miner...")

    global STACK, TARGET_STACK, CITY

    CITY = city

    STACK = MineStack()
    TARGET_STACK = MineStack()

    try:
        CR, R, Dev = init_env(adb_serial, host, port)
        MainLogger.info(f"屏幕 分辨率: {CR}")
    except Exception as e:
        MainLogger.error("环境初始化失败 : ", e)

    # 判断是否满足激活条件

    while sentinel():
        sleep(5)
        zoom_with_salting()
        sleep(5)
        walk_random()
        sleep(5)

    MainLogger.info("greedy miner exit...")
    send_card_notification("", "哨兵下线，请检查")


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

    # adb_serial = "192.168.50.44:43457"
    # host = "127.0.0.1"
    # port = '5555'

    # adb_serial = "192.168.50.44:38561"
    # host = '127.0.0.1'
    # port = '5037'

    greedy_miner(adb_serial, host, port, args.city)
