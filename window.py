import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import threading


class MainWindow(QMainWindow):
    def __init__(self, stop_event, app):
        super().__init__()

        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.interval = 5000
        timer.timeout.connect(
            5000, app, slot=self.checkClosedWindow)
        timer.start()

        self.window(app)

    def window(self, app):

        w = QWidget()
        b = QLabel(w)
        b.setText("Hello World!")
        w.setGeometry(100, 100, 200, 50)
        b.move(50, 20)
        w.setWindowTitle("PyQt5")

        w.show()

    def checkClosedWindow(self, stop_event):
        if (stop_event.is_set()):
            self.close()
