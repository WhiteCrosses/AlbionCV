
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
        layout = QVBoxLayout()

        pixmap = QPixmap(tmp_img_path)

        self.ima = QLabel()
        self.ima.setPixmap(pixmap)

        layout.addWidget(self.ima)
        self.setLayout(layout)

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
