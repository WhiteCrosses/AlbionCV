import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import threading
from urllib.request import urlopen
import time
import cv2
import numpy as np
import map
import routePlanner

app = QApplication(sys.argv)
tmp_img_path = "resources/map.jpg"


class Path(QWidget):
    def __init__(self):
        super(Path, self).__init__()
        self.route = None

        layout = QHBoxLayout()

        left_column = QVBoxLayout()
        right_column = QVBoxLayout()

        new_route_btn = QPushButton("New Route")
        save_curr_map_btn = QPushButton("Save current map")
        load_route_btn = QPushButton("Load Route")
        self.angle_text = QLabel(f"Angle: ")

        left_column.addWidget(new_route_btn)
        left_column.addWidget(save_curr_map_btn)
        left_column.addWidget(self.angle_text)

        new_route_btn.clicked.connect(self.new_route)
        load_route_btn.clicked.connect(self.load_route)
        save_curr_map_btn.clicked.connect(self.save_current_map)

        pixmap = QPixmap(tmp_img_path)
        ima = QLabel()
        ima.setPixmap(pixmap)
        right_column.addWidget(ima)

        layout.addLayout(left_column)
        layout.addLayout(right_column)

        self.setLayout(layout)

    def save_current_map(self):
        pass

    def new_route(self):
        self.route = routePlanner.RoutePlanner()
        self.route.show()

    def load_route(self):
        path = "test.txt"
        with open(path, "r") as f:
            for line in f:
                x, y = line.strip().split()
                self.route.list_widget.addItem(f"({x}, {y})")
                self.route.point_list.append((int(x), int(y)))


class MainWindow(QMainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.angle = 0
        self.playerPos = (0, 0)

        mainWidget = QWidget()

        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.tab1 = map.Map()
        self.tab2 = Path()
        self.tabs.resize(300, 200)

        # Add tabs
        self.tabs.addTab(self.tab1, "Map")
        self.tabs.addTab(self.tab2, "Path")

        layout.addWidget(self.tabs)
        mainWidget.setLayout(layout)

        self.setCentralWidget(mainWidget)

    def keyPressEvent(self, e):  # doesnt work when app is in background
        if e.key() == Qt.Key_Q:
            self.close()

    def setAngle(self, angle):
        self.tab2.angle_text.setText(f"Angle: {angle}")

    def setMap(self, img):

        height, width, channel = img.shape
        bytesPerLine = 3 * width
        qImg = QImage(img.data, width, height,
                      bytesPerLine, QImage.Format_RGB888).rgbSwapped()
        if (self.tab2.route is not None):
            if (self.tab2.route.map_requested):
                self.tab2.route.map_requested = False
                self.tab2.route.map_widget.setPixmap(QPixmap(qImg))

        self.tab1.ima.setPixmap(QPixmap(qImg))
        self.setPlayerPos(self.playerPos)
        self.setTargetPos(self.targetPos)

    def setPlayerPos(self, pos):
        self.playerPos = pos
        self.tab1.drawPlayerPos(pos)

    def setTargetPos(self, pos):
        self.targetPos = pos
        self.tab1.drawTargetPos(pos)


if __name__ == '__main__':
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
