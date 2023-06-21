
from airtest.core.helper import G

from common import constants
from common.tools import process_target_panel, init_env, click, send_card_notification
from config.log import MainLogger


if __name__ == '__main__':


    send_card_notification("","[告警]有一个错误2")
    exit()


    adb_serial = "192.168.1.56:5555"
    host = "127.0.0.1"
    port = "5555"

    CR, R, Dev = init_env(adb_serial, host, port)

    # while True:
    #     _screen = G.DEVICE.snapshot(quality=1)
    #     x,y,d = get_current_coordinates(_screen,(269, 1057))
    #     cv.waitKey(1)

    #deploy_gem_squad_ex(5, 60 * 5)
    MainLogger.info("Dev Tools")
    _screen = G.DEVICE.snapshot(quality=1)
    _r = constants.RM.get("BTN_VERIFY").match_in(_screen)
    MainLogger.info(_r)
    click(_r)

    #process_target_panel(_screen)
