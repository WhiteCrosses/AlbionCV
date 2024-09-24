from dataclasses import dataclass
import cv2 as cv
import numpy as np
import os
from time import time, sleep
import matplotlib.pyplot as plt
import pyautogui
import mss
from multiprocessing import Process
import win32gui
from PIL import Image
import dxcam

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

# bot class takes bool thread exit value as argument


class Bot:
    def __init__(self):
        self.east = cv.imread(eastFile, cv.IMREAD_COLOR)
        self.north = cv.imread(northFile, cv.IMREAD_COLOR)
        self.west = cv.imread(westFile, cv.IMREAD_COLOR)
        self.player_icon = cv.imread(playerIcon, cv.IMREAD_COLOR)

        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]

        self.lines_count = 0
        self.game_screenshot = None
        self.game_screenshot_past = None
        self.threshold = 0.7

        loop = self.loop()

    def cvprint(self, text):
        cv.putText(self.game_screenshot, text,
                   (50, 200 + self.lines_count*20), FontSettings.font,
                   FontSettings.fontScale, FontSettings.fontColor, FontSettings.lineType)
        self.lines_count += 1

    def run(self):
        self.loop()

    def find_player_pos(self, img):
        blues = self.game_screenshot[:, :, 0]
        blues[blues < 200] = 0
        blues[self.game_screenshot[:, :, 1] >= 200] = 0
        self.game_screenshot[:, :, 0] = blues
        self.game_screenshot[:, :, 1] = 0
        self.game_screenshot[:, :, 2] = 0

        player_pos = cv.matchTemplate(
            self.game_screenshot[750:1080, 1500:1920], self.player_icon, cv.TM_CCORR)

        cv.imshow(
            "test2", player_pos)

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
            # x_player /= width_reset_multiplier
            # y_player /= height_reset_multiplier
            x_player_c = ((x_player + x_player + player_w) //
                          2).astype('int')
            y_player_c = ((y_player + y_player + player_h) //
                          2).astype('int')

        cv.circle(self.game_screenshot, (x_player_c,
                                         y_player_c), 10, (255, 0, 0), 2)

        # self.cvprint(('FPS {}'.format(1 / (time() - loop_time))))

        return x_player_c, y_player_c

    def loop(self):
        loop_time = time()
        while (True):
            try:
                img = camera.grab()
                if img is None:
                    continue

                self.game_screenshot = img

                if (img is None):
                    continue

                if (self.game_screenshot_past is not None):
                    cv.imshow(
                        "test", self.game_screenshot_past[750:1080, 1500:1920])

                player_position = self.find_player_pos(img)
                print(player_position)

                key = cv.waitKey(1)
                if key == ord('q'):
                    cv.destroyAllWindows()
                    break
                loop_time = time()
                self.game_screenshot_past = self.game_screenshot
            except Exception as e:
                print(e)
                cv.destroyAllWindows()
                break

            self.lines_count = 0
