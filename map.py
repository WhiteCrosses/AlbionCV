
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import threading
from urllib.request import urlopen
import time
import cv2
import numpy as np

app = QApplication(sys.argv)
tmp_img_path = "resources/map.jpg"


class Map(QWidget):
    def __init__(self):
        super(Map, self).__init__()
        # Initialize tab screen
        layout = QHBoxLayout()

        self.left_column = QVBoxLayout()
        self.right_column = QGridLayout()

        self._leftColumnInit()
        self._rightColumnInit()

        layout.addLayout(self.left_column)
        layout.addLayout(self.right_column)

        self.setLayout(layout)

    def _leftColumnInit(self):
        pixmap = QPixmap(tmp_img_path)

        self.ima = QLabel()
        self.ima.setPixmap(pixmap)

        self.left_column.addWidget(self.ima)

    def _rightColumnInit(self):
        self.player_pos_display = QLabel()
        self.target_pos_display = QLabel()

        self.player_pos_display.setFrameShadow(1)
        self.target_pos_display.setFrameShadow(1)

        self.player_pos_display.setText(f"123, 456")
        self.target_pos_display.setText(f"654, 321")

        self.right_column.addWidget(self.player_pos_display, 0, 0, 1, 1)
        self.right_column.addWidget(self.target_pos_display, 1, 0, 1, 1)
        self.right_column.addWidget(QWidget(), 2, 0, 8, 1)

    def drawPlayerPos(self, pos):
        painter = QPainter()
        painter.begin(self.ima.pixmap())
        painter.drawEllipse(pos[0] - 1500 - 5, pos[1] - 750 - 5, 10, 10)
        painter.end()
        self.ima.update()

    def drawTargetPos(self, pos):
        painter = QPainter()

        painter.begin(self.ima.pixmap())
        painter.setPen(QPen(Qt.red, 4, Qt.SolidLine))
        painter.drawEllipse(pos[0] - 5, pos[1] - 5, 10, 10)
        painter.end()
        self.ima.update()
