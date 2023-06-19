# coding=utf-8
from airtest.core.cv import Template
from model.points import *

#CR = (1280, 800)

# Template(r"tpl1607670573539.png", threshold=0.8, rgb=True, target_pos=1, record_pos=(0.101, -0.089), resolution=(1280, 800))

LJ_CAPTCHA_USERNAME = "pixywen"
LJ_CAPTCHA_PWD = "WEn$1016l"


TEMPLATE_DISPATCH_TARGET = Template(r"dispatch_target.png", record_pos=(0.06, 0.0), resolution=(1280, 800))

# 部队配置按钮

TEMPLATE_BTN_RED_TROOP_1 = Template(r"btn_troop_red_1.png", rgb=True, threshold=0.85, record_pos=(0.362, -0.029),
                                    resolution=(1280, 800))
TEMPLATE_BTN_RED_TROOP_1X = Template(r"btn_troop_red_1x.png", threshold=0.85, rgb=False, record_pos=(0.362, -0.028), resolution=(1664, 1040))

TEMPLATE_BTN_BLUE_TROOP_1 = Template(r"btn_troop_blue_1.png", rgb=True, threshold=0.85, record_pos=(0.273, -0.028),
                                     resolution=(1280, 800))
TEMPLATE_BTN_YELLOW_TROOP_1 = Template(r"btn_troop_yellow_1.png", rgb=True, threshold=0.85, record_pos=(0.275, -0.027),
                                       resolution=(1280, 800))
TEMPLATE_BTN_BLUE_TROOP_2 = Template(r"btn_troop_blue_2.png", rgb=True, threshold=0.85, record_pos=(0.274, 0.016),
                                     resolution=(1280, 800))

TEMPLATE_BTN_CAPTCHA_REFRESH = Template(r"btn_captcha_refresh.png", record_pos=(-0.126, 0.277), resolution=(1280, 800))

POINT_CAPTCHA_CONFIRM = point(xy=(807, 750), resolution=(1280, 800))
POINT_CAPTCHA_REFRESH = point(xy=(483, 753), resolution=(1280, 800))

POINT_CAPTCHA_X = point(xy=(369, 101), resolution=(1280, 800))
POINT_CAPTCHA_Y = point(xy=(912, 796), resolution=(1280, 800))

DISPATCH_TYPE_SAVAGE = 1
DISPATCH_TYPE_FARMLAND = 2
DISPATCH_TYPE_SAWMILL = 3
DISPATCH_TYPE_QUARRY = 4
DISPATCH_TYPE_GOLD_MINE = 5

# TEMPLATE

TEMPLATE_APP_ICON = Template(r"APP_ICON.png", record_pos=(0.344, 0.044), resolution=(1280, 800))

TEMPLATE_BTN_CITY = Template(r"btn_city.png", record_pos=(-0.445, 0.261), resolution=(1664, 1040))
TEMPLATE_BTN_MAP = Template(r"btn_map.png", record_pos=(-0.45, 0.261), resolution=(1664, 1040))
TEMPLATE_BTN_MENU = Template(r"btn_menu.png", record_pos=(0.466, 0.275), resolution=(1280, 800))

TEMPLATE_BTN_MARCH_STAY = Template(r"btn_march_stay.png", record_pos=(0.005, 0.079), resolution=(1664, 1040))

TEMPLATE_BTN_EXIT_CONFIRM = Template(r"btn_exit_confirm.png", record_pos=(-0.088, 0.091), resolution=(1280, 800))
TEMPLATE_BTN_SEARCH = Template(r"btn_search.png", record_pos=(-0.45, 0.171), resolution=(1664, 1040))
TEMPLATE_BTN_SAVAGE = Template(r"btn_savage.png", record_pos=(-0.289, 0.244), resolution=(1280, 800))
TEMPLATE_BTN_GOLD_MINE = Template(r"btn_gold_mine.png", record_pos=(0.302, 0.249), resolution=(1280, 800))
TEMPLATE_BTN_FARMLAND = Template(r"btn_farmland.png", record_pos=(-0.145, 0.249), resolution=(1280, 800))
TEMPLATE_BTN_SAWMILL = Template(r"btn_sawmill.png", record_pos=(0.003, 0.248), resolution=(1280, 800))
TEMPLATE_BTN_QUARRY = Template(r"btn_quarry.png", record_pos=(0.153, 0.249), resolution=(1280, 800))
TEMPLATE_BTN_SEARCH_X = Template(r"btn_search_x.png", record_pos=(-0.287, 0.13), resolution=(1664, 1040))
TEMPLATE_BTN_ATTACK = Template(r"btn_attack.png", record_pos=(-0.093, 0.072), resolution=(1664, 1040))
TEMPLATE_BTN_COLLECTION = Template(r"btn_collection.png", record_pos=(0.126, -0.037), resolution=(1664, 1040))
TEMPLATE_BTN_CREATE_TROOPS = Template(r"btn_create_troops.png", record_pos=(0.291, -0.171), resolution=(1664, 1040))
TEMPLATE_BTN_MARCH = Template(r"btn_march.png", record_pos=(0.229, 0.2), resolution=(1664, 1040))
TEMPLATE_BTN_VERIFICATION = Template(r"btn_verification.png", record_pos=(0.331, -0.226), resolution=(1664, 1040))
TEMPLATE_BTN_VERIFICATION_X = Template(r"btn_verification_x1.png", record_pos=(0.134, -0.026), resolution=(1280, 800))
TEMPLATE_TARGET_ARROW = Template(r"btn_target_arrow.png", record_pos=(0.001, -0.09), resolution=(1280, 800))
TEMPLATE_BTN_SEARCH_XY = Template(r"btn_search_xy.png", record_pos=(0.191, -0.172), resolution=(1280, 800))
TEMPLATE_BTN_CITY_INFO = Template(r"btn_city_info.png", record_pos=(-0.391, -0.042), resolution=(1280, 800))


POINT_FIRST_TROOP = point(xy=(1595, 331), resolution=(1664, 1040))

# DISPATCH

POINT_SCROLL_MAX_PROGRESS_SAVAGE = point(xy=(376, 485), resolution=(1280, 800))
POINT_SCROLL_DEC_BTN_SAVAGE = point(xy=(178, 625), resolution=(1664, 1040))

# 粮食
POINT_SCROLL_MAX_PROGRESS_FARMLAND = point(xy=(550, 485), resolution=(1280, 800))
POINT_SCROLL_DEC_BTN_FARMLAND = point(xy=(311, 485), resolution=(1280, 800))

# 木头
POINT_SCROLL_MAX_PROGRESS_SAWMILL = point(xy=(742, 485), resolution=(1280, 800))
POINT_SCROLL_DEC_BTN_SAWMILL = point(xy=(507, 485), resolution=(1280, 800))

# 石头
POINT_SCROLL_MAX_PROGRESS_QUARRY = point(xy=(935, 485), resolution=(1280, 800))
POINT_SCROLL_DEC_BTN_QUARRY = point(xy=(692, 485), resolution=(1280, 800))

# 金矿
POINT_SCROLL_MAX_PROGRESS_GOLD_MINE = point(xy=(1124, 485), resolution=(1280, 800))
POINT_SCROLL_DEC_BTN_GOLD_MINE = point(xy=(888, 485), resolution=(1280, 800))

MAX_SAVAGE_LEVEL = 40

POINT_Q_X = point(xy=(698, 10), resolution=(1280, 800))
POINT_Q_Y = point(xy=(780, 32), resolution=(1280, 800))

POINT_TROOP_NUM_X = point(xy=(1213, 200), resolution=(1280, 800))
# POINT_TROOP_NUM_Y = point(xy=(1258, 218), resolution=(1280, 800))
POINT_TROOP_NUM_Y = point(xy=(1225, 218), resolution=(1280, 800))

POINT_TROOP_MAX_NUM_X = point(xy=(1229, 200), resolution=(1280, 800))
POINT_TROOP_MAX_NUM_Y = point(xy=(1240, 218), resolution=(1280, 800))

