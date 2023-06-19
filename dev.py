
from airtest.core.helper import G
from common.tools import process_target_panel, init_env
from config.log import MainLogger


if __name__ == '__main__':

    adb_serial = "192.168.1.68:5555"
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
    process_target_panel(_screen)
