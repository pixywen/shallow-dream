# coding=utf-8
import os
import sysconfig
from model.points import *
from airtest.core.cv import Template
from pathlib import Path, PurePath

# ADB PATH
ADB_PATH = sysconfig.get_paths()['platlib'] + os.sep + "airtest/core/android/static/adb/mac/adb"
# ADB_PATH = '/Users/pixy/Library/Android/sdk/platform-tools/adb'
# 联众打码
LJ_CAPTCHA_USERNAME = "pixywen"
LJ_CAPTCHA_PWD = "WEn$1016l"

# 识别辅助资源
RESOURCE_PATH = Path('resources')

DISPATCH_TYPE_SAVAGE = 1
# 玉米
DISPATCH_TYPE_FARMLAND = 2
# 木头
DISPATCH_TYPE_SAWMILL = 3
# 石矿
DISPATCH_TYPE_QUARRY = 4
# 金矿
DISPATCH_TYPE_GOLD_MINE = 5


def template_path(name):
    return RESOURCE_PATH.joinpath(name)


# 应用图标(官网)
APP_ICON = Template(template_path("app_icon.png"), record_pos=(0.344, 0.044), resolution=(1280, 800))
# 主界面右下角 MENU BTN , 用于协助判定是否开启应用
BTN_MENU = Template(template_path("btn_menu.png"), record_pos=(0.466, 0.275), resolution=(1280, 800))
BTN_CITY = Template(template_path("btn_city.png"), record_pos=(-0.445, 0.261), resolution=(1664, 1040))
BTN_MAP = Template(template_path("btn_map.png"), record_pos=(-0.45, 0.261), resolution=(1664, 1040))
# 人机验证码
BTN_VERIFICATION = Template(template_path("btn_verification.png"), record_pos=(0.331, -0.226), resolution=(1664, 1040))
BTN_VERIFICATION_X = Template(template_path("btn_verification_x1.png"), record_pos=(0.134, -0.026),
                              resolution=(1280, 800))
BTN_CAPTCHA_REFRESH = Template(template_path("btn_captcha_refresh.png"), record_pos=(-0.126, 0.277),
                               resolution=(1280, 800))
# 主界面搜索按钮
BTN_SEARCH = Template(template_path("btn_search.png"), record_pos=(-0.45, 0.171), resolution=(1664, 1040))
# 目标搜索界面搜索按钮
BTN_SEARCH_1 = Template(template_path("btn_search_1.png"), record_pos=(-0.287, 0.13), resolution=(1664, 1040))
# 「搜索野蛮人」按钮
BTN_SAVAGE = Template(template_path("btn_savage.png"), record_pos=(-0.289, 0.244), resolution=(1280, 800))
# 「攻击」按钮
BTN_ATTACK = Template(template_path("btn_attack.png"), record_pos=(-0.093, 0.072), resolution=(1664, 1040))
# 「创建部队」按钮
BTN_CREATE_TROOPS = Template(template_path("btn_create_troops.png"), record_pos=(0.288, -0.168), resolution=(1280, 800))
# 预置部队 1(不区分颜色)
BTN_TROOP_1 = Template(template_path("btn_troop_blue_1.png"), rgb=False, record_pos=(0.361, -0.027),
                       resolution=(1280, 800))

# 「行军」按钮
BTN_MARCH = Template(template_path("btn_march.png"), record_pos=(0.225, 0.2), resolution=(1280, 800))
# 「行军帐篷」图标
BTN_MARCH_STAY = Template(template_path("btn_march_stay.png"), record_pos=(0.005, 0.079), resolution=(1664, 1040))
# 目标箭头
TARGET_ARROW = Template(template_path("btn_target_arrow.png"), record_pos=(0.001, -0.09), resolution=(1280, 800))

BTN_NAME_MORE = Template(template_path("btn_name_more.png"), record_pos=(0.016, -0.102), resolution=(1664, 1040))
BTN_NAME_CLIPBOARD = Template(template_path("btn_name_copy.png"), record_pos=(0.016, -0.158), resolution=(1664, 1040))

# TAG-联盟-战力
TAG_CE = Template(template_path("btn_ce.png"), record_pos=(-0.111, -0.035), resolution=(1664, 1040))
# BTN-联盟-信息
BTN_USER_INFO = Template(template_path("btn_user_info.png"), record_pos=(-0.102, 0.001), resolution=(1664, 1040))

BTN_R5 = Template(template_path("btn_r5.png"), record_pos=(-0.24, -0.169), resolution=(1664, 1040))
BTN_R4 = Template(template_path("btn_r4.png"), record_pos=(-0.346, -0.081), resolution=(1664, 1040))
BTN_R3 = Template(template_path("btn_r3.png"), record_pos=(-0.344, -0.026), resolution=(1664, 1040))
BTN_R2 = Template(template_path("btn_r2.png"), record_pos=(-0.346, 0.029), resolution=(1664, 1040))
BTN_R1 = Template(template_path("btn_r1.png"), record_pos=(-0.344, 0.084), resolution=(1664, 1040))
BTN_CLOSE = Template(template_path("btn_close.png"), record_pos=(0.354, -0.215), resolution=(1664, 1040))

# 按钮-执政官资料-更多信息
BTN_MORE_INFO = Template(template_path("btn_more_info.png"), record_pos=(-0.252, 0.131), resolution=(1664, 1040))
# TAG-KD详情-Title
TAG_KD_TITLE = Template(template_path("tag_kd_screen.png"), record_pos=(0.016, -0.055), resolution=(1664, 1040))

# POINT
# 人机验证码 确认 & 刷个牙西边
POINT_CAPTCHA_CONFIRM = point(xy=(807, 750), resolution=(1280, 800))
POINT_CAPTCHA_REFRESH = point(xy=(483, 753), resolution=(1280, 800))
# 人机验证码 XY
POINT_CAPTCHA_X = point(xy=(369, 101), resolution=(1280, 800))
POINT_CAPTCHA_Y = point(xy=(912, 796), resolution=(1280, 800))
# 部队派遣数量 XY
POINT_TROOP_NUM_X = point(xy=(1213, 200), resolution=(1280, 800))
POINT_TROOP_NUM_Y = point(xy=(1225, 218), resolution=(1280, 800))
# 部队派遣按钮 XY
POINT_TROOP_MAX_NUM_X = point(xy=(1229, 200), resolution=(1280, 800))
POINT_TROOP_MAX_NUM_Y = point(xy=(1240, 218), resolution=(1280, 800))
# 野蛮人派遣进度条及等级减号
POINT_SCROLL_MAX_PROGRESS_SAVAGE = point(xy=(376, 485), resolution=(1280, 800))
POINT_SCROLL_DEC_BTN_SAVAGE = point(xy=(178, 625), resolution=(1664, 1040))
# 首个派遣队列位置
POINT_FIRST_TROOP = point(xy=(1595, 331), resolution=(1664, 1040))

POINT_UID_X = point(xy=(783, 300), resolution=(1664, 1040))
POINT_UID_Y = point(xy=(900, 330), resolution=(1664, 1040))

POINT_UCE_X = point(xy=(940, 433), resolution=(1664, 1040))
POINT_UCE_Y = point(xy=(1110, 460), resolution=(1664, 1040))

POINT_USERNAME_X = point(xy=(678, 325), resolution=(1664, 1040))
POINT_USERNAME_Y = point(xy=(900, 360), resolution=(1664, 1040))
# 阵亡
POINT_DD_X = point(xy=(1224, 524), resolution=(1664, 1040))
POINT_DD_Y = point(xy=(1357, 546), resolution=(1664, 1040))
# 历史最高战力
POINT_HCE_X = point(xy=(1224, 331), resolution=(1664, 1040))
POINT_HCE_Y = point(xy=(1357, 356), resolution=(1664, 1040))

# POINT_KDA_T1_X = point(xy=(1243, 463), resolution=(1664, 1040))
# POINT_KDA_T1_Y = point(xy=(1434, 485), resolution=(1664, 1040))
#
# POINT_KDA_T2_X = point(xy=(1243, 507), resolution=(1664, 1040))
# POINT_KDA_T2_Y = point(xy=(1434, 530), resolution=(1664, 1040))
#
# POINT_KDA_T3_X = point(xy=(1243, 554), resolution=(1664, 1040))
# POINT_KDA_T3_Y = point(xy=(1434, 577), resolution=(1664, 1040))
#
# POINT_KDA_T4_X = point(xy=(1243, 600), resolution=(1664, 1040))
# POINT_KDA_T4_Y = point(xy=(1434, 623), resolution=(1664, 1040))
#
# POINT_KDA_T5_X = point(xy=(1243, 646), resolution=(1664, 1040))
# POINT_KDA_T5_Y = point(xy=(1434, 669), resolution=(1664, 1040))


POINT_KDA_T1_X = point(xy=(858, 463), resolution=(1664, 1040))
POINT_KDA_T1_Y = point(xy=(1024, 485), resolution=(1664, 1040))

POINT_KDA_T2_X = point(xy=(858, 507), resolution=(1664, 1040))
POINT_KDA_T2_Y = point(xy=(1024, 530), resolution=(1664, 1040))

POINT_KDA_T3_X = point(xy=(858, 554), resolution=(1664, 1040))
POINT_KDA_T3_Y = point(xy=(1024, 577), resolution=(1664, 1040))

POINT_KDA_T4_X = point(xy=(858, 600), resolution=(1664, 1040))
POINT_KDA_T4_Y = point(xy=(1024, 623), resolution=(1664, 1040))

POINT_KDA_T5_X = point(xy=(858, 646), resolution=(1664, 1040))
POINT_KDA_T5_Y = point(xy=(1024, 669), resolution=(1664, 1040))
