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
import json


# returns a DXCamera instance on primary monitor
camera = dxcam.create(output_color="BGR")

northFile = "resources/north.jpg"
eastFile = "resources/east.jpg"
westFile = "resources/west.jpg"
playerIcon = "resources/player_icon.jpg"

MOVEMENT_ENABLED = False
MAX_DISTANCE = 20
MAX_ANGLE_OFFSET = 5


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
        self.target_dict = {}
        self.last_player_pos = None
        # open file with coordinates
        with open("test.txt", "r") as f:
            for line in f:
                line = line.strip()
                x, y = line.split(" ")
                self.target_list = np.append(
                    self.target_list, [[int(x), int(y)]], axis=0)

        with open("test_json.json", "r") as f:
            self.target_dict = json.load(f)
            print(self.target_dict)

        self.curr_point = 0
        self.movementStarted = False
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]

        self.lines_count = 0
        self.game_screenshot = None
        self.game_screenshot_past = None
        self.raw_img = None
        self.threshold = 0.7

        self.target_pos = None

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

        if (self.last_player_pos is not None):

            mask2 = np.full_like(img, 255)
            mask2 = cv.circle(
                mask2, (self.last_player_pos[0]-10, self.last_player_pos[1]-10), 20, (0, 0, 0), -1)
            # self.game_screenshot[:, :, 0] = mask2[:, :, 0]
            cv.subtract(self.game_screenshot, mask2, self.game_screenshot)
            cv.imshow("mask2", self.game_screenshot[750:1080, 1500:1920])
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

        self.last_player_pos = (x_player_c, y_player_c)

        return x_player_c, y_player_c

    def loop(self):
        loop_time = time()
        while (True):
            try:
                img = camera.grab()

                # check if there any targets in the list. If so, set next target to be tracked
                if (len(self.target_list) != 0):
                    self.target_pos = self.target_list[self.curr_point]

                # check if there is an image captured from screen
                if img is None:
                    continue

                # bad bad bad
                # make copies of raw image for different outputs.
                # Might change to make image as object with different versions
                self.game_screenshot = np.copy(img)
                self.raw_img = np.copy(img)

                # find player position
                player_position = self.find_player_pos(img)

                # check if plater is in target position with proximity of MAX_DISTANCE
                if (player_position is not None and self.target_pos is not None):
                    if (abs(player_position[0] - 1500 - self.target_pos[0]) < MAX_DISTANCE) and (abs(player_position[1] - 750 - self.target_pos[1]) < MAX_DISTANCE):
                        self.curr_point = (
                            self.curr_point + 1) % len(self.target_list)

                    # get and emit player position based on angle of player position from middle of map
                    angle = 0
                    angle = math.atan2(
                        (player_position[0] - self.target_pos[0] - 1500), (player_position[1] - self.target_pos[1] - 750))

                    self.playerPosSignal.emit(player_position)
                    self.targetPosSignal.emit(self.target_pos)

                    # get current mouse angle from middle of the screen
                    mouse_angle = math.atan2(
                        1920 / 2 - pyautogui.position()[0], 1080 / 2 - pyautogui.position()[1])
                    print(abs(mouse_angle - angle) * 180 / math.pi)

                if (not self.movementStarted):
                    self.movementStarted = True

                # check mouse offset of angle is based on mouse position from target angle to target
                # if mouse offset is greater than MAX_ANGLE_OFFSET, then move mouse to target
                # with ease in and out quartic
                if (abs(mouse_angle - angle) * 180 / math.pi > MAX_ANGLE_OFFSET):
                    # based on:
                    # https://gist.github.com/robweychert/7efa6a5f762207245646b16f29dd6671
                    def easeInOutQuart(t):
                        t *= 2
                        if t < 1:
                            return t * t * t * t / 2
                        else:
                            t -= 2
                            return -(t * t * t * t - 2) / 2

                    # position of mouse in angle direction with distance of 300 from center of screen
                    mouse_target_pos_x = 1920 / 2 - 300 * math.sin(angle)
                    mouse_target_pos_y = 1080 / 2 - 300 * math.cos(angle)

                    print(f"x : {300 * math.sin(angle)}")
                    print(f"y : {300 * math.cos(angle)}")

                    start_pos_x = pyautogui.position()[0]
                    start_pos_y = pyautogui.position()[1]

                    x_d = mouse_target_pos_x - start_pos_x
                    y_d = mouse_target_pos_y - start_pos_y

                    points_x = np.linspace(0, 1, 20)
                    points_y = np.linspace(0, 1, 20)

                    tmp_points_x = []
                    tmp_points_y = []
                    for i in points_x:
                        tmp_points_x.append(easeInOutQuart(
                            i) * (1 - np.sinc(i * np.pi*2)) * x_d)
                        tmp_points_y.append(easeInOutQuart(
                            i) * (1 - np.sinc(i * np.pi*3)) * y_d)

                    if (MOVEMENT_ENABLED):
                        for i in range(len(tmp_points_x)):
                            pyautogui.moveTo(start_pos_x + tmp_points_x[i],
                                             start_pos_y + tmp_points_y[i], 0)

                    # cv.waitKey(1000)

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
