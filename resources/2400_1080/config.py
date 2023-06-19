from airtest.utils.transform import TargetPos

config = {

    "screen_resolution": (2400, 1080),
    "templates": {
        # 信息提取
        "BTN_CE": {
            "path": "btn_ce.png",
            "rp": (0.082, -0.005),
            "r": (2400, 1080)
        },
        "BTN_USER_INFO": {
            "path": "btn_user_info.png",
            "rp": (-0.028, -0.03),
            "r": (2400, 1080)
        },
        "BTN_MORE_INFO": {
            "path": "btn_more_info.png",
            "rp": (-0.2, 0.103),
            "r": (2400, 1080),
            "th": 0.90
        },
        "BTN_CLOSE": {
            "path": "btn_close.png",
            "rp": (0.282, -0.173),
            "r": (2400, 1080)
        },
        "BTN_NAME_MORE": {
            "path": "btn_name_more.png",
            "rp": (-0.019, -0.081),
            "r": (2400, 1080)
        },
        "BTN_NAME_CLIPBOARD": {
            "path": "btn_name_clipboard.png",
            "rp": (-0.018, -0.127),
            "r": (2400, 1080)
        },
        "TAG_MORE_INFO": {
            "path": "tag_more_info.png",
            "rp": (0.002, -0.198),
            "r": (2400, 1080)
        },
        "BTN_KDA": {
            "path": "btn_kda.png",
            "rp": (0.16, -0.05),
            "r": (2400, 1080)
        },
        "TAG_KDA": {
            "path": "tag_kda.png",
            "rp": (0.033, 0.041),
            "r": (2400, 1080)
        },

        # 派遣

        "BTN_SEARCH": {
            "path": "btn_search.png",
            "rp": (-0.437, 0.107),
            "r": (2400, 1080)
        },

        "BTN_SAVAGE": {
            "path": "btn_savage.png",
            "rp": (-0.237, 0.156),
            "r": (2400, 1080)
        },

        "BTN_SEARCH_CONFIRM": {
            "path": "btn_search_confirm.png",
            "rp": (-0.226, 0.076),
            "r": (2400, 1080)
        },

        "ICON_TARGET_ARROW": {
            "path": "icon_target_arrow.png",
            "rp": (-0.0, -0.1),
            "r": (2400, 1080)
        },

        "BTN_ATTACK": {
            "path": "btn_attack.png",
            "rp": (0.175, 0.071),
            "r": (2400, 1080)
        },

        "BTN_COLLECTION": {
            "path": "btn_collection.png",
            "rp": (0.244, 0.096),
            "r": (1920, 1080)
        },

        "BTN_CREATE_TROOPS": {
            "path": "btn_create_troops.png",
            "rp": (0.302, -0.136),
            "r": (2400, 1080)
        },

        "BTN_TROOP_1": {
            "path": "btn_troop_1.png",
            "rp": (0.29, -0.023),
            "r": (2400, 1080),
            "th": 0.90
        },

        "BTN_MARCH": {
            "path": "btn_march.png",
            "rp": (0.182, 0.16),
            "r": (2400, 1080),
            "th": 0.90
        },

        "ICON_MARCHING": {
            "path": "icon_marching.png",
            "rp": (0.018, 0.061),
            "r": (2400, 1080),
            "th": 0.90
        },

        # Home

        "BTN_CANCEL": {
            "path": "btn_cancel.png",
            "rp": (0.101, 0.09),
            "r": (2400, 1080),
            "th": 0.90
        },

        "BTN_MAP": {
            "path": "btn_map.png",
            "rp": (-0.434, 0.185),
            "r": (2400, 1080),
            "th": 0.90
        },

        "BTN_HOME": {
            "path": "btn_home.png",
            "rp": (-0.434, 0.185),
            "r": (2400, 1080),
            "th": 0.90
        },

        "ICON_GEM": {
            "path": "btn_gem.png",
            "rp": (0.085, -0.038),
            "r": (2400, 1080),
            "tp": TargetPos.LEFTDOWN
        },

        "ICON_GEM_SMALL": {
            "path": "gem_small.png",
            "r": (2400, 1080),
            "tp": TargetPos.LEFTDOWN,
            "th": 0.90
        },

        "ICON_GEM_BIG": {
            "path": "gem_big.png",
            "r": (2400, 1080)
        },

        "ICON_TROOP_EXTEND": {
            "path": "icon_troop_extend.png",
            "r": (2400, 1080),
            "tp": TargetPos.LEFTUP,
            "th": 0.95
        },

        "ICON_POSITION_SEARCH": {
            "path": "icon_coor_search.png",
            "r": (2400, 1080),
            "tp": TargetPos.LEFTUP,
            "th": 0.95
        },

        # 矿点面板-更多图标
        "ICON_MORE": {
            "path": "icon_more.png",
            "r": (2400, 1080),
            "th": 0.95
        },

        # 矿点面板-分享
        "ICON_SHARE": {
            "path": "icon_share.png",
            "r": (2400, 1080),
            "th": 0.95
        },

    },
    "points": {

        # 数据采集

        "POINT_UID_X": {
            "xy": (1135, 289),
            "r": (2400, 1080)
        },
        "POINT_UID_Y": {
            "xy": (1285, 314),
            "r": (2400, 1080)
        },

        "POINT_UCE_X": {
            "xy": (1327, 441),
            "r": (2400, 1080)
        },
        "POINT_UCE_Y": {
            "xy": (1536, 469),
            "r": (2400, 1080)
        },

        # 更多信息
        "POINT_HCE_X": {
            "xy": (1625, 320),
            "r": (2400, 1080)
        },
        "POINT_HCE_Y": {
            "xy": (1805, 350),
            "r": (2400, 1080)
        },
        "POINT_DD_X": {
            "xy": (1625, 541),
            "r": (2400, 1080)
        },
        "POINT_DD_Y": {
            "xy": (1805, 573),
            "r": (2400, 1080)
        },
        "POINT_RG_X": {
            "xy": (1580, 746),
            "r": (2400, 1080)
        },
        "POINT_RG_Y": {
            "xy": (1805, 770),
            "r": (2400, 1080)
        },
        "POINT_HT_X": {
            "xy": (1625, 891),
            "r": (2400, 1080)
        },
        "POINT_HT_Y": {
            "xy": (1805, 921),
            "r": (2400, 1080)
        },
        "POINT_KDA_T1_X": {
            "xy": (1280, 681),
            "r": (2400, 1080)
        },
        "POINT_KDA_T1_Y": {
            "xy": (1485, 705),
            "r": (2400, 1080)
        },
        "POINT_KDA_T2_X": {
            "xy": (1280, 730),
            "r": (2400, 1080)
        },
        "POINT_KDA_T2_Y": {
            "xy": (1485, 760),
            "r": (2400, 1080)
        },
        "POINT_KDA_T3_X": {
            "xy": (1280, 782),
            "r": (2400, 1080)
        },
        "POINT_KDA_T3_Y": {
            "xy": (1485, 813),
            "r": (2400, 1080)
        },
        "POINT_KDA_T4_X": {
            "xy": (1280, 836),
            "r": (2400, 1080)
        },
        "POINT_KDA_T4_Y": {
            "xy": (1485, 867),
            "r": (2400, 1080)
        },
        "POINT_KDA_T5_X": {
            "xy": (1280, 888),
            "r": (2400, 1080)
        },
        "POINT_KDA_T5_Y": {
            "xy": (1485, 916),
            "r": (2400, 1080)
        },

        "POINT_LEADER_BOARD_NEXT": {
            "xy": (1228, 736),
            "r": (1920, 1080)
        },

        "POINT_LEADER_BOARD_RANK_X": {
            "xy": (471, 685),
            "r": (1920, 1080)
        },

        "POINT_LEADER_BOARD_RANK_Y": {
            "xy": (530, 750),
            "r": (1920, 1080)
        },

        # 派遣

        "POINT_SCROLL_MAX_PROGRESS_SAVAGE": {
            "xy": (807, 605),
            "r": (2400, 1080)
        },

        "POINT_SCROLL_DEC_BTN_SAVAGE": {
            "xy": (854, 612),
            "r": (2400, 1080)
        },

        "POINT_FIRST_TROOP": {
            "xy": (2257, 329),
            "r": (2400, 1080)
        },

        "POINT_TROOP_NUM_X": {
            "xy": (2230, 244),
            "r": (2400, 1080)
        },

        "POINT_TROOP_NUM_Y": {
            "xy": (2247, 263),
            "r": (2400, 1080)
        },

        # 坐标

        # "POINT_CD_NUM_X1": {
        #     "xy": (592, 20),
        #     "r": (2400, 1080)
        # },

        "POINT_CD_NUM_X1": {
            "xy": (570, 20),
            "r": (2400, 1080)
        },

        "POINT_CD_NUM_Y1": {
            "xy": (645, 40),
            "r": (2400, 1080)
        },

        "POINT_CD_NUM_X2": {
            "xy": (664, 20),
            "r": (2400, 1080)
        },

        "POINT_CD_NUM_Y2": {
            "xy": (712, 40),
            "r": (2400, 1080)
        },

        "POINT_COR_TOP": {
            "xy": (475, 16),
            "r": (2400, 1080)
        },

        "POINT_COR_BOTTOM": {
            "xy": (709, 42),
            "r": (2400, 1080)
        },

    }

}
