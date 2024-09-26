from dataclasses import dataclass
import cv2 as cv
import numpy as np
import os
from time import time, sleep
from windowcapture import WindowCapture
import matplotlib.pyplot as plt
import pyautogui
import mss
import bot
import window
import threading
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # threadpool = QThreadPool()

    thread = QThread()

    window = window.MainWindow()

    bot = bot.Bot()
    bot.moveToThread(thread)
    bot.angleSignal.connect(window.setAngle)
    bot.mapSignal.connect(window.setMap)
    bot.playerPosSignal.connect(window.setPlayerPos)
    bot.targetPosSignal.connect(window.setTargetPos)

    thread.start()
    thread.started.connect(bot.loop)

    # bot.sig_carrier.bot_Signal.connect(window.setImage)
    # threadpool.start(bot)

    window.show()

    sys.exit(app.exec_())
    # bot = bot.Bot()
