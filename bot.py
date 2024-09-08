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


northFile = "north.jpg"
eastFile = "east.jpg"
westFile = "west.jpg"
playerIcon = "player_icon.jpg"


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
        print(self.monitor)
        self.lines_count = 0
        self.game_screenshot = None

        self.threshold = 0.7
        DEBUG = True
        # self.wincap = WindowCapture("Albion Online Client")

        loop = self.loop()

    def cvprint(self, text):
        cv.putText(self.game_screenshot, text,
                   (50, 200 + self.lines_count*20), FontSettings.font,
                   FontSettings.fontScale, FontSettings.fontColor, FontSettings.lineType)
        self.lines_count += 1

    def run(self):
        self.loop()

    def loop(self):

        # self.wincap.start()
        self.hwnd = win32gui.FindWindow(None, "Albion Online Client")

        loop_time = time()
        while (True):
            try:
                img = self.sct.grab(self.monitor)

                game_screenshot = np.array(img)
                game_screenshot = game_screenshot[..., :3]
                self.game_screenshot = np.ascontiguousarray(game_screenshot)

                north_result = cv.matchTemplate(
                    self.game_screenshot, self.north, cv.TM_CCOEFF_NORMED)

                west_result = cv.matchTemplate(
                    self.game_screenshot, self.west, cv.TM_CCOEFF_NORMED)

                north_pos = cv.matchTemplate(
                    self.game_screenshot, self.north, cv.TM_CCOEFF_NORMED)

                west_pos = cv.matchTemplate(
                    self.game_screenshot, self.west, cv.TM_CCOEFF_NORMED)

                player_pos = cv.matchTemplate(
                    self.game_screenshot[750:1080, 1500:1920], self.player_icon, cv.TM_CCOEFF_NORMED)

                # =================================================

                north_y_coords,     north_x_coords = np.where(
                    north_result >= self.threshold)

                west_y_coords,      west_x_coords = np.where(
                    west_result >= self.threshold)

                player_y_coords,    player_x_coords = np.where(
                    player_pos >= player_pos.max())

                tmp_img = player_pos
                cv.imshow("tmp", tmp_img)

                cv.waitKey(0)

                player_y_coords = player_y_coords + 750
                player_x_coords = player_x_coords + 1500

                print(player_x_coords, player_y_coords)

                width_reset_multiplier = self.game_screenshot.shape[1] / \
                    self.monitor["width"]
                height_reset_multiplier = self.game_screenshot.shape[0] / \
                    self.monitor["height"]

                w_north = self.north.shape[1]
                h_north = self.north.shape[0]

                w_west = self.west.shape[1]
                h_west = self.west.shape[0]

                player_w = self.player_icon.shape[1]
                player_h = self.player_icon.shape[0]

                if (len(north_x_coords)):
                    x_north, y_north = north_x_coords[0].astype(
                        'float64'),  north_y_coords[0].astype('float64')
                    # x_north /= width_reset_multiplier
                    # y_north /= height_reset_multiplier

                    x_north_c = ((x_north + x_north + w_north) //
                                 2).astype('int')
                    y_north_c = ((y_north + y_north + h_north) //
                                 2).astype('int')

                if (len(west_x_coords)):
                    x_west, y_west = west_x_coords[0].astype(
                        'float64'),   west_y_coords[0].astype('float64')
                    # x_west /= width_reset_multiplier
                    # y_west /= height_reset_multiplier
                    x_west_c = ((x_west + x_west + w_west) // 2).astype('int')
                    y_west_c = ((y_west + y_west + h_west) // 2).astype('int')

                if (len(player_x_coords)):
                    x_player, y_player = player_x_coords[0].astype(
                        'float64'), player_y_coords[0].astype('float64')
                    # x_player /= width_reset_multiplier
                    # y_player /= height_reset_multiplier
                    x_player_c = ((x_player + x_player + player_w) //
                                  2).astype('int')
                    y_player_c = ((y_player + y_player + player_h) //
                                  2).astype('int')

                # Draw circles on points found
                cv.circle(self.game_screenshot, (x_north_c,
                                                 y_north_c), 10, (255, 0, 0), 2)
                cv.circle(self.game_screenshot, (x_player_c,
                                                 y_player_c), 10, (255, 0, 0), 2)

                west_border = x_west_c
                north_border = y_north_c

                # draw rectangle from 3 points and calculate fourth

                point_1 = (west_border, north_border)
                point_2 = (west_border + 2*(west_border-x_north_c),
                           north_border + 2*(north_border-y_north_c))

                new_point_1 = (0, 0)
                new_point_2 = (point_2[0] - point_1[0],
                               point_2[1] - point_1[1])

                player_relative_coords = (
                    int(x_player - point_1[0]), int(y_player - point_1[1]))

                cv.rectangle(self.game_screenshot, point_1,
                             (point_1[0] + 360, point_1[1] + 250), (0, 255, 0), 2)

                self.cvprint(('FPS {}'.format(1 / (time() - loop_time))))

                loop_time = time()
                cv.imshow('Game screenshot', self.game_screenshot)
                key = cv.waitKey(1)
                if key == ord('q'):
                    cv.destroyAllWindows()
                    break
                self.game_screenshot = None
            except Exception as e:
                print(e)
                cv.destroyAllWindows()
                break

            self.lines_count = 0
            self.game_screenshot = np.zeros_like(self.game_screenshot)
