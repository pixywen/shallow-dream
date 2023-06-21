import logging
import sys
import time

import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, \
    QGroupBox, QScrollArea
import argparse
import threading

from airtest.core import cv
from airtest.core.android.cap_methods.minicap import Minicap
from airtest.core.api import device

from config.log import MainLogger
from miner import init_miner, stop_greedy_miner, greedy_miner_ex


class LogHandler(logging.Handler):
    def __init__(self, log_output):
        super().__init__()
        self.log_output = log_output

    def emit(self, record):
        msg = self.format(record)
        self.log_output.append(msg)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())  # 自动滚动到底部


class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("配置窗口")
        self.resize(500, 800)

        # 创建界面元素
        self.serial_label = QLabel("ADB Serial:")
        self.serial_edit = QLineEdit()
        self.host_label = QLabel("Host:")
        self.host_edit = QLineEdit()
        self.port_label = QLabel("Port:")
        self.port_edit = QLineEdit()
        self.x_label = QLabel("X:")
        self.x_edit = QLineEdit()
        self.y_label = QLabel("Y:")
        self.y_edit = QLineEdit()

        button_layout = QHBoxLayout()
        self.init_button = QPushButton("初始化")
        self.start_button = QPushButton("开始脚本")
        self.stop_button = QPushButton("停止脚本")
        self.operation_button = QPushButton("操作")
        button_layout.addWidget(self.init_button)
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.operation_button)

        self.init_button.clicked.connect(self.init_env)
        self.start_button.clicked.connect(self.start_script)
        self.stop_button.clicked.connect(self.stop_script)
        self.operation_button.clicked.connect(self.toggle_preview)

        # 创建日志输出框
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.log_output)
        scroll_area.setWidgetResizable(True)

        # 创建预览区域

        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)

        main_layout.addWidget(self.serial_label)
        main_layout.addWidget(self.serial_edit)
        main_layout.addWidget(self.host_label)
        main_layout.addWidget(self.host_edit)
        main_layout.addWidget(self.port_label)
        main_layout.addWidget(self.port_edit)
        main_layout.addWidget(self.x_label)
        main_layout.addWidget(self.x_edit)
        main_layout.addWidget(self.y_label)
        main_layout.addWidget(self.y_edit)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)
        log_handler = LogHandler(self.log_output)
        MainLogger.addHandler(log_handler)
        MainLogger.setLevel(logging.INFO)

        self.greedy_miner_thread = None
        self.greedy_miner_lock = threading.Lock()

    def init_env(self):
        if self.greedy_miner_thread and self.greedy_miner_thread.is_alive():
            self.log_output.append("已经有一个脚本在运行")
            return

        # 获取配置参数
        adb_serial = self.serial_edit.text()
        host = self.host_edit.text()
        port = self.port_edit.text()
        x = self.x_edit.text()
        y = self.y_edit.text()

        if not port:
            port = '5555'

        if not host:
            host = '127.0.0.1'

        # 默认将 x 和 y 设置为 0
        if not x:
            x = '0'
        if not y:
            y = '0'

        # 将 x 和 y 拼接成城市坐标字符串
        city = f"({x},{y})"

        # 在日志输出框中显示参数
        self.log_output.append(f"adb_serial: {adb_serial}")
        self.log_output.append(f"host: {host}")
        self.log_output.append(f"port: {port}")
        self.log_output.append(f"city: {city}")

        init_miner(adb_serial, host, port, city)
        time.sleep(0.5)
        # self.preview_widget = PreviewWidget()
        # self.preview_widget.hide()

    def start_script(self):
        # 检查是否已经有 greedy_miner 线程在运行
        # 创建并启动 greedy_miner 线程
        self.greedy_miner_thread = threading.Thread(target=self.run_greedy_miner, args=())
        self.greedy_miner_thread.start()

    def stop_script(self):
        # 检查是否有 greedy_miner 线程在运行
        if self.greedy_miner_thread and self.greedy_miner_thread.is_alive():
            stop_greedy_miner()

        if self.greedy_miner_thread and self.greedy_miner_thread.is_alive():
            # 获取线程锁
            with self.greedy_miner_lock:
                self.log_output.append("停止脚本运行")
        else:
            self.log_output.append("没有脚本在运行")

    def run_greedy_miner(self):
        # 获取线程锁
        with self.greedy_miner_lock:
            greedy_miner_ex()

    def toggle_preview(self):
        #self.mini_frame()
        pass

    def mini_frame(self):
        cap = Minicap(device().adb)

        cv2.namedWindow("image", cv2.WINDOW_NORMAL)

        while True:
            image_bytes = cap.get_frame_from_stream()
            img = cv2.imdecode(np.fromstring(image_bytes, np.uint8), cv2.IMREAD_COLOR)
            cv2.imshow('image', img)
            cv2.waitKey(16)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec_())
