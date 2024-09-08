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

if __name__ == '__main__':
    bot = bot.Bot()
