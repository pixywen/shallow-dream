import time

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer
from airtest.core.android.cap_methods.minicap import Minicap
import subprocess
import cv2 as cv
import numpy as np
from airtest.core.api import device


class PreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("预览区域")
        self.setFixedSize(768, 1800)

        # 创建用于显示模拟器截图的标签
        self.preview_label = QLabel(self)
        self.preview_label.setFixedSize(768, 1800)

        # 垂直布局
        layout = QVBoxLayout()
        layout.addWidget(self.preview_label)
        self.setLayout(layout)

        # 开始获取模拟器截图
        self.start_preview()

    def start_preview(self):
        # 调用 minicap 获取模拟器截图
        cap = Minicap(device().adb)
        image_bytes = cap.get_frame_from_stream()

        # 将图像数据转换为 QImage
        image = QImage(image_bytes, 1080, 2400, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)

        # 缩放图片以适应窗口大小
        scaled_pixmap = pixmap.scaled(768, 1800)

        # 显示截图
        self.preview_label.setPixmap(scaled_pixmap)
        time.sleep(40)

        # 每隔一段时间更新截图
        QTimer.singleShot(1000, self.start_preview)

    def mousePressEvent(self, event):
        # 获取鼠标点击的坐标
        x = event.pos().x()
        y = event.pos().y()

        # 调用 airtest 实现点击操作透传至模拟器
        subprocess.run(['adb', 'shell', f'input tap {x} {y}'], shell=True)


if __name__ == "__main__":
    app = QApplication([])
    widget = PreviewWidget()
    widget.show()
    app.exec_()
