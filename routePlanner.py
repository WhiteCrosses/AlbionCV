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


class RoutePlanner(QWidget):
    def __init__(self):
        super(RoutePlanner, self).__init__()
        self.map_requested = False
        self.point_list = []

        layout = QHBoxLayout()

        self.left_column = QVBoxLayout()
        self.right_column = QVBoxLayout()

        request_map_btn = QPushButton("Request Map")
        try_again_btn = QPushButton("Try Again")
        save_btn = QPushButton("Save")
        self.list_widget = QListWidget()
        self.map_widget = QLabel()

        self.left_column.addWidget(request_map_btn)
        self.left_column.addWidget(try_again_btn)
        self.left_column.addWidget(save_btn)
        self.left_column.addWidget(self.list_widget)

        self.right_column.addWidget(self.map_widget)

        request_map_btn.clicked.connect(self.request_map)
        try_again_btn.clicked.connect(self.reset_path)
        save_btn.clicked.connect(self.save_current_map)

        layout.addLayout(self.left_column)
        layout.addLayout(self.right_column)

        self.setLayout(layout)

    def mousePressEvent(self, event):
        # get mouse position

        x = event.pos().x() - self.map_widget.pos().x()
        y = event.pos().y() - self.map_widget.pos().y()

        self.list_widget.addItem(f"({x}, {y})")
        self.point_list.append((x, y))

        painter = QPainter()
        painter.begin(self.map_widget.pixmap())

        if len(self.point_list) > 1:
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))

            painter.drawLine(self.point_list[len(self.point_list) - 2][0], self.point_list[len(self.point_list) - 2]
                             [1], self.point_list[len(self.point_list) - 1][0], self.point_list[len(self.point_list) - 1][1])

        painter.drawEllipse(x-2, y-2, 4, 4)
        painter.end()

        self.map_widget.update()

    def request_map(self):
        self.map_requested = True

    def reset_path(self):
        self.list_widget.clear()
        self.point_list = []

    def save_current_map(self):
        # save to txt file
        path = "test.txt"
        with open(path, "w") as f:
            for point in self.point_list:
                f.write(f"{point[0]} {point[1]}\n")
