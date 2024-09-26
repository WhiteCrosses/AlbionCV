from dataclasses import dataclass
import cv2 as cv
import numpy as np
from time import time, sleep
import matplotlib.pyplot as plt
import pyautogui
import mss
from multiprocessing import Process
from PIL import Image
import dxcam
import math
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# returns a DXCamera instance on primary monitor
camera = dxcam.create(output_color="BGR")

northFile = "resources/north.jpg"
eastFile = "resources/east.jpg"
westFile = "resources/west.jpg"
playerIcon = "resources/player_icon.jpg"


@dataclass
class FontSettings:
    font = cv.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (10, 50)
    fontScale = 0.75
    fontColor = (0, 0, 20)
    lineType = 2


class Bot(QThread):
    angleSignal = pyqtSignal(float)
    mapSignal = pyqtSignal(np.ndarray)
    playerPosSignal = pyqtSignal(tuple)
    targetPosSignal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.east = cv.imread(eastFile, cv.IMREAD_COLOR)
        self.north = cv.imread(northFile, cv.IMREAD_COLOR)
        self.west = cv.imread(westFile, cv.IMREAD_COLOR)
        self.player_icon = cv.imread(playerIcon, cv.IMREAD_COLOR)

        self.target_list = np.empty((0, 2), dtype=int)
        # open file with coordinates
        with open("test.txt", "r") as f:
            for line in f:
                line = line.strip()
                x, y = line.split(" ")
                self.target_list = np.append(
                    self.target_list, [[int(x), int(y)]], axis=0)

        self.curr_point = 0
        self.movementStarted = False
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]

        self.lines_count = 0
        self.game_screenshot = None
        self.game_screenshot_past = None
        self.raw_img = None
        self.threshold = 0.7

        self.target_pos = (200, 200)

        self.ease_start = time()

    def cvprint(self, text):
        """!
        @brief [Description de la fonction]

        Paramètres :
            @param self => [description]
            @param text => [description]

        """
        cv.putText(self.game_screenshot, text,
                   (50, 200 + self.lines_count*20), FontSettings.font,
                   FontSettings.fontScale, FontSettings.fontColor, FontSettings.lineType)
        self.lines_count += 1

    def easeInOutQuad(self, t):
        t *= 2
        if t < 1:
            return t * t / 2
        else:
            t -= 1
            return -(t * (t - 2) - 1) / 2

    def find_player_pos(self, img):
        blues = self.game_screenshot[:, :, 0]
        blues[blues < 200] = 0
        blues[self.game_screenshot[:, :, 1] >= 200] = 0
        self.game_screenshot[:, :, 0] = blues
        self.game_screenshot[:, :, 1] = 0
        self.game_screenshot[:, :, 2] = 0

        player_pos = cv.matchTemplate(
            self.game_screenshot[750:1080, 1500:1920], self.player_icon, cv.TM_CCORR)

        # =================================================
        if (player_pos.min() <= 0.5):
            player_y_coords,    player_x_coords = np.where(
                player_pos >= player_pos.max())

        player_y_coords = player_y_coords + 750
        player_x_coords = player_x_coords + 1500

        player_w = self.player_icon.shape[1]
        player_h = self.player_icon.shape[0]

        if (len(player_x_coords)):
            x_player, y_player = player_x_coords[0].astype(
                'float64'), player_y_coords[0].astype('float64')
            x_player_c = ((x_player + x_player + player_w) //
                          2).astype('int')
            y_player_c = ((y_player + y_player + player_h) //
                          2).astype('int')

        return x_player_c, y_player_c

    def loop(self):
        loop_time = time()
        while (True):
            try:
                img = camera.grab()
                self.target_pos = self.target_list[self.curr_point]
                if img is None:
                    continue

                self.game_screenshot = np.copy(img)
                self.raw_img = np.copy(img)

                if (img is None):
                    continue

                player_position = self.find_player_pos(img)

                if (player_position is not None):
                    if (abs(player_position[0] - 1500 - self.target_pos[0]) < 20) and (abs(player_position[1] - 750 - self.target_pos[1]) < 20):
                        self.curr_point = (
                            self.curr_point + 1) % len(self.target_list)

                angle = 0

                if (player_position is not None):
                    angle = math.atan2(
                        (player_position[0] - self.target_pos[0] - 1500), (player_position[1] - self.target_pos[1] - 750))

                    self.playerPosSignal.emit(player_position)
                    self.targetPosSignal.emit(self.target_pos)

                    # get current mouse angle from middle of the screen
                    mouse_angle = math.atan2(
                        1920 / 2 - pyautogui.position()[0], 1080 / 2 - pyautogui.position()[1])
                    print(abs(mouse_angle - angle) * 180 / math.pi)

                if (not self.movementStarted):
                    self.mouse_d_x = 1920 / 2 - 300 * \
                        math.sin(angle) - pyautogui.position()[0]
                    self.mouse_d_y = 1080 / 2 - 300 * \
                        math.cos(angle) - pyautogui.position()[1]
                    self.ease_start = time()
                    self.movementStarted = True

                if (abs(mouse_angle - angle) * 180 / math.pi > 5):
                    movement_duration = time() - self.ease_start

                    # pyautogui.moveTo(
                    #    pyautogui.position()[0] + self.easeInOutQuad(movement_duration / 10) * self.mouse_d_x, pyautogui.position()[1] + self.easeInOutQuad(movement_duration / 10) * self.mouse_d_y, 0.1)

                else:
                    self.movementStarted = False

                self.angleSignal.emit(angle * 180 / math.pi)

                raw_img_cpy = np.copy(self.raw_img[750:1080, 1500:1920])
                self.mapSignal.emit(raw_img_cpy)

                key = cv.waitKey(50)
                if key == ord('q'):
                    cv.destroyAllWindows()
                    exit()
                    break
                loop_time = time()
                self.game_screenshot_past = self.game_screenshot
            except Exception as e:
                print(e)
                cv.destroyAllWindows()
                exit()
                break

            self.lines_count = 0
